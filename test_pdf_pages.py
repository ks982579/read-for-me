#!/usr/bin/env python3
"""
Test script to understand how PyMuPDF handles page numbering,
especially for PDFs with Roman numerals in front matter.
"""

import pymupdf

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def test_page_numbering():
    """Test how PyMuPDF indexes pages and what text appears on each page."""
    doc = pymupdf.open(pdf_path)

    print(f"Total pages in PDF: {len(doc)}")
    print("\n" + "="*80)

    # Check first 15 pages to see front matter (likely Roman numerals)
    print("\nFRONT MATTER (first 15 pages):")
    print("="*80)
    for page_num in range(min(15, len(doc))):
        page = doc[page_num]
        text = page.get_text()

        # Get first 200 characters to see what's on the page
        preview = text.strip()[:200].replace('\n', ' ')

        print(f"\nPyMuPDF Index: {page_num} (1-based: {page_num + 1})")
        print(f"Preview: {preview}...")

    # Check pages around where Chapter 1 should start (page 1 according to index.yaml)
    print("\n" + "="*80)
    print("\nCHAPTER 1 AREA (checking pages that might be 'page 1'):")
    print("="*80)

    # In many academic books, the actual content starts after front matter
    # Let's check pages 10-20 in the PyMuPDF index
    for page_num in range(10, min(25, len(doc))):
        page = doc[page_num]
        text = page.get_text()

        # Look for "Introduction to Data Science" or "Chapter 1"
        if "Introduction to Data Science" in text or "Chapter 1" in text or "1.1" in text:
            preview = text.strip()[:300].replace('\n', ' ')
            print(f"\nPyMuPDF Index: {page_num} (1-based: {page_num + 1})")
            print(f"MATCH FOUND!")
            print(f"Preview: {preview}...")

    doc.close()

if __name__ == "__main__":
    test_page_numbering()
