#!/usr/bin/env python3
"""
List Available TTS Voices

Shows all available speakers/voices for the XTTS-v2 model.
"""

import torch

def main():
    print("=" * 60)
    print("🎤 Available TTS Voices")
    print("=" * 60)
    print()

    # Check CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print()

    try:
        from TTS.api import TTS

        print("Loading XTTS-v2 model...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        if hasattr(tts, 'speakers') and tts.speakers:
            print(f"\n✅ Found {len(tts.speakers)} speakers:\n")
            for i, speaker in enumerate(tts.speakers, 1):
                print(f"  {i}. {speaker}")

            print("\n" + "=" * 60)
            print("Using Voices")
            print("=" * 60)
            print("\nThe default speaker is:", tts.speakers[0])
            print("\nTo use a different speaker, you would need to modify")
            print("the code to specify the speaker name.")
            print("\nAlternatively, XTTS-v2 supports voice cloning from")
            print("a 6-10 second audio sample of any voice.")

        else:
            print("⚠️  This model doesn't have multiple speakers")
            print("   It uses a single default voice.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
