#!/usr/bin/env python3

import click
import os
import sys
from pathlib import Path
from tqdm import tqdm

from src.pdf_extractor import PDFExtractor
from src.text_chunker import TextChunker
from src.note_generator import NoteGenerator
from src.markdown_formatter import MarkdownFormatter


@click.command()
@click.argument('pdf_path', type=click.Path(exists=True))
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
def main(pdf_path, model, chunk_size, overlap, output_dir, obsidian, device, pages):
    """
    Extract and generate structured notes from PDF documents.

    This tool processes technical PDFs and creates comprehensive markdown notes
    optimized for knowledge management systems like Obsidian.
    """

    click.echo(f"🔍 Processing PDF: {pdf_path}")
    click.echo(f"🤖 Using model: {model}")
    click.echo(f"📱 Device: {device}")

    if not os.path.exists(pdf_path):
        click.echo(f"❌ Error: PDF file not found: {pdf_path}", err=True)
        sys.exit(1)

    try:
        # Initialize components
        click.echo("🔧 Initializing components...")

        with PDFExtractor(pdf_path) as extractor:
            # Extract text from PDF
            click.echo("📖 Extracting text from PDF...")
            if pages:
                # Parse page specification
                page_list = parse_pages(pages)
                extracted_sections = []
                for page_num in page_list:
                    text = extractor.get_text_by_pages(page_num-1, page_num)
                    if text.strip():
                        from src.pdf_extractor import ExtractedText
                        extracted_sections.append(ExtractedText(
                            content=text,
                            page_number=page_num,
                            chapter_title=""
                        ))
            else:
                extracted_sections = extractor.extract_text()

            if not extracted_sections:
                click.echo("❌ No text extracted from PDF", err=True)
                sys.exit(1)

            click.echo(f"📄 Extracted {len(extracted_sections)} sections")

        # Initialize chunker and chunk text
        click.echo("✂️ Chunking text...")
        chunker = TextChunker(max_chunk_size=chunk_size, overlap_size=overlap)

        all_chunks = []
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
        note_generator = NoteGenerator(model_name=model, device=device)

        # Generate notes
        click.echo("✍️ Generating notes...")
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
            markdown_content = formatter.format_notes_to_markdown(notes, pdf_path)

        output_path = formatter.save_markdown_file(markdown_content, pdf_path)

        # Generate summary
        summary_content = formatter.create_summary_section(notes, pdf_path)
        summary_path = output_path.replace('.md', '_summary.md')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        click.echo(f"✅ Notes saved to: {output_path}")
        click.echo(f"📊 Summary saved to: {summary_path}")
        click.echo(f"📈 Generated {len(notes)} notes from {len(all_chunks)} chunks")

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


if __name__ == '__main__':
    main()