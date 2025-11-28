"""
Sliding window text chunker with hierarchical summarization.
Creates overlapping chunks to ensure no content is missed, then intelligently merges notes.
"""

import tiktoken
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class WindowedChunk:
    """A chunk created using sliding window with overlap information."""
    content: str
    chunk_id: int
    source_pages: List[int]
    chapter_title: str = ""
    token_count: int = 0
    start_token_idx: int = 0  # Position in original text
    end_token_idx: int = 0    # Position in original text
    overlap_with_prev: bool = False  # Is this chunk overlapping with previous?


class SlidingWindowChunker:
    """
    Creates overlapping chunks using a sliding window approach.

    This ensures better continuity and prevents information loss that can occur
    with non-overlapping chunks, especially for models that struggle with
    long context.
    """

    def __init__(self,
                 chunk_size: int = 1024,
                 overlap_ratio: float = 0.3):
        """
        Initialize the sliding window chunker.

        Args:
            chunk_size: Size of each chunk in tokens
            overlap_ratio: How much chunks overlap (0.3 = 30% overlap)
                          This means if chunk_size=1024, overlap_size=307
        """
        self.chunk_size = chunk_size
        self.overlap_ratio = overlap_ratio
        self.overlap_size = int(chunk_size * overlap_ratio)
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def chunk_with_sliding_window(self,
                                   text: str,
                                   source_pages: List[int],
                                   chapter_title: str = "") -> List[WindowedChunk]:
        """
        Create overlapping chunks using a sliding window.

        Args:
            text: The text to chunk
            source_pages: Which pages this text comes from
            chapter_title: Chapter title for context

        Returns:
            List of WindowedChunk objects with overlap information
        """
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        # If text is smaller than chunk size, return as single chunk
        if total_tokens <= self.chunk_size:
            return [WindowedChunk(
                content=text,
                chunk_id=0,
                source_pages=source_pages,
                chapter_title=chapter_title,
                token_count=total_tokens,
                start_token_idx=0,
                end_token_idx=total_tokens,
                overlap_with_prev=False
            )]

        chunks = []
        chunk_id = 0
        stride = self.chunk_size - self.overlap_size  # How far to move each window

        start_idx = 0
        while start_idx < total_tokens:
            end_idx = min(start_idx + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)

            if chunk_text.strip():
                # Mark if this chunk overlaps with previous
                overlap_with_prev = (chunk_id > 0)

                chunks.append(WindowedChunk(
                    content=chunk_text.strip(),
                    chunk_id=chunk_id,
                    source_pages=source_pages.copy(),
                    chapter_title=chapter_title,
                    token_count=len(chunk_tokens),
                    start_token_idx=start_idx,
                    end_token_idx=end_idx,
                    overlap_with_prev=overlap_with_prev
                ))
                chunk_id += 1

            # Move window forward by stride
            start_idx += stride

            # Avoid infinite loop at the end
            if end_idx >= total_tokens:
                break

        return chunks

    def chunk_by_smart_boundaries(self,
                                   text: str,
                                   source_pages: List[int],
                                   chapter_title: str = "",
                                   target_chunk_size: int = None) -> List[WindowedChunk]:
        """
        Create chunks respecting sentence/paragraph boundaries with overlap.
        Better quality than pure token-based chunking as it doesn't split mid-sentence.

        Args:
            text: The text to chunk
            source_pages: Which pages this text comes from
            chapter_title: Chapter title for context
            target_chunk_size: Override chunk size (defaults to self.chunk_size)

        Returns:
            List of WindowedChunk objects
        """
        import re

        if target_chunk_size is None:
            target_chunk_size = self.chunk_size

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""
        chunk_id = 0
        overlap_buffer = ""  # Keep track of last part for overlap
        token_idx = 0

        for i, sentence in enumerate(sentences):
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            test_token_count = self.count_tokens(test_chunk)

            if test_token_count <= target_chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full, save it
                if current_chunk:
                    chunk_text = current_chunk.strip()
                    token_count = self.count_tokens(chunk_text)

                    chunks.append(WindowedChunk(
                        content=chunk_text,
                        chunk_id=chunk_id,
                        source_pages=source_pages.copy(),
                        chapter_title=chapter_title,
                        token_count=token_count,
                        start_token_idx=token_idx,
                        end_token_idx=token_idx + token_count,
                        overlap_with_prev=(chunk_id > 0)
                    ))

                    # Keep the last ~30% of this chunk as overlap for next chunk
                    overlap_size_tokens = int(token_count * self.overlap_ratio)
                    if overlap_size_tokens > 0:
                        # Get last sentences that fit in overlap
                        overlap_sentences = []
                        overlap_tokens = 0
                        for sent in reversed(chunk_text.split('. ')):
                            sent_tokens = self.count_tokens(sent)
                            if overlap_tokens + sent_tokens <= overlap_size_tokens:
                                overlap_sentences.insert(0, sent)
                                overlap_tokens += sent_tokens
                            else:
                                break
                        overlap_buffer = '. '.join(overlap_sentences) + ". "

                    token_idx += token_count
                    chunk_id += 1

                # Start new chunk with overlap
                current_chunk = overlap_buffer + sentence if overlap_buffer else sentence

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = current_chunk.strip()
            token_count = self.count_tokens(chunk_text)
            chunks.append(WindowedChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                source_pages=source_pages.copy(),
                chapter_title=chapter_title,
                token_count=token_count,
                start_token_idx=token_idx,
                end_token_idx=token_idx + token_count,
                overlap_with_prev=(chunk_id > 0)
            ))

        return chunks
