from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class SkincareState(TypedDict):
    """
    Shared state flowing through every node in the LangGraph pipeline.

    messages        — Full conversation history. add_messages reducer
                      APPENDS new messages instead of replacing the list.
    skin_profile    — Accumulated entities: skin_type, conditions, areas, etc.
    search_results  — Raw DuckDuckGo web search results (RAG context)
    products        — Parsed product recommendation dicts
    skin_analysis   — Skin profile summary + ingredient guidance
    response_type   — "chat" | "products" | "error"
    final_message   — Last assistant message to return to the user
    """
    messages: Annotated[list, add_messages]
    skin_profile: Dict[str, Any]
    search_results: str
    products: List[Dict]
    skin_analysis: Optional[Dict]
    response_type: str
    final_message: str
