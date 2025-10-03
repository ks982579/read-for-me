from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict
from dataclasses import dataclass
from .text_chunker import TextChunk


@dataclass
class GeneratedNote:
    content: str
    source_chunk_ids: List[int]
    source_pages: List[int]
    chapter_title: str = ""


class NoteGenerator:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", device: str = "auto"):
        self.device = self._get_device(device)
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.load_model()

    def _get_device(self, device: str) -> str:
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device

    def load_model(self):
        try:
            if "flan-t5" in self.model_name.lower():
                self.pipeline = pipeline(
                    "text2text-generation",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token

                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )

                if self.device != "cuda":
                    self.model = self.model.to(self.device)

                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1
                )

        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            print("Falling back to smaller model...")
            self.model_name = "microsoft/DialoGPT-small"
            self.load_model()

    def generate_note_from_chunk(self, chunk: TextChunk) -> GeneratedNote:
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)

        try:
            if "flan-t5" in self.model_name.lower():
                response = self.pipeline(
                    prompt,
                    max_length=512,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    num_return_sequences=1
                )
                note_content = response[0]['generated_text'].strip()
            else:
                response = self.pipeline(
                    prompt,
                    max_new_tokens=400,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1,
                    return_full_text=False
                )
                note_content = response[0]['generated_text'].strip()

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
        if "flan-t5" in self.model_name.lower():
            base_prompt = "Summarize the key technical concepts and important points from this text in a structured note format: "
        else:
            base_prompt = """Create comprehensive technical notes from the following text. Focus on:
- Key concepts and definitions
- Important technical details
- Main takeaways and insights
- Code examples or algorithms mentioned

Text: """

        if chapter_title:
            return f"Chapter: {chapter_title}\n\n{base_prompt}{text}\n\nNotes:"
        else:
            return f"{base_prompt}{text}\n\nNotes:"

    def _clean_generated_note(self, note: str) -> str:
        lines = note.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if (line and
                not line.startswith("Chapter:") and
                not line.startswith("Text:") and
                not line.startswith("Notes:") and
                len(line) > 10):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _create_fallback_note(self, text: str) -> str:
        sentences = text.split('. ')
        key_sentences = []

        for sentence in sentences[:5]:
            if (len(sentence) > 20 and
                any(keyword in sentence.lower() for keyword in
                    ['important', 'key', 'main', 'concept', 'algorithm', 'method', 'approach', 'technique'])):
                key_sentences.append(sentence.strip())

        if not key_sentences and sentences:
            key_sentences = sentences[:3]

        return "• " + "\n• ".join(key_sentences)

    def generate_notes_batch(self, chunks: List[TextChunk]) -> List[GeneratedNote]:
        notes = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} (Page {chunk.source_pages[0] if chunk.source_pages else 'Unknown'})")
            note = self.generate_note_from_chunk(chunk)
            notes.append(note)
        return notes