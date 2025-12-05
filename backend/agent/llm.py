"""LLM setup with Groq."""
import os
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to current directory
    load_dotenv()


def get_llm(temperature: float = 0.1, model: str = "llama-3.1-8b-instant") -> ChatGroq:
    """
    Initialize Groq LLM.
    
    Args:
        temperature: Sampling temperature
        model: Model name
        
    Returns:
        ChatGroq instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model,
        temperature=temperature,
    )


def create_prompt_template(template: str) -> ChatPromptTemplate:
    """Create a prompt template."""
    return ChatPromptTemplate.from_template(template)

