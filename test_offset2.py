#!/usr/bin/env python3
"""
Better test to determine the offset between book page numbers and PyMuPDF indices.
"""

import pymupdf
import re

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def find_chapter_starts():
    """
    Search for chapter starts more carefully.
    """
    doc = pymupdf.open(pdf_path)

    print("Searching for chapter locations...")
    print("="*80)

    # Search for chapter markers
    chapter_locations = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Look for chapter headings at the start of text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) > 0:
            first_line = lines[0]

            # Check for "Chapter X" pattern
            chapter_match = re.match(r'Chapter\s+(\d+)', first_line)
            if chapter_match:
                chapter_num = int(chapter_match.group(1))
                if chapter_num not in chapter_locations:
                    # Get a preview of the content
                    preview = ' '.join(lines[:3])
                    chapter_locations[chapter_num] = {
                        'pymupdf_index': page_num,
                        'preview': preview[:150]
                    }

    print("\nChapters found:")
    print("="*80)
    for chapter_num in sorted(chapter_locations.keys()):
        info = chapter_locations[chapter_num]
        print(f"\nChapter {chapter_num}:")
        print(f"  PyMuPDF index: {info['pymupdf_index']} (1-based: {info['pymupdf_index'] + 1})")
        print(f"  Preview: {info['preview']}...")

    # Now compare with index.yaml expected pages
    print("\n" + "="*80)
    print("\nCOMPARING WITH INDEX.YAML:")
    print("="*80)

    expected_pages = {
        1: 1,
        2: 31,
        3: 53,
        4: 95,
        5: 125,
        6: 157,
    }

    offsets = []
    for chapter_num, book_page in expected_pages.items():
        if chapter_num in chapter_locations:
            actual_index = chapter_locations[chapter_num]['pymupdf_index']
            actual_page_1based = actual_index + 1
            offset = actual_page_1based - book_page

            print(f"\nChapter {chapter_num}:")
            print(f"  Expected book page: {book_page}")
            print(f"  Actual PyMuPDF index: {actual_index} (1-based: {actual_page_1based})")
            print(f"  Offset: {offset}")

            offsets.append(offset)

    print("\n" + "="*80)
    print("\nOFFSET ANALYSIS:")
    print(f"Offsets found: {offsets}")
    if len(set(offsets)) == 1:
        offset_value = offsets[0]
        print(f"✅ Consistent offset: {offset_value}")
        print(f"\nFormula to convert book page to PyMuPDF index:")
        print(f"  pymupdf_index = (book_page + {offset_value}) - 1")
        print(f"  (subtract 1 because PyMuPDF uses 0-based indexing)")
        print(f"\nFormula to convert PyMuPDF 1-based page to book page:")
        print(f"  book_page = pymupdf_1based_page - {offset_value}")
    else:
        print("❌ Inconsistent offsets - need to investigate further")
        print("\nThis might indicate:")
        print("- The book has different sections with different numbering")
        print("- Or we need a different approach to finding the offset")

    doc.close()

if __name__ == "__main__":
    find_chapter_starts()
