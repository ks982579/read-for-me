# Read For Me - Technical Documentation

## Overview

Read For Me is an intelligent PDF note-taking system that extracts structured notes from technical books using LLMs. It automatically detects document structure from PDF bookmarks and creates hierarchical markdown notes that mirror the book's organization.

## Core Features

### 1. Automatic Structure Detection
- Extracts table of contents from PDF bookmarks
- Detects chapters, sections, and subsections automatically
- Zero manual configuration required for well-formatted PDFs

### 2. Heading-Based Text Extraction
- Searches for actual section headings in PDF text
- Extracts content precisely between headings (not just page boundaries)
- Handles variable heading formats:
  - "1.1 Introduction" (section with number)
  - "Chapter 1\nTitle" (chapter with prefix)
  - "Managing Data Flow" (subsection titles)

### 3. Hierarchical Note Generation
- Preserves document structure in output
- Auto-inserts missing parent headers when page filtering is used
- Includes metadata (title, authors, model used, generation date)

### 4. Flexible Chunking
- Smart splitting of large sections with overlap
- Respects semantic boundaries (complete sections)
- Token-aware to fit within LLM context windows

### 5. Multiple LLM Support
- **Ollama** (local models): Fast, private, no API costs
- **Claude API**: High-quality notes, requires API key
- Configurable model selection

## Architecture

### Key Components

```
src/
├── bookmark_chunker.py       # Core: Extracts structure from bookmarks
├── pdf_extractor.py          # PDF text extraction (fallback)
├── text_chunker.py           # Token-based chunking utilities
├── note_generator.py         # Ollama-based note generation
├── api_note_generator.py     # Claude API-based note generation
└── markdown_formatter.py     # Hierarchical markdown output
```

### Data Flow

```
PDF Input
    ↓
Bookmark Extraction (get_toc)
    ↓
Heading-Based Text Extraction
    ↓
    ├─ Find section heading in text
    ├─ Extract content until next heading
    └─ Repeat for all sections
    ↓
Chunking (if section > max_tokens)
    ↓
LLM Note Generation
    ↓
Hierarchical Markdown Output
```

## Heading-Based Extraction Algorithm

### Problem
Page-based extraction includes content from the next section if it starts mid-page.

### Solution
1. **Use bookmarks as hints** for approximate section locations
2. **Search for actual headings** in PDF text starting from bookmark page
3. **Extract text between headings** regardless of page boundaries

### Implementation

```python
def extract_text_between_headings(
    start_page,           # Where to start searching
    start_heading_title,  # "Introduction"
    start_section_number, # "1.1"
    end_heading_title,    # "History of Data Science"
    end_section_number    # "1.2"
):
    # 1. Search for start heading on start_page
    # 2. Once found, extract all text after heading
    # 3. Continue to next pages searching for end heading
    # 4. Stop when end heading found
    # 5. Return only content between the two headings
```

### Heading Detection

Handles multiple formats with normalization:
```python
# Normalizes whitespace (spaces, tabs, newlines → single space)
"1.1     Introduction"  → "1.1 Introduction"
"1.1\tIntroduction"     → "1.1 Introduction"
"1.1\nIntroduction"     → "1.1 Introduction"

# Tries multiple patterns
patterns = [
    "1.1\\s+Introduction",  # Number + whitespace + title
    "Introduction"           # Title only (fallback)
]
```

## Usage

### Basic Usage (Auto Mode)

```bash
# Process entire book with automatic structure detection
python main.py book.pdf --auto --use-api
```

### Test Single Chapter First

```bash
# Check bookmark structure
python test_bookmarks.py book.pdf

# Process specific page range (recommended for testing)
python main.py book.pdf --auto --use-api --pages 1-30
```

### Configuration Options

```bash
python main.py book.pdf \
    --auto \                          # Enable bookmark-based chunking
    --use-api \                       # Use Claude API (or omit for Ollama)
    --api-model claude-3-5-sonnet-20241022 \
    --chunk-size 2048 \              # Max tokens per chunk
    --overlap 64 \                    # Token overlap for splits
    --pages 1-30 \                    # Optional: specific pages
    --output-dir ./output             # Output directory
```

### Page Numbering

