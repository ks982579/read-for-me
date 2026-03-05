#!/bin/bash

# TTS Audiobook Setup Script
# Installs all dependencies needed for PDF to audiobook conversion

set -e  # Exit on error

echo "🎙️  PDF to Audiobook Converter - Setup"
echo "======================================"
echo ""

# Check if ffmpeg is installed
echo "📦 Checking for ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "❌ ffmpeg is NOT installed"
    echo ""
    echo "Please install ffmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: choco install ffmpeg"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🐍 Checking Python environment..."
python --version

echo ""
echo "📦 Installing TTS dependencies..."
pip install -r requirements-tts.txt

echo ""
echo "🔍 Verifying CUDA support..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "🎙️  Testing TTS installation..."
python -c "from TTS.api import TTS; print('✅ TTS library loaded successfully')"

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick start:"
echo "  python tts_main.py yourbook.pdf --pages 1-5"
echo ""
echo "📖 Full guide: TTS_GUIDE.md"
echo "======================================"
