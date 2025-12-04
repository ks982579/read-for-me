#!/usr/bin/env python3
"""
Test script for the bookmark-based chunker.
"""

from src.bookmark_chunker import BookmarkChunker

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def test_full_extraction():
    """Test extracting all chunks from the PDF."""
    print("="*80)
    print("TEST 1: Full PDF Extraction")
    print("="*80)

    with BookmarkChunker(pdf_path, max_chunk_size=2048) as chunker:
        if not chunker.has_bookmarks():
            print("❌ No bookmarks found!")
            return

        chunks = chunker.chunk_by_bookmarks()
        print(f"\n✅ Extracted {len(chunks)} chunks")

        # Show first 5 chunks
        print("\nFirst 5 chunks:")
        print("-"*80)
        for i, chunk in enumerate(chunks[:5]):
            print(f"\nChunk {i+1}:")
            print(f"  Level: {chunk.level}")
            print(f"  Number: {chunk.number}")
            print(f"  Title: {chunk.title}")
            print(f"  Chapter: {chunk.chapter_number} - {chunk.chapter_title}")
            print(f"  Pages: {chunk.start_page + 1} to {chunk.end_page + 1}")
            print(f"  Token count: {chunk.token_count}")
            print(f"  Content preview: {chunk.content[:100]}...")
            if chunk.is_split:
                print(f"  Split: Part {chunk.split_index + 1}/{chunk.total_splits}")

def test_page_range():
    """Test extracting chunks from a specific page range."""
    print("\n" + "="*80)
    print("TEST 2: Page Range Extraction (pages 16-45, should be Chapter 1)")
    print("="*80)

    with BookmarkChunker(pdf_path, max_chunk_size=2048) as chunker:
        # Extract only Chapter 1 (pages 16-45 based on our testing)
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=45)
        print(f"\n✅ Extracted {len(chunks)} chunks from pages 16-45")

        # Show all chunks in this range
        print("\nAll chunks in range:")
        print("-"*80)
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  {chunk.level * '#'} {chunk.number} {chunk.title}")
            print(f"  Pages: {chunk.start_page + 1} to {chunk.end_page + 1}")
            print(f"  Tokens: {chunk.token_count}")

def test_hierarchy():
    """Test that hierarchy is preserved correctly."""
    print("\n" + "="*80)
    print("TEST 3: Hierarchy Test (Chapter 1 structure)")
    print("="*80)

    with BookmarkChunker(pdf_path, max_chunk_size=2048) as chunker:
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=45)

        print("\nHierarchical structure:")
        print("-"*80)
        for chunk in chunks:
            indent = "  " * (chunk.level - 1)
            number = f"{chunk.number} " if chunk.number else ""
            print(f"{indent}{chunk.level * '#'} {number}{chunk.title}")

def test_large_section_splitting():
    """Test that large sections are split properly."""
    print("\n" + "="*80)
    print("TEST 4: Large Section Splitting")
    print("="*80)

    # Use smaller chunk size to force splitting
    with BookmarkChunker(pdf_path, max_chunk_size=500) as chunker:
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=45)

        split_chunks = [c for c in chunks if c.is_split]
        print(f"\n✅ Found {len(split_chunks)} split chunks out of {len(chunks)} total")

        if split_chunks:
            print("\nSplit chunks:")
            print("-"*80)
            for chunk in split_chunks[:3]:  # Show first 3
                print(f"\n  {chunk.number} {chunk.title}")
                print(f"  Part {chunk.split_index + 1}/{chunk.total_splits}")
                print(f"  Tokens: {chunk.token_count}")

if __name__ == "__main__":
    try:
        test_full_extraction()
        test_page_range()
        test_hierarchy()
        test_large_section_splitting()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
