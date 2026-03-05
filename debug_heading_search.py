#!/usr/bin/env python3
"""
Debug script to see exactly why heading detection is failing.
Shows what text is being searched and what patterns are being tried.
"""

import sys
import re
from src.bookmark_chunker import BookmarkChunker


def debug_heading_detection(pdf_path, section_number, section_title, page_num):
    """
    Show detailed information about heading detection for a specific section.

    Args:
        pdf_path: Path to PDF
        section_number: Section number to search for (e.g., "1.5.1")
        section_title: Section title (e.g., "Managing Data Flow")
        page_num: Page number to search on (0-based)
    """
    print(f"🔍 Debugging heading detection")
    print(f"   Looking for: {section_number} {section_title}")
    print(f"   On page: {page_num}\n")

    with BookmarkChunker(pdf_path) as chunker:
        page = chunker.doc[page_num]
        page_text = page.get_text()

        print("="*80)
        print("RAW PAGE TEXT (first 1000 chars)")
        print("="*80)
        print(page_text[:1000])
        print("..."if len(page_text) > 1000 else "")
        print()

        # Normalize text like the code does
        normalized_text = chunker.normalize_text_for_matching(page_text)
        normalized_title = chunker.normalize_text_for_matching(section_title)

        print("="*80)
        print("NORMALIZED TEXT (first 1000 chars)")
        print("="*80)
        print(normalized_text[:1000])
        print("..." if len(normalized_text) > 1000 else "")
        print()

        # Show what patterns are being tried
        print("="*80)
        print("PATTERNS BEING TRIED")
        print("="*80)

        patterns = []
        if section_number:
            escaped_number = re.escape(section_number)
            pattern1 = f"{escaped_number}\\s+{re.escape(normalized_title)}"
            pattern2 = f"{escaped_number}\\s*{re.escape(normalized_title)}"
            patterns.append(("Number + spaces + Title", pattern1))
            patterns.append(("Number + optional spaces + Title", pattern2))

        pattern3 = re.escape(normalized_title)
        patterns.append(("Title only", pattern3))

        for i, (desc, pattern) in enumerate(patterns, 1):
            print(f"\n{i}. {desc}")
            print(f"   Pattern: {pattern}")
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                print(f"   ✅ MATCH FOUND at position {match.start()}")
                print(f"   Matched text: '{match.group()}'")
                # Show context
                context_start = max(0, match.start() - 50)
                context_end = min(len(normalized_text), match.end() + 50)
                print(f"   Context: ...{normalized_text[context_start:context_end]}...")
            else:
                print(f"   ❌ NO MATCH")

        # Now test with the actual find_heading_in_text method
        print("\n" + "="*80)
        print("ACTUAL METHOD RESULT")
        print("="*80)
        result = chunker.find_heading_in_text(page_text, section_title, section_number)
        if result >= 0:
            print(f"✅ Heading found at position {result}")
        else:
            print(f"❌ Heading NOT found (returned {result})")

        # Search for section number alone
        print("\n" + "="*80)
        print("SEARCHING FOR SECTION NUMBER ALONE")
        print("="*80)
        if section_number:
            # Try to find any occurrence of the section number
            variations = [
                section_number,
                section_number + ".",
                section_number + " ",
                section_number + "\t",
                section_number + "\n",
            ]
            for var in variations:
                if var in page_text:
                    print(f"✅ Found variation: '{var}'")
                    # Show where it appears
                    idx = page_text.find(var)
                    context = page_text[max(0, idx-30):min(len(page_text), idx+80)]
                    print(f"   Context: ...{context}...")
                    break
            else:
                print(f"❌ Section number '{section_number}' not found in any common format")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python debug_heading_search.py <pdf_path> <section_number> <section_title> <page_num>")
        print('Example: python debug_heading_search.py book.pdf "1.5.1" "Managing Data Flow" 23')
        sys.exit(1)

    pdf_path = sys.argv[1]
    section_number = sys.argv[2]
    section_title = sys.argv[3]
    page_num = int(sys.argv[4])

    debug_heading_detection(pdf_path, section_number, section_title, page_num)
