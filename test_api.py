#!/usr/bin/env python3
"""
Simple test script to verify Claude API integration works.
"""

import os
from dotenv import load_dotenv
from src.api_note_generator import APIBasedNoteGenerator
from src.text_chunker import TextChunk

def test_api_connection():
    """Test basic API connection and note generation."""

    # Load environment variables
    load_dotenv()

    # Check if API key is loaded
    api_key = os.getenv('CLAUDE_KEY')
    if not api_key:
        print("❌ CLAUDE_KEY not found in .env file")
        return False

    print(f"✅ API key loaded (starts with: {api_key[:15]}...)")

    # Create a test chunk
    test_text = """
    Machine learning is a subset of artificial intelligence that focuses on
    enabling computers to learn from data without being explicitly programmed.
    The key concept is that algorithms can improve their performance on a task
    through experience. There are three main types of machine learning:
    supervised learning, unsupervised learning, and reinforcement learning.
    """

    test_chunk = TextChunk(
        content=test_text,
        chunk_id=0,
        source_pages=[1],
        chapter_title="Introduction to Machine Learning"
    )

    try:
        # Initialize API-based note generator
        print("\n🧠 Initializing Claude API note generator...")
        generator = APIBasedNoteGenerator(model_name="claude-3-5-sonnet-20241022")

        # Generate a note
        print("✍️  Generating test note...")
        note = generator.generate_note_from_chunk(test_chunk)

        # Display results
        print("\n" + "="*60)
        print("GENERATED NOTE:")
        print("="*60)
        print(note.content)
        print("="*60)
        print(f"\nSource pages: {note.source_pages}")
        print(f"Chapter: {note.chapter_title}")

        print("\n✅ API integration test PASSED!")
        return True

    except Exception as e:
        print(f"\n❌ API integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_connection()
    exit(0 if success else 1)
