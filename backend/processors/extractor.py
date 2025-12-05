"""Information extraction with validation and pattern matching."""
import re
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage

from agent.llm import get_llm


def extract_information(document: str, extraction_type: str = "all") -> Dict[str, Any]:
    """
    Extract structured information from document with validation.
    
    Args:
        document: Document text
        extraction_type: Type of extraction (emails, names, dates, totals, keywords, all)
        
    Returns:
        Dictionary with extracted information
    """
    llm = get_llm(temperature=0.1)
    
    # Pattern-based extraction
    patterns = {
        "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "dates": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
        "phone_numbers": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\(\d{3}\)\s?\d{3}[-.]?\d{4}',
        "amounts": r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
    }
    
    extracted = {}
    
    # Extract using regex patterns
    if extraction_type in ["emails", "all"]:
        emails = list(set(re.findall(patterns["emails"], document)))
        extracted["emails"] = emails
    
    if extraction_type in ["dates", "all"]:
        dates = list(set(re.findall(patterns["dates"], document)))
        extracted["dates"] = dates
    
    if extraction_type in ["totals", "all"]:
        amounts = re.findall(patterns["amounts"], document)
        extracted["amounts"] = amounts[:20]  # Limit to 20
    
    if extraction_type in ["phone_numbers", "all"]:
        phones = list(set(re.findall(patterns["phone_numbers"], document)))
        extracted["phone_numbers"] = phones
    
    # LLM-based extraction for names and keywords
    if extraction_type in ["names", "keywords", "all"]:
        extraction_prompt = """Extract the following information from the document:
1. Person names (full names of people mentioned)
2. Key keywords/phrases (important terms, concepts, or topics)

Document:
{document}

Provide a JSON-like structure with:
- names: list of person names
- keywords: list of important keywords/phrases

Format your response clearly."""
        
        response = llm.invoke([
            HumanMessage(content=extraction_prompt.format(document=document[:4000]))
        ])
        
        # Parse response (simple extraction)
        content = response.content
        if "names" in extraction_type or extraction_type == "all":
            # Extract names from response
            name_pattern = r'(?:name[s]?|person[s]?)[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
            names = re.findall(name_pattern, content, re.IGNORECASE)
            if not names:
                # Try to find capitalized words that look like names
                potential_names = re.findall(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', content)
                names = potential_names[:10]
            extracted["names"] = list(set(names))
        
        if "keywords" in extraction_type or extraction_type == "all":
            # Extract keywords
            keyword_section = re.search(r'keyword[s]?[:\-]?\s*(.+?)(?:\n\n|\Z)', content, re.IGNORECASE | re.DOTALL)
            if keyword_section:
                keywords = [k.strip() for k in keyword_section.group(1).split(',') if k.strip()]
                extracted["keywords"] = keywords[:20]
    
    # Validation step: Remove false positives using LLM
    if extracted:
        validation_prompt = """Review the following extracted information and remove any false positives or invalid entries.
Keep only valid, relevant information.

Extracted Data:
{extracted}

Document Context (first 2000 chars):
{document_preview}

Provide cleaned, validated information in the same format."""
        
        extracted_str = "\n".join([f"{k}: {v}" for k, v in extracted.items()])
        validation_response = llm.invoke([
            HumanMessage(content=validation_prompt.format(
                extracted=extracted_str,
                document_preview=document[:2000]
            ))
        ])
        
        # Re-parse validated results (simplified - in production, use proper JSON parsing)
        validated_content = validation_response.content
        for key in extracted.keys():
            # Try to find the key in validated content
            pattern = rf'{key}[:\-]?\s*\[?([^\]]+)\]?'
            match = re.search(pattern, validated_content, re.IGNORECASE)
            if match:
                # Extract values
                values_str = match.group(1)
                values = [v.strip().strip('"\'') for v in values_str.split(',')]
                extracted[key] = [v for v in values if v][:20]
    
    return {
        "extracted": extracted,
        "extraction_type": extraction_type,
        "total_items": sum(len(v) if isinstance(v, list) else 1 for v in extracted.values())
    }

