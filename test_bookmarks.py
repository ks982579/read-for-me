#!/usr/bin/env python3
"""
Test if PDF has extractable bookmarks/outline.
"""

import pymupdf

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def check_bookmarks():
    doc = pymupdf.open(pdf_path)

    toc = doc.get_toc()

    if not toc:
        print("❌ No bookmarks found in PDF")
        return

    print(f"✅ Found {len(toc)} bookmark entries")
    print("\n" + "="*80)
    print("BOOKMARK STRUCTURE (first 30 entries):")
    print("="*80)

    for i, entry in enumerate(toc[:30]):
        level, title, page = entry
        indent = "  " * (level - 1)
        print(f"{indent}[Level {level}] {title} → Page {page}")

    if len(toc) > 30:
        print(f"\n... and {len(toc) - 30} more entries")

    print("\n" + "="*80)
    print("ANALYSIS:")
    print("="*80)

    # Check if it matches our index.yaml expectations
    chapter_1 = [e for e in toc if "Introduction to Data Science" in e[1]]
    if chapter_1:
        print(f"✅ Chapter 1 found at page {chapter_1[0][2]}")
        print(f"   (Expected: page 16 based on our testing)")

    chapter_2 = [e for e in toc if "Data Analytics" in e[1] and "Chapter" in str(e)]
    if chapter_2:
        print(f"✅ Chapter 2 found at page {chapter_2[0][2]}")

    doc.close()

if __name__ == "__main__":
    check_bookmarks()
