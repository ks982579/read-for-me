"""
Hierarchical note merging for overlapping chunks.
Combines notes from sliding window chunks while avoiding redundancy.
"""

import os
from typing import List
from anthropic import Anthropic
from dotenv import load_dotenv
from dataclasses import dataclass
from .api_note_generator import GeneratedNote


class NoteMerger:
    """
    Intelligently merges notes from overlapping chunks to create a cohesive narrative.

    When using sliding window chunking with overlap, this class:
    1. Identifies overlapping regions
    2. Merges notes while eliminating redundancy
    3. Ensures smooth transitions between notes
    4. Maintains all unique information
    """

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the note merger.

        Args:
            model_name: Claude model to use for merging
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

    def merge_consecutive_notes(self,
                               note1: GeneratedNote,
                               note2: GeneratedNote,
                               overlap_context: str = "") -> GeneratedNote:
        """
        Merge two consecutive notes from overlapping chunks.

        Args:
            note1: First note
            note2: Second note (comes after note1)
            overlap_context: Optional context about what overlaps between them

        Returns:
            Merged GeneratedNote
        """
        merge_prompt = f"""You are merging notes from two consecutive sections of text that have some overlap.

FIRST NOTE (from earlier section):
{note1.content}

---

SECOND NOTE (from later section):
{note2.content}

---

TASK: Create a single, coherent merged note that:
1. Combines all unique information from both notes
2. Eliminates redundancy - if the same point is made in both notes, keep it once with the best explanation
3. Maintains logical flow and organization
4. Preserves all technical details, examples, and relationships
5. Smoothly transitions between topics
6. Keeps paragraph and bullet point formatting from the originals

Return ONLY the merged note, with no preamble or explanation."""

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                temperature=0.5,  # Lower temp for more deterministic merging
                messages=[
                    {
                        "role": "user",
                        "content": merge_prompt
                    }
                ]
            )

            merged_content = message.content[0].text.strip()

            # Combine source tracking
            combined_chunk_ids = list(set(note1.source_chunk_ids + note2.source_chunk_ids))
            combined_pages = list(set(note1.source_pages + note2.source_pages))

            return GeneratedNote(
                content=merged_content,
                source_chunk_ids=combined_chunk_ids,
                source_pages=sorted(combined_pages),
                chapter_title=note1.chapter_title or note2.chapter_title
            )

        except Exception as e:
            print(f"Error merging notes: {e}")
            # Fallback: simple concatenation
            return GeneratedNote(
                content=f"{note1.content}\n\n---\n\n{note2.content}",
                source_chunk_ids=list(set(note1.source_chunk_ids + note2.source_chunk_ids)),
                source_pages=sorted(list(set(note1.source_pages + note2.source_pages))),
                chapter_title=note1.chapter_title or note2.chapter_title
            )

    def merge_notes_in_batches(self,
                              notes: List[GeneratedNote],
                              batch_size: int = 2) -> List[GeneratedNote]:
        """
        Merge a list of notes in a hierarchical fashion.

        For example, with 4 notes and batch_size=2:
        - First pass: merge (note1, note2) and (note3, note4)
        - Second pass: merge the two results

        Args:
            notes: List of GeneratedNote objects
            batch_size: How many notes to merge at once (2 = merge pairs)

        Returns:
            List of merged notes
        """
        if len(notes) <= 1:
            return notes

        print(f"\n=== Merging {len(notes)} notes in batches of {batch_size} ===")

        current_notes = notes.copy()
        merge_level = 1

        while len(current_notes) > 1:
            merged_notes = []

            # Process notes in batches
            for i in range(0, len(current_notes), batch_size):
                batch = current_notes[i:i+batch_size]

                if len(batch) == 1:
                    # If last batch has only 1 note, keep it as is
                    merged_notes.append(batch[0])
                else:
                    print(f"Merge Level {merge_level}: Merging {len(batch)} notes...", end=" ")
                    # Merge all notes in this batch together
                    merged = batch[0]
                    for j in range(1, len(batch)):
                        merged = self.merge_consecutive_notes(merged, batch[j])
                    merged_notes.append(merged)
                    print("✓")

            current_notes = merged_notes
            merge_level += 1

        print(f"=== Merging complete: {len(current_notes)} final note(s) ===\n")
        return current_notes

    def merge_all_to_single(self,
                           notes: List[GeneratedNote]) -> GeneratedNote:
        """
        Merge all notes into a single comprehensive note.

        This creates a unified narrative from all chunks.

        Args:
            notes: List of GeneratedNote objects

        Returns:
            Single merged GeneratedNote
        """
        if not notes:
            return GeneratedNote(
                content="",
                source_chunk_ids=[],
                source_pages=[],
                chapter_title=""
            )

        if len(notes) == 1:
            return notes[0]

        # Hierarchically merge down to one
        merged_list = self.merge_notes_in_batches(notes, batch_size=2)
        return merged_list[0]
