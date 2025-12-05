# DocSense — Smart Document Processing Agent

DocSense is an intelligent document-processing agent that allows users to upload PDF, DOCX, or TXT files and choose exactly what they want the system to do. Built with a lightweight HTML frontend and a FastAPI backend, DocSense uses LangChain, LangGraph, and Groq LLMs to intelligently analyze, summarize, extract, classify, convert, and compare documents — all with multi-step validation to ensure correctness and zero hallucinations.

## 🛠 Tech Stack

- **Frontend**: HTML (single file), Embedded CSS, JavaScript
- **Backend**: FastAPI, Python
- **AI Framework**: LangChain, LangGraph, Groq LLM
- **Libraries**: PyPDF2, pdfplumber, python-docx, uvicorn

## ⭐ Features

### 1️⃣ Document Summarization

Generates short, structured summaries of the entire document. Uses a multi-step consistency check to ensure no major section is missed.

### 2️⃣ Information Extraction

Extracts emails, names, dates, totals, keywords, or custom patterns. Removes false matches using validation and repeated checks.

### 3️⃣ Document Classification

Detects if a file is a resume, invoice, contract, report, or another type. Re-evaluates unclear cases using LangGraph's decision loop for accuracy.

### 4️⃣ JSON Conversion

Converts the document into structured JSON key-value fields. Retries extraction if fields are missing or incomplete.

### 5️⃣ Document Comparison

Compares two documents and identifies additions, deletions, and modifications. Chunk-aligns documents to detect even subtle differences.

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Groq API key (get one at https://console.groq.com/)

### Installation

1. **Clone or navigate to the project directory:**

   ```bash
   cd docSSS
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root:

   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start the FastAPI backend:**

   ```bash
   cd backend
   python main.py
   ```

   The API will be available at `http://localhost:8000`

6. **Open the frontend:**
   - Open `frontend/code.html` in your web browser
   - Or serve it using a simple HTTP server:
     ```bash
     # Python 3
     cd frontend
     python -m http.server 8080
     ```
     Then open `http://localhost:8080/code.html` in your browser

## 📖 Usage

1. **Upload a document**: Drag and drop or browse for a PDF, DOCX, or TXT file
2. **Select an action**: Choose from Summarizer, Information Extractor, Document Classifier, JSON Converter, or Document Comparison
3. **For comparison**: Upload a second file when "Document Comparison" is selected
4. **Process**: Click "Process Document" to get results
5. **View results**: Results appear in the right panel with options to copy or download

## 🔧 API Endpoints

- `POST /api/summarize` - Summarize a document
- `POST /api/extract` - Extract information from a document
- `POST /api/classify` - Classify a document
- `POST /api/convert-json` - Convert document to JSON
- `POST /api/compare` - Compare two documents
- `GET /api/health` - Health check

## 📁 Project Structure

```
docSense/
├── backend/
│   ├── agent/
│   │   ├── llm.py          # Groq LLM setup
│   │   └── graph.py         # LangGraph workflows
│   ├── loaders/
│   │   ├── pdf_loader.py   # PDF document loader
│   │   ├── docx_loader.py  # DOCX document loader
│   │   └── txt_loader.py   # TXT document loader
│   ├── processors/
│   │   ├── summarizer.py   # Document summarization
│   │   ├── extractor.py    # Information extraction
│   │   ├── classifier.py    # Document classification
│   │   ├── json_convertor.py # JSON conversion
│   │   └── comparator.py    # Document comparison
│   ├── utils/
│   │   └── cleaner.py      # Text cleaning utilities
│   └── main.py             # FastAPI application
├── frontend/
│   └── code.html           # Single-page HTML frontend
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔑 Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

## 🐛 Troubleshooting

- **Import errors**: Make sure you're running from the project root or adjust import paths
- **API connection errors**: Verify the backend is running on port 8000 and CORS is enabled
- **File upload errors**: Check that the file type is supported (PDF, DOCX, TXT)
- **Groq API errors**: Verify your API key is set correctly in the `.env` file

## 📝 Notes

- The frontend expects the backend to be running on `http://localhost:8000`
- For production, update the `API_BASE_URL` in `code.html` to point to your backend server
- Large documents may take longer to process
- The system uses chunking for large documents to stay within token limits

## 📄 License

This project is open source and available for educational and commercial use.
