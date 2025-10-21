import os
from typing import List
from anthropic import Anthropic
from dotenv import load_dotenv
from dataclasses import dataclass
from .text_chunker import TextChunk


@dataclass
class GeneratedNote:
    content: str
    source_chunk_ids: List[int]
    source_pages: List[int]
    chapter_title: str = ""


class APIBasedNoteGenerator:
    """
    Note generator using Claude API instead of local models.
    This is useful when GPU resources are limited.
    """

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the API-based note generator.

        Args:
            model_name: Claude model to use. Options:
                - claude-3-5-sonnet-20241022 (recommended for quality)
                - claude-3-5-haiku-20241022 (faster, more economical)
        """
        load_dotenv()
        api_key = os.getenv('CLAUDE_KEY')

        if not api_key:
            raise ValueError(
                "CLAUDE_KEY not found in environment variables. "
                "Please add it to your .env file."
            )

        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        print(f"✅ Initialized Claude API with model: {model_name}")

    def generate_note_from_chunk(self, chunk: TextChunk) -> GeneratedNote:
        """
        Generate a structured note from a text chunk using Claude API.

        Args:
            chunk: TextChunk containing the content to process

        Returns:
            GeneratedNote with formatted content
        """
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            note_content = message.content[0].text.strip()
            note_content = self._clean_generated_note(note_content)

            return GeneratedNote(
                content=note_content,
                source_chunk_ids=[chunk.chunk_id],
                source_pages=chunk.source_pages,
                chapter_title=chunk.chapter_title
            )

        except Exception as e:
            print(f"Error generating note for chunk {chunk.chunk_id}: {e}")
            return GeneratedNote(
                content=self._create_fallback_note(chunk.content),
                source_chunk_ids=[chunk.chunk_id],
                source_pages=chunk.source_pages,
                chapter_title=chunk.chapter_title
            )

    def _create_note_prompt(self, text: str, chapter_title: str = "") -> str:
        """Create an optimized prompt for Claude API."""
        base_prompt = """Create comprehensive, structured technical notes from the following text.

Focus on:
- Key concepts and definitions
- Important technical details and explanations
- Main takeaways and insights
- Code examples, algorithms, or formulas mentioned
- Connections between ideas

Format your notes as clear, concise bullet points or short paragraphs. Make them useful for studying and reference.
"""

        if chapter_title:
            return f"{base_prompt}\nChapter: {chapter_title}\n\nText to summarize:\n{text}"
        else:
            return f"{base_prompt}\nText to summarize:\n{text}"

    def _clean_generated_note(self, note: str) -> str:
        """Clean up the generated note by removing unnecessary prefixes."""
        lines = note.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Keep all meaningful content, just remove meta-text
            if (line and
                not line.startswith("Chapter:") and
                not line.startswith("Text to summarize:") and
                len(line) > 5):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _create_fallback_note(self, text: str) -> str:
        """Create a simple fallback note if API call fails."""
        sentences = text.split('. ')
        key_sentences = []

        for sentence in sentences[:5]:
            if (len(sentence) > 20 and
                any(keyword in sentence.lower() for keyword in
                    ['important', 'key', 'main', 'concept', 'algorithm',
                     'method', 'approach', 'technique', 'definition', 'theorem'])):
                key_sentences.append(sentence.strip())

        if not key_sentences and sentences:
            key_sentences = sentences[:3]

        return "• " + "\n• ".join(key_sentences)

    def generate_notes_batch(self, chunks: List[TextChunk]) -> List[GeneratedNote]:
        """
        Generate notes for a batch of chunks.

        Args:
            chunks: List of TextChunk objects to process

        Returns:
            List of GeneratedNote objects
        """
        notes = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} (Page {chunk.source_pages[0] if chunk.source_pages else 'Unknown'})")
            note = self.generate_note_from_chunk(chunk)
            notes.append(note)
        return notes
