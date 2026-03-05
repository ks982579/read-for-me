#!/usr/bin/env python3
"""
Quick TTS Test Script

Tests that the TTS system is working properly before processing PDFs.
Generates a short audio sample to verify installation and GPU acceleration.
"""

import torch
from pathlib import Path
import sys

def test_cuda():
    """Test CUDA availability"""
    print("🔍 Testing CUDA Support...")
    print(f"   PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"   CUDA version: {torch.version.cuda}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print("   ✅ GPU acceleration available!")
        return "cuda"
    else:
        print("   ⚠️  No GPU found, will use CPU (slower)")
        return "cpu"

def test_tts_import():
    """Test TTS library import"""
    print("\n📦 Testing TTS Library...")
    try:
        from TTS.api import TTS
        print("   ✅ TTS library imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import TTS library: {e}")
        print("\n   Install with: pip install -r requirements-tts.txt")
        return False

def test_audio_import():
    """Test audio processing libraries"""
    print("\n🎵 Testing Audio Libraries...")
    try:
        from pydub import AudioSegment
        print("   ✅ pydub imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import pydub: {e}")
        print("\n   Install with: pip install pydub")
        return False

def test_ffmpeg():
    """Test ffmpeg availability"""
    print("\n🎬 Testing ffmpeg...")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            return True
        else:
            print("   ❌ ffmpeg found but returned error")
            return False
    except FileNotFoundError:
        print("   ❌ ffmpeg not found")
        print("\n   Install ffmpeg:")
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Windows: choco install ffmpeg")
        return False
    except Exception as e:
        print(f"   ❌ Error checking ffmpeg: {e}")
        return False

def test_tts_generation(device):
    """Test actual TTS generation"""
    print(f"\n🎙️  Testing TTS Generation (using {device})...")

    try:
        from TTS.api import TTS
        from pydub import AudioSegment
        import numpy as np

        print("   Loading TTS model (this may take a minute)...")
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC").to(device)

        print("   Generating test audio...")
        test_text = "Hello! This is a test of the text to speech system. If you can hear this, everything is working correctly."

        # Simple single-speaker model - no speaker parameter needed
        wav = tts.tts(text=test_text)

        # Convert to AudioSegment
        audio_array = np.array(wav)
        audio_array = (audio_array * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            audio_array.tobytes(),
            frame_rate=22050,
            sample_width=2,
            channels=1
        )

        # Save test file
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "tts_test.mp3"

        audio_segment.export(output_file, format="mp3", bitrate="192k")

        print(f"   ✅ Test audio generated successfully!")
        print(f"   📁 Saved to: {output_file}")
        print(f"   ⏱️  Duration: {len(audio_segment) / 1000:.1f} seconds")
        print(f"\n   🎧 Play the file to verify audio quality")

        return True

    except Exception as e:
        print(f"   ❌ TTS generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🎙️  TTS System Test")
    print("=" * 60)

    all_passed = True

    # Test CUDA
    device = test_cuda()

    # Test imports
    if not test_tts_import():
        all_passed = False

    if not test_audio_import():
        all_passed = False

    if not test_ffmpeg():
        all_passed = False

    # If basic tests passed, try actual TTS generation
    if all_passed:
        if not test_tts_generation(device):
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        print("\n🚀 You're ready to convert PDFs to audiobooks!")
        print("\nTry: python tts_main.py yourbook.pdf --pages 1-5")
    else:
        print("❌ Some tests failed")
        print("\nPlease install missing dependencies and try again.")
        print("Run: ./setup_tts.sh")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
