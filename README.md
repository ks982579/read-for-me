# Read For Me - PDF Note Generator

An intelligent PDF processing tool that extracts technical content from ebooks and PDFs, generates structured notes using open-source language models, and outputs Obsidian-compatible markdown files.

## Features

- **PDF Text Extraction**: Uses pymupdf for reliable text extraction from technical documents
- **Intelligent Chunking**: Smart text segmentation that preserves context and handles overlaps
- **AI-Powered Note Generation**: Uses HuggingFace models to create structured, technical notes
- **Markdown Output**: Generates clean markdown compatible with Obsidian and other note-taking apps
- **GPU Acceleration**: Supports CUDA, MPS, and CPU for flexible hardware requirements
- **Configurable Processing**: Customizable chunk sizes, models, and output formats

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd read-for-me
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Process a PDF with default settings:
```bash
python main.py path/to/your/document.pdf
```

### Advanced Options

```bash
python main.py document.pdf \
  --model "google/flan-t5-base" \
  --chunk-size 1536 \
  --overlap 150 \
  --output-dir "./my-notes" \
  --obsidian \
  --device cuda
```

### Command Line Options

- `--model, -m`: HuggingFace model name (default: microsoft/DialoGPT-medium)
- `--chunk-size, -c`: Maximum tokens per chunk (default: 2048)
- `--overlap, -o`: Token overlap between chunks (default: 200)
- `--output-dir, -d`: Output directory (default: output)
- `--obsidian`: Generate Obsidian-compatible markdown
- `--device`: Processing device (auto, cpu, cuda, mps)
- `--pages, -p`: Process specific pages (e.g., "1-10" or "5,7,9-12")

### Examples

**Process specific pages**:
```bash
python main.py book.pdf --pages "1-5,10,15-20"
```

**Use smaller model for limited GPU**:
```bash
python main.py book.pdf --model "microsoft/DialoGPT-small" --device cpu
```

**Generate Obsidian notes**:
```bash
python main.py book.pdf --obsidian --output-dir "./obsidian-vault/technical-notes"
```

## Recommended Models

### For Limited GPU Memory (< 4GB)
- `microsoft/DialoGPT-small`
- `google/flan-t5-small`

### For Moderate GPU (4-8GB)
- `microsoft/DialoGPT-medium` (default)
- `google/flan-t5-base`

### For High-End GPU (> 8GB)
- `microsoft/DialoGPT-large`
- `google/flan-t5-large`

## Output Structure

The tool generates:
- **Main notes file**: `[filename]_notes_[timestamp].md`
- **Summary file**: `[filename]_notes_[timestamp]_summary.md`

### Sample Output Structure
```markdown
# Notes: Clean Code

## Chapter 1: Clean Code
### Note 1 (Page 15)
**Key Concept:** Clean code is readable, maintainable, and expressive
• Code should tell a story
• Names should be meaningful and descriptive
• Functions should be small and focused

---
```

## Configuration

Edit `config.yaml` to customize default settings:
- Model preferences by size category
- Chunking strategies
- Generation parameters
- Output formatting options

## System Requirements

- **Python**: 3.8+
- **RAM**: 8GB+ recommended
- **GPU**: Optional but recommended (CUDA or MPS)
- **Storage**: 2GB+ for model caching

## Troubleshooting

**GPU Memory Issues**:
- Use smaller models (`-m microsoft/DialoGPT-small`)
- Reduce chunk size (`-c 1024`)
- Force CPU usage (`--device cpu`)

**Poor Note Quality**:
- Try different models (flan-t5 models often work well for summarization)
- Adjust chunk size based on your content
- Ensure your PDF has good text extraction quality

**Slow Processing**:
- Enable GPU acceleration
- Use smaller chunk sizes
- Process specific page ranges for testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]