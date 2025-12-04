#!/usr/bin/env python3
"""
Test that StructuredChunk is compatible with NoteGenerator interface.
"""

from src.bookmark_chunker import BookmarkChunker, StructuredChunk

def test_compatibility():
    """Test that StructuredChunk has all required attributes for NoteGenerator."""

    pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

    with BookmarkChunker(pdf_path) as chunker:
        # Get a few chunks
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=30)

        if not chunks:
            print("❌ No chunks extracted")
            return

        # Test first chunk
        chunk = chunks[0]

        print("Testing StructuredChunk compatibility...")
        print("="*80)

        # Test required attributes
        required_attrs = ['content', 'chapter_title', 'chunk_id', 'source_pages']

        for attr in required_attrs:
            if hasattr(chunk, attr):
                value = getattr(chunk, attr)
                print(f"✅ {attr}: {type(value).__name__} = {repr(value)[:100]}")
            else:
                print(f"❌ MISSING: {attr}")
                return

        print("\n" + "="*80)
        print("✅ ALL COMPATIBILITY ATTRIBUTES PRESENT")
        print("\nChunk details:")
        print(f"  Level: {chunk.level}")
        print(f"  Number: {chunk.number}")
        print(f"  Title: {chunk.title}")
        print(f"  Chapter: {chunk.chapter_number} - {chunk.chapter_title}")
        print(f"  Pages (0-based): {chunk.start_page} to {chunk.end_page}")
        print(f"  source_pages (1-based): {chunk.source_pages}")
        print(f"  chunk_id: {chunk.chunk_id}")
        print(f"  Content length: {len(chunk.content)} chars")
        print(f"  Token count: {chunk.token_count}")

if __name__ == "__main__":
    try:
        test_compatibility()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
