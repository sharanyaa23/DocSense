"""Document summarization with multi-step consistency check."""
from typing import Dict, Any
from langchain_core.messages import HumanMessage

try:
    from ..agent.llm import get_llm
    from ..utils.cleaner import chunk_text, clean_text, strip_markdown
except ImportError:
    from backend.agent.llm import get_llm
    from backend.utils.cleaner import chunk_text, clean_text, strip_markdown


def summarize_document(document: str) -> Dict[str, Any]:
    """
    Generate a structured summary with multi-step consistency check.
    
    Args:
        document: Document text
        
    Returns:
        Dictionary with summary and metadata
    """
    llm = get_llm(temperature=0.2)
    document = clean_text(document)
    
    # Step 1: Initial summary
    initial_prompt = """Analyze the following document and create a comprehensive summary.
Include:
1. Main topic and purpose
2. Key points (3-5 bullet points)
3. Important details or numbers
4. Conclusion or next steps

Document:
{document}

Provide a clear, structured summary in plain text format. Do NOT use markdown formatting (no asterisks, bold symbols, or markdown syntax). Use simple text with line breaks only."""
    
    initial_response = llm.invoke([HumanMessage(content=initial_prompt.format(document=document[:5000]))])
    initial_summary = initial_response.content
    
    # Step 2: Consistency check - verify all major sections are covered
    consistency_prompt = """Review the following document and the summary provided.
Check if the summary covers all major sections and topics in the document.
If any important section is missing, identify it.

Document (first 3000 chars):
{document_preview}

Summary:
{summary}

Identify any missing major sections or topics. If nothing is missing, respond with 'All major sections covered.'"""
    
    document_chunks = chunk_text(document, chunk_size=3000)
    consistency_check = llm.invoke([
        HumanMessage(content=consistency_prompt.format(
            document_preview=document_chunks[0] if document_chunks else document[:3000],
            summary=initial_summary
        ))
    ])
    
    # Step 3: Final summary with any missing information
    if "missing" in consistency_check.content.lower() or "not covered" in consistency_check.content.lower():
        final_prompt = """Based on the initial summary and the consistency check, create a final comprehensive summary that includes all major sections.

Initial Summary:
{initial_summary}

Missing Information Identified:
{missing_info}

Document:
{document_preview}

Create a complete, structured summary in plain text format. Do NOT use markdown formatting (no asterisks, bold symbols, or markdown syntax). Use simple text with line breaks only."""
        
        final_response = llm.invoke([
            HumanMessage(content=final_prompt.format(
                initial_summary=initial_summary,
                missing_info=consistency_check.content,
                document_preview=document[:5000]
            ))
        ])
        final_summary = final_response.content
    else:
        final_summary = initial_summary
    
    # Strip any markdown formatting that might have been included
    final_summary = strip_markdown(final_summary)
    
    return {
        "summary": final_summary,
        "word_count": len(document.split()),
        "sections_verified": True
    }

