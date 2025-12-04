#!/usr/bin/env python3
"""
Test that heading-based extraction properly stops at the next heading.
"""

from src.bookmark_chunker import BookmarkChunker

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def test_section_boundaries():
    """
    Test that we extract only content belonging to each section,
    not content from the next section.
    """
    print("="*80)
    print("TEST: Section Boundary Extraction")
    print("="*80)

    with BookmarkChunker(pdf_path) as chunker:
        # Get chunks for a small range to inspect closely
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=25)

        print("\nInspecting section content boundaries:")
        print("-"*80)

        for i, chunk in enumerate(chunks[:5]):  # Look at first 5 chunks
            print(f"\n{'='*60}")
            print(f"Chunk {i+1}: {chunk.number} {chunk.title}")
            print(f"Token count: {chunk.token_count}")
            print(f"{'='*60}")

            # Show last 200 characters to see where it ends
            content_end = chunk.content[-200:] if len(chunk.content) > 200 else chunk.content
            print(f"\nLast 200 chars:")
            print(content_end)

            # Check if the next section's title appears in this chunk's content
            if i + 1 < len(chunks):
                next_chunk = chunks[i + 1]
                next_title = next_chunk.title
                next_number = next_chunk.number

                # Look for the next section's heading in current content
                if next_number and next_number in chunk.content:
                    print(f"\n⚠️  WARNING: Found next section number '{next_number}' in content!")
                    # Find where it appears
                    idx = chunk.content.find(next_number)
                    snippet = chunk.content[max(0, idx-50):idx+100]
                    print(f"Context: ...{snippet}...")

                if next_title in chunk.content:
                    # Check if it's just a mention or the actual heading
                    # The heading should be preceded by the section number
                    heading_pattern = f"{next_number} {next_title}" if next_number else next_title
                    if heading_pattern in chunk.content:
                        print(f"\n⚠️  WARNING: Found next section heading '{heading_pattern}' in content!")
                    else:
                        print(f"\n✅ Title '{next_title}' appears but not as heading (just mentioned)")

if __name__ == "__main__":
    try:
        test_section_boundaries()
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
