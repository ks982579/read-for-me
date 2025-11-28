"""
Example: Using the sliding window chunking approach with hierarchical note merging.

This approach:
1. Chunks text into overlapping pieces (e.g., 30% overlap)
2. Generates notes for each chunk independently
3. Merges notes hierarchically to eliminate redundancy while preserving content
4. Produces a comprehensive, coherent final document

Better results than simple chunking because:
- Smaller chunks = less context saturation, fewer repetition loops
- Overlap ensures no information is lost at chunk boundaries
- Hierarchical merging maintains narrative flow
- Works well even with smaller models like Flan-T5
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_extractor import PDFExtractor
from src.sliding_window_chunker import SlidingWindowChunker
from src.api_note_generator import APIBasedNoteGenerator
from src.note_merger import NoteMerger
from src.markdown_formatter import MarkdownFormatter


def process_pdf_with_sliding_window(
    pdf_path: str,
    start_page: int = None,
    end_page: int = None,
    chunk_size: int = 1024,
    overlap_ratio: float = 0.3,
    output_dir: str = "output"
) -> str:
    """
    Process a PDF using sliding window chunking and hierarchical merging.

    Args:
        pdf_path: Path to PDF file
        start_page: Start page (inclusive)
        end_page: End page (inclusive)
        chunk_size: Size of chunks in tokens (smaller = fewer repetition issues)
        overlap_ratio: Overlap between chunks (0.3 = 30%)
        output_dir: Where to save results

    Returns:
        Path to generated markdown file
    """

    # Step 1: Extract text from PDF
    print(f"📄 Extracting text from {pdf_path}...")
    extractor = PDFExtractor(pdf_path)
    extracted_sections = extractor.extract_text()
    text = ' '.join([section.content for section in extracted_sections])
    page_count = len(set(section.page_number for section in extracted_sections))
    print(f"✅ Extracted {page_count} pages")

    # Step 2: Create overlapping chunks (SMALLER CHUNKS = BETTER RESULTS)
    print(f"\n🔄 Creating {chunk_size}-token chunks with {int(overlap_ratio*100)}% overlap...")
    chunker = SlidingWindowChunker(chunk_size=chunk_size, overlap_ratio=overlap_ratio)

    # Use smart chunking for better boundaries (sentence/paragraph level)
    chunks = chunker.chunk_by_smart_boundaries(
        text=text,
        source_pages=list(range(start_page or 1, (end_page or page_count) + 1)),
        chapter_title="PDF Content"
    )
    print(f"✅ Created {len(chunks)} overlapping chunks")

    # Step 3: Generate notes for each chunk
    print(f"\n📝 Generating notes for {len(chunks)} chunks...")
    generator = APIBasedNoteGenerator()
    notes = []

    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}/{len(chunks)}: {chunk.token_count} tokens", end="")
        note = generator.generate_note_from_chunk(chunk)
        notes.append(note)
        print(" ✓")

    print(f"✅ Generated {len(notes)} individual notes")

    # Step 4: Merge overlapping notes hierarchically
    print(f"\n🔗 Merging {len(notes)} notes hierarchically...")
    merger = NoteMerger()

    # For large numbers of notes, merge in batches first
    if len(notes) > 10:
        merged_notes = merger.merge_notes_in_batches(notes, batch_size=3)
    else:
        merged_notes = merger.merge_notes_in_batches(notes, batch_size=2)

    # Then merge remaining notes into single comprehensive note
    if len(merged_notes) > 1:
        final_note = merger.merge_all_to_single(merged_notes)
    else:
        final_note = merged_notes[0]

    print(f"✅ Merged to single comprehensive note")

    # Step 5: Format as markdown
    print(f"\n📋 Formatting as markdown...")
    formatter = MarkdownFormatter()
    markdown = formatter.format_notes_to_markdown(
        notes=[final_note],
        title=Path(pdf_path).stem,
        include_metadata=True
    )

    # Step 6: Save output
    output_path = Path(output_dir) / f"{Path(pdf_path).stem}_sliding_window.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"✅ Saved to {output_path}")
    return str(output_path)


def main():
    """Example usage with recommended settings."""

    # Example 1: Process specific page range with smaller chunks
    pdf_path = "./ebooks/Distributed_Systems_4.pdf"  # Replace with your PDF

    print("=" * 70)
    print("SLIDING WINDOW CHUNKING EXAMPLE")
    print("=" * 70)
    print("\nSettings:")
    print("  • Chunk size: 1024 tokens (prevents large context issues)")
    print("  • Overlap: 30% (ensures continuity between chunks)")
    print("  • Smart boundaries: sentences/paragraphs (better coherence)")
    print("  • Note merging: hierarchical (eliminates redundancy)")
    print("=" * 70)

    # Process pages 18-54 with sliding window approach
    output = process_pdf_with_sliding_window(
        pdf_path=pdf_path,
        start_page=18,
        end_page=54,
        chunk_size=1024,        # Smaller chunk = better (avoid saturation)
        overlap_ratio=0.3,      # 30% overlap
        output_dir="output"
    )

    print(f"\n{'='*70}")
    print(f"✨ Complete! Output saved to: {output}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
