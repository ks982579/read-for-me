from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict
from dataclasses import dataclass
from .text_chunker import TextChunk
import requests
import json

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
        self.model_name = "llama3.1:8b" # must have pulled | uses 94% GPU-Util
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def generate_note_from_chunk(self, chunk: TextChunk) -> GeneratedNote:
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        # "num_predict": 800
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
        base_prompt = """Create comprehensive study notes from this text. Extract:
- All key definitions and terminology
- Technical explanations of how things work
- Formulas, algorithms, or code examples
- Relationships between concepts
- Concrete examples

Write in clear paragraphs and bullet points. Preserve all important technical content.

Text: """
        
        if chapter_title:
            return f"Chapter: {chapter_title}\n\n{base_prompt}{text}\n\nNotes:"
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



class NoteGenerator_DEPRECATED:
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
        max_retries = 2
        fallback_models = [self.model_name, "microsoft/DialoGPT-small", "distilgpt2"]

        for attempt, model_name in enumerate(fallback_models):
            try:
                print(f"Loading model: {model_name}...")

                if "flan-t5" in model_name.lower() or "bart" in model_name.lower():
                    # For T5 and BART models, use text2text-generation or summarization
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    task = "summarization" if "bart" in model_name.lower() else "text2text-generation"
                    self.pipeline = pipeline(
                        task,
                        model=model_name,
                        tokenizer=self.tokenizer,
                        device_map="auto" if self.device == "cuda" else None,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                else:
                    # For GPT models, don't specify device in pipeline - let accelerate handle it
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token

                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None,
                        low_cpu_mem_usage=True
                    )

                    # Create pipeline without specifying device - accelerate will handle it
                    self.pipeline = pipeline(
                        "text-generation",
                        model=self.model,
                        tokenizer=self.tokenizer,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )

                self.model_name = model_name
                print(f"✅ Successfully loaded model: {model_name}")
                return

            except Exception as e:
                print(f"❌ Error loading model {model_name}: {e}")
                if attempt < len(fallback_models) - 1:
                    print(f"Trying fallback model...")
                else:
                    print("❌ All model loading attempts failed!")
                    raise RuntimeError(f"Failed to load any model. Last error: {e}")

    def generate_note_from_chunk(self, chunk: TextChunk) -> GeneratedNote:
        prompt = self._create_note_prompt(chunk.content, chunk.chapter_title)

        try:
            if "flan-t5" in self.model_name.lower() or "bart" in self.model_name.lower():
                # Get model's max context window from tokenizer or model config
                max_context_length = self.tokenizer.model_max_length if hasattr(self.tokenizer, 'model_max_length') else 512

                # BART returns an unreasonably large number, use config instead
                if max_context_length > 100000:
                    if hasattr(self.pipeline.model.config, 'max_position_embeddings'):
                        max_context_length = self.pipeline.model.config.max_position_embeddings
                    else:
                        max_context_length = 1024  # Safe default

                # Reserve 70% for input, 30% for output
                max_input_tokens = int(max_context_length * 0.7)

                # Truncate input to fit within model limits
                input_tokens = self.tokenizer.encode(prompt, truncation=True, max_length=max_input_tokens)
                truncated_prompt = self.tokenizer.decode(input_tokens, skip_special_tokens=True)

                response = self.pipeline(
                    truncated_prompt,
                    max_length=max_context_length,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    num_return_sequences=1
                )
                note_content = response[0]['generated_text'].strip()
            else:
                # For GPT-style models, check if we need to truncate
                max_input_tokens = self.tokenizer.model_max_length if hasattr(self.tokenizer, 'model_max_length') else 2048

                max_input_tokens = min(max_input_tokens, 8000) # safe limit for most 7B models
                # Increase output tokens for more detailed notes
                max_output_tokens = 800

                # Leave room for output tokens
                input_limit = max_input_tokens - max_output_tokens
                input_tokens = self.tokenizer.encode(prompt, truncation=True, max_length=input_limit)
                truncated_prompt = self.tokenizer.decode(input_tokens, skip_special_tokens=True)

                response = self.pipeline(
                    truncated_prompt,
                    max_new_tokens=max_output_tokens,
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
        system_msg = """You are an expert at creating detailed technical study notes. Extract all substantive content including definitions, explanations, technical details, formulas, and relationships between concepts."""
        
        user_msg = f"""Create comprehensive study notes from this text:

        {text}

        Generate detailed notes that include:
        - All key definitions and terminology
        - Technical explanations of how things work
        - Formulas, algorithms, or code examples
        - Relationships between concepts
        - Concrete examples

        Write in clear paragraphs and bullet points. Preserve all important technical content."""

        # Format for Mistral/Llama
        return f"<s>[INST] {system_msg}\n\n{user_msg} [/INST]"

    def _create_note_prompt_deprecated(self, text: str, chapter_title: str = "") -> str:
        if "flan-t5" in self.model_name.lower():
            # FLAN-T5 is instruction-tuned and works best with clear, directive prompts
            # Keep it concise since T5 models have smaller context windows
            base_prompt = """Extract detailed technical notes from the text below. Include:
1. Definitions of all key terms and concepts
2. Explanations of how things work (mechanisms, processes, theories)
3. Technical details (algorithms, formulas, parameters)
4. Relationships between concepts
5. Examples and applications

Format as structured notes with clear sections. Focus on substantive content, not summaries.

Text: """
        elif "bart" in self.model_name.lower():
            # BART is primarily trained for summarization
            base_prompt = """Generate comprehensive study notes from this text. Extract:
- Complete definitions and terminology
- Detailed concept explanations
- Technical mechanisms and processes
- Key formulas, algorithms, or code examples
- How concepts relate and build on each other

Write detailed notes, not brief summaries.

Text: """
        else:
            # For GPT-style models, use more conversational, detailed prompting
            base_prompt = """Create detailed technical notes from the following text. Your goal is to capture substantive content for deep understanding.

Focus on:
- Definitions: Define all key terms and concepts with full explanations
- Concepts & Theories: Explain core ideas, how they work, and why
- Technical Details: Include algorithms, formulas, mechanisms, and processes
- Relationships: Show how concepts connect and build on each other
- Examples: Include concrete examples that illustrate abstract ideas

Write notes suitable for graduate-level study. Use paragraphs for complex explanations and bullet points for lists. Cut fluff but preserve all substantive content.

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
