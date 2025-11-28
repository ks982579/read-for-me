# Sliding Window Chunking & Hierarchical Merging Guide

## Problem: Why Your Model Gets Stuck

When you ask Flan-T5-large to summarize pages 18-54 in one go, you see repetitive output like:

```
Definition of services
Definition of services
Definition of services
...
```

This happens because:

1. **Context Saturation**: Flan-T5-large has a small context window (512 tokens for base, up to 1024 for some variants). Feeding it 3072 tokens at once pushes it past optimal performance.

2. **Decoding Loop**: The model's token generation process gets stuck in a high-probability loop where the same word(s) have highest probability, so it keeps generating them.

3. **Information Density**: Too much technical information in one chunk causes the model to lose coherence.

## Solution: Sliding Window Chunking with Hierarchical Merging

### How It Works

```
Original Text (Pages 18-54)
├─ Chunk 1: tokens 0-1024 [Overlap: 0-307]
├─ Chunk 2: tokens 717-1741 [Overlap: 1024-1331] ← 30% overlap with Chunk 1
├─ Chunk 3: tokens 1434-2458 [Overlap: 1741-2048] ← 30% overlap with Chunk 2
└─ Chunk 4: tokens 2151-2900 [Overlap: 2458-2757]

↓ Generate notes for each chunk

Note 1 ✓
Note 2 ✓
Note 3 ✓
Note 4 ✓

↓ Hierarchically merge (Claude handles redundancy)

Merged 1-2 ✓
Merged 3-4 ✓

↓ Final merge

Comprehensive Final Note ✓
```

### Key Benefits

| Problem | Solution |
|---------|----------|
| Model gets stuck repeating | Smaller chunks (1024 tokens) fit better in context |
| Information lost at boundaries | 30% overlap ensures nothing is missed |
| Notes are fragmented | Hierarchical merging creates cohesive narrative |
| Redundancy across chunks | Claude intelligently deduplicates during merge |
| Works only with large models | Works with smaller models like Flan-T5 |

## Usage Examples

### Basic Usage

```python
from src.sliding_window_chunker import SlidingWindowChunker
from src.api_note_generator import APIBasedNoteGenerator
from src.note_merger import NoteMerger

# 1. Create overlapping chunks
chunker = SlidingWindowChunker(
    chunk_size=1024,       # Tokens per chunk (smaller is safer)
    overlap_ratio=0.3      # 30% overlap
)
chunks = chunker.chunk_by_smart_boundaries(
    text=your_text,
    source_pages=[18, 19, 20, ...],
    chapter_title="Distributed Systems"
)

# 2. Generate notes for each chunk
generator = APIBasedNoteGenerator()
notes = [
    generator.generate_note_from_chunk(chunk)
    for chunk in chunks
]

# 3. Merge hierarchically
merger = NoteMerger()
final_note = merger.merge_all_to_single(notes)
```

### Recommended Settings by Model

#### For Flan-T5-large (248M params)
```python
chunker = SlidingWindowChunker(
    chunk_size=512,         # Keep it small!
    overlap_ratio=0.3
)
```

#### For Flan-T5-xl (3B params)
```python
chunker = SlidingWindowChunker(
    chunk_size=1024,        # Can handle more
    overlap_ratio=0.3
)
```

#### For Claude API (highly recommended)
```python
chunker = SlidingWindowChunker(
    chunk_size=2048,        # Claude has large context
    overlap_ratio=0.2       # Less overlap needed
)
generator = APIBasedNoteGenerator()
```

### Advanced: Batch Merging for Many Chunks

If you have many chunks, merge in stages:

```python
merger = NoteMerger()

# For 20 chunks, first merge in groups of 3
partially_merged = merger.merge_notes_in_batches(notes, batch_size=3)
# Result: 7 notes

# Then merge the 7
final = merger.merge_all_to_single(partially_merged)
```

## Why This Fixes the Repetition Problem

### Without Sliding Window (What You Were Doing)
```
[37 pages worth of text] → Flan-T5 → [Gets stuck in loop] →
"Definition of services" × 100
```

**Why**: Model is overwhelmed by context size, decoding process unstable.

