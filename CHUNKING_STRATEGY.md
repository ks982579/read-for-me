# Improved Chunking Strategy Using index.yaml

## Executive Summary

This document outlines a new chunking strategy that leverages the `index.yaml` table of contents file to create semantically meaningful chunks aligned with the book's structure, rather than arbitrary token-based chunks.

## Problem Analysis

### Current Implementation Issues

1. **Generic Chunking**: The current `TextChunker` class uses token-based chunking (paragraphs, sentences, or fixed-size token windows) without considering the document's semantic structure.

2. **Lost Context**: Chunks may break in the middle of important concepts, separating related information across multiple chunks.

3. **No Section Awareness**: Generated notes don't follow the book's hierarchical structure (chapters → sections → subsections).

4. **Page Number Mismatch**: PDFs with front matter (Roman numerals) have inconsistent offsets between:
   - **Book page numbers** (as shown in the index.yaml, e.g., "page 1" for Chapter 1)
   - **PyMuPDF indices** (absolute position in PDF file, 0-based)

### Key Findings from Analysis

#### Page Numbering Investigation

Testing on `IntelligentTechniquesForDataScience.pdf` revealed:

- **Total PDF pages**: 282
- **Front matter**: ~15 pages (table of contents, preface, etc.)
- **Variable offset**: The offset between book pages and PyMuPDF indices is NOT constant:
  - Chapter 1 (book page 1) → PyMuPDF index 15 (offset: 15)
  - Chapter 2 (book page 31) → PyMuPDF index 45 (offset: 15)
  - Chapter 3 (book page 53) → PyMuPDF index 67 (offset: 15)
  - Chapter 4 (book page 95) → PyMuPDF index 108 (offset: 14)
  - Chapter 5 (book page 125) → PyMuPDF index 137 (offset: 13)
  - Chapter 6 (book page 157) → PyMuPDF index 168 (offset: 12)

**Conclusion**: The decreasing offset indicates blank/unnumbered pages between chapters. A fixed offset calculation won't work reliably.

## Proposed Strategy

### Core Approach: Content-Based Section Detection

Instead of relying on page numbers, **search for section headings directly in the PDF content** and extract text between consecutive headings.

### Algorithm

```
For each section in index.yaml (in order):
    1. Search PDF for the section heading text
    2. Record the PyMuPDF page index where it's found
    3. Extract text from that page until:
       - The next section heading is found, OR
       - The end of the chapter/document is reached
    4. Create a chunk for this section with:
       - Section hierarchy (chapter.section.subsection)
       - Actual content text
       - Starting page (PyMuPDF index)
    5. Send chunk to LLM for note generation
    6. Format notes in markdown following the book's structure
```

### Benefits

1. **Semantic Alignment**: Each chunk corresponds to a logical section of the book
2. **Structure Preservation**: Generated notes mirror the book's hierarchy
3. **Robust to Page Numbering**: No dependency on page number arithmetic
4. **Better Context**: The LLM processes complete conceptual units
5. **Easier Navigation**: Notes have clear section headers matching the original book

## Implementation Plan

### 1. Create New Module: `src/structured_chunker.py`

```python
class StructuredChunker:
    def __init__(self, pdf_path: str, index_yaml_path: str):
        """
        Initialize with PDF and its corresponding index.yaml file.
        """

    def load_index(self) -> dict:
        """
        Load and parse the index.yaml file.
        Returns the book structure as a nested dictionary.
        """

    def find_section_in_pdf(self, section_title: str, start_page: int = 0) -> int:
        """
        Search for a section heading in the PDF.

        Args:
            section_title: The title to search for (e.g., "Introduction to Data Science")
            start_page: PyMuPDF page index to start searching from

        Returns:
            PyMuPDF page index where the section starts, or -1 if not found
        """

    def extract_section_text(self, start_page: int, end_page: int) -> str:
        """
        Extract text content between two page indices.

        Args:
            start_page: PyMuPDF index where section starts
            end_page: PyMuPDF index where section ends (exclusive)

        Returns:
            Cleaned text content of the section
        """

    def chunk_by_structure(self) -> List[StructuredChunk]:
        """
        Main method: Create chunks following the book's structure.

        Returns:
            List of StructuredChunk objects, one per section/subsection
        """
```

### 2. Define New Data Structure: `StructuredChunk`

```python
@dataclass
class StructuredChunk:
    """A chunk representing a complete section from the book."""

    # Hierarchical position
    chapter_num: str          # e.g., "1"
    section_num: str          # e.g., "1.5" or "1.5.1"

    # Titles
    chapter_title: str        # e.g., "Introduction to Data Science"
    section_title: str        # e.g., "Data Science Activities in Three Dimensions"

    # Content
    content: str              # The actual text content

    # Location
    start_page_index: int     # PyMuPDF page index where section starts
    end_page_index: int       # PyMuPDF page index where section ends
    book_page: int            # Page number as shown in the book/index.yaml

    # Metadata
    token_count: int          # Number of tokens in content
    parent_section: str       # e.g., "1.5" for subsection "1.5.1"
```

### 3. Update Note Generation Workflow

Modify `main.py` to use the new structured chunking:

```python
# Instead of:
chunker = TextChunker(max_chunk_size=chunk_size, overlap_size=overlap)
all_chunks = []
for section in extracted_sections:
    chunks = chunker.smart_chunk(section.content, ...)
    all_chunks.extend(chunks)

# Use:
if index_yaml_path:
    # Structured chunking with index.yaml
    chunker = StructuredChunker(pdf_path, index_yaml_path)
    all_chunks = chunker.chunk_by_structure()
else:
    # Fall back to original chunking for PDFs without index.yaml
    chunker = TextChunker(max_chunk_size=chunk_size, overlap_size=overlap)
    # ... existing logic
```

