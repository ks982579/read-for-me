#!/usr/bin/env python3
"""
Debug script to inspect what content is being extracted for each section.
This helps identify if parent sections are incorrectly including child content.
"""

import sys
from src.bookmark_chunker import BookmarkChunker


def debug_section_extraction(pdf_path, start_page=None, end_page=None):
    """
    Print detailed information about what content is extracted for each bookmark.
    """
    print(f"🔍 Debugging extraction for: {pdf_path}\n")

    with BookmarkChunker(pdf_path, max_chunk_size=2048, overlap_size=64) as chunker:
        bookmarks = chunker.extract_bookmarks()

        if start_page and end_page:
            bookmarks = chunker.filter_bookmarks_by_page_range(bookmarks, start_page, end_page)

        print(f"📚 Found {len(bookmarks)} bookmarks:\n")

        # Print bookmark structure
        for i, (level, title, page) in enumerate(bookmarks):
            indent = "  " * (level - 1)
            print(f"{i:2d}. {indent}[L{level}] {title} (p. {page})")

        print("\n" + "="*80)
        print("EXTRACTION DETAILS")
        print("="*80 + "\n")

        # Now show what gets extracted for each
        chunks = chunker.chunk_by_bookmarks(start_page, end_page)

        for i, chunk in enumerate(chunks):
            print(f"\n{'='*80}")
            print(f"CHUNK #{i}")
            print(f"{'='*80}")
            print(f"Level: {chunk.level}")
            print(f"Number: {chunk.number}")
            print(f"Title: {chunk.title}")
            print(f"Parent: {chunk.parent_section} - {chunk.parent_section_title}")
            print(f"Pages: {chunk.start_page} to {chunk.end_page}")
            print(f"Token count: {chunk.token_count}")
            print(f"\nContent preview (first 500 chars):")
            print("-" * 80)
            print(chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content)
            print("-" * 80)

            # Check if this looks like it includes child content
            if i + 1 < len(chunks):
                next_chunk = chunks[i + 1]
                # If next chunk is a child (deeper level) and has same/similar content
                if next_chunk.level > chunk.level:
                    # Check if parent's content contains significant portion of child's content
                    child_preview = next_chunk.content[:200]
                    if child_preview in chunk.content:
                        print("\n⚠️  WARNING: This parent section appears to contain child content!")
                        print(f"   Child section '{next_chunk.number} {next_chunk.title}' content found in parent")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_extraction.py <pdf_path> [start_page] [end_page]")
        print("Example: python debug_extraction.py book.pdf 20 40")
        sys.exit(1)

    pdf_path = sys.argv[1]
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else None
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else None

    debug_section_extraction(pdf_path, start_page, end_page)
