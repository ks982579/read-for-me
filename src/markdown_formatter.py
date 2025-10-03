import os
from datetime import datetime
from typing import List, Dict
from .note_generator import GeneratedNote


class MarkdownFormatter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def format_notes_to_markdown(self, notes: List[GeneratedNote], pdf_filename: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]

        markdown_content = []
        markdown_content.append(f"# Notes: {base_filename}")
        markdown_content.append(f"*Generated on: {timestamp}*")
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