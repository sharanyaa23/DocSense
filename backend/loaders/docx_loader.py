"""DOCX document loader using python-docx."""
from typing import List
from docx import Document
import io


def load_docx(file_content: bytes) -> str:
    """
    Load text from DOCX file content.
    
    Args:
        file_content: DOCX file bytes
        
    Returns:
        Extracted text from DOCX
    """
    try:
        doc = Document(io.BytesIO(file_content))
        paragraphs = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)
        return "\n\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

