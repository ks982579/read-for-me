# PDF to Audiobook Converter - User Guide

Transform your PDF books into high-quality audiobooks using GPU-accelerated text-to-speech!

## Features

- **GPU-Accelerated**: Uses your RTX 5070-Ti for fast, high-quality TTS generation
- **Natural Voices**: Powered by Coqui XTTS-v2, one of the best open-source TTS models
- **Smart Structure**: Automatically detects chapters and sections from PDF bookmarks
- **Chapter Markers**: Adds longer pauses between chapters for natural listening
- **Multiple Formats**: Output as MP3, WAV, OGG, or other audio formats
- **Flexible Range**: Convert entire books or specific page ranges

## Installation

### 1. Install System Dependencies

You need `ffmpeg` for audio encoding:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

### 2. Install Python Dependencies

```bash
# Install TTS requirements
pip install -r requirements-tts.txt
```

### 3. Verify GPU Support

Check that PyTorch can see your GPU:

```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

Should output: `CUDA available: True`

## Quick Start

### Convert Entire Book

```bash
python tts_main.py mybook.pdf
```

This will:
1. Extract text from the PDF
2. Detect chapters from bookmarks (if available)
3. Convert to speech using GPU
4. Save as `audiobooks/mybook.mp3`

### Convert Specific Pages

Test with a small section first:

```bash
# Convert just the first chapter (pages 1-30)
python tts_main.py mybook.pdf --pages 1-30
```

### Advanced Options

```bash
# Use CPU instead of GPU (slower but works without CUDA)
python tts_main.py mybook.pdf --device cpu

# Output as WAV for maximum quality
python tts_main.py mybook.pdf --format wav

# Custom output directory
python tts_main.py mybook.pdf --output-dir ./my_audiobooks

# Specific page ranges
python tts_main.py mybook.pdf --pages 1-10,25-50,100-150
```

## Command Reference

```
Usage: tts_main.py [OPTIONS] PDF_PATH

Options:
  -c, --chunk-size INTEGER    Max tokens per chunk (default: 2048)
  -o, --overlap INTEGER       Token overlap between chunks (default: 200)
  -d, --output-dir PATH       Output directory (default: audiobooks)
  --device TEXT               Device: cuda or cpu (default: cuda)
  -p, --pages TEXT            Page range (e.g., "1-10" or "5,7,9-12")
  --auto / --no-auto          Auto-detect structure from bookmarks (default: True)
  --voice TEXT                Voice preset or reference audio path
  -m, --model TEXT            TTS model to use (default: xtts_v2)
  -f, --format TEXT           Audio format: mp3, wav, ogg (default: mp3)
  --help                      Show this message and exit
```

## Typical Workflow

### 1. Test with a Small Section

Always test with a few pages first to verify quality:

```bash
python tts_main.py book.pdf --pages 1-5
```

Listen to the output to ensure:
- Voice quality is acceptable
- Speed is comfortable
- No weird pronunciation issues

### 2. Check Bookmark Structure

See if your PDF has bookmarks for better chapter handling:

```bash
python test_bookmarks.py book.pdf
```

### 3. Convert Full Book

Once satisfied with quality:

```bash
python tts_main.py book.pdf
```

## Performance

With your **RTX 5070-Ti GPU**:

- **Processing Speed**: ~10-20x real-time (generates 1 hour of audio in 3-6 minutes)
- **Memory Usage**: ~4-8GB VRAM depending on batch size
- **Quality**: Near-human speech quality with XTTS-v2

### Benchmarks (Approximate)

| Book Size | GPU Time | CPU Time | Output Size (MP3) |
|-----------|----------|----------|-------------------|
| 100 pages | ~5-10 min | ~2-3 hours | ~150-200 MB |
| 300 pages | ~15-30 min | ~6-9 hours | ~450-600 MB |
| 500 pages | ~25-50 min | ~10-15 hours | ~750 MB-1 GB |

## Audio Quality Settings

### MP3 (Recommended for Audiobooks)
- **Bitrate**: 192kbps (good quality, reasonable file size)
- **Typical Size**: ~1.5 MB per minute
- **Use Case**: General listening, podcasts, audiobooks

### WAV (Maximum Quality)
- **Bitrate**: Uncompressed 24kHz 16-bit
- **Typical Size**: ~2.8 MB per minute
- **Use Case**: Archival, further processing

### OGG (Best Compression)
- **Bitrate**: Variable (comparable to MP3 but smaller)
- **Typical Size**: ~1.2 MB per minute
- **Use Case**: Web streaming, mobile devices

## Voice Customization

### Using Default Voice

The default English voice is high quality and works out of the box:

```bash
python tts_main.py book.pdf
```

### Voice Cloning (Advanced)

You can clone any voice using a 6-10 second reference audio:

```bash
# Use your own voice
python tts_main.py book.pdf --voice /path/to/voice_sample.wav
```

Requirements for reference audio:
- Clear, noise-free recording
- 6-10 seconds of speech
- Single speaker
- WAV or MP3 format

## Troubleshooting

### Out of Memory (CUDA OOM)

If you get CUDA out-of-memory errors:

```bash
# Reduce chunk size
python tts_main.py book.pdf --chunk-size 1024

