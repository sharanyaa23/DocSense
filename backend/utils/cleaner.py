"""Text cleaning utilities."""
import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    import re
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)  # Remove __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)  # Remove _italic_
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove markdown list markers but keep the content
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Maximum chunk size
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            if break_point > start + chunk_size // 2:
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks

