"""
models:
- mistralai/Mistral-7B-Instruct-v0.3
- meta-llama/Meta-Llama-3.1-8B-Instruct
- Qwen/Qwen2.5-7B-Instruct
"""
#!/usr/bin/env python3

import click
import os
import sys
from pathlib import Path
from tqdm import tqdm

from src.pdf_extractor import PDFExtractor
from src.text_chunker import TextChunker
from src.note_generator import NoteGenerator
from src.api_note_generator import APIBasedNoteGenerator
from src.markdown_formatter import MarkdownFormatter
from src.gpu_optimizer import GPUOptimizer
from src.bookmark_chunker import BookmarkChunker


@click.command()
@click.argument('pdf_path', type=click.Path(exists=True), required=False)
@click.option('--model', '-m', default="microsoft/DialoGPT-medium",
              help='HuggingFace model to use for note generation')
@click.option('--chunk-size', '-c', default=2048,
              help='Maximum tokens per text chunk')
@click.option('--overlap', '-o', default=200,
              help='Token overlap between chunks')
@click.option('--output-dir', '-d', default="output",
              help='Output directory for generated notes')
@click.option('--obsidian', is_flag=True,
              help='Generate Obsidian-compatible markdown')
@click.option('--device', default="auto",
              help='Device to use: auto, cpu, cuda, or mps')
@click.option('--pages', '-p', default=None,
              help='Page range to process (e.g., "1-10" or "5,7,9-12")')
@click.option('--auto-optimize', is_flag=True, default=True,
              help='Automatically optimize settings based on GPU (default: True)')
@click.option('--show-gpu-info', is_flag=True,
              help='Show GPU analysis and exit')
@click.option('--use-api', is_flag=True,
              help='Use Claude API instead of local models (requires CLAUDE_KEY in .env)')
@click.option('--api-model', default="claude-3-5-sonnet-20241022",
              help='Claude API model to use (sonnet or haiku)')
@click.option('--auto', is_flag=True,
              help='Auto-detect book structure from PDF bookmarks (recommended)')
def main(pdf_path, model, chunk_size, overlap, output_dir, obsidian, device, pages, auto_optimize, show_gpu_info, use_api, api_model, auto):
    """
    Extract and generate structured notes from PDF documents.

    This tool processes technical PDFs and creates comprehensive markdown notes
    optimized for knowledge management systems like Obsidian.
    """

    # Initialize GPU optimizer
    gpu_optimizer = GPUOptimizer()

    # Show GPU info and exit if requested
    if show_gpu_info:
        gpu_optimizer.print_gpu_analysis()
        return

    # Check if PDF path is provided when not showing GPU info
    if not pdf_path:
        click.echo("❌ Error: PDF_PATH is required unless using --show-gpu-info", err=True)
        click.echo("Try 'python main.py --help' for usage information.")
        sys.exit(1)

    # Auto-optimize settings if enabled (skip if using API)
    # if auto_optimize and not use_api:
    optimized = gpu_optimizer.get_optimized_settings()

        # Override defaults with optimized settings if not explicitly set by user
       # if model == "microsoft/DialoGPT-medium":  # Default model
       #     model = optimized['recommended_model']
       # if chunk_size == 2048:  # Default chunk size
       #     chunk_size = optimized['chunk_size']

    click.echo("🎯 GPU Auto-Optimization Enabled")
    click.echo(f"   Detected: {optimized['gpu_name']} ({optimized['vram_gb']}GB)")
    click.echo(f"   Tier: {optimized.get('performance_tier', 'Basic')}")

    click.echo(f"🔍 Processing PDF: {pdf_path}")

    if auto:
        click.echo(f"📚 Auto mode: Will detect structure from PDF bookmarks")

    if use_api:
        click.echo(f"🌐 Using Claude API: {api_model}")
        click.echo(f"💰 Note: API calls will consume tokens from your account")
    else:
        click.echo(f"🤖 Using local model: {model}")
        click.echo(f"📱 Device: {device}")

    click.echo(f"📏 Chunk size: {chunk_size} tokens")

    if not os.path.exists(pdf_path):
        click.echo(f"❌ Error: PDF file not found: {pdf_path}", err=True)
        sys.exit(1)

    try:
        # Initialize components
        click.echo("🔧 Initializing components...")

        # Parse page range if specified
        start_page, end_page = None, None
        if pages:
            page_list = parse_pages(pages)
            start_page = page_list[0]  # 1-based
            end_page = page_list[-1]   # 1-based
            click.echo(f"📄 Page range: {start_page}-{end_page}")

        # Try auto mode (bookmark-based chunking) if --auto flag is set
        use_bookmark_chunking = False
        all_chunks = []

        if auto:
            click.echo("🔍 Checking for PDF bookmarks...")
            try:
                with BookmarkChunker(pdf_path, chunk_size, overlap) as chunker:
                    if chunker.has_bookmarks():
                        click.echo("✅ Bookmarks found! Using structure-aware chunking...")
                        use_bookmark_chunking = True

                        # Extract structured chunks
                        all_chunks = chunker.chunk_by_bookmarks(start_page, end_page)

                        if not all_chunks:
                            click.echo("⚠️  No content in specified page range", err=True)
                            sys.exit(1)

                        click.echo(f"📚 Created {len(all_chunks)} structured chunks")
                    else:
                        click.echo("⚠️  No bookmarks found, falling back to token-based chunking...")
            except Exception as e:
                click.echo(f"⚠️  Bookmark extraction failed: {e}")
                click.echo("   Falling back to token-based chunking...")

        # Fallback to traditional token-based chunking if auto mode failed or not requested
        if not use_bookmark_chunking:
            with PDFExtractor(pdf_path) as extractor:
                # Extract text from PDF
                click.echo("📖 Extracting text from PDF...")
                if pages:
                    # Extract specified page range as one continuous block
                    text = extractor.get_text_by_pages(start_page - 1, end_page)
                    if text.strip():
                        from src.pdf_extractor import ExtractedText
                        extracted_sections = [ExtractedText(
                            content=text,
                            page_number=start_page,
                            chapter_title=""
                        )]
                    else:
                        extracted_sections = []
                else:
                    extracted_sections = extractor.extract_text()

                if not extracted_sections:
                    click.echo("❌ No text extracted from PDF", err=True)
                    sys.exit(1)

                click.echo(f"📄 Extracted {len(extracted_sections)} sections")

            # Initialize chunker and chunk text
            click.echo("✂️ Chunking text...")
            chunker = TextChunker(max_chunk_size=chunk_size, overlap_size=overlap)

            for section in extracted_sections:
                chunks = chunker.smart_chunk(
                    section.content,
                    [section.page_number],
                    section.chapter_title
                )
                all_chunks.extend(chunks)

            click.echo(f"📝 Created {len(all_chunks)} text chunks")

        # Initialize note generator
        click.echo("🧠 Loading language model...")
        if use_api:
            note_generator = APIBasedNoteGenerator(model_name=api_model)
        else:
            note_generator = NoteGenerator(model_name=model, device=device)

        # Generate notes
        click.echo("✍️ Generating notes...")

        # Generate notes differently based on chunking mode
        if use_bookmark_chunking:
            # For structured chunks, pair them with generated notes
            structured_notes = []

            with tqdm(total=len(all_chunks), desc="Processing chunks") as pbar:
                for chunk in all_chunks:
                    # Generate note for this structured chunk
                    note = note_generator.generate_note_from_chunk(chunk)
                    structured_notes.append((chunk, note))
                    pbar.update(1)

            # Format structured notes with hierarchy
            click.echo("📋 Formatting structured notes...")
            formatter = MarkdownFormatter(output_dir)
            markdown_content = formatter.format_structured_notes_to_markdown(
                structured_notes,
                pdf_path,
                model_name=note_generator.model_name
            )

        else:
            # Traditional note generation and formatting
            with tqdm(total=len(all_chunks), desc="Processing chunks") as pbar:
                notes = []
                for chunk in all_chunks:
                    note = note_generator.generate_note_from_chunk(chunk)
                    notes.append(note)
                    pbar.update(1)

            # Format and save notes
            click.echo("📋 Formatting notes...")
            formatter = MarkdownFormatter(output_dir)

            if obsidian:
                markdown_content = formatter.create_obsidian_compatible_note(notes, pdf_path)
            else:
                markdown_content = formatter.format_notes_to_markdown(
                    notes,
                    pdf_path,
                    model_name=note_generator.model_name
                )

        output_path = formatter.save_markdown_file(markdown_content, pdf_path)

        # Generate summary (only for traditional mode)
        if not use_bookmark_chunking:
            summary_content = formatter.create_summary_section(notes, pdf_path)
            summary_path = output_path.replace('.md', '_summary.md')
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            click.echo(f"📊 Summary saved to: {summary_path}")

        click.echo(f"✅ Notes saved to: {output_path}")
        click.echo(f"📈 Generated notes from {len(all_chunks)} chunks")

    except Exception as e:
        click.echo(f"❌ Error processing PDF: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def parse_pages(pages_str):
    """Parse page specification like '1-10' or '5,7,9-12' into list of page numbers."""
    pages = []
    parts = pages_str.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))

    return sorted(list(set(pages)))

def kevstest():
    Path("")

if __name__ == '__main__':
    main()
