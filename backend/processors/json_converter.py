"""JSON conversion with retry logic for missing fields."""
import json
import re
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage

try:
    from ..agent.llm import get_llm
except ImportError:
    from backend.agent.llm import get_llm


def convert_to_json(document: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Convert document to structured JSON with retry logic.
    
    Args:
        document: Document text
        max_retries: Maximum retry attempts
        
    Returns:
        Dictionary with JSON structure and metadata
    """
    llm = get_llm(temperature=0.1)
    
    document_preview = document[:4000] if len(document) > 4000 else document
    
    # Initial conversion prompt
    conversion_prompt = """Convert the following document into a structured JSON format.
Extract all key information and organize it into logical fields.

Document:
{document}

Provide a JSON object with relevant fields. Include:
- title (if available)
- author/creator (if available)
- date (if available)
- main_content
- key_points (array)
- metadata (any other relevant information)

Respond with ONLY valid JSON, no additional text."""
    
    result = None
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = llm.invoke([
                HumanMessage(content=conversion_prompt.format(document=document_preview))
            ])
            
            content = response.content.strip()
            
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            # Parse JSON
            result = json.loads(content)
            
            # Validate required fields
            required_fields = ["main_content"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if not missing_fields:
                break  # Success
            else:
                # Retry with focus on missing fields
                retry_prompt = """The previous JSON conversion was missing some fields: {missing}.
Please regenerate the JSON with ALL fields included.

Document:
{document}

Previous JSON:
{previous_json}

Provide complete JSON with all fields:"""
                
                conversion_prompt = retry_prompt.format(
                    missing=", ".join(missing_fields),
                    document=document_preview,
                    previous_json=json.dumps(result, indent=2)
                )
                
        except json.JSONDecodeError as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                # Try to fix JSON
                fix_prompt = """The following JSON is invalid. Fix it and provide valid JSON only.

Invalid JSON:
{invalid_json}

Error: {error}

Provide corrected JSON:"""
                
                conversion_prompt = fix_prompt.format(
                    invalid_json=content if 'content' in locals() else "",
                    error=str(e)
                )
            else:
                # Last attempt - create minimal valid JSON
                result = {
                    "main_content": document[:1000],
                    "error": "Failed to parse structured JSON",
                    "raw_text": document[:500]
                }
                break
        
        except Exception as e:
            last_error = str(e)
            if attempt == max_retries - 1:
                result = {
                    "main_content": document[:1000],
                    "error": f"Conversion failed: {str(e)}"
                }
                break
    
    if result is None:
        result = {
            "main_content": document[:1000],
            "error": "Failed to convert document to JSON"
        }
    
    return {
        "json": result,
        "json_string": json.dumps(result, indent=2),
        "fields_count": len(result),
        "retries_used": min(attempt + 1, max_retries) if 'attempt' in locals() else 1
    }

