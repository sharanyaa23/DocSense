"""TXT document loader."""
from typing import Optional


def load_txt(file_content: bytes, encoding: str = "utf-8") -> str:
    """
    Load text from TXT file content.
    
    Args:
        file_content: TXT file bytes
        encoding: Text encoding (default: utf-8)
        
    Returns:
        Extracted text from TXT
    """
    try:
        return file_content.decode(encoding)
    except UnicodeDecodeError:
        # Try with error handling
        return file_content.decode(encoding, errors="ignore")
    except Exception as e:
        raise ValueError(f"Failed to extract text from TXT: {str(e)}")

