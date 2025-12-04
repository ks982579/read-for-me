# Bookmark-Based Chunking Guide

## Overview

The bookmark-based chunking system automatically extracts document structure from PDF bookmarks and creates semantically meaningful chunks aligned with chapters, sections, and subsections. This eliminates the need for manual `index.yaml` creation and works out-of-the-box with most well-formatted technical PDFs.

## Key Features

✅ **Zero manual work** - Extracts structure automatically from PDF metadata
✅ **Hierarchical notes** - Output mirrors the book's organization
✅ **Page range filtering** - Test single chapters before processing entire books
✅ **Automatic fallback** - Falls back to token-based chunking if no bookmarks exist
✅ **Large section handling** - Automatically splits sections exceeding token limits
✅ **Metadata extraction** - Includes title, author, subject in output

## Usage

### Basic Usage with Auto Mode

```bash
# Process entire PDF with bookmark-based chunking
python main.py book.pdf --auto --use-api

# The --auto flag enables automatic structure detection
```

### Test Single Chapter

```bash
# Process only pages 16-45 (Chapter 1 in the example book)
python main.py book.pdf --auto --use-api --pages 16-45

# This extracts only sections that START in the page range
# Useful for testing before processing the full book
```

### Full Command Options

```bash
python main.py your_book.pdf \
    --auto \                      # Enable bookmark-based chunking
    --use-api \                   # Use Claude API for note generation
    --api-model claude-3-5-sonnet-20241022 \
    --chunk-size 2048 \           # Max tokens per chunk (for splitting large sections)
    --overlap 200 \               # Overlap when splitting (preserves context)
    --pages 16-45 \               # Optional: process specific pages only
    --output-dir ./output         # Where to save notes
```

## How It Works

### 1. Bookmark Extraction

The system reads PDF bookmarks (the outline you see in PDF readers):

```python
toc = doc.get_toc()  # Returns [(level, title, page), ...]
# Example:
# (1, "1 Introduction to Data Science", 16)      # Chapter
# (2, "1.1 Introduction", 17)                    # Section
# (3, "1.5.1 Managing Data Flow", 24)            # Subsection
```

### 2. Hierarchy Detection

Bookmark levels directly map to document structure:
- **Level 1** = Chapters (e.g., "1 Introduction to Data Science")
- **Level 2** = Sections (e.g., "1.1 Introduction")
- **Level 3** = Subsections (e.g., "1.5.1 Managing Data Flow")
- **Level 4** = Sub-subsections (rare, very detailed sections)

### 3. Text Extraction

For each bookmark, the system:
1. Extracts text from the bookmark's page to the next bookmark's page
2. Counts tokens in the extracted content
3. If too large, splits using `TextChunker` with overlap
4. Creates `StructuredChunk` objects with hierarchy metadata

### 4. Page Range Filtering (--pages flag)

When you specify a page range:
- System finds the **first complete section** that starts on/after the start page
- This avoids backtracking to get partial sections
- Example: If page 50 starts mid-section 2.4, it skips to section 2.5

**Why this design?**
- Cleaner section boundaries
- No partial/incomplete sections
- Easier implementation
- Better for testing specific chapters

### 5. Note Generation

For each chunk:
1. Send content to LLM (Claude API or local model)
2. LLM generates structured notes
3. Notes are paired with chunk metadata (level, number, title, etc.)

### 6. Markdown Output

Output follows the book's hierarchical structure:

```markdown
---
title: Intelligent Techniques for Data Science
authors:
  - Rajendra Akerkar
  - Priti Srinivas Sajja
generated: 2025-12-04
---

# 1 Introduction to Data Science

> p. 16

[Chapter-level notes]

## 1.1 Introduction

> p. 17

[Section notes from LLM]

### 1.5.1 Managing Data Flow

> p. 24

[Subsection notes from LLM]
```

## Test Results

Tested with `IntelligentTechniquesForDataScience.pdf`:

### Full PDF Extraction
- ✅ **185 chunks** extracted from 269 bookmarks
- ✅ All hierarchy levels preserved (1-4)
- ✅ Page numbers accurate

### Page Range Filtering (pages 16-45, Chapter 1)
- ✅ **18 chunks** extracted
- ✅ Only sections starting in range included
- ✅ Clean section boundaries maintained

### Large Section Splitting
- ✅ Sections exceeding token limits automatically split
- ✅ Overlap preserved for context
- ✅ Split indicators in output (e.g., "Part 2/3")

## Fallback Behavior

If PDF has **no bookmarks**, the system:
1. Logs a warning: "⚠️ No bookmarks found, falling back to token-based chunking..."
2. Uses traditional `TextChunker` approach
3. Output format remains flat (no hierarchy)

This ensures the tool works with any PDF, even poorly formatted ones.

## Output Structure

### With Bookmarks (Hierarchical)

```markdown
---
title: Book Title
authors:
  - Author Name
generated: 2025-12-04
---

# 1 Chapter Title

> p. X

[Notes]

## 1.1 Section Title

> p. Y

[Notes]

### 1.1.1 Subsection Title

> p. Z

[Notes]
```

### Without Bookmarks (Flat)

```markdown
# Notes: Book Title
*Generated on: 2025-12-04*

## Chapter Title

### Note 1 (Page X)

[Notes]

---

### Note 2 (Page Y)

[Notes]
```

## Code Architecture

### New Files

1. **`src/bookmark_chunker.py`**
   - `StructuredChunk` dataclass - represents a section with hierarchy
   - `BookmarkChunker` class - main chunking logic

2. **`src/markdown_formatter.py`** (extended)
   - `extract_pdf_metadata()` - gets title, author, etc.
   - `format_structured_notes_to_markdown()` - hierarchical output

