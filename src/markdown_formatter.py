import os
import pymupdf
from datetime import datetime
from typing import List, Dict, Union
from .note_generator import GeneratedNote


class MarkdownFormatter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def format_notes_to_markdown(self, notes: List[GeneratedNote], pdf_filename: str, model_name: str = "unknown") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]

        markdown_content = []
        markdown_content.append(f"# Notes: {base_filename}")
        markdown_content.append(f"*Generated on: {timestamp}*")
        markdown_content.append(f"*Model: {model_name}*")
        markdown_content.append("")

        current_chapter = ""
        note_counter = 1

        for note in notes:
            if note.chapter_title and note.chapter_title != current_chapter:
                current_chapter = note.chapter_title
                markdown_content.append(f"## {current_chapter}")
                markdown_content.append("")

            if note.content.strip():
                page_info = f"Pages {min(note.source_pages)}-{max(note.source_pages)}" if len(note.source_pages) > 1 else f"Page {note.source_pages[0]}" if note.source_pages else "Unknown page"

                markdown_content.append(f"### Note {note_counter} ({page_info})")
                markdown_content.append("")

                formatted_content = self._format_note_content(note.content)
                markdown_content.append(formatted_content)
                markdown_content.append("")
                markdown_content.append("---")
                markdown_content.append("")

                note_counter += 1

        return "\n".join(markdown_content)

    def _format_note_content(self, content: str) -> str:
        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                formatted_lines.append(line)
            elif ':' in line and len(line.split(':')[0]) < 50:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    formatted_lines.append(f"**{parts[0].strip()}:** {parts[1].strip()}")
                else:
                    formatted_lines.append(f"• {line}")
            elif line.lower().startswith(('key', 'important', 'note', 'concept', 'definition')):
                formatted_lines.append(f"**{line}**")
            else:
                formatted_lines.append(f"• {line}")

        return "\n".join(formatted_lines)

    def save_markdown_file(self, markdown_content: str, pdf_filename: str) -> str:
        base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_filename}_notes_{timestamp}.md"
        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return output_path

    def create_summary_section(self, notes: List[GeneratedNote], pdf_filename: str) -> str:
        base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]

        summary_lines = []
        summary_lines.append(f"# Summary: {base_filename}")
        summary_lines.append("")

        chapters = {}
        for note in notes:
            chapter = note.chapter_title or "General"
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append(note.content)

        for chapter, chapter_notes in chapters.items():
            summary_lines.append(f"## {chapter}")
            summary_lines.append("")

            key_points = []
            for note_content in chapter_notes:
                lines = note_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if (line and
                        (line.startswith('•') or line.startswith('-') or line.startswith('*')) and
                        len(line) > 20):
                        key_points.append(line)

            for point in key_points[:5]:
                summary_lines.append(point)

            summary_lines.append("")

        return "\n".join(summary_lines)

    def create_obsidian_compatible_note(self, notes: List[GeneratedNote], pdf_filename: str) -> str:
        base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]
        timestamp = datetime.now().strftime("%Y-%m-%d")

        obsidian_content = []
        obsidian_content.append(f"# {base_filename}")
        obsidian_content.append("")
        obsidian_content.append(f"**Source:** [[{base_filename}.pdf]]")
        obsidian_content.append(f"**Date:** {timestamp}")
        obsidian_content.append(f"**Tags:** #technical-book #programming #notes")
        obsidian_content.append("")

        obsidian_content.append("## Key Concepts")
        obsidian_content.append("")

        all_concepts = []
        for note in notes:
            lines = note.content.split('\n')
            for line in lines:
                line = line.strip()
                if (line and
                    any(keyword in line.lower() for keyword in ['concept', 'definition', 'important', 'key']) and
                    len(line) > 15):
                    all_concepts.append(line)

        for concept in all_concepts[:10]:
            obsidian_content.append(f"- {concept}")

        obsidian_content.append("")
        obsidian_content.append("## Detailed Notes")
        obsidian_content.append("")

        for i, note in enumerate(notes, 1):
            if note.content.strip():
                page_ref = f"Page {note.source_pages[0]}" if note.source_pages else f"Section {i}"
                obsidian_content.append(f"### {page_ref}")
                if note.chapter_title:
                    obsidian_content.append(f"*Chapter: {note.chapter_title}*")
                obsidian_content.append("")
                obsidian_content.append(self._format_note_content(note.content))
                obsidian_content.append("")

        return "\n".join(obsidian_content)

    def extract_pdf_metadata(self, pdf_path: str) -> Dict[str, str]:
        """
        Extract metadata from PDF for frontmatter.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with title, author, subject, etc.
        """
        try:
            doc = pymupdf.open(pdf_path)
            metadata = doc.metadata

            # Clean up metadata values (remove None, empty strings)
            cleaned = {
                'title': metadata.get('title', '').strip() or os.path.splitext(os.path.basename(pdf_path))[0],
                'author': metadata.get('author', '').strip() or 'Unknown',
                'subject': metadata.get('subject', '').strip() or '',
                'keywords': metadata.get('keywords', '').strip() or '',
                'creator': metadata.get('creator', '').strip() or '',
                'producer': metadata.get('producer', '').strip() or '',
            }

            doc.close()
            return cleaned
        except Exception:
            # Fallback if metadata extraction fails
            return {
                'title': os.path.splitext(os.path.basename(pdf_path))[0],
                'author': 'Unknown',
                'subject': '',
                'keywords': '',
                'creator': '',
                'producer': '',
            }

    def format_structured_notes_to_markdown(
        self,
        notes: List[tuple],  # List of (StructuredChunk, GeneratedNote) pairs
        pdf_path: str,
        model_name: str = "unknown"
    ) -> str:
        """
        Format notes from StructuredChunk objects into hierarchical markdown.

        Creates output that mirrors the book's structure with proper heading levels
        and includes metadata frontmatter.

        Args:
            notes: List of (StructuredChunk, GeneratedNote) tuples
            pdf_path: Path to the source PDF
            model_name: Name of the model used to generate notes

        Returns:
            Formatted markdown string
        """
        metadata = self.extract_pdf_metadata(pdf_path)
        timestamp = datetime.now().strftime("%Y-%m-%d")

        markdown_lines = []

        # YAML frontmatter with metadata
        markdown_lines.append("---")
        markdown_lines.append(f"title: {metadata['title']}")
        if metadata['author'] and metadata['author'] != 'Unknown':
            # Handle multiple authors (split by semicolon or comma)
            authors = [a.strip() for a in metadata['author'].replace(';', ',').split(',')]
            markdown_lines.append("authors:")
            for author in authors:
                if author:
                    markdown_lines.append(f"  - {author}")
        else:
            markdown_lines.append("authors: []")

        if metadata['subject']:
            markdown_lines.append(f"subject: {metadata['subject']}")
        markdown_lines.append(f"generated: {timestamp}")
        markdown_lines.append(f"model: {model_name}")
        markdown_lines.append("---")
        markdown_lines.append("")

        # Track current chapter/section to avoid repeating headers
        current_chapter = None
        current_section = None

        for chunk, note in notes:
            # Determine markdown heading level based on bookmark level
            # Level 1 (chapter) -> # (h1)
            # Level 2 (section) -> ## (h2)
            # Level 3 (subsection) -> ### (h3)
            # Level 4 (sub-subsection) -> #### (h4)
            heading_prefix = '#' * chunk.level

            # Create section identifier
            section_id = f"{chunk.number} {chunk.title}" if chunk.number else chunk.title

            # Skip duplicate headers (important when sections are split)
            # We track chapter and section separately to avoid re-printing headers
            if chunk.level == 1:
                if current_chapter != section_id:
                    markdown_lines.append(f"{heading_prefix} {section_id}")
                    markdown_lines.append("")
                    markdown_lines.append(f"> p. {chunk.start_page}")  # 0-based page number
                    markdown_lines.append("")
                    current_chapter = section_id
                    current_section = None  # Reset section when new chapter
            elif chunk.level == 2:
                # Check if we need to insert missing chapter header
                # This happens when page filtering skips the chapter but includes sections
                chapter_id = f"{chunk.chapter_number} {chunk.chapter_title}" if chunk.chapter_number else chunk.chapter_title
                if current_chapter != chapter_id and chunk.chapter_number:
                    # Insert missing chapter header (without notes, just structure)
                    markdown_lines.append(f"# {chapter_id}")
                    markdown_lines.append("")
                    markdown_lines.append(f"> p. {chunk.start_page}")  # Best guess - same page as first section
                    markdown_lines.append("")
                    markdown_lines.append("*[Chapter header - no separate notes generated]*")
                    markdown_lines.append("")
                    current_chapter = chapter_id

                if current_section != section_id:
                    markdown_lines.append(f"{heading_prefix} {section_id}")
                    markdown_lines.append("")
                    markdown_lines.append(f"> p. {chunk.start_page}")  # 0-based page number
                    markdown_lines.append("")
                    current_section = section_id
            else:
                # For level 3+ (subsections), check if we need parent section header
                # This handles cases where subsections are in range but parent section isn't
                if chunk.parent_section and chunk.parent_section_title:
                    parent_section_id = f"{chunk.parent_section} {chunk.parent_section_title}"

                    # Check if we need to insert the parent section header
                    # (i.e., we haven't seen this parent section yet)
                    if current_section != parent_section_id:
                        # Also check if we need chapter header first
                        chapter_id = f"{chunk.chapter_number} {chunk.chapter_title}" if chunk.chapter_number else chunk.chapter_title
                        if current_chapter != chapter_id and chunk.chapter_number:
                            # Insert missing chapter header
                            markdown_lines.append(f"# {chapter_id}")
                            markdown_lines.append("")
                            markdown_lines.append(f"> p. {chunk.start_page}")
                            markdown_lines.append("")
                            markdown_lines.append("*[Chapter header - no separate notes generated]*")
                            markdown_lines.append("")
                            current_chapter = chapter_id

                        # Insert the parent section header
                        markdown_lines.append(f"## {parent_section_id}")
                        markdown_lines.append("")
                        markdown_lines.append(f"> p. {chunk.start_page}")
                        markdown_lines.append("")
                        markdown_lines.append("*[Section header - content starts with subsections below]*")
                        markdown_lines.append("")
                        current_section = parent_section_id

                # Always print subsection headers (level 3+)
                markdown_lines.append(f"{heading_prefix} {section_id}")
                markdown_lines.append("")
                markdown_lines.append(f"> p. {chunk.start_page}")  # 0-based page number
                markdown_lines.append("")

            # Add note content
            if note and note.content.strip():
                formatted_content = self._format_note_content(note.content)
                markdown_lines.append(formatted_content)
                markdown_lines.append("")

                # If this is a split chunk, indicate it's a continuation
                if chunk.is_split and chunk.split_index < chunk.total_splits - 1:
                    markdown_lines.append(f"*[Continued in part {chunk.split_index + 2}/{chunk.total_splits}...]*")
                    markdown_lines.append("")

        return "\n".join(markdown_lines)