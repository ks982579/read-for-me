#!/usr/bin/env python3
"""
Test to determine the offset between book page numbers and PyMuPDF indices.
"""

import pymupdf

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def find_offset():
    """
    According to index.yaml:
    - Chapter 1 starts at page 1
    - Chapter 2 "Data Analytics" starts at page 31
    - Chapter 3 "Basic Learning Algorithms" starts at page 53

    We need to find where these actually are in the PyMuPDF index.
    """
    doc = pymupdf.open(pdf_path)

    print("Searching for chapter locations...")
    print("="*80)

    # Known data from index.yaml
    chapters_to_find = [
        ("Chapter 1: Introduction to Data Science", 1),
        ("Chapter 2: Data Analytics", 31),
        ("Chapter 3: Basic Learning Algorithms", 53),
    ]

    offsets = []

    for chapter_name, book_page in chapters_to_find:
        print(f"\nLooking for: {chapter_name} (book page {book_page})")

        # Search through the PDF
        found = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            # Check if this page contains the chapter title
            if "Introduction to Data Science" in text and "Chapter 1" in text and not found and "Data Analytics" not in chapter_name:
                print(f"  Found at PyMuPDF index: {page_num} (1-based: {page_num + 1})")
                offset = page_num + 1 - book_page  # Convert to 1-based and calculate offset
                print(f"  Offset: {offset} (PyMuPDF 1-based page - book page)")
                offsets.append(offset)
                found = True
            elif "Data Analytics" in text and "Chapter 2" in text and not found:
                print(f"  Found at PyMuPDF index: {page_num} (1-based: {page_num + 1})")
                offset = page_num + 1 - book_page
                print(f"  Offset: {offset} (PyMuPDF 1-based page - book page)")
                offsets.append(offset)
                found = True
            elif "Basic Learning Algorithms" in text and "Chapter 3" in text and not found:
                print(f"  Found at PyMuPDF index: {page_num} (1-based: {page_num + 1})")
                offset = page_num + 1 - book_page
                print(f"  Offset: {offset} (PyMuPDF 1-based page - book page)")
                offsets.append(offset)
                found = True

    print("\n" + "="*80)
    print("\nOFFSET ANALYSIS:")
    print(f"Offsets found: {offsets}")
    if len(set(offsets)) == 1:
        print(f"✅ Consistent offset: {offsets[0]}")
        print(f"\nFormula: PyMuPDF_index = book_page + {offsets[0]} - 1")
        print(f"         (subtract 1 because PyMuPDF uses 0-based indexing)")
    else:
        print("❌ Inconsistent offsets - need to investigate further")

    doc.close()

if __name__ == "__main__":
    find_offset()
