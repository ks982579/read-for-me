# TTS Model Changed to Tacotron2 ✅

## What Changed

Switched from **XTTS-v2** (complex multi-speaker) to **Tacotron2-DDC** (simple single-speaker).

## Why

- XTTS-v2 requires speaker configuration (was causing errors)
- Tacotron2 is simpler, faster, and "just works"
- Single-speaker = no configuration needed
- Still produces high-quality speech

## New Model: Tacotron2-DDC

**Pros:**
- ✅ Simple - no speaker configuration needed
- ✅ Fast - processes quickly on GPU
- ✅ High quality - clear, natural English voice
- ✅ Reliable - well-tested and stable
- ✅ Smaller model size (~100MB vs 1.8GB)

**Cons:**
- Single voice only (female English voice)
- No voice cloning capability
- English only

## Try It Now

```bash
python3 test_tts.py
```

Should now work without any speaker errors!

## Model Comparison

| Model | Size | Speakers | Languages | Quality | Speed |
|-------|------|----------|-----------|---------|-------|
| **Tacotron2-DDC** (NEW) | ~100MB | 1 (female) | English | Excellent | Fast |
| XTTS-v2 (old) | ~1.8GB | Many + cloning | Multilingual | Excellent | Medium |

## What's Next

1. Run test: `python3 test_tts.py`
2. Convert PDF: `python3 tts_main.py book.pdf --pages 1-5`
3. Enjoy your audiobook!

## If You Want Multi-Speaker Later

Once the basic system is working, we can add XTTS-v2 back as an optional model with proper speaker configuration. For now, let's get it working with the simple model.

## Using Different Models

You can still use other models via command line:

```bash
# Use VITS model (another good single-speaker option)
python3 tts_main.py book.pdf --model tts_models/en/ljspeech/vits

# Use fast_pitch (very fast)
python3 tts_main.py book.pdf --model tts_models/en/ljspeech/fast_pitch
```

But the default Tacotron2 should work great for most use cases.
