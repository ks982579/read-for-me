"""
TTS Audiobook Generator using Coqui TTS (XTTS-v2)

This module converts text chunks to speech using GPU-accelerated TTS models.
Supports multiple voices and automatic chunking for long texts.
"""

import torch
from TTS.api import TTS
from typing import List
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from pydub import AudioSegment
import io
from .text_chunker import TextChunk

@dataclass
class GeneratedAudio:
    """Container for generated audio data"""
    audio_data: AudioSegment
    source_chunk_ids: List[int]
    source_pages: List[int]
    chapter_title: str = ""
    duration_seconds: float = 0.0


class TTSGenerator:
    """
    Generates natural-sounding speech from text chunks using Coqui TTS.

    Features:
    - GPU acceleration with CUDA
    - High-quality XTTS-v2 model
    - Multiple voice options
    - Automatic sentence-level chunking to avoid memory issues
    """

    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
                 device: str = "cuda", voice: str = "default"):
        """
        Initialize TTS generator.

        Args:
            model_name: Coqui TTS model to use
            device: 'cuda' for GPU, 'cpu' for CPU
            voice: Voice preset or path to reference audio file for cloning
        """
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else "cpu"
        self.voice = voice

        print(f"🔊 Loading TTS model: {model_name}")
        print(f"📱 Device: {self.device}")

        # Initialize TTS model
        self.tts = TTS(model_name=model_name).to(self.device)

        # Sample rate for the model
        self.sample_rate = 22050  # Tacotron2 uses 22.05kHz

        # Maximum characters per TTS call (to avoid OOM)
        self.max_chars_per_chunk = 500

        print("✅ TTS model loaded successfully")

    def generate_audio_from_chunk(self, chunk: TextChunk) -> GeneratedAudio:
        """
        Generate audio from a text chunk.

        Args:
            chunk: TextChunk containing the text to convert

        Returns:
            GeneratedAudio with the synthesized speech
        """
        text = chunk.content.strip()

        if not text:
            # Return silent audio for empty chunks
            return self._create_silent_audio(chunk)

        try:
            # Split text into smaller pieces if needed
            text_segments = self._split_text_for_tts(text)

            # Generate audio for each segment
            audio_segments = []
            for segment in text_segments:
                audio_data = self._generate_segment(segment)
                if audio_data is not None:
                    audio_segments.append(audio_data)

            # Combine all audio segments
            if audio_segments:
                combined_audio = audio_segments[0]
                for audio in audio_segments[1:]:
                    # Add small pause between segments (100ms)
                    silence = AudioSegment.silent(duration=100)
                    combined_audio = combined_audio + silence + audio

                return GeneratedAudio(
                    audio_data=combined_audio,
                    source_chunk_ids=[chunk.chunk_id],
                    source_pages=chunk.source_pages,
                    chapter_title=chunk.chapter_title,
                    duration_seconds=len(combined_audio) / 1000.0
                )
            else:
                return self._create_silent_audio(chunk)

        except Exception as e:
            print(f"❌ Error generating audio for chunk {chunk.chunk_id}: {e}")
            return self._create_silent_audio(chunk)

    def _generate_segment(self, text: str) -> AudioSegment:
        """
        Generate audio for a single text segment.

        Args:
            text: Text to convert to speech

        Returns:
            AudioSegment with the generated audio
        """
        try:
            # Generate audio (single-speaker model, no speaker parameter needed)
            wav = self.tts.tts(text=text)

            # Convert numpy array to AudioSegment
            # XTTS returns float32 array in range [-1, 1]
            audio_array = np.array(wav)
            audio_array = (audio_array * 32767).astype(np.int16)

            # Create AudioSegment from numpy array
            audio_segment = AudioSegment(
                audio_array.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,  # 16-bit audio
                channels=1  # mono
            )

            return audio_segment

        except Exception as e:
            print(f"⚠️  Error generating segment: {e}")
            return None

    def _split_text_for_tts(self, text: str) -> List[str]:
        """
        Split text into manageable chunks for TTS processing.
        Splits on sentence boundaries to maintain natural speech.

        Args:
            text: Text to split

        Returns:
            List of text segments
        """
        # If text is short enough, return as-is
        if len(text) <= self.max_chars_per_chunk:
            return [text]

        # Split on sentence boundaries
        sentences = []
        current_segment = ""

        # Simple sentence splitting (can be improved)
        for sentence in text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|'):
            sentence = sentence.strip()
            if not sentence:
                continue

            # If adding this sentence would exceed limit, save current segment
            if len(current_segment) + len(sentence) > self.max_chars_per_chunk:
                if current_segment:
                    sentences.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence if current_segment else sentence

        # Add remaining text
        if current_segment:
            sentences.append(current_segment.strip())

        return sentences

    def _create_silent_audio(self, chunk: TextChunk) -> GeneratedAudio:
        """Create a silent audio segment as fallback."""
        silence = AudioSegment.silent(duration=1000)  # 1 second of silence
        return GeneratedAudio(
            audio_data=silence,
            source_chunk_ids=[chunk.chunk_id],
            source_pages=chunk.source_pages,
            chapter_title=chunk.chapter_title,
            duration_seconds=1.0
        )

    def combine_audio_segments(self, audio_segments: List[GeneratedAudio],
                               add_chapter_markers: bool = True) -> AudioSegment:
        """
        Combine multiple audio segments into a single audiobook.

        Args:
            audio_segments: List of GeneratedAudio objects
            add_chapter_markers: If True, add longer pauses between chapters

        Returns:
            Combined AudioSegment
        """
        if not audio_segments:
            return AudioSegment.silent(duration=1000)

        combined = audio_segments[0].audio_data
        current_chapter = audio_segments[0].chapter_title

        for i, segment in enumerate(audio_segments[1:], 1):
            # Add pause between segments
            if add_chapter_markers and segment.chapter_title != current_chapter:
                # Longer pause for chapter transitions (2 seconds)
                pause = AudioSegment.silent(duration=2000)
                current_chapter = segment.chapter_title
            else:
                # Shorter pause between sections (500ms)
                pause = AudioSegment.silent(duration=500)

            combined = combined + pause + segment.audio_data

        return combined

    def save_audio(self, audio: AudioSegment, output_path: str, format: str = "mp3"):
        """
        Save audio to file.

        Args:
            audio: AudioSegment to save
            output_path: Path to save the audio file
            format: Audio format (mp3, wav, ogg, etc.)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"💾 Saving audio to: {output_path}")

        # Export with appropriate settings
        if format == "mp3":
            audio.export(output_path, format="mp3", bitrate="192k")
        elif format == "wav":
            audio.export(output_path, format="wav")
        else:
            audio.export(output_path, format=format)

        print(f"✅ Audio saved: {output_path} ({len(audio) / 1000:.1f} seconds)")