# Or use CPU (slower but stable)
python tts_main.py book.pdf --device cpu
```

### Poor Voice Quality

- Try a different TTS model (see available models below)
- Ensure your PDF text extraction is clean (check for OCR errors)
- Adjust chunk size for better context

### Slow Processing

- Verify GPU is being used: Check NVIDIA GPU usage with `nvidia-smi`
- Close other GPU applications
- Ensure CUDA drivers are up to date

### Audio Artifacts

If you hear pops, clicks, or distortions:

- Check that ffmpeg is properly installed
- Try WAV format to isolate encoding issues
- Reduce chunk overlap: `--overlap 100`

## Available TTS Models

| Model | Quality | Speed | VRAM | Notes |
|-------|---------|-------|------|-------|
| xtts_v2 | Excellent | Fast | 6-8GB | **Recommended**, voice cloning |
| tacotron2 | Good | Very Fast | 2-4GB | Older, but reliable |
| glow-tts | Good | Fast | 3-5GB | Natural prosody |

Change model with:
```bash
python tts_main.py book.pdf --model tts_models/en/ljspeech/tacotron2-DDC
```

## Advanced Use Cases

### Batch Processing Multiple Books

```bash
#!/bin/bash
for pdf in books/*.pdf; do
    python tts_main.py "$pdf" --output-dir audiobooks/
done
```

### Converting Specific Chapters

```bash
# Chapter 1 (pages 1-30)
python tts_main.py book.pdf --pages 1-30 -d audiobooks/chapter1

# Chapter 2 (pages 31-65)
python tts_main.py book.pdf --pages 31-65 -d audiobooks/chapter2
```

Then combine manually if needed.

### Testing Voice Quality

Create a test snippet:

```bash
# Just convert first 3 pages to test voice
python tts_main.py book.pdf --pages 1-3 --output-dir test/
```

## Integration with Existing Note Generator

This TTS system works independently but uses the same PDF extraction:

- **For Notes**: Use `main.py` to generate markdown notes
- **For Audio**: Use `tts_main.py` to generate audiobooks
- Both can share the same PDF and benefit from bookmark detection

## Tips for Best Results

1. **Test First**: Always test with 5-10 pages before converting entire book
2. **Check Bookmarks**: Use `test_bookmarks.py` to verify PDF structure
3. **Clean PDFs**: OCR-scanned PDFs may have text errors; preview extraction first
4. **Monitor GPU**: Use `nvidia-smi` to watch VRAM usage
5. **Save WAV First**: For archival, save as WAV then convert to MP3 later

## Future Enhancements

Potential improvements (not yet implemented):

- [ ] Multiple voice support for dialogue
- [ ] Speed adjustment (1.0x, 1.25x, 1.5x, etc.)
- [ ] Emotion/tone control
- [ ] Background music support
- [ ] Chapter metadata for audiobook players
- [ ] Resume from interruption

## License

Built on top of Coqui TTS (Mozilla Public License 2.0)

## Credits

- **Coqui TTS**: https://github.com/coqui-ai/TTS
- **XTTS-v2**: State-of-the-art multilingual TTS
- **PyDub**: Audio manipulation library

---

**Questions or Issues?** Open an issue on GitHub or check the main project README.
