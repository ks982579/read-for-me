import pymupdf
import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedText:
    content: str
    page_number: int
    chapter_title: str = ""


class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(pdf_path)

    def extract_text(self) -> List[ExtractedText]:
        extracted_sections = []
        current_chapter = ""

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()

            if not text.strip():
                continue

            chapter_title = self._detect_chapter_title(text)
            if chapter_title:
                current_chapter = chapter_title

            cleaned_text = self._clean_text(text)
            if len(cleaned_text.strip()) > 100:
                extracted_sections.append(
                    ExtractedText(
                        content=cleaned_text,
                        page_number=page_num + 1,
                        chapter_title=current_chapter
                    )
                )

        return extracted_sections

    def _detect_chapter_title(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if (re.match(r'^(Chapter|CHAPTER)\s+\d+', line) or
                re.match(r'^\d+\.\s+[A-Z]', line) or
                (len(line) < 100 and len(line) > 10 and line.isupper())):
                return line
        return ""

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|\\]', '', text)
        text = text.strip()
        return text

    def get_text_by_pages(self, start_page: int = 0, end_page: int = None) -> str:
        if end_page is None:
            end_page = len(self.doc)

        text_content = []
        for page_num in range(start_page, min(end_page, len(self.doc))):
            page = self.doc[page_num]
            text = page.get_text()
            if text.strip():
                text_content.append(self._clean_text(text))

        return ' '.join(text_content)

    def close(self):
        if self.doc:
            self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()