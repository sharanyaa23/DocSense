"""FastAPI backend for DocSense."""
import sys
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os

# Try both import styles for flexibility
try:
    from backend.loaders.pdf_loader import load_pdf
    from backend.loaders.docx_loader import load_docx
    from backend.loaders.txt_loader import load_txt
    from backend.processors.summarizer import summarize_document
    from backend.processors.extractor import extract_information
    from backend.processors.classifier import classify_document
    from backend.processors.json_convertor import convert_to_json
    from backend.processors.comparator import compare_documents
except ImportError:
    from loaders.pdf_loader import load_pdf
    from loaders.docx_loader import load_docx
    from loaders.txt_loader import load_txt
    from processors.summarizer import summarize_document
    from processors.extractor import extract_information
    from processors.classifier import classify_document
    from processors.json_convertor import convert_to_json
    from processors.comparator import compare_documents

app = FastAPI(title="DocSense API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_document(file: UploadFile) -> str:
    """Load document based on file type."""
    content = file.file.read()
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension == ".pdf":
        return load_pdf(content)
    elif file_extension in [".docx", ".doc"]:
        return load_docx(content)
    elif file_extension == ".txt":
        return load_txt(content)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Supported: .pdf, .docx, .txt"
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "DocSense API is running", "version": "1.0.0"}


@app.post("/api/summarize")
async def summarize(file: UploadFile = File(...)):
    """Summarize a document."""
    try:
        document_text = load_document(file)
        result = summarize_document(document_text)
        return JSONResponse(content=result)
    except ValueError as e:
        # Handle API key errors specifically
        if "GROQ_API_KEY" in str(e):
            raise HTTPException(status_code=500, detail="Groq API key not configured. Please check your .env file.")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\n{traceback.format_exc()}"
        print(f"Error in /api/summarize: {error_detail}")  # Print to console for debugging
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/extract")
async def extract(
    file: UploadFile = File(...),
    extraction_type: str = Form("all")
):
    """Extract information from a document."""
    try:
        document_text = load_document(file)
        result = extract_information(document_text, extraction_type)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/classify")
async def classify(file: UploadFile = File(...)):
    """Classify a document."""
    try:
        document_text = load_document(file)
        result = classify_document(document_text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert-json")
async def convert_json(file: UploadFile = File(...)):
    """Convert document to JSON."""
    try:
        document_text = load_document(file)
        result = convert_to_json(document_text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare")
async def compare(
    file: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """Compare two documents."""
    try:
        doc1_text = load_document(file)
        doc2_text = load_document(file2)
        result = compare_documents(doc1_text, doc2_text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preview")
async def preview(file: UploadFile = File(...)):
    """Preview document content (extract text for display)."""
    try:
        # Read file content
        content = await file.read()
        file_extension = Path(file.filename).suffix.lower()
        
        # Extract text based on file type
        if file_extension == ".pdf":
            document_text = load_pdf(content)
        elif file_extension in [".docx", ".doc"]:
            document_text = load_docx(content)
        elif file_extension == ".txt":
            document_text = load_txt(content)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported: .pdf, .docx, .txt"
            )
        
        # Return first 5000 characters for preview
        preview_text = document_text[:5000]
        return JSONResponse(content={
            "preview": preview_text,
            "total_length": len(document_text),
            "truncated": len(document_text) > 5000
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

