#!/usr/bin/env python3
"""
PDF to Audiobook Converter

Converts PDF documents to audiobooks using GPU-accelerated TTS.
Preserves document structure (chapters, sections) with automatic pauses.
"""

import click
import os
import sys
from pathlib import Path
from tqdm import tqdm

from src.pdf_extractor import PDFExtractor
from src.text_chunker import TextChunker
from src.tts_generator import TTSGenerator
from src.bookmark_chunker import BookmarkChunker


@click.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--chunk-size', '-c', default=2048,
              help='Maximum tokens per text chunk')
@click.option('--overlap', '-o', default=200,
              help='Token overlap between chunks')
@click.option('--output-dir', '-d', default="audiobooks",
              help='Output directory for generated audiobooks')
@click.option('--device', default="cuda",
              help='Device to use: cuda or cpu')
@click.option('--pages', '-p', default=None,
              help='Page range to process (e.g., "1-10" or "5,7,9-12")')
@click.option('--auto', is_flag=True, default=True,
              help='Auto-detect book structure from PDF bookmarks (default: True)')
@click.option('--voice', default="default",
              help='Voice to use (default or path to reference audio)')
@click.option('--model', '-m', default="tts_models/en/ljspeech/tacotron2-DDC",
              help='TTS model to use (default: tacotron2-DDC)')
@click.option('--format', '-f', default="mp3",
              help='Output audio format (mp3, wav, ogg)')
def main(pdf_path, chunk_size, overlap, output_dir, device, pages, auto, voice, model, format):
    """
    Convert PDF documents to audiobooks using GPU-accelerated TTS.

    This tool extracts text from PDFs and converts it to natural-sounding
    speech, preserving the document's chapter and section structure.

    Examples:
        # Convert entire book
        python tts_main.py book.pdf

        # Convert specific pages only
        python tts_main.py book.pdf --pages 1-50

        # Use CPU instead of GPU
        python tts_main.py book.pdf --device cpu

        # Output as WAV instead of MP3
        python tts_main.py book.pdf --format wav
    """

    click.echo("🎙️  PDF to Audiobook Converter")
    click.echo("=" * 50)
    click.echo(f"📖 PDF: {pdf_path}")
    click.echo(f"🔊 TTS Model: {model}")
    click.echo(f"📱 Device: {device}")
    click.echo(f"💾 Output: {output_dir}")
    click.echo(f"🎵 Format: {format}")
    click.echo()

    if not os.path.exists(pdf_path):
        click.echo(f"❌ Error: PDF file not found: {pdf_path}", err=True)
        sys.exit(1)

    try:
        # Parse page range if specified
        start_page, end_page = None, None
        if pages:
            page_list = parse_pages(pages)
            start_page = page_list[0]
            end_page = page_list[-1]
            click.echo(f"📄 Processing pages: {start_page}-{end_page}")
            click.echo()

        # Extract text chunks
        all_chunks = []
        use_bookmark_chunking = False

        if auto:
            click.echo("🔍 Checking for PDF bookmarks...")
            try:
                with BookmarkChunker(pdf_path, chunk_size, overlap) as chunker:
                    if chunker.has_bookmarks():
                        click.echo("✅ Bookmarks found! Using structure-aware extraction...")
                        use_bookmark_chunking = True

                        all_chunks = chunker.chunk_by_bookmarks(start_page, end_page)

                        if not all_chunks:
                            click.echo("⚠️  No content in specified page range", err=True)
                            sys.exit(1)

                        click.echo(f"📚 Created {len(all_chunks)} structured chunks")
                    else:
                        click.echo("⚠️  No bookmarks found, using page-based extraction...")
            except Exception as e:
                click.echo(f"⚠️  Bookmark extraction failed: {e}")
                click.echo("   Using page-based extraction...")

        # Fallback to page-based extraction
        if not use_bookmark_chunking:
            with PDFExtractor(pdf_path) as extractor:
                click.echo("📖 Extracting text from PDF...")
                if pages:
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

            # Chunk text
            click.echo("✂️  Chunking text...")
            chunker = TextChunker(max_chunk_size=chunk_size, overlap_size=overlap)

            for section in extracted_sections:
                chunks = chunker.smart_chunk(
                    section.content,
                    [section.page_number],
                    section.chapter_title
                )
                all_chunks.extend(chunks)

            click.echo(f"📝 Created {len(all_chunks)} text chunks")

        click.echo()

        # Initialize TTS generator
        click.echo("🔊 Initializing TTS engine...")
        tts_generator = TTSGenerator(model_name=model, device=device, voice=voice)
        click.echo()

        # Generate audio for each chunk
        click.echo("🎙️  Converting text to speech...")
        audio_segments = []
        total_duration = 0.0

        with tqdm(total=len(all_chunks), desc="Generating audio") as pbar:
            for chunk in all_chunks:
                audio = tts_generator.generate_audio_from_chunk(chunk)
                audio_segments.append(audio)
                total_duration += audio.duration_seconds
                pbar.update(1)
                pbar.set_postfix({"duration": f"{total_duration:.1f}s"})

        click.echo()
        click.echo(f"✅ Generated {len(audio_segments)} audio segments")
        click.echo(f"⏱️  Total duration: {total_duration / 60:.1f} minutes")
        click.echo()

        # Combine all audio segments
        click.echo("🔗 Combining audio segments...")
        combined_audio = tts_generator.combine_audio_segments(
            audio_segments,
            add_chapter_markers=use_bookmark_chunking
        )

        # Create output filename
        pdf_name = Path(pdf_path).stem
        output_file = Path(output_dir) / f"{pdf_name}.{format}"

        # Save the audiobook
        tts_generator.save_audio(combined_audio, str(output_file), format=format)

        click.echo()
        click.echo("=" * 50)
        click.echo(f"✅ Audiobook created successfully!")
        click.echo(f"📁 Location: {output_file}")
        click.echo(f"⏱️  Duration: {len(combined_audio) / 1000 / 60:.1f} minutes")
        click.echo(f"💾 Size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
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
