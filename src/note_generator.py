"""
Ollama does best results.
However, -c 256 -o 64 was only OK.
Trying -c 1024 -o 128

python main.py ./ebooks/<book>.pdf -c 1024 -o 128
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict
from dataclasses import dataclass
from .text_chunker import TextChunk
import requests
import json
from pathlib import Path
from enum import Enum

class Model(Enum):
    Qwen3_8b = "qwen3:8b"
    Qwen3_14b = "qwen3:14b"
    Deepseekr1_8b = "deepseek-r1:8b"
    Deepseekr1_14b = "deepseek-r1:14b"
    Llama31_8b = "llama3.1:8b"

@dataclass
class GeneratedNote:
    content: str
    source_chunk_ids: List[int]
    source_pages: List[int]
    chapter_title: str = ""

class NoteGenerator:
    def __init__(self, model_name: str = "mistral", device = None):

        # NOTE: Forcing DeepSeek here
        # self.model_name = model_name
        # self.model_name = "deepseek-r1:8b" # must have pulled
        # self.model_name = "llama3.1:8b" # must have pulled | uses 94% GPU-Util
        # self.model_name = str(Model.Qwen3_14b) # "qwen3:8b" # must have pulled | uses 94% GPU-Util
        self.model_name = "qwen3:14b" # "qwen3:8b" # must have pulled | uses 94% GPU-Util
        self.ollama_url = "http://localhost:11434/api/generate"
        with open(Path(__file__).resolve().parent / "prompts" / "latest" / "system_prompt.txt", 'r') as file:
            self.system_prompt = file.read()
        with open(Path(__file__).resolve().parent / "prompts" / "latest" / "base_prompt.txt", 'r') as file:
            self.base_prompt = file.read()
    
    def generate_note_from_chunk(self, chunk: TextChunk) -> GeneratedNote:
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "system": self.system_prompt,
                    "options": {
                        "temperature": 0.4, # 0.6, # lower temp for more focus
                        # "num_predict": 800
                        "num_ctx": 8192,
                        "top_p": 0.85, # 0.9, # slightly lower for more consistent structure
                        "repeat_penalty": 1.1, # help to reduce repetitive formatting
                    }
                }
            )
            
            result = response.json()
            note_content = result['response'].strip()
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
        
        if chapter_title:
            return f"Chapter: {chapter_title}\n\n{self.base_prompt}\n\n{text}\n\nNotes:"
        return f"{self.base_prompt}\n\n{text}\n\nNotes:"

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

