#!/bin/bash

# Fix TTS compatibility with PyTorch 2.8
# Issue: PyTorch 2.6+ changed weights_only default to True, breaking TTS library

echo "🔧 Fixing TTS/PyTorch Compatibility Issue"
echo "=========================================="
echo ""

echo "Current PyTorch version:"
python3 -c "import torch; print(f'  {torch.__version__}')"

echo ""
echo "The issue: PyTorch 2.6+ changed security defaults that break TTS."
echo ""
echo "Choose a fix:"
echo "  1) Downgrade PyTorch to 2.5.1 (recommended - stable and tested)"
echo "  2) Keep PyTorch 2.8 and patch TTS library (requires manual file edit)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "📦 Downgrading PyTorch to 2.5.1..."
    echo "   This version is stable and compatible with TTS"
    echo ""

    # Uninstall current PyTorch
    pip uninstall -y torch torchvision torchaudio

    # Install PyTorch 2.5.1 with CUDA 12.4 support
    pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124

    echo ""
    echo "✅ PyTorch downgraded successfully!"
    echo ""
    echo "New version:"
    python3 -c "import torch; print(f'  PyTorch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}')"

    echo ""
    echo "🧪 Testing TTS..."
    python3 test_tts.py

elif [ "$choice" = "2" ]; then
    echo ""
    echo "⚠️  Manual patch required"
    echo ""
    echo "Edit this file:"
    echo "  .venv/lib/python3.10/site-packages/TTS/utils/io.py"
    echo ""
    echo "Find line ~54:"
    echo "  return torch.load(f, map_location=map_location, **kwargs)"
    echo ""
    echo "Replace with:"
    echo "  return torch.load(f, map_location=map_location, weights_only=False, **kwargs)"
    echo ""
    echo "Then run: python3 test_tts.py"

else
    echo "Invalid choice. Exiting."
    exit 1
fi
