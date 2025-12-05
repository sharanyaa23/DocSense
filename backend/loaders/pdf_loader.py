"""PDF document loader using PyPDF2 and pdfplumber."""
import io
from typing import Optional
import PyPDF2
import pdfplumber


def load_pdf(file_content: bytes) -> str:
    """
    Load text from PDF file content.
    
    Args:
        file_content: PDF file bytes
        
    Returns:
        Extracted text from PDF
    """
    text_parts = []
    
    # Try pdfplumber first (better for complex layouts)
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        # Fallback to PyPDF2
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    return "\n\n".join(text_parts)