**Important**: Page numbers use **0-based indexing** (PyMuPDF's internal format).
- Page 1 in PDF reader = Page 0 in command
- Use `test_bookmarks.py` to see actual page numbers

## Output Format

### Structured Notes (with --auto)

```markdown
---
title: Book Title
authors:
  - Author Name
generated: 2025-12-04
model: qwen3:8b
---

# 1 Introduction to Data Science

> p. 15

*[Chapter header - no separate notes generated]*

## 1.1 Introduction

> p. 16

[LLM-generated notes for section 1.1]

## 1.5 Data Science Activities in Three Dimensions

> p. 22

*[Section header - content starts with subsections below]*

### 1.5.1 Managing Data Flow

> p. 23

[LLM-generated notes for subsection 1.5.1]
```

### Key Features of Output

1. **YAML Frontmatter**: Metadata including model used (for comparison)
2. **Hierarchical Structure**: Mirrors book's organization
3. **Auto-inserted Headers**: Missing parent sections included with notes
4. **Page References**: 0-based page numbers for each section
5. **Model Attribution**: Track which model generated the notes

## Fallback Behavior

### No Bookmarks Found
Falls back to traditional token-based chunking:
```
⚠️  No bookmarks found, falling back to token-based chunking...
```

Output uses flat structure without hierarchy.

### Heading Not Found
If heading search fails (rare), uses page boundaries as fallback:
```python
if heading_not_found:
    # Take entire page content
    content = page.get_text()
```

This ensures extraction always succeeds even with unusual PDF formats.

## Page Range Filtering

### Behavior
When using `--pages X-Y`:
- Only processes bookmarks that **START** within range
- Auto-inserts parent headers if children are in range but parents aren't
- This avoids backtracking and keeps clean section boundaries

### Example
```bash
--pages 16-30
```

If Chapter 1 starts at page 15 (outside range) but Section 1.1 starts at page 16 (inside):
- Skips Chapter 1 bookmark
- Processes Section 1.1 bookmark
- Output auto-inserts Chapter 1 header for structure
- Marks it as "*[Chapter header - no separate notes generated]*"

## Model Configuration

### Ollama (Local)
Configured in `src/note_generator.py`:
```python
self.model_name = "qwen3:8b"  # Default
```

Change this to use different Ollama models.

### Claude API
Requires `.env` file with:
```
CLAUDE_KEY=your_api_key_here
```

Specify model with `--api-model`:
- `claude-3-5-sonnet-20241022` (best quality)
- `claude-3-5-haiku-20241022` (faster, cheaper)

## Comparing Models

The output includes model name in metadata, making it easy to compare:

```bash
# Generate with Qwen
python main.py book.pdf --auto --pages 16-30 -o output/qwen

# Generate with Claude Sonnet
python main.py book.pdf --auto --use-api --pages 16-30 -o output/sonnet

# Generate with Claude Haiku
python main.py book.pdf --auto --use-api \
    --api-model claude-3-5-haiku-20241022 \
    --pages 16-30 -o output/haiku

# Compare outputs
diff output/qwen/*.md output/sonnet/*.md
```

Each file will have its model in the frontmatter for easy tracking.

## Known Limitations

### Headers and Footers
Currently included in extraction. The LLM usually filters them during note generation, but they appear in raw content.

**Future Enhancement**: Detect and strip headers/footers automatically.

### Chapter Format Assumptions
Assumes chapters start on new pages (common for technical books).

Handles:
- "Chapter 1\nTitle" format
- Numbered chapters (1, 2, 3...)
- Section numbering (1.1, 1.2, etc.)

### Variable Heading Spacing
Handles most spacing variations, but very unusual formats might fail.

Falls back to page-based extraction if heading not found.

### Roman Numeral Front Matter
Front matter pages (i, ii, iii...) are handled automatically via bookmarks.
No special offset calculation needed.

## Troubleshooting

### "No bookmarks found"
**Solution**: PDF lacks outline metadata. Use traditional mode or create bookmarks in PDF editor.

### "No content in specified page range"
**Solution**: Page range too narrow or doesn't contain bookmarks. Widen range or check with `test_bookmarks.py`.

### Section boundaries seem wrong
**Solution**: Check if PDF headings match bookmark titles. Slight variations are handled, but major differences may cause issues.

### Notes include content from next section
**Solution**: This shouldn't happen with heading-based extraction. Please report as bug with PDF sample.

## File Structure

```
read-for-me/
├── src/
│   ├── bookmark_chunker.py      # Main logic
│   ├── pdf_extractor.py
│   ├── text_chunker.py
│   ├── note_generator.py
│   ├── api_note_generator.py
│   └── markdown_formatter.py
├── main.py                       # CLI entry point
├── test_bookmarks.py            # Utility to check PDF structure
├── CLAUDE.md                    # This file (technical docs)
├── BOOKMARK_CHUNKING_GUIDE.md   # User guide
└── output/                      # Generated notes
```

## Development Notes

### Adding New LLM Support
Implement interface matching:
```python
class YourNoteGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_note_from_chunk(self, chunk) -> GeneratedNote:
        # chunk has: content, chapter_title, chunk_id, source_pages
        # Return GeneratedNote with: content, source_chunk_ids, source_pages
```

### Customizing Note Prompts
Edit prompts in:
- `src/note_generator.py` → `_create_note_prompt()`
- `src/api_note_generator.py` → `_create_note_prompt()`

### Adding Header/Footer Detection
Implement in `bookmark_chunker.py`:
```python
def remove_headers_footers(self, text: str, page_num: int) -> str:
    # Detect repeated text across pages
    # Strip lines matching header/footer patterns
    return cleaned_text
```

Call before returning from `extract_text_between_headings()`.

## Performance

### Benchmark (Example Book, 282 pages)
- **Bookmark extraction**: < 1 second
- **Heading-based text extraction**: ~0.5 seconds per section
- **Note generation**:
  - Ollama (qwen3:8b): ~2-5 seconds per chunk
  - Claude API: ~1-3 seconds per chunk
- **Total for Chapter 1 (30 pages)**: ~5-10 minutes

### Optimization Tips
1. Use `--pages` to process incrementally
2. Larger `--chunk-size` = fewer LLM calls but higher token cost
3. Local Ollama is faster for bulk processing (no API rate limits)
4. Claude API gives better quality notes but costs money

## Future Enhancements

### Planned
- [ ] Header/footer detection and removal
- [ ] Table and figure extraction
- [ ] Cross-reference detection
- [ ] Multi-level note summarization (chapter summaries)
- [ ] Equation/formula preservation

### Possible
- [ ] Visual heading detection (for PDFs without bookmarks)
- [ ] Auto-generate bookmarks from typography
- [ ] Support for multi-column layouts
- [ ] Embedded image descriptions

## Contributing

When modifying extraction logic:
1. Test with multiple PDF formats
2. Verify heading detection with unusual spacing
3. Check fallback behavior when headings not found
4. Ensure page range filtering works correctly
5. Test with both short and long sections

## License & Attribution

Built with Claude Code assistance.
Uses PyMuPDF for PDF processing, Anthropic Claude API, and Ollama for local models.

---

**Last Updated**: 2025-12-04
**Current Version**: Heading-based extraction with auto structure detection
