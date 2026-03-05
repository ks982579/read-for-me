# Getting Started with TTS Audiobooks - Quick Checklist

## Installation & Testing (5 minutes)

### Step 1: Install Dependencies
```bash
# Run the automated setup
./setup_tts.sh
```

**Expected Output:**
- ✅ ffmpeg is installed
- ✅ TTS library loaded successfully
- ✅ CUDA available: True
- GPU: NVIDIA GeForce RTX 5070-Ti

**If setup fails:** See troubleshooting section below.

---

### Step 2: Verify Installation
```bash
# Run the test suite
python3 test_tts.py
```

**Expected Output:**
- ✅ All tests passed!
- 📁 Test audio saved to: `test_output/tts_test.mp3`

**Action:** Listen to `test_output/tts_test.mp3` to verify audio quality.

---

### Step 3: Try a Small Test with Your PDF
```bash
# Convert just the first 5 pages of one of your books
python3 tts_main.py ./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf --pages 1-5
```

**Expected Output:**
```
🎙️  PDF to Audiobook Converter
✅ Bookmarks found! Using structure-aware extraction...
📚 Created X structured chunks
🔊 Initializing TTS engine...
🎙️  Converting text to speech...
✅ Audiobook created successfully!
📁 Location: audiobooks/IntelligentTechniquesForDataScience.mp3
⏱️  Duration: ~2-5 minutes
```

**Action:** Listen to the generated audiobook!

---

## Full Book Conversion

Once you're happy with the test, convert the whole book:

### Option 1: Intelligent Techniques for Data Science
```bash
python3 tts_main.py ./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf
```

**Estimated Time:** 15-30 minutes (depends on book length)
**Output:** `audiobooks/IntelligentTechniquesForDataScience.mp3`

### Option 2: Distributed Systems
```bash
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf
```

**Output:** `audiobooks/Distributed_Systems_4.mp3`

---

## Common Scenarios

### Convert Specific Chapters

If you want just Chapter 1 (assuming pages 1-30):
```bash
python3 tts_main.py ./ebooks/IntelligentTechsForDS/IntelligentTechniquesForDataScience.pdf \
    --pages 1-30 \
    --output-dir audiobooks/chapter1/
```

### Save as WAV for Maximum Quality
```bash
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf --format wav
```

### Process on CPU (if GPU issues)
```bash
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf --device cpu
```

---

## Troubleshooting

### ❌ Error: "No module named 'TTS'"

**Fix:**
```bash
pip install -r requirements-tts.txt
```

---

### ❌ Error: "ffmpeg: not found"

**Fix:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Check installation
ffmpeg -version
```

---

### ❌ Error: "CUDA out of memory"

**Fix 1:** Reduce chunk size
```bash
python3 tts_main.py yourbook.pdf --chunk-size 1024
```

**Fix 2:** Use CPU instead
```bash
python3 tts_main.py yourbook.pdf --device cpu
```

---

### ❌ Error: "RuntimeError: No CUDA GPUs are available"

**Check CUDA:**
```bash
python3 -c "import torch; print(torch.cuda.is_available())"
```

**If False:**
- Verify NVIDIA drivers: `nvidia-smi`
- Reinstall PyTorch with CUDA support
- Or use CPU: `--device cpu`

---

### ⚠️  Audio is silent or garbled

**Fix:**
```bash
# Re-run test
python3 test_tts.py

# Check ffmpeg
ffmpeg -version
```

---

## Expected Results

### Processing Speed (RTX 5070-Ti)
- **100-page book**: 5-10 minutes
- **300-page book**: 15-30 minutes
- **500-page book**: 25-50 minutes

### Output Quality
- **Voice**: Natural AI voice (female English by default)
- **Bitrate**: 192kbps MP3 (good quality)
- **Size**: ~1.5 MB per minute of audio

### Example Output Sizes
- **5 pages**: ~7-15 MB
- **50 pages**: ~70-150 MB
- **300 pages**: ~400-600 MB

---

## Monitoring Progress

### Check GPU Usage (Optional)
Open a second terminal:
```bash
watch -n 1 nvidia-smi
```

You should see:
- GPU-Util: 60-95%
- Memory-Usage: 6-8 GB / 16 GB

---

## Command Reference

### Basic Conversion
```bash
python3 tts_main.py <pdf_file>
```

### All Options
```bash
python3 tts_main.py <pdf_file> \
    --pages 1-50 \              # Specific pages
    --device cuda \             # cuda or cpu
    --format mp3 \              # mp3, wav, or ogg
    --output-dir audiobooks/ \  # Output directory
    --chunk-size 2048 \         # Tokens per chunk
    --overlap 200               # Token overlap
```

### Help
```bash
python3 tts_main.py --help
```

---

## What's Next?

### Try Different Features
1. Convert different page ranges
2. Try WAV format for archival quality
3. Process multiple books
4. Experiment with chunk sizes

### Read Full Documentation
- **Quick Guide**: `TTS_README.md`
- **Detailed Manual**: `TTS_GUIDE.md`
- **Setup Info**: `SETUP_SUMMARY.md`

### Advanced Features (see TTS_GUIDE.md)
- Voice cloning from audio samples
- Batch processing multiple PDFs
- Different TTS models
- Speed adjustments

---

## Success Checklist

- [ ] Ran `./setup_tts.sh` successfully
- [ ] Ran `python3 test_tts.py` - all tests passed
- [ ] Listened to `test_output/tts_test.mp3` - sounds good
- [ ] Converted 5 pages of a book
- [ ] Listened to the audiobook - quality is acceptable
- [ ] Ready to convert full books!

---

## Getting Help

If you encounter issues:

1. **Check test output**: `python3 test_tts.py`
2. **Read troubleshooting**: See section above
3. **Check logs**: Error messages usually indicate the issue
4. **Verify GPU**: `nvidia-smi` should show your RTX 5070-Ti

---

## Your First Audiobook Awaits! 🎧

```bash
# Start with a small test
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf --pages 1-10

# Then go for the full book
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf
```

**Enjoy your audiobooks!** 📚 → 🎧
