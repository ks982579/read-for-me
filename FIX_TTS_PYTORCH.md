# TTS/PyTorch Compatibility Fix

## The Problem

You have PyTorch 2.8.0 installed, but Coqui TTS was built for PyTorch 2.5 and earlier. PyTorch 2.6+ changed security defaults that break TTS model loading.

**Error:** `Weights only load failed... weights_only argument in torch.load from False to True`

## The Solution (Choose One)

### ✅ Option 1: Downgrade PyTorch (Recommended)

**Pros:**
- Clean, stable solution
- No code modifications
- PyTorch 2.5.1 is well-tested and stable
- Still has full CUDA support for your RTX 5070-Ti

**Cons:**
- Using slightly older PyTorch version (but only a few versions back)

**How to do it:**
```bash
./fix_tts_pytorch.sh
# Choose option 1
```

This will:
1. Uninstall PyTorch 2.8.0
2. Install PyTorch 2.5.1 (with CUDA 12.4 support)
3. Test TTS automatically

---

### 🔧 Option 2: Patch TTS Library

**Pros:**
- Keep PyTorch 2.8.0
- Uses latest PyTorch features

**Cons:**
- Modifies installed library files
- May need to re-patch after TTS updates
- Slightly less secure (disables weights_only check)

**How to do it:**
```bash
python3 patch_tts_library.py
# Confirm with 'y'
```

This will:
1. Find your TTS library installation
2. Modify `TTS/utils/io.py` to add `weights_only=False`
3. Create a backup of the original file

---

## Quick Start (Recommended Path)

```bash
# Use the downgrade option (easiest and most reliable)
./fix_tts_pytorch.sh
```

When prompted, enter **1** for the downgrade option.

Then verify it works:
```bash
python3 test_tts.py
```

You should see:
```
✅ All tests passed!
📁 Saved to: test_output/tts_test.mp3
```

---

## Detailed Instructions for Option 1 (Downgrade)

### Step 1: Run the fix script
```bash
./fix_tts_pytorch.sh
```

### Step 2: Choose option 1
```
Enter choice (1 or 2): 1
```

### Step 3: Wait for installation
This will:
- Uninstall PyTorch 2.8.0
- Install PyTorch 2.5.1 with CUDA support
- Takes 2-5 minutes depending on internet speed

### Step 4: Verify
The script will automatically run tests. You should see:
```
✅ All tests passed!
```

---

## Detailed Instructions for Option 2 (Patch)

### Step 1: Run the patch script
```bash
python3 patch_tts_library.py
```

### Step 2: Confirm
```
Apply patch? (y/n): y
```

### Step 3: Verify changes
The script will show:
```
✅ Patch applied successfully!

Changes made:
  OLD: return torch.load(f, map_location=map_location, **kwargs)
  NEW: return torch.load(f, map_location=map_location, weights_only=False, **kwargs)
```

### Step 4: Test
```bash
python3 test_tts.py
```

---

## If Both Fail

If neither option works, try this manual approach:

### Manual PyTorch Downgrade
```bash
# Uninstall current version
pip uninstall -y torch torchvision torchaudio

# Install PyTorch 2.5.1
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cu124

# Verify
python3 -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

Should output:
```
2.5.1
True
```

Then test:
```bash
python3 test_tts.py
```

---

## Verification Checklist

After applying the fix:

- [ ] Run `python3 test_tts.py`
- [ ] See "✅ All tests passed!"
- [ ] File created: `test_output/tts_test.mp3`
- [ ] Audio file plays and sounds clear
- [ ] Ready to convert PDFs!

---

## What Version Do I Have Now?

Check your PyTorch version:
```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')"
```

Check your CUDA support:
```bash
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

Both should work fine with either PyTorch 2.5.1 or 2.8.0 (after patching).

---

## Why This Happened

PyTorch 2.6+ changed the default value of `weights_only` in `torch.load()` from `False` to `True` for security reasons. This breaks loading of TTS model checkpoints which were created with custom classes.

**Security Note:** The `weights_only=False` parameter is safe for TTS models from the official Coqui repository. Don't use it for untrusted model files.

---

## Next Steps After Fix

Once tests pass:

```bash
# Convert a small test
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf --pages 1-5

# Listen to the output
# If happy, convert the full book!
python3 tts_main.py ./ebooks/Distributed_Systems_4.pdf
```

---

## Still Having Issues?

1. **Check PyTorch version:**
   ```bash
   python3 -c "import torch; print(torch.__version__)"
   ```

2. **Check CUDA:**
   ```bash
   nvidia-smi
   python3 -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Check TTS installation:**
   ```bash
   python3 -c "from TTS.api import TTS; print('OK')"
   ```

4. **Re-install TTS:**
   ```bash
   pip uninstall -y TTS
   pip install TTS
   ```

5. **Try the other option:**
   - If Option 1 didn't work, try Option 2
   - If Option 2 didn't work, try Option 1

---

## Recommended: Option 1

**Just run this:**
```bash
./fix_tts_pytorch.sh
```

Choose **1** when prompted, and you'll be up and running in a few minutes!