3. **`main.py`** (extended)
   - `--auto` flag for bookmark mode
   - Automatic fallback logic
   - Handles both chunking modes

### Key Classes

#### StructuredChunk

```python
@dataclass
class StructuredChunk:
    # Hierarchy
    level: int                    # 1=chapter, 2=section, 3=subsection
    number: str                   # e.g., "1.5.1"
    title: str                    # e.g., "Managing Data Flow"

    # Context
    chapter_number: str           # e.g., "1"
    chapter_title: str            # e.g., "Introduction to Data Science"
    parent_section: str           # e.g., "1.5" for subsection "1.5.1"

    # Content
    content: str                  # Actual text

    # Location
    start_page: int               # PyMuPDF index (0-based)
    end_page: int                 # PyMuPDF index (0-based)

    # Metadata
    token_count: int
    is_split: bool                # True if split from large section
    split_index: int              # Which part (0-based)
    total_splits: int             # Total parts

    # Compatibility properties for NoteGenerator interface
    @property
    def chunk_id(self) -> int:
        # Returns split_index for compatibility
        return self.split_index

    @property
    def source_pages(self) -> List[int]:
        # Returns 1-based page numbers from start to end
        return list(range(self.start_page + 1, self.end_page + 1))
```

#### BookmarkChunker

```python
class BookmarkChunker:
    def has_bookmarks() -> bool
        # Check if PDF has bookmarks

    def chunk_by_bookmarks(start_page, end_page) -> List[StructuredChunk]
        # Main method: extract structured chunks

    def filter_bookmarks_by_page_range(...)
        # Filter to specific pages

    def extract_text_between_pages(start, end) -> str
        # Extract and clean text
```

## Advantages Over Token-Based Chunking

| Aspect | Token-Based | Bookmark-Based |
|--------|-------------|----------------|
| **Setup** | Works immediately | Requires bookmarks in PDF |
| **Chunk boundaries** | Arbitrary (token limits) | Semantic (sections) |
| **Context** | May break mid-concept | Complete conceptual units |
| **Output structure** | Flat | Hierarchical |
| **Navigation** | Hard to map to book | Direct correspondence |
| **Note quality** | Generic | Section-aware context |
| **Reusability** | Low | High (logical sections) |

## Limitations

1. **Requires bookmarks** - PDF must have proper outline metadata
   - Most technical books from publishers have this
   - Scanned PDFs often don't
   - Solution: Falls back to token-based chunking

2. **Bookmark quality varies** - Some PDFs have incomplete/poor bookmarks
   - Missing subsections
   - Incorrect page numbers (rare)
   - Solution: System is robust to missing sections

3. **Page range may miss parent sections** - By design
   - If you request pages 20-30, but section 1.5 starts on page 18
   - You'll get subsections 1.5.1, 1.5.2 but not 1.5 itself
   - Solution: Include a few extra pages before your target range

## Best Practices

### 1. Test First with Single Chapter

```bash
# Find where your target chapter starts (check PDF)
# Then process just that chapter first
python main.py book.pdf --auto --use-api --pages 16-45
```

### 2. Check for Bookmarks First

```bash
# Quick check if your PDF has bookmarks
python test_bookmarks.py  # Our test script

# Or use PyMuPDF:
import pymupdf
doc = pymupdf.open("book.pdf")
toc = doc.get_toc()
print(f"Found {len(toc)} bookmarks")
```

### 3. Adjust Chunk Size Based on Content

```bash
# For dense technical content, use larger chunks
python main.py book.pdf --auto --use-api --chunk-size 4096

# For lighter content or faster processing, use smaller chunks
python main.py book.pdf --auto --use-api --chunk-size 1024
```

### 4. Use Overlap for Better Context

```bash
# More overlap = better context but more duplication
python main.py book.pdf --auto --use-api --overlap 500
```

## Troubleshooting

### "No bookmarks found"
- PDF doesn't have outline metadata
- Check: Open PDF in reader, look for bookmarks panel
- Solution: Falls back to token-based chunking automatically

### "No content in specified page range"
- Page range too narrow or no bookmarks in that range
- Solution: Widen the range or check bookmark locations first

### Notes are too fragmented
- Chunk size is too small, causing excessive splitting
- Solution: Increase `--chunk-size` to 4096 or 8192

### Missing sections in output
- Page range filtering excludes sections starting before range
- Solution: Include a few pages before your target chapter

## Future Enhancements

Potential improvements (not yet implemented):

1. **Include parent sections** - When filtering by page range, include parent sections for context even if they start earlier
2. **Fuzzy bookmark matching** - Handle OCR errors in bookmark titles
3. **Merge split notes** - Combine notes from split sections into single coherent note
4. **Chapter summaries** - Generate overview notes for each chapter
5. **Cross-references** - Detect and preserve references between sections
6. **Auto-detect chapter boundaries** - For PDFs without bookmarks, detect chapters by typography

## Comparison: Original Strategy vs. Implemented

### Original Strategy (index.yaml)
- Required manual creation of index.yaml for each book
- Used text search to find section headings
- Page number offset calculations
- More complex, more manual work

### Implemented Strategy (bookmarks)
- Zero manual work
- Bookmarks provide structure directly
- Page numbers already accurate
- Simpler, more reliable

**Why the change?** Testing revealed that well-formatted PDFs have excellent bookmark metadata that's more reliable than text search. This makes the tool much more practical for real-world use.

## Conclusion

The bookmark-based chunking system provides:
- ✅ Automatic structure detection
- ✅ High-quality hierarchical notes
- ✅ Minimal manual work
- ✅ Robust fallback for PDFs without bookmarks
- ✅ Page range filtering for testing

It's ready for use with most technical books and documentation!
