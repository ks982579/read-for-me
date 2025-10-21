# Claude API Usage Guide

This guide explains how to use the Claude API integration for note generation without requiring a powerful GPU.

## Setup

1. **Get your API key**:
   - You should have already purchased API credits from Anthropic
   - Your API key should be in format: `sk-ant-api03-...`

2. **Add API key to .env file**:
   The `.env` file should already exist in your project root with:
   ```
   CLAUDE_KEY=sk-ant-api03-your-key-here
   ```

3. **Install dependencies** (if not already done):
   ```bash
   pip install anthropic python-dotenv
   ```

## Usage

### Basic API Usage

Process a PDF using Claude API:
```bash
python main.py path/to/document.pdf --use-api
```

### Model Selection

**Claude 3.5 Sonnet** (default, high quality):
```bash
python main.py document.pdf --use-api
```

**Claude 3.5 Haiku** (faster and cheaper):
```bash
python main.py document.pdf --use-api --api-model "claude-3-5-haiku-20241022"
```

### Combined with Other Options

**Process specific pages with API**:
```bash
python main.py book.pdf --use-api --pages "1-50"
```

**Generate Obsidian notes with API**:
```bash
python main.py technical-paper.pdf --use-api --obsidian --output-dir "./notes"
```

**Custom chunk size with API**:
```bash
python main.py document.pdf --use-api --chunk-size 1024
```

## Model Comparison

| Model | Quality | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| **claude-3-5-sonnet-20241022** | Highest | Slower | Higher | Technical content, research papers, detailed analysis |
| **claude-3-5-haiku-20241022** | High | Faster | Lower | Quick summaries, large documents, bulk processing |

## Cost Estimation

Approximate token usage for a typical technical PDF:
- **30-page paper**: ~50-100k input tokens, ~10-20k output tokens
- **200-page book**: ~300-500k input tokens, ~60-100k output tokens

Check current pricing at: https://www.anthropic.com/pricing

## Testing

Test your API connection:
```bash
python test_api.py
```

This will:
1. Verify your API key is loaded correctly
2. Generate a sample note
3. Display the output to confirm everything works

## Advantages of API Mode

1. **No GPU Required**: Works on any machine, including laptops without dedicated GPUs
2. **High Quality**: Claude 3.5 models provide excellent technical note generation
3. **No Model Downloads**: No need to download and cache large HuggingFace models
4. **Consistent Performance**: Cloud-based, no local resource constraints
5. **Latest Models**: Always using the most recent Claude models

## Switching Between API and Local Models

You can easily switch between modes:

**Use API** (when you want quality or lack GPU):
```bash
python main.py document.pdf --use-api
```

**Use Local Models** (when you have GPU and want to save API costs):
```bash
python main.py document.pdf
```

## Troubleshooting

**"CLAUDE_KEY not found" error**:
- Check that `.env` file exists in project root
- Verify the key is named exactly `CLAUDE_KEY` (not `ANTHROPIC_API_KEY` or similar)
- Make sure there are no quotes around the key value in the .env file

**API Rate Limits**:
- If you hit rate limits, consider using Haiku model (faster processing)
- Process documents in smaller batches using `--pages` option

**High API Costs**:
- Use `--api-model "claude-3-5-haiku-20241022"` for cheaper processing
- Reduce chunk size with `--chunk-size 1024` to generate less content per chunk
- Process only specific pages you need with `--pages "10-20"`

## When to Use Each Mode

**Use API Mode When**:
- You don't have a powerful GPU (< 6GB VRAM)
- You need the highest quality notes
- Processing small to medium documents (< 500 pages)
- You want fast setup without downloading models

**Use GPU Mode When**:
- You have a good GPU (6GB+ VRAM)
- Processing many large documents (API costs would add up)
- You prefer local processing for privacy
- You're offline or have limited internet

## Example Workflow

1. **Test the connection**:
   ```bash
   python test_api.py
   ```

2. **Process a sample chapter**:
   ```bash
   python main.py textbook.pdf --use-api --pages "1-20" --obsidian
   ```

3. **Review the quality**, then process the full book:
   ```bash
   python main.py textbook.pdf --use-api --obsidian
   ```

4. **Check your output** in the `output/` directory

That's it! You're now ready to use Claude API for high-quality note generation without needing a powerful GPU.
