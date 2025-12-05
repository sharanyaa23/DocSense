"""Document classification with LangGraph decision loop."""
from typing import Dict, Any
from langchain_core.messages import HumanMessage

try:
    from ..agent.llm import get_llm
    from ..utils.cleaner import strip_markdown
except ImportError:
    from backend.agent.llm import get_llm
    from backend.utils.cleaner import strip_markdown


def classify_document(document: str) -> Dict[str, Any]:
    """
    Classify document type with re-evaluation for unclear cases.
    
    Args:
        document: Document text
        
    Returns:
        Dictionary with classification and confidence
    """
    llm = get_llm(temperature=0.1)
    
    document_preview = document[:3000] if len(document) > 3000 else document
    
    # Initial classification
    classification_prompt = """Classify the following document into one of these categories:
- resume
- invoice
- contract
- research_paper
- report
- letter
- other

Important distinctions:
- research_paper: Academic papers with abstract, methodology, results, references/citations, data analysis, research contribution
- report: Business reports, project reports, progress reports, or general informational reports (usually no academic structure)

Document:
{document}

Respond with ONLY the category name and a confidence level (high/medium/low)."""
    
    initial_response = llm.invoke([
        HumanMessage(content=classification_prompt.format(document=document_preview))
    ])
    
    initial_classification = initial_response.content.lower()
    
    # Extract category and confidence
    category = None
    confidence = "medium"
    
    categories = ["resume", "invoice", "contract", "research_paper", "report", "letter", "other"]
    # Check for research paper variations
    if "research paper" in initial_classification or "research_paper" in initial_classification:
        category = "research_paper"
    else:
        for cat in categories:
            if cat in initial_classification:
                category = cat
                break
    
    if not category:
        category = "other"
    
    if "high" in initial_classification:
        confidence = "high"
    elif "low" in initial_classification:
        confidence = "low"
    
    # Re-evaluation for unclear cases (low/medium confidence)
    if confidence in ["low", "medium"]:
        reevaluation_prompt = """Re-evaluate the document classification. The initial classification had {confidence} confidence.
Analyze the document more carefully and provide a definitive classification.

Important: Distinguish between research_paper and report:
- research_paper: Has abstract, methodology, results, references/citations, academic structure, research contribution
- report: Business or informational document without academic research structure

Document:
{document}

Initial Classification: {initial_class}

Provide:
1. Final category (resume/invoice/contract/research_paper/report/letter/other)
2. Confidence (high/medium/low)
3. Reasoning (1-2 sentences)"""
        
        reevaluation = llm.invoke([
            HumanMessage(content=reevaluation_prompt.format(
                document=document_preview,
                initial_class=category,
                confidence=confidence
            ))
        ])
        
        reeval_content = reevaluation.content.lower()
        
        # Update category if found
        # Check for research paper variations first
        if "research paper" in reeval_content or "research_paper" in reeval_content:
            category = "research_paper"
        else:
            for cat in categories:
                if cat in reeval_content:
                    category = cat
                    break
        
        # Update confidence
        if "high" in reeval_content:
            confidence = "high"
        elif "low" in reeval_content:
            confidence = "low"
    
    # Extract key indicators
    indicators_prompt = """List 2-3 key indicators that support the classification of this document as "{category}".

Document:
{document_preview}

Provide brief indicators:"""
    
    indicators_response = llm.invoke([
        HumanMessage(content=indicators_prompt.format(
            category=category,
            document_preview=document_preview[:2000]
        ))
    ])
    
    # Strip markdown from indicators
    indicators = strip_markdown(indicators_response.content)
    
    return {
        "category": category,
        "confidence": confidence,
        "indicators": indicators,
        "document_length": len(document)
    }

