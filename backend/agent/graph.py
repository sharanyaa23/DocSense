"""LangGraph workflow definitions."""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from agent.llm import get_llm


class GraphState(TypedDict):
    """State for LangGraph workflows."""
    messages: Annotated[list, lambda x, y: x + y]
    document: str
    result: str
    iteration: int
    max_iterations: int
    validated: bool


def create_validation_graph(validation_prompt: str, max_iterations: int = 3):
    """
    Create a LangGraph workflow for validation with retry logic.
    
    Args:
        validation_prompt: Prompt template for validation
        max_iterations: Maximum retry iterations
        
    Returns:
        Compiled LangGraph
    """
    llm = get_llm()
    
    def process_node(state: GraphState) -> GraphState:
        """Process the document."""
        messages = [
            HumanMessage(content=validation_prompt.format(document=state["document"]))
        ]
        response = llm.invoke(messages)
        return {
            "messages": [response],
            "result": response.content,
            "iteration": state.get("iteration", 0) + 1,
        }
    
    def should_continue(state: GraphState) -> Literal["validate", "end"]:
        """Decide whether to continue or end."""
        if state.get("validated", False) or state.get("iteration", 0) >= max_iterations:
            return "end"
        # Simple validation: check if result is not empty
        if state.get("result") and len(state.get("result", "").strip()) > 50:
            return "end"
        return "validate"
    
    def validate_node(state: GraphState) -> GraphState:
        """Validate and mark as validated if good."""
        if state.get("result") and len(state.get("result", "").strip()) > 50:
            return {"validated": True}
        return {"validated": False}
    
    workflow = StateGraph(GraphState)
    workflow.add_node("process", process_node)
    workflow.add_node("validate", validate_node)
    workflow.set_entry_point("process")
    workflow.add_conditional_edges("process", should_continue)
    workflow.add_edge("validate", "process")
    workflow.add_edge("end", END)
    
    return workflow.compile()

