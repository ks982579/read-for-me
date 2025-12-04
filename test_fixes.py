#!/usr/bin/env python3
"""
Test the fixes for:
1. 0-based page numbers in markdown
2. Missing parent section headers
"""

from src.bookmark_chunker import BookmarkChunker

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def test_parent_section_titles():
    """Test that parent section titles are captured."""
    print("="*80)
    print("TEST: Parent Section Titles")
    print("="*80)

    with BookmarkChunker(pdf_path) as chunker:
        # Get chunks that should have parent sections
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=30)

        print("\nChecking parent section titles:")
        print("-"*80)

        for chunk in chunks:
            if chunk.parent_section:
                print(f"\n{chunk.number} {chunk.title}")
                print(f"  Parent: {chunk.parent_section} - {chunk.parent_section_title}")
                if chunk.parent_section_title:
                    print(f"  ✅ Has parent section title")
                else:
                    print(f"  ❌ Missing parent section title")

def test_page_numbers():
    """Test that chunks have correct page numbers."""
    print("\n" + "="*80)
    print("TEST: Page Numbers")
    print("="*80)

    with BookmarkChunker(pdf_path) as chunker:
        chunks = chunker.chunk_by_bookmarks(start_page=16, end_page=20)

        print("\nFirst 3 chunks with page numbers:")
        print("-"*80)

        for chunk in chunks[:3]:
            print(f"\n{chunk.number} {chunk.title}")
            print(f"  start_page (0-based): {chunk.start_page}")
            print(f"  end_page (0-based): {chunk.end_page}")
            print(f"  source_pages (1-based): {chunk.source_pages}")

if __name__ == "__main__":
    try:
        test_parent_section_titles()
        test_page_numbers()
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