### With Sliding Window (Recommended)
```
[512 tokens] → Flan-T5 → Note 1 ✓
[512 tokens] → Flan-T5 → Note 2 ✓
[512 tokens] → Flan-T5 → Note 3 ✓
...
[All notes] → Claude Merge → Cohesive Document ✓
```

**Why**: Each chunk is manageable, Claude handles coherence during merge.

## Benchmark: Pages 18-54 of Your PDF

### Current Approach
- Chunk size: 3072 tokens
- Result: Gets stuck repeating
- Time: ~30-60 seconds (but output is broken)

### Recommended Approach
- Chunk size: 512-1024 tokens per chunk
- 5-10 chunks for 37 pages
- Time per chunk: ~10-30 seconds (depending on API)
- Total: ~2-5 minutes
- Result: Comprehensive, coherent notes ✓

## Step-by-Step for Your Use Case

### Want to process pages 18-54 better?

```python
from examples.sliding_window_example import process_pdf_with_sliding_window

output = process_pdf_with_sliding_window(
    pdf_path="Distributed_Systems_4.pdf",
    start_page=18,
    end_page=54,
    chunk_size=1024,        # Start here
    overlap_ratio=0.3,
    output_dir="output"
)

# If still getting repetition, try:
output = process_pdf_with_sliding_window(
    pdf_path="Distributed_Systems_4.pdf",
    start_page=18,
    end_page=54,
    chunk_size=512,         # Even smaller
    overlap_ratio=0.35,     # Slightly more overlap
    output_dir="output"
)
```

## Technical Details

### Smart Boundary Detection

The chunker respects sentence and paragraph boundaries rather than hard token limits:

```
# What you DON'T want:
"In a distributed sys[CUT MID-WORD]tem..."

# What you DO get:
"In a distributed system, we need to consider..."
[New chunk starts]
"The primary concern is maintaining..."
```

### Overlap Handling

Chunks overlap like this:

```
Chunk 1: [============================]
Chunk 2:                [============================]
                        ^ Overlap region (last 30% of Chunk 1)

This ensures: If an important concept appears near the boundary,
it's not split across chunks - it's fully present in both.
```

### Hierarchical Merging

When merging notes, Claude:
1. **Identifies** redundant information
2. **Keeps** the best explanation of each point
3. **Combines** unique information from both notes
4. **Maintains** flow and organization

Example merge:

```
Note 1: "DNS uses a hierarchical structure with 13 root servers."
Note 2: "DNS implements a tree with root servers distributed globally."

After merge: "DNS is implemented as a hierarchical tree structure with 13 root
servers distributed globally, ensuring no single point of failure."
```

## Performance Tips

### To speed up processing:
1. Use smaller chunk sizes (512 vs 1024) → more chunks, faster each
2. Use less overlap (0.2 vs 0.3) → fewer redundant generations
3. Use batched merging → reduces final merge complexity

### To improve quality:
1. Use larger chunk sizes (1024 vs 512) → more context per chunk
2. Increase overlap (0.4 vs 0.3) → better boundary continuity
3. Use Claude API → better merging intelligence

## Troubleshooting

### Still getting repetition?
- Reduce chunk size: `chunk_size=512`
- Check your model: Flan-T5-large has limited capacity
- Try Claude API: `APIBasedNoteGenerator()`

### Missing information?
- Increase overlap: `overlap_ratio=0.4`
- Check chunk boundaries: Use `chunk_by_smart_boundaries()` not `chunk_with_sliding_window()`

### Notes seem fragmented?
- Check merge batch size: May need smaller batches
- Verify final merge completed: Should have 1 note in the end

### Takes too long?
- Reduce chunk count: Increase `chunk_size`
- Reduce overlap: Set `overlap_ratio=0.2`
- Skip merging: Process chunks independently if merging is bottleneck

## Files

- `src/sliding_window_chunker.py` - Core chunking logic
- `src/note_merger.py` - Intelligent note merging
- `examples/sliding_window_example.py` - Complete example
- This file - Full documentation

Run the example:
```bash
python examples/sliding_window_example.py
```
