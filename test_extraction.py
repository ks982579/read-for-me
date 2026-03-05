#!/usr/bin/env python3
"""
Test the extract_text_between_headings method directly to see what content it extracts.
"""

import sys
from src.bookmark_chunker import BookmarkChunker
from src.text_chunker import TextChunker


def test_section_extraction(pdf_path):
    """
    Test extraction for section 1.5 (parent) and 1.5.1 (child).
    This will show us exactly what content is being extracted for each.
    """
    print("🧪 Testing text extraction between headings\n")

    with BookmarkChunker(pdf_path, max_chunk_size=2048, overlap_size=64) as chunker:
        text_chunker = TextChunker(max_chunk_size=2048, overlap_size=64)

        # Test 1: Extract section 1.5 content (should stop at 1.5.1)
        print("="*80)
        print("TEST 1: Extracting Section 1.5")
        print("="*80)
        print("Start: 1.5 Data Science Activities in Three Dimensions")
        print("End: 1.5.1 Managing Data Flow")
        print("Expected: Only the introductory paragraph before subsections start\n")

        content_1_5 = chunker.extract_text_between_headings(
            start_page=22,  # Adjust if needed
            start_heading_title="Data Science Activities in Three Dimensions",
            start_section_number="1.5",
            end_heading_title="Managing Data Flow",
            end_section_number="1.5.1",
            max_pages=10
        )

        token_count_1_5 = text_chunker.count_tokens(content_1_5)
        print(f"📊 Extracted {len(content_1_5)} characters, {token_count_1_5} tokens")
        print(f"\n📝 Content preview (first 500 chars):")
        print("-"*80)
        print(content_1_5[:500])
        print("-"*80)

        # Check if it contains the subsection content (it shouldn't!)
        if "first dimension of data science activities" in content_1_5.lower():
            print("\n⚠️  WARNING: Content appears to include subsection 1.5.1!")
            print("   Found phrase from 1.5.1 content in extracted text")
        else:
            print("\n✅ Content appears to be correct (doesn't include subsection)")

        # Test 2: Extract subsection 1.5.1 content (should be just that subsection)
        print("\n" + "="*80)
        print("TEST 2: Extracting Subsection 1.5.1")
        print("="*80)
        print("Start: 1.5.1 Managing Data Flow")
        print("End: Next subsection (e.g., 1.5.2) or next section")
        print("Expected: Just the content of subsection 1.5.1\n")

        # We need to figure out what comes after 1.5.1
        bookmarks = chunker.extract_bookmarks()

        # Find 1.5.1 in bookmarks
        next_heading = None
        next_number = None
        for i, (level, title, page) in enumerate(bookmarks):
            if "1.5.1" in title:
                print(f"Found 1.5.1 at bookmark index {i}")
                if i + 1 < len(bookmarks):
                    next_level, next_title, next_page = bookmarks[i + 1]
                    next_number = chunker.parse_section_number(next_title)
                    if next_number:
                        next_heading = next_title.replace(next_number, "").strip()
                    else:
                        next_heading = next_title
                    print(f"Next bookmark: {next_title} at page {next_page}")
                break

        if next_heading:
            content_1_5_1 = chunker.extract_text_between_headings(
                start_page=22,  # Adjust if needed
                start_heading_title="Managing Data Flow",
                start_section_number="1.5.1",
                end_heading_title=next_heading,
                end_section_number=next_number,
                max_pages=10
            )

            token_count_1_5_1 = text_chunker.count_tokens(content_1_5_1)
            print(f"\n📊 Extracted {len(content_1_5_1)} characters, {token_count_1_5_1} tokens")
            print(f"\n📝 Content preview (first 500 chars):")
            print("-"*80)
            print(content_1_5_1[:500])
            print("-"*80)

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Section 1.5: {token_count_1_5} tokens")
        if next_heading:
            print(f"Subsection 1.5.1: {token_count_1_5_1} tokens")

        print("\n💡 Analysis:")
        if token_count_1_5 > 500:  # Arbitrary threshold
            print("   ⚠️  Section 1.5 seems too large - likely includes subsection content")
        else:
            print("   ✅ Section 1.5 size seems reasonable for an intro paragraph")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_extraction.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    test_section_extraction(pdf_path)
