#!/usr/bin/env python3
"""
Automatic TTS Library Patcher

Fixes compatibility between Coqui TTS and PyTorch 2.6+
Patches TTS/utils/io.py to add weights_only=False parameter
"""

import sys
from pathlib import Path

def find_tts_io_file():
    """Find the TTS io.py file in the virtual environment"""
    try:
        import TTS
        tts_path = Path(TTS.__file__).parent
        io_file = tts_path / "utils" / "io.py"

        if io_file.exists():
            return io_file
        else:
            print(f"❌ Could not find io.py at expected location: {io_file}")
            return None
    except ImportError:
        print("❌ TTS library not installed")
        return None

def patch_file(file_path):
    """Patch the io.py file to fix PyTorch 2.6+ compatibility"""

    print(f"📄 Reading: {file_path}")

    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'weights_only=False' in content:
        print("✅ File is already patched!")
        return True

    # Find and replace the problematic line
    # Original: return torch.load(f, map_location=map_location, **kwargs)
    # New:      return torch.load(f, map_location=map_location, weights_only=False, **kwargs)

    original_line = "return torch.load(f, map_location=map_location, **kwargs)"
    patched_line = "return torch.load(f, map_location=map_location, weights_only=False, **kwargs)"

    if original_line in content:
        print("🔧 Applying patch...")
        content = content.replace(original_line, patched_line)

        # Create backup
        backup_path = file_path.with_suffix('.py.backup')
        print(f"💾 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            f.write(content.replace(patched_line, original_line))  # Write original to backup

        # Write patched content
        print(f"✍️  Writing patched file...")
        with open(file_path, 'w') as f:
            f.write(content)

        print("✅ Patch applied successfully!")
        print("")
        print("Changes made:")
        print(f"  OLD: {original_line}")
        print(f"  NEW: {patched_line}")
        print("")
        print(f"Backup saved to: {backup_path}")
        return True
    else:
        print("⚠️  Could not find expected line to patch")
        print("The TTS library may have been updated or the file structure changed")
        return False

def main():
    print("=" * 60)
    print("🔧 TTS Library Auto-Patcher")
    print("=" * 60)
    print("")
    print("This script fixes compatibility with PyTorch 2.6+")
    print("It modifies TTS/utils/io.py to add weights_only=False")
    print("")

    # Find the file
    io_file = find_tts_io_file()
    if not io_file:
        sys.exit(1)

    print(f"Found TTS io.py: {io_file}")
    print("")

    # Ask for confirmation
    response = input("Apply patch? (y/n): ")
    if response.lower() != 'y':
        print("❌ Patch cancelled")
        sys.exit(0)

    print("")

    # Apply patch
    success = patch_file(io_file)

    print("")
    print("=" * 60)
    if success:
        print("✅ Patching complete!")
        print("")
        print("🧪 Next step: Test the fix")
        print("   python3 test_tts.py")
    else:
        print("❌ Patching failed")
        print("")
        print("Alternative: Downgrade PyTorch")
        print("   ./fix_tts_pytorch.sh")
    print("=" * 60)

if __name__ == "__main__":
    main()
