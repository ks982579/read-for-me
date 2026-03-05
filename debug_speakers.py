#!/usr/bin/env python3
"""
Debug speaker detection in TTS API
"""

import torch
from TTS.api import TTS

print("Loading TTS model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

print("\n" + "=" * 60)
print("Checking for speakers...")
print("=" * 60)

# Check various attributes
print(f"\nhasattr(tts, 'speakers'): {hasattr(tts, 'speakers')}")
if hasattr(tts, 'speakers'):
    print(f"tts.speakers: {tts.speakers}")
    print(f"Type: {type(tts.speakers)}")
    if tts.speakers:
        print(f"Length: {len(tts.speakers)}")
        print(f"First speaker: {tts.speakers[0] if tts.speakers else None}")

print(f"\nhasattr(tts, 'synthesizer'): {hasattr(tts, 'synthesizer')}")
if hasattr(tts, 'synthesizer'):
    synth = tts.synthesizer
    print(f"hasattr(synthesizer, 'tts_speakers_file'): {hasattr(synth, 'tts_speakers_file')}")
    if hasattr(synth, 'tts_speakers_file'):
        print(f"synthesizer.tts_speakers_file: {synth.tts_speakers_file}")

print(f"\nhasattr(tts, 'speaker_manager'): {hasattr(tts, 'speaker_manager')}")
if hasattr(tts, 'speaker_manager'):
    print(f"tts.speaker_manager: {tts.speaker_manager}")
    if tts.speaker_manager:
        print(f"hasattr(speaker_manager, 'speaker_names'): {hasattr(tts.speaker_manager, 'speaker_names')}")
        if hasattr(tts.speaker_manager, 'speaker_names'):
            print(f"speaker_manager.speaker_names: {tts.speaker_manager.speaker_names}")

# Try to get speakers using the synthesizer
if hasattr(tts, 'synthesizer') and tts.synthesizer:
    synth = tts.synthesizer
    if hasattr(synth, 'tts_model'):
        model = synth.tts_model
        print(f"\nhasattr(model, 'speaker_manager'): {hasattr(model, 'speaker_manager')}")
        if hasattr(model, 'speaker_manager') and model.speaker_manager:
            sm = model.speaker_manager
            print(f"Model speaker_manager: {sm}")
            if hasattr(sm, 'speaker_names'):
                print(f"Speaker names: {sm.speaker_names}")

# Check model config
if hasattr(tts, 'synthesizer') and hasattr(tts.synthesizer, 'tts_config'):
    config = tts.synthesizer.tts_config
    print(f"\nConfig attributes:")
    print(f"  num_speakers: {getattr(config, 'num_speakers', 'not found')}")
    print(f"  use_speaker_embedding: {getattr(config, 'use_speaker_embedding', 'not found')}")

print("\n" + "=" * 60)
print("All TTS object attributes:")
print("=" * 60)
for attr in dir(tts):
    if not attr.startswith('_'):
        print(f"  {attr}")
