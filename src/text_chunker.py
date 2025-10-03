import tiktoken
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_id: int
    source_pages: List[int]
    chapter_title: str = ""
    token_count: int = 0


class TextChunker:
    def __init__(self, max_chunk_size: int = 2048, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_by_tokens(self, text: str, source_pages: List[int], chapter_title: str = "") -> List[TextChunk]:
        chunks = []
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= self.max_chunk_size:
            decoded_text = self.encoding.decode(tokens)
            return [TextChunk(
                content=decoded_text,
                chunk_id=0,
                source_pages=source_pages,
                chapter_title=chapter_title,
                token_count=total_tokens
            )]

        chunk_id = 0
        start_idx = 0

        while start_idx < total_tokens:
            end_idx = min(start_idx + self.max_chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)

            if chunk_text.strip():
                chunks.append(TextChunk(
                    content=chunk_text.strip(),
                    chunk_id=chunk_id,
                    source_pages=source_pages.copy(),
                    chapter_title=chapter_title,
                    token_count=len(chunk_tokens)
                ))
                chunk_id += 1

            if end_idx >= total_tokens:
                break

            start_idx = end_idx - self.overlap_size

        return chunks

    def chunk_by_sentences(self, text: str, source_pages: List[int], chapter_title: str = "") -> List[TextChunk]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        chunk_id = 0

        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence

            if self.count_tokens(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        chunk_id=chunk_id,
                        source_pages=source_pages.copy(),
                        chapter_title=chapter_title,
                        token_count=self.count_tokens(current_chunk)
                    ))
                    chunk_id += 1

                if self.count_tokens(sentence) <= self.max_chunk_size:
                    current_chunk = sentence
                else:
                    sentence_chunks = self.chunk_by_tokens(sentence, source_pages, chapter_title)
                    for sc in sentence_chunks:
                        sc.chunk_id = chunk_id
                        chunks.append(sc)
                        chunk_id += 1
                    current_chunk = ""

        if current_chunk:
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                chunk_id=chunk_id,
                source_pages=source_pages.copy(),
                chapter_title=chapter_title,
                token_count=self.count_tokens(current_chunk)
            ))

        return chunks

    def smart_chunk(self, text: str, source_pages: List[int], chapter_title: str = "") -> List[TextChunk]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        chunk_id = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph

            if self.count_tokens(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        chunk_id=chunk_id,
                        source_pages=source_pages.copy(),
                        chapter_title=chapter_title,
                        token_count=self.count_tokens(current_chunk)
                    ))
                    chunk_id += 1

                if self.count_tokens(paragraph) <= self.max_chunk_size:
                    current_chunk = paragraph
                else:
                    para_chunks = self.chunk_by_sentences(paragraph, source_pages, chapter_title)
                    for pc in para_chunks:
                        pc.chunk_id = chunk_id
                        chunks.append(pc)
                        chunk_id += 1
                    current_chunk = ""

        if current_chunk:
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                chunk_id=chunk_id,
                source_pages=source_pages.copy(),
                chapter_title=chapter_title,
                token_count=self.count_tokens(current_chunk)
            ))

        return chunks