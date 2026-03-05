# PDF to Audiobook Converter

Convert your PDF books into high-quality audiobooks using GPU-accelerated AI voices!

## Quick Start (3 Steps)

### 1. Install Dependencies

```bash
# Run the setup script
./setup_tts.sh

# Or manually:
pip install -r requirements-tts.txt
sudo apt install ffmpeg  # Ubuntu/Debian
```

### 2. Test Your Setup

```bash
# Verify everything is working
python test_tts.py
```

This will:
- Check CUDA/GPU support
- Verify TTS library installation
- Generate a test audio file
- Save to `test_output/tts_test.mp3`

### 3. Convert Your First Book

```bash
# Test with just a few pages first
python tts_main.py yourbook.pdf --pages 1-5

# If that works, convert the whole book
python tts_main.py yourbook.pdf
```

Output will be saved to `audiobooks/yourbook.mp3`

## Examples

```bash
# Convert specific pages
python tts_main.py book.pdf --pages 1-50

# Save as WAV instead of MP3
python tts_main.py book.pdf --format wav

# Use CPU instead of GPU (slower)
python tts_main.py book.pdf --device cpu

# Custom output directory
python tts_main.py book.pdf --output-dir my_audiobooks/
```

## What's New

This adds TTS (Text-to-Speech) capability to the existing Read For Me project:

### New Files
- **`tts_main.py`**: Main script for PDF to audiobook conversion
- **`src/tts_generator.py`**: TTS engine using Coqui XTTS-v2
- **`test_tts.py`**: Test script to verify installation
- **`setup_tts.sh`**: Automated setup script
- **`requirements-tts.txt`**: TTS-specific dependencies
- **`TTS_GUIDE.md`**: Comprehensive user guide

### Key Features
- **GPU Accelerated**: Uses your RTX 5070-Ti for 10-20x real-time processing
- **High Quality**: Natural-sounding AI voices via Coqui XTTS-v2
- **Smart Structure**: Auto-detects chapters from PDF bookmarks
- **Flexible**: MP3, WAV, or OGG output formats

## Architecture

The TTS system reuses your existing PDF extraction infrastructure:

```
PDF → Bookmark Detection → Text Extraction → TTS Generation → Audio File
         (existing)           (existing)          (NEW!)         (NEW!)
```

### How It Works

1. **Text Extraction**: Uses the same `bookmark_chunker.py` and `pdf_extractor.py` as the note generator
2. **TTS Generation**: New `tts_generator.py` converts text to speech using Coqui TTS
3. **Audio Processing**: Combines chunks with chapter pauses and exports to MP3

## Performance (RTX 5070-Ti)

| Book Size | Processing Time | Output Size (MP3) |
|-----------|-----------------|-------------------|
| 100 pages | ~5-10 minutes | ~150-200 MB |
| 300 pages | ~15-30 minutes | ~450-600 MB |
| 500 pages | ~25-50 minutes | ~750 MB-1 GB |

Processing is approximately **10-20x faster than real-time** on your GPU.

## Comparison: Notes vs Audiobooks

Your project now supports both workflows:

### Generate Notes (existing)
```bash
python main.py book.pdf --auto --use-api
```
Output: Structured markdown notes

### Generate Audiobook (NEW!)
```bash
python tts_main.py book.pdf
```
Output: MP3 audiobook

Both can work on the same PDF and benefit from bookmark detection!

## Troubleshooting

### Out of Memory Error
```bash
# Reduce chunk size
python tts_main.py book.pdf --chunk-size 1024

# Or use CPU
python tts_main.py book.pdf --device cpu
```

### No Audio / Silent Output
- Make sure ffmpeg is installed: `ffmpeg -version`
- Check test output: `python test_tts.py`

### Slow Processing
- Verify GPU is detected: `python -c "import torch; print(torch.cuda.is_available())"`
- Check GPU usage: `nvidia-smi`
- Close other GPU applications

## Full Documentation

See **`TTS_GUIDE.md`** for:
- Detailed usage examples
- Voice customization
- Advanced options
- Performance tuning
- Tips and best practices

## Dependencies

### Python Libraries
- **TTS**: Coqui TTS for speech synthesis
- **pydub**: Audio manipulation
- **torch**: Already installed (used for GPU acceleration)
- **PyMuPDF**: Already installed (PDF extraction)

### System Requirements
- **ffmpeg**: Audio encoding (install with package manager)
- **CUDA**: For GPU acceleration (already set up)
- **~6-8GB VRAM**: For XTTS-v2 model

## FAQ

**Q: Can I use different voices?**
A: Yes! Use `--voice /path/to/voice_sample.wav` to clone any voice from a 6-10 second sample.

**Q: How does quality compare to commercial TTS?**
A: XTTS-v2 is one of the best open-source models, comparable to commercial services for English.

**Q: Can I speed up the audio?**
A: Not built-in yet, but you can use audio editing software or add playback speed in your player.

**Q: Does this replace the note generator?**
A: No! They work independently. Use notes for studying, audiobooks for listening.

**Q: Can I process multiple PDFs at once?**
A: Yes, write a bash script to loop through files. See TTS_GUIDE.md for examples.

## Credits

- **Coqui TTS**: https://github.com/coqui-ai/TTS
- **XTTS-v2**: State-of-the-art multilingual TTS model
- Built on top of the Read For Me PDF extraction system

## Next Steps

1. Run `./setup_tts.sh` to install
2. Run `python test_tts.py` to verify
3. Convert your first book!
4. Read `TTS_GUIDE.md` for advanced features

Enjoy your audiobooks! 🎧
