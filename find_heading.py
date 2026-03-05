#!/usr/bin/env python3
"""
Search through pages to find where a specific heading actually appears.
"""

import sys
import pymupdf


def find_heading_in_pdf(pdf_path, search_text, start_page=0, max_pages=20):
    """
    Search for a heading across multiple pages.

    Args:
        pdf_path: Path to PDF
        search_text: Text to search for (e.g., "Managing Data Flow" or "1.5.1")
        start_page: Page to start searching (0-based)
        max_pages: How many pages to search
    """
    print(f"🔍 Searching for: '{search_text}'")
    print(f"   Starting from page: {start_page}")
    print(f"   Searching up to {max_pages} pages\n")

    doc = pymupdf.open(pdf_path)
    found_on_pages = []

    for page_offset in range(max_pages):
        page_num = start_page + page_offset

        if page_num >= len(doc):
            break

        page = doc[page_num]
        page_text = page.get_text()

        # Search for the text (case insensitive)
        if search_text.lower() in page_text.lower():
            found_on_pages.append(page_num)
            print(f"✅ Found on page {page_num}")

            # Show context around the match
            lower_text = page_text.lower()
            pos = lower_text.find(search_text.lower())

            # Get surrounding text
            context_start = max(0, pos - 100)
            context_end = min(len(page_text), pos + len(search_text) + 100)
            context = page_text[context_start:context_end]

            print(f"   Context:")
            print(f"   ...{context}...")
            print()

    doc.close()

    if not found_on_pages:
        print(f"❌ '{search_text}' not found in pages {start_page} to {start_page + max_pages - 1}")
        print("\n💡 Suggestions:")
        print("   - Try a shorter search term (e.g., just 'Managing Data')")
        print("   - Check if the text uses different formatting")
        print("   - Try searching in a wider page range")
    else:
        print(f"\n📊 Summary: Found on {len(found_on_pages)} page(s): {found_on_pages}")

    return found_on_pages


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python find_heading.py <pdf_path> <search_text> [start_page] [max_pages]")
        print('Example: python find_heading.py book.pdf "Managing Data Flow" 20 10')
        print('Example: python find_heading.py book.pdf "1.5.1" 20 10')
        sys.exit(1)

    pdf_path = sys.argv[1]
    search_text = sys.argv[2]
    start_page = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    max_pages = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    find_heading_in_pdf(pdf_path, search_text, start_page, max_pages)
