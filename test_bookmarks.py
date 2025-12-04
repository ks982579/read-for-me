#!/usr/bin/env python3
"""
Utility script to check if a PDF has bookmarks and preview its structure.

Usage:
    python test_bookmarks.py path/to/your/book.pdf
"""

import sys
import pymupdf


def check_bookmarks(pdf_path):
    """Check if PDF has bookmarks and display structure."""
    try:
        doc = pymupdf.open(pdf_path)
        toc = doc.get_toc()

        if not toc:
            print("❌ No bookmarks found in PDF")
            print("\nThis PDF will fall back to token-based chunking.")
            print("Consider using --pages flag to process specific sections.")
            doc.close()
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
        print("RECOMMENDATION:")
        print("="*80)
        print("This PDF has good bookmark structure.")
        print("Use --auto flag for best results:")
        print(f"  python main.py {pdf_path} --auto --use-api")

        doc.close()

    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_bookmarks.py <pdf_path>")
        print("\nExample:")
        print("  python test_bookmarks.py ./ebooks/book.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    check_bookmarks(pdf_path)
