"""Document comparison with chunk-aligned diff detection."""
from typing import Dict, Any, List, Tuple
from langchain_core.messages import HumanMessage

try:
    from ..agent.llm import get_llm
    from ..utils.cleaner import chunk_text
except ImportError:
    from backend.agent.llm import get_llm
    from backend.utils.cleaner import chunk_text


def compare_documents(doc1: str, doc2: str) -> Dict[str, Any]:
    """
    Compare two documents and identify differences.
    
    Args:
        doc1: First document text
        doc2: Second document text
        
    Returns:
        Dictionary with comparison results
    """
    llm = get_llm(temperature=0.1)
    
    # Chunk both documents for alignment
    chunk_size = 500
    chunks1 = chunk_text(doc1, chunk_size=chunk_size, overlap=50)
    chunks2 = chunk_text(doc2, chunk_size=chunk_size, overlap=50)
    
    additions = []
    deletions = []
    modifications = []
    
    # Compare chunks
    max_chunks = max(len(chunks1), len(chunks2))
    
    for i in range(max_chunks):
        chunk1 = chunks1[i] if i < len(chunks1) else ""
        chunk2 = chunks2[i] if i < len(chunks2) else ""
        
        if not chunk1 and chunk2:
            # Addition
            additions.append({
                "position": i,
                "content": chunk2[:200]  # Preview
            })
        elif chunk1 and not chunk2:
            # Deletion
            deletions.append({
                "position": i,
                "content": chunk1[:200]  # Preview
            })
        elif chunk1 != chunk2:
            # Potential modification - use LLM to identify specific changes
            comparison_prompt = """Compare these two text chunks and identify:
1. What was added (if anything)
2. What was removed (if anything)
3. What was modified (if anything)

Chunk 1 (Original):
{chunk1}

Chunk 2 (Modified):
{chunk2}

Provide a brief summary of changes. If they are identical, say "No changes"."""
            
            comparison = llm.invoke([
                HumanMessage(content=comparison_prompt.format(
                    chunk1=chunk1[:500],
                    chunk2=chunk2[:500]
                ))
            ])
            
            if "no changes" not in comparison.content.lower():
                modifications.append({
                    "position": i,
                    "original": chunk1[:200],
                    "modified": chunk2[:200],
                    "summary": comparison.content
                })
    
    # Overall comparison using LLM
    overall_prompt = """Provide a high-level comparison of these two documents.
Identify:
1. Main differences in content
2. Structural changes
3. Key additions or deletions

Document 1 (first 2000 chars):
{doc1_preview}

Document 2 (first 2000 chars):
{doc2_preview}

Provide a concise comparison summary:"""
    
    overall_comparison = llm.invoke([
        HumanMessage(content=overall_prompt.format(
            doc1_preview=doc1[:2000],
            doc2_preview=doc2[:2000]
        ))
    ])
    
    # Calculate similarity score
    similarity_score = calculate_similarity(doc1, doc2, chunks1, chunks2)
    
    return {
        "additions": additions[:10],  # Limit to 10
        "deletions": deletions[:10],
        "modifications": modifications[:10],
        "overall_summary": overall_comparison.content,
        "similarity_score": similarity_score,
        "doc1_length": len(doc1),
        "doc2_length": len(doc2),
        "total_changes": len(additions) + len(deletions) + len(modifications)
    }


def calculate_similarity(doc1: str, doc2: str, chunks1: List[str], chunks2: List[str]) -> float:
    """Calculate similarity score between documents."""
    # Simple word overlap similarity
    words1 = set(doc1.lower().split())
    words2 = set(doc2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

