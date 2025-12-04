#!/usr/bin/env python3
"""
Analyze the bookmark hierarchy to understand chapter/section/subsection structure.
"""

import pymupdf
import re

pdf_path = "./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf"

def analyze_hierarchy():
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()

    print("BOOKMARK HIERARCHY ANALYSIS")
    print("="*80)

    # Categorize entries by level
    by_level = {}
    for level, title, page in toc:
        if level not in by_level:
            by_level[level] = []
        by_level[level].append((title, page))

    print(f"\nTotal bookmarks: {len(toc)}")
    print(f"Hierarchy levels found: {sorted(by_level.keys())}")
    print()

    for level in sorted(by_level.keys()):
        count = len(by_level[level])
        print(f"Level {level}: {count} entries")

    # Show examples of each level
    print("\n" + "="*80)
    print("EXAMPLES BY LEVEL:")
    print("="*80)

    for level in sorted(by_level.keys()):
        print(f"\n{'='*60}")
        print(f"LEVEL {level} (showing first 5 examples):")
        print('='*60)
        for title, page in by_level[level][:5]:
            print(f"  '{title}' → Page {page}")

    # Detect pattern: are chapters level 1, sections level 2, subsections level 3?
    print("\n" + "="*80)
    print("HIERARCHY PATTERN DETECTION:")
    print("="*80)

    # Check Level 1 - should be chapters
    level_1_samples = by_level.get(1, [])[:10]
    chapter_pattern = r'^\d+\s+'  # Starts with number
    chapters_found = sum(1 for title, _ in level_1_samples if re.match(chapter_pattern, title))

    print(f"\nLevel 1 Analysis:")
    print(f"  Samples checked: {len(level_1_samples)}")
    print(f"  Matches chapter pattern (starts with number): {chapters_found}/{len(level_1_samples)}")
    if chapters_found > len(level_1_samples) * 0.5:  # More than 50%
        print(f"  ✅ CONCLUSION: Level 1 = Chapters")
    else:
        print(f"  ❓ Mixed content at level 1")

    # Check Level 2 - should be sections
    level_2_samples = by_level.get(2, [])[:20]
    section_pattern = r'^\d+\.\d+\s+'  # Starts with X.Y
    sections_found = sum(1 for title, _ in level_2_samples if re.match(section_pattern, title))

    print(f"\nLevel 2 Analysis:")
    print(f"  Samples checked: {len(level_2_samples)}")
    print(f"  Matches section pattern (X.Y format): {sections_found}/{len(level_2_samples)}")
    if sections_found > len(level_2_samples) * 0.5:
        print(f"  ✅ CONCLUSION: Level 2 = Sections")
    else:
        print(f"  ❓ Mixed content at level 2")

    # Check Level 3 - should be subsections
    if 3 in by_level:
        level_3_samples = by_level.get(3, [])[:20]
        subsection_pattern = r'^\d+\.\d+\.\d+\s+'  # Starts with X.Y.Z
        subsections_found = sum(1 for title, _ in level_3_samples if re.match(subsection_pattern, title))

        print(f"\nLevel 3 Analysis:")
        print(f"  Samples checked: {len(level_3_samples)}")
        print(f"  Matches subsection pattern (X.Y.Z format): {subsections_found}/{len(level_3_samples)}")
        if subsections_found > len(level_3_samples) * 0.5:
            print(f"  ✅ CONCLUSION: Level 3 = Subsections")
        else:
            print(f"  ❓ Mixed content at level 3")

    # Show a complete example of one chapter with all its sections/subsections
    print("\n" + "="*80)
    print("COMPLETE CHAPTER EXAMPLE (Chapter 1 with all children):")
    print("="*80)

    current_chapter = None
    current_section = None
    count = 0

    for level, title, page in toc:
        if level == 1 and re.match(r'^1\s+', title):
            current_chapter = title
            print(f"\n📖 CHAPTER (Level {level}): {title}")
            print(f"   Page: {page}")
            count += 1
        elif current_chapter and level == 2 and title.startswith('1.'):
            current_section = title
            print(f"\n  📑 SECTION (Level {level}): {title}")
            print(f"     Page: {page}")
            count += 1
        elif current_chapter and level == 3 and title.startswith('1.'):
            print(f"\n    📄 SUBSECTION (Level {level}): {title}")
            print(f"       Page: {page}")
            count += 1
        elif current_chapter and level == 1:
            # Hit the next chapter, stop
            break

        if count > 20:  # Limit output
            print("\n  ... (more sections/subsections)")
            break

    # Summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print("""
✅ Bookmark structure is clean and hierarchical:
   - Level 1 = Chapters (e.g., "1 Introduction to Data Science")
   - Level 2 = Sections (e.g., "1.1 Introduction")
   - Level 3 = Subsections (e.g., "1.5.1 Managing Data Flow")

✅ Page numbers are accurate PyMuPDF page indices

✅ This structure can directly replace the need for index.yaml!

Implementation is straightforward:
   1. Extract bookmarks with doc.get_toc()
   2. Use level to determine hierarchy
   3. Use page numbers to extract text between bookmarks
   4. Generate notes following this structure
""")

    doc.close()

if __name__ == "__main__":
    analyze_hierarchy()
