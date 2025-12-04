"""
Bookmark-based chunking that extracts document structure from PDF bookmarks
and creates semantically meaningful chunks aligned with chapters/sections.
"""

import pymupdf
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from src.text_chunker import TextChunker


@dataclass
class StructuredChunk:
    """
    A chunk representing a complete section from the book.

    Preserves hierarchical context and page locations for better note organization.
    Compatible with both NoteGenerator and APIBasedNoteGenerator interfaces.
    """
    # Hierarchical position
    level: int                    # Bookmark level (1=chapter, 2=section, 3=subsection, etc.)
    number: str                   # Section number (e.g., "1.5.1")
    title: str                    # Section title (e.g., "Managing Data Flow")

    # Parent context for hierarchy
    chapter_number: str           # e.g., "1"
    chapter_title: str            # e.g., "Introduction to Data Science"
    parent_section: Optional[str] # e.g., "1.5" for subsection "1.5.1"

    # Content
    content: str                  # The actual text content

    # Location
    start_page: int               # PyMuPDF page index (0-based) where section starts
    end_page: int                 # PyMuPDF page index (0-based) where section ends

    # Metadata
    token_count: int              # Number of tokens in content

    # Fields with defaults (must come after non-default fields in dataclass)
    parent_section_title: Optional[str] = None  # e.g., "Data Science Activities" for subsection "1.5.1"
    is_split: bool = False        # True if this chunk was split from a larger section
    split_index: int = 0          # If split, which part this is (0-based)
    total_splits: int = 1         # If split, total number of parts

    # Compatibility attributes for NoteGenerator interface
    # These make StructuredChunk compatible with existing note generators
    @property
    def chunk_id(self) -> int:
        """
        Compatibility property for NoteGenerator.
        Returns split_index as the chunk ID.
        """
        return self.split_index

    @property
    def source_pages(self) -> List[int]:
        """
        Compatibility property for NoteGenerator.
        Returns list of pages spanned by this chunk (1-based page numbers).
        """
        # Convert 0-based indices to 1-based page numbers
        # Include all pages from start to end (inclusive)
        return list(range(self.start_page + 1, self.end_page + 1))


