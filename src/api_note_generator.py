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

    def generate_note_from_chunk(self, chunk: TextChunk,
                                  temperature: float = 0.7,
                                  max_tokens: int = 4096) -> GeneratedNote:
        """
        Generate a structured note from a text chunk using Claude API.

        Args:
            chunk: TextChunk containing the content to process
            temperature: Controls randomness (0.7 = balanced, lower = more focused)
            max_tokens: Maximum tokens to generate

        Returns:
            GeneratedNote with formatted content
        """
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
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
        base_prompt = """Create comprehensive, detailed technical notes from the following text. Your goal is to capture substantive content, not just surface-level summaries.

IMPORTANT: Focus on depth over brevity. Include:

**Definitions & Terminology:**
- Define all key terms, concepts, and specialized vocabulary
- Explain what things ARE, not just that they exist
- Include formal definitions where provided

**Concepts & Theories:**
- Explain the core ideas and how they work
- Describe the reasoning, logic, or proof behind concepts
- Include the "why" and "how", not just the "what"
- Capture theoretical frameworks and mental models

**Technical Details:**
- Preserve specific technical explanations, mechanisms, and processes
- Include algorithms, formulas, equations, and their explanations
- Document code examples with context about what they demonstrate
- Note important parameters, constraints, or conditions

**Relationships & Context:**
- Show how concepts connect to and build upon each other
- Explain cause-and-effect relationships
- Note comparisons, contrasts, or trade-offs discussed
- Identify prerequisites or dependencies

**Examples & Applications:**
- Include concrete examples that illustrate abstract concepts
- Document use cases, scenarios, or practical applications
- Note any warnings, common mistakes, or edge cases

**Format Guidelines:**
- Use paragraph form for complex explanations that need flow
- Use bullet points for lists, steps, or distinct items
- Use headers (###) to organize major topics
- Preserve the logical structure and progression of ideas
- Cut marketing fluff, redundant introductions, and filler, but keep substantive content

Write notes as if for a graduate student who needs to deeply understand the material, not just get a high-level overview."""

        if chapter_title:
            return f"{base_prompt}\n\nChapter: {chapter_title}\n\nText to analyze:\n\n{text}"
        else:
            return f"{base_prompt}\n\nText to analyze:\n\n{text}"

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

    def generate_notes_batch(self,
                            chunks: List[TextChunk],
                            temperature: float = 0.7,
                            max_tokens: int = 4096) -> List[GeneratedNote]:
        """
        Generate notes for a batch of chunks.

        Args:
            chunks: List of TextChunk objects to process
            temperature: Controls randomness (lower = more focused)
            max_tokens: Maximum tokens per note

        Returns:
            List of GeneratedNote objects
        """
        notes = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} (Page {chunk.source_pages[0] if chunk.source_pages else 'Unknown'})")
            note = self.generate_note_from_chunk(
                chunk,
                temperature=temperature,
                max_tokens=max_tokens
            )
            notes.append(note)
        return notes