### 4. Update Markdown Formatter

Modify `src/markdown_formatter.py` to output notes following the hierarchical structure:

```markdown
# [Chapter Number]. [Chapter Title]

> Book page: [X]

[Chapter-level notes if any]

## [Section Number] [Section Title]

> Book page: [Y]

[Section notes from LLM]

### [Subsection Number] [Subsection Title]

> Book page: [Z]

[Subsection notes from LLM]
```

### 5. Handle Edge Cases

#### A. Section Heading Not Found

If a section heading cannot be found in the PDF:
- Log a warning with the section title
- Try fuzzy matching (allowing for OCR errors or slight variations)
- As a fallback, estimate the page based on the previous section's end

#### B. Large Sections Exceeding Token Limits

If a section's content exceeds the LLM's context window:
- Split the section into smaller chunks using the existing `TextChunker`
- Process each sub-chunk separately
- Merge the notes back together for that section

#### C. Subsections vs. Sections

The index.yaml has nested structure (sections contain subsections). Two approaches:

**Option 1: Flat Processing**
- Process all sections and subsections as separate chunks
- Easier to implement
- Each gets its own note

**Option 2: Hierarchical Processing**
- Process parent sections including all subsection content
- Then process subsections individually
- Parent section note provides overview, subsection notes provide details
- More complex but better context

**Recommendation**: Start with Option 1 for simplicity.

#### D. Missing index.yaml

If a PDF doesn't have an index.yaml:
- Fall back to the existing `TextChunker` approach
- Or provide a tool to generate a basic index.yaml from the PDF's table of contents

## Implementation Steps

### Phase 1: Core Functionality
1. ✅ Analyze page numbering behavior (DONE)
2. Create `StructuredChunker` class
3. Implement `find_section_in_pdf()` with heading search
4. Implement `extract_section_text()`
5. Implement `chunk_by_structure()` to iterate through index.yaml

### Phase 2: Integration
6. Update `main.py` to support `--index` flag for index.yaml path
7. Update note generation to handle `StructuredChunk` objects
8. Update markdown formatter to output hierarchical structure

### Phase 3: Polish
9. Add fuzzy matching for section headings
10. Handle large sections exceeding token limits
11. Add validation to check if all sections were found
12. Create utility to generate index.yaml from PDF ToC

### Phase 4: Testing
13. Test with the example book (IntelligentTechsForDS)
14. Compare output quality vs. current chunking
15. Test with other PDFs (with and without index.yaml)

## Example Usage

```bash
# With index.yaml (new structured approach)
python main.py ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf \
    --index ebooks/IntelligentTechsForDS/index.yaml \
    --use-api \
    --output-dir ebooks/IntelligentTechsForDS/

# Without index.yaml (falls back to existing chunking)
python main.py some_other_book.pdf --use-api
```

## Expected Output Structure

Based on the example `notes.md`, the output should look like:

```markdown
```yaml
title: Intelligent Techniques for Data Science
subtitle: n/a
authors:
- Rajendra Akerkar
- Priti Srinivas Sajja
publisher: Springer International Publishing Switzerland
year: 2016
```

# 1. Introduction to Data Science

> p. 1

[LLM-generated chapter overview notes]

## 1.1 Introduction

> p. 1

[LLM-generated section notes]

## 1.2 History of Data Science

> p. 2

[LLM-generated section notes]

## 1.5 Data Science Activities in Three Dimensions

> p. 8

[LLM-generated section notes]

### 1.5.1 Managing Data Flow

> p. 8

[LLM-generated subsection notes]

### 1.5.2 Managing Data Curation

> p. 11

[LLM-generated subsection notes]

...
```

## Advantages Over Current Approach

| Aspect | Current Chunking | Structured Chunking |
|--------|-----------------|-------------------|
| **Chunk boundaries** | Arbitrary (based on tokens) | Semantic (based on sections) |
| **Context preservation** | May break mid-concept | Complete conceptual units |
| **Output structure** | Flat list of notes | Hierarchical, matches book |
| **Navigation** | Difficult to map back to book | Direct correspondence to ToC |
| **Page numbers** | Relies on offset calculation | Searches for actual content |
| **LLM prompts** | Generic "summarize this text" | Can include section context |
| **Reusability** | Must re-chunk for different use cases | Logical sections reusable |

## Potential Challenges

1. **Heading variation**: Book headings may not exactly match index.yaml
   - **Solution**: Fuzzy matching with similarity threshold

2. **Very large sections**: Some sections may exceed LLM context limits
   - **Solution**: Hybrid approach - split large sections using TextChunker

3. **Complex formatting**: Tables, equations, figures may disrupt text extraction
   - **Solution**: Enhanced PDF parsing, possibly with layout analysis

4. **Performance**: Searching for each heading individually could be slow
   - **Solution**: Single-pass algorithm that finds all headings in one iteration

## Future Enhancements

1. **Auto-generate index.yaml**: Parse PDF table of contents automatically
2. **Multi-level summarization**: Chapter summaries that synthesize section notes
3. **Cross-references**: Detect and preserve references between sections
4. **Visual elements**: Extract and describe figures, tables, equations
5. **Configurable granularity**: User chooses depth (chapter-level vs. subsection-level)

## Conclusion

The structured chunking approach addresses the core limitations of token-based chunking by aligning with the document's inherent organization. While it requires an index.yaml file, this additional metadata enables:

- Higher quality notes that respect conceptual boundaries
- Output that mirrors the source material's structure
- Robust handling of complex page numbering schemes
- Better context for the LLM to generate meaningful summaries

The implementation can coexist with the current chunking strategy, providing a fallback for documents without index.yaml files.
