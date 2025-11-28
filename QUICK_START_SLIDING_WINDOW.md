# Quick Start: Sliding Window Approach

## TL;DR - Why Your Model Gets Stuck and How to Fix It

**Problem**: Large chunks → model gets stuck repeating words
**Solution**: Smaller overlapping chunks + merge with Claude

## Three Steps to Fix

### 1. Use Smaller Chunks (512-1024 tokens instead of 3072)

```python
from src.sliding_window_chunker import SlidingWindowChunker

chunker = SlidingWindowChunker(
    chunk_size=1024,      # ← Much smaller
    overlap_ratio=0.3     # ← Chunks overlap 30%
)
```

**Why this works**: Smaller chunks don't overwhelm the model's context. Less chance of getting stuck in repetition loops.

### 2. Generate Notes Independently

```python
from src.api_note_generator import APIBasedNoteGenerator

generator = APIBasedNoteGenerator()
chunks = chunker.chunk_by_smart_boundaries(text, pages)

notes = []
for chunk in chunks:
    note = generator.generate_note_from_chunk(chunk)
    notes.append(note)
```

Each chunk gets processed separately - no more "Definition of services" × 100.

### 3. Merge Notes Intelligently

```python
from src.note_merger import NoteMerger

merger = NoteMerger()
final_note = merger.merge_all_to_single(notes)
```

Claude removes duplicates, creates smooth flow, produces one coherent document.

## Complete Example (Copy-Paste Ready)

```python
from pathlib import Path
from src.pdf_extractor import PDFExtractor
from src.sliding_window_chunker import SlidingWindowChunker
from src.api_note_generator import APIBasedNoteGenerator
from src.note_merger import NoteMerger
from src.markdown_formatter import MarkdownFormatter

# 1. Extract PDF
extractor = PDFExtractor()
text, page_count = extractor.extract_text(
    "Distributed_Systems_4.pdf",
    start_page=18,
    end_page=54
)

# 2. Create overlapping chunks
chunker = SlidingWindowChunker(chunk_size=1024, overlap_ratio=0.3)
chunks = chunker.chunk_by_smart_boundaries(
    text=text,
    source_pages=list(range(18, 55)),
    chapter_title="Distributed Systems Ch1"
)
print(f"Created {len(chunks)} chunks")

# 3. Generate notes for each
generator = APIBasedNoteGenerator()
notes = [
    generator.generate_note_from_chunk(chunk)
    for chunk in chunks
]
print(f"Generated {len(notes)} notes")

# 4. Merge intelligently
merger = NoteMerger()
final_note = merger.merge_all_to_single(notes)
print("Merged to single note")

# 5. Format and save
formatter = MarkdownFormatter()
markdown = formatter.format_notes_to_markdown(
    notes=[final_note],
    title="Distributed Systems Chapter 1",
    include_metadata=True
)

Path("output").mkdir(exist_ok=True)
with open("output/notes.md", 'w') as f:
    f.write(markdown)

print("✅ Done! Check output/notes.md")
```

## Key Settings to Remember

| Setting | Value | Why |
|---------|-------|-----|
| `chunk_size` | 512-1024 | Prevents context saturation |
| `overlap_ratio` | 0.3 | Ensures no info lost at boundaries |
| Chunking method | `chunk_by_smart_boundaries()` | Respects sentence boundaries |
| Merge strategy | Hierarchical | Prevents duplication |

## If Still Getting Repetition?

1. **Try smaller chunks**:
   ```python
   chunker = SlidingWindowChunker(chunk_size=512)  # ← Smaller
   ```

2. **Try more overlap**:
   ```python
   chunker = SlidingWindowChunker(overlap_ratio=0.4)  # ← More
   ```

3. **Check which chunk is broken**:
   ```python
   for i, note in enumerate(notes):
       if "Definition of services" in note.content * 10:
           print(f"Chunk {i} is broken")
   ```

4. **Consider using Claude instead of Flan-T5**:
   ```python
   # Claude is more stable with large context
   generator = APIBasedNoteGenerator(
       model_name="claude-3-5-sonnet-20241022"
   )
   ```

## Run the Full Example

```bash
python examples/sliding_window_example.py
```

## Files You Need

- ✅ `src/sliding_window_chunker.py` - Creates overlapping chunks
- ✅ `src/note_merger.py` - Merges notes intelligently
- ✅ `src/api_note_generator.py` - Updated with better params
- ✅ `examples/sliding_window_example.py` - Complete runnable example
- ✅ `SLIDING_WINDOW_GUIDE.md` - Full technical details

All files have been created. You're ready to go!

## Next Steps

1. Try the complete example above
2. If results are good, integrate into your main pipeline
3. If still having issues, refer to `SLIDING_WINDOW_GUIDE.md` for troubleshooting

Good luck! 🚀
