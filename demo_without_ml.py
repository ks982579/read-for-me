#!/usr/bin/env python3

"""
Demo script that shows the PDF processing pipeline without ML models.
This helps test the core functionality before installing heavy dependencies.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def demo_pdf_extraction():
    """Demo the PDF extraction capabilities"""
    print("🔍 PDF Extraction Demo")
    print("=" * 30)

    try:
        # Test if we can at least import the structure
        from pdf_extractor import PDFExtractor, ExtractedText
        from text_chunker import TextChunker, TextChunk
        from markdown_formatter import MarkdownFormatter

        print("✅ Core modules imported successfully")

        # Create a sample text to demonstrate chunking
        sample_text = """
        Clean Code by Robert C. Martin is a comprehensive guide to writing maintainable,
        readable, and efficient code. The book emphasizes that code is read far more
        often than it is written, so it must be optimized for readability.

        Key principles include:
        - Meaningful names: Variables, functions, and classes should have descriptive names
        - Small functions: Functions should do one thing and do it well
        - Comments: Good code is self-documenting, but when comments are needed, they should explain why, not what
        - Error handling: Proper exception handling makes code more robust
        - Testing: Unit tests are essential for maintaining code quality

        The book also covers formatting, objects and data structures, and system architecture.
        Martin argues that clean code is not just about following rules, but about caring
        for the craft of programming and respecting future maintainers of the code.
        """

        # Test text chunking
        chunker = TextChunker(max_chunk_size=500, overlap_size=50)
        print(f"📝 Testing text chunking with sample text ({len(sample_text)} chars)")

        # Note: We can't test tiktoken without installing it, so we'll simulate
        print("⚠️ Tiktoken not installed - using character-based chunking simulation")

        # Simulate chunks by splitting on sentences
        sentences = sample_text.split('.')
        chunks = []
        current_chunk = ""
        chunk_id = 0

        for sentence in sentences:
            if len(current_chunk + sentence) < 200:  # Simulate token limit
                current_chunk += sentence + "."
            else:
                if current_chunk:
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        chunk_id=chunk_id,
                        source_pages=[1],
                        chapter_title="Chapter 1: Clean Code",
                        token_count=len(current_chunk.split())
                    ))
                    chunk_id += 1
                current_chunk = sentence + "."

        if current_chunk:
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                chunk_id=chunk_id,
                source_pages=[1],
                chapter_title="Chapter 1: Clean Code",
                token_count=len(current_chunk.split())
            ))

        print(f"✅ Created {len(chunks)} text chunks")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {len(chunk.content)} chars, ~{chunk.token_count} words")

        # Test markdown formatting
        formatter = MarkdownFormatter(output_dir="demo_output")
        print("📋 Testing markdown formatting...")

        # Create mock notes
        from note_generator import GeneratedNote
        mock_notes = []
        for chunk in chunks:
            # Create a simple mock note
            mock_content = f"Key points from this section:\n• {chunk.content[:100]}...\n• Important concepts mentioned\n• Technical details to remember"
            mock_notes.append(GeneratedNote(
                content=mock_content,
                source_chunk_ids=[chunk.chunk_id],
                source_pages=chunk.source_pages,
                chapter_title=chunk.chapter_title
            ))

        # Generate markdown
        markdown_content = formatter.format_notes_to_markdown(mock_notes, "clean_code_demo.pdf")

        # Save demo output
        os.makedirs("demo_output", exist_ok=True)
        demo_file = "demo_output/demo_notes.md"
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Demo markdown saved to: {demo_file}")
        print(f"📊 Generated {len(mock_notes)} mock notes")

        # Show a sample of the output
        print("\n📖 Sample Output:")
        print("-" * 40)
        print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Read For Me - Demo Mode")
    print("This demo shows the core functionality without ML dependencies\n")

    success = demo_pdf_extraction()

    if success:
        print("\n✅ Demo completed successfully!")
        print("\n📝 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test with a real PDF: python main.py your_document.pdf")
        print("3. Check the output/ directory for generated notes")
    else:
        print("\n❌ Demo failed. Check the error messages above.")

if __name__ == "__main__":
    main()