class BookmarkChunker:
    """
    Extracts document structure from PDF bookmarks and creates structured chunks.

    Automatically detects chapters, sections, and subsections from PDF outline,
    eliminating the need for manual index.yaml creation.
    """

    def __init__(self, pdf_path: str, max_chunk_size: int = 2048, overlap_size: int = 200):
        """
        Initialize the bookmark-based chunker.

        Args:
            pdf_path: Path to the PDF file
            max_chunk_size: Maximum tokens per chunk (for splitting large sections)
            overlap_size: Token overlap when splitting large sections
        """
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(pdf_path)
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.text_chunker = TextChunker(max_chunk_size, overlap_size)

    def has_bookmarks(self) -> bool:
        """
        Check if the PDF has extractable bookmarks.

        Returns:
            True if bookmarks exist, False otherwise
        """
        toc = self.doc.get_toc()
        return len(toc) > 0

    def extract_bookmarks(self) -> List[Tuple[int, str, int]]:
        """
        Extract all bookmarks from the PDF.

        Returns:
            List of (level, title, page) tuples where:
            - level: hierarchy level (1=chapter, 2=section, etc.)
            - title: bookmark title
            - page: PyMuPDF page index (0-based)
        """
        return self.doc.get_toc()

    def filter_bookmarks_by_page_range(
        self,
        bookmarks: List[Tuple[int, str, int]],
        start_page: int,
        end_page: int
    ) -> List[Tuple[int, str, int]]:
        """
        Filter bookmarks to only include those starting at or after start_page.

        Finds the first complete bookmark (chapter/section/subsection) that begins
        on or after start_page, ensuring clean section boundaries without backtracking.

        Args:
            bookmarks: List of (level, title, page) tuples
            start_page: Start page (1-based, human-readable)
            end_page: End page (1-based, human-readable)

        Returns:
            Filtered list of bookmarks
        """
        # Convert 1-based human page numbers to 0-based PyMuPDF indices
        start_idx = start_page - 1
        end_idx = end_page - 1

        # Filter to bookmarks that start within or before the range
        filtered = []
        for level, title, page in bookmarks:
            # Include if bookmark starts within range
            if start_idx <= page <= end_idx:
                filtered.append((level, title, page))
            # Stop if we've passed the end
            elif page > end_idx:
                break

        return filtered

    def parse_section_number(self, title: str) -> Optional[str]:
        """
        Extract section number from bookmark title.

        Handles formats like:
        - "1.5.1 Managing Data Flow" -> "1.5.1"
        - "3 Basic Learning Algorithms" -> "3"
        - "Preface" -> None

        Args:
            title: Bookmark title

        Returns:
            Section number string, or None if no number found
        """
        # Match patterns like "1", "1.5", "1.5.1", "1.5.1.2" at start of title
        match = re.match(r'^(\d+(?:\.\d+)*)\s+', title)
        if match:
            return match.group(1)
        return None

    def get_chapter_context(
        self,
        bookmarks: List[Tuple[int, str, int]],
        current_index: int
    ) -> Tuple[str, str]:
        """
        Find the chapter number and title for a given bookmark.

        Walks backwards through bookmarks to find the parent chapter (level 1).

        Args:
            bookmarks: List of all bookmarks
            current_index: Index of current bookmark in the list

        Returns:
            Tuple of (chapter_number, chapter_title)
        """
        # Walk backwards to find the chapter (level 1)
        for i in range(current_index, -1, -1):
            level, title, _ = bookmarks[i]
            if level == 1:
                number = self.parse_section_number(title)
                if number:
                    # Remove number from title
                    clean_title = re.sub(r'^\d+(?:\.\d+)*\s+', '', title)
                    return number, clean_title
                else:
                    # No number (e.g., "Preface"), use full title
                    return "", title

        return "", ""

    def get_parent_section(self, section_number: str) -> Optional[str]:
        """
        Get the parent section number for a given section.

        Examples:
        - "1.5.1" -> "1.5"
        - "1.5" -> "1"
        - "1" -> None

        Args:
            section_number: Section number string

        Returns:
            Parent section number, or None if already at top level
        """
        parts = section_number.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        return None

    def get_parent_section_title(
        self,
        bookmarks: List[Tuple[int, str, int]],
        current_index: int,
        parent_section_number: str
    ) -> Optional[str]:
        """
        Find the title of a parent section by searching backwards through bookmarks.

        Args:
            bookmarks: List of all bookmarks
            current_index: Index of current bookmark
            parent_section_number: The parent section number to find (e.g., "1.5")

        Returns:
            Parent section title, or None if not found
        """
        # Walk backwards to find the parent section
        for i in range(current_index - 1, -1, -1):
            level, title, _ = bookmarks[i]
            section_num = self.parse_section_number(title)

            if section_num == parent_section_number:
                # Found the parent section - extract title without number
                clean_title = re.sub(r'^\d+(?:\.\d+)*\s+', '', title)
                return clean_title

        return None

    def normalize_text_for_matching(self, text: str) -> str:
        """
        Normalize text for heading matching by removing extra whitespace.

        Handles cases where headings might have tabs, multiple spaces, or
        newlines between the section number and title.

        Args:
            text: Text to normalize

        Returns:
            Normalized text with single spaces
        """
        # Replace all whitespace (spaces, tabs, newlines) with single space
        normalized = re.sub(r'\s+', ' ', text)
        return normalized.strip()

    def find_heading_in_text(self, text: str, heading_title: str, section_number: str = None) -> int:
        """
        Find the position of a heading in text.

        Handles various heading formats:
        - "1.1 Introduction" (section number + title)
        - "Introduction to Data Science" (chapter title only)
        - "Chapter 1\\nIntroduction to Data Science" (chapter with prefix)

        Args:
            text: Text to search in (from page)
            heading_title: The heading title to find (e.g., "Introduction")
            section_number: Optional section number (e.g., "1.1")

        Returns:
            Character position where heading starts, or -1 if not found
        """
        # Normalize the text for searching
        normalized_text = self.normalize_text_for_matching(text)
        normalized_title = self.normalize_text_for_matching(heading_title)

        # Try different heading patterns
        patterns = []

        if section_number:
            # Pattern: "1.1 Introduction" or "1.1\tIntroduction" etc.
            # The \s+ allows for any whitespace between number and title
            escaped_number = re.escape(section_number)
            patterns.append(f"{escaped_number}\\s+{re.escape(normalized_title)}")
            patterns.append(f"{escaped_number}\\s*{re.escape(normalized_title)}")

        # Also try just the title (for chapters or when number matching fails)
        patterns.append(re.escape(normalized_title))

        for pattern in patterns:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                return match.start()

        return -1

    def extract_text_between_headings(
        self,
        start_page: int,
        start_heading_title: str,
        start_section_number: str,
        end_heading_title: str = None,
        end_section_number: str = None,
        max_pages: int = 50
    ) -> str:
        """
        Extract text between two section headings, searching across pages.

        This is more accurate than page-based extraction because it finds actual
        heading positions in text rather than assuming headings align with pages.

        Args:
            start_page: Page to start searching (0-based)
            start_heading_title: Title of starting section
            start_section_number: Section number (e.g., "1.1")
            end_heading_title: Title of ending section (optional)
            end_section_number: Section number of ending section (optional)
            max_pages: Maximum pages to search (prevents infinite loops)

        Returns:
            Text content between the two headings
        """
        content_parts = []
        found_start = False
        start_position = 0

        # Search for the start heading and extract until end heading
        for page_offset in range(max_pages):
            page_num = start_page + page_offset

            if page_num >= len(self.doc):
                break

            page = self.doc[page_num]
            page_text = page.get_text()

            if not page_text.strip():
                continue

            # Look for start heading on first page
            if not found_start and page_offset == 0:
                start_pos = self.find_heading_in_text(
                    page_text,
                    start_heading_title,
                    start_section_number
                )

                if start_pos >= 0:
                    found_start = True
                    # Extract text after the heading on this page
                    # Skip the heading itself by finding the end of the line
                    lines = page_text.split('\n')
                    current_pos = 0

                    for i, line in enumerate(lines):
                        line_end = current_pos + len(line)

                        if current_pos <= start_pos < line_end:
                            # Found the line with the heading, start from next line
                            remaining_text = '\n'.join(lines[i+1:])

                            # Check if end heading is on same page
                            if end_heading_title:
                                end_pos = self.find_heading_in_text(
                                    remaining_text,
                                    end_heading_title,
                                    end_section_number
                                )

                                if end_pos >= 0:
                                    # End heading found on same page
                                    content_parts.append(remaining_text[:end_pos])
                                    found_start = False  # Signal we're done
                                    break

                            # End heading not on this page, take all remaining text
                            content_parts.append(remaining_text)
                            break

                        current_pos = line_end + 1  # +1 for newline
                else:
                    # Heading not found on expected page - take the whole page as fallback
                    # This handles cases where bookmark page is slightly off
                    found_start = True
                    content_parts.append(page_text)

            elif found_start:
                # We're past the start heading, look for end heading
                if end_heading_title:
                    end_pos = self.find_heading_in_text(
                        page_text,
                        end_heading_title,
                        end_section_number
                    )

                    if end_pos >= 0:
                        # Found end heading - extract text up to it
                        content_parts.append(page_text[:end_pos])
                        break

                # End heading not found yet, add entire page
                content_parts.append(page_text)

            # Stop if we signaled we're done
            if not found_start and page_offset > 0:
                break

        # Join and clean the extracted text
        full_text = ' '.join(content_parts)

        # Basic cleaning - normalize whitespace
        cleaned = re.sub(r'\n+', ' ', full_text)
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def extract_text_between_pages(self, start_page: int, end_page: int) -> str:
        """
        Extract and clean text content between two page indices.

        DEPRECATED: Use extract_text_between_headings() for more accurate extraction.

        Args:
            start_page: Starting page index (0-based, inclusive)
            end_page: Ending page index (0-based, exclusive)

        Returns:
            Cleaned text content
        """
        text_parts = []

        for page_num in range(start_page, min(end_page, len(self.doc))):
            page = self.doc[page_num]
            text = page.get_text()

            if text.strip():
                # Basic cleaning - remove excessive whitespace
                cleaned = re.sub(r'\n+', ' ', text)
                cleaned = re.sub(r'\s+', ' ', cleaned)
                text_parts.append(cleaned.strip())

        return ' '.join(text_parts)

    def chunk_by_bookmarks(
        self,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> List[StructuredChunk]:
        """
        Create structured chunks based on PDF bookmarks.

        Main method that orchestrates the chunking process:
        1. Extracts bookmarks from PDF
        2. Filters by page range if specified
        3. For each bookmark, extracts text until next bookmark
        4. Splits large sections if needed
        5. Returns list of structured chunks

        Args:
            start_page: Optional start page (1-based, human-readable)
            end_page: Optional end page (1-based, human-readable)

        Returns:
            List of StructuredChunk objects
        """
        bookmarks = self.extract_bookmarks()

        if not bookmarks:
            return []

        # Filter by page range if specified
        if start_page is not None and end_page is not None:
            bookmarks = self.filter_bookmarks_by_page_range(bookmarks, start_page, end_page)

            if not bookmarks:
                return []

        chunks = []

        for i, (level, title, page) in enumerate(bookmarks):
            # Parse section number from title
            section_number = self.parse_section_number(title)

            # Skip non-content bookmarks (like "Contents", "Preface" etc.) unless they have numbers
            # This keeps the output focused on actual book content
            if section_number is None and level == 1:
                continue

            # Get clean title (without section number)
            clean_title = re.sub(r'^\d+(?:\.\d+)*\s+', '', title) if section_number else title

            # Get chapter context
            chapter_num, chapter_title = self.get_chapter_context(bookmarks, i)

            # Get parent section number and title
            parent = self.get_parent_section(section_number) if section_number else None
            parent_title = None
            if parent:
                parent_title = self.get_parent_section_title(bookmarks, i, parent)

            # Get next section info for boundary detection
            next_section_title = None
            next_section_number = None
            next_page = len(self.doc)

            if i + 1 < len(bookmarks):
                next_level, next_title, next_page = bookmarks[i + 1]
                next_section_number = self.parse_section_number(next_title)
                next_section_title = re.sub(r'^\d+(?:\.\d+)*\s+', '', next_title) if next_section_number else next_title

            # Apply end_page limit if specified
            if end_page is not None:
                next_page = min(next_page, end_page - 1)  # Convert to 0-based

            # Extract text content using heading-based extraction
            # This is more accurate than page-based extraction
            content = self.extract_text_between_headings(
                start_page=page,
                start_heading_title=clean_title,
                start_section_number=section_number,
                end_heading_title=next_section_title,
                end_section_number=next_section_number,
                max_pages=min(50, next_page - page + 5)  # Search a bit beyond bookmark page
            )

            if not content.strip():
                continue

            # Count tokens
            token_count = self.text_chunker.count_tokens(content)

            # If content exceeds max size, split it using TextChunker
            if token_count > self.max_chunk_size:
                # Split large section into smaller chunks with overlap
                text_chunks = self.text_chunker.smart_chunk(
                    content,
                    [page],
                    clean_title
                )

                # Create StructuredChunk for each split
                for idx, text_chunk in enumerate(text_chunks):
                    chunk = StructuredChunk(
                        level=level,
                        number=section_number or "",
                        title=clean_title,
                        chapter_number=chapter_num,
                        chapter_title=chapter_title,
                        parent_section=parent,
                        parent_section_title=parent_title,
                        content=text_chunk.content,
                        start_page=page,
                        end_page=next_page,
                        token_count=text_chunk.token_count,
                        is_split=True,
                        split_index=idx,
                        total_splits=len(text_chunks)
                    )
                    chunks.append(chunk)
            else:
                # Create single StructuredChunk
                chunk = StructuredChunk(
                    level=level,
                    number=section_number or "",
                    title=clean_title,
                    chapter_number=chapter_num,
                    chapter_title=chapter_title,
                    parent_section=parent,
                    parent_section_title=parent_title,
                    content=content,
                    start_page=page,
                    end_page=next_page,
                    token_count=token_count,
                    is_split=False,
                    split_index=0,
                    total_splits=1
                )
                chunks.append(chunk)

        return chunks

    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures PDF is closed."""
        self.close()
