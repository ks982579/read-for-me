#!/usr/bin/env python3

"""
Basic test script to verify the application structure works
before full dependency installation completes.
"""

import sys
import os

print("🧪 Testing Read For Me Application Structure")
print("=" * 50)

# Test basic imports
try:
    import src
    print("✅ src module structure: OK")
except ImportError as e:
    print(f"❌ src module structure: {e}")

# Test file existence
required_files = [
    'src/pdf_extractor.py',
    'src/text_chunker.py',
    'src/note_generator.py',
    'src/markdown_formatter.py',
    'main.py',
    'requirements.txt',
    'config.yaml'
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path}: Found")
    else:
        print(f"❌ {file_path}: Missing")

# Test CLI interface structure
try:
    import click
    print("✅ Click CLI framework: Available")

    # Test basic CLI help
    from main import main
    print("✅ Main CLI function: Available")
except ImportError as e:
    print(f"⚠️ Click not yet installed: {e}")
except Exception as e:
    print(f"⚠️ Main CLI function issue: {e}")

print("\n📋 Application Structure Test Complete")
print("💡 Run 'pip install -r requirements.txt' to install dependencies")
print("📖 Then test with: python main.py --help")