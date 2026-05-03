from functools import partial


from langgraph.graph import StateGraph, START, END


from graph.state import SkincareState
from graph.nodes import (
    extract_entities_node,
    chat_node,
    search_node,
    recommend_node,
    route_after_extraction,
)


def build_graph(api_key: str):
    """
    Compile and return the GlowAI LangGraph pipeline.

    Graph topology:
    ┌─────────────────────────────────────────────────────┐
    │  START                                              │
    │    │                                                │
    │    ▼                                                │
    │  extract  ← NLP entity extraction (NER)             │
    │    │                                                │
    │    ▼  conditional edge                              │
    │  ┌─┴──────────────┐                                 │
    │  │                │                                 │
    │  ▼                ▼                                 │
    │ chat           search  ← RAG / DuckDuckGo           │
    │ (ask more)       │                                  │
    │  │               ▼                                  │
    │  │           recommend  ← Synthesize + format       │
    │  │               │                                  │
    │  └──────┬────────┘                                  │
    │         ▼                                           │
    │        END                                          │
    └─────────────────────────────────────────────────────┘
    """
    extract = partial(extract_entities_node, api_key=api_key)
    chat = partial(chat_node, api_key=api_key)
    recommend = partial(recommend_node, api_key=api_key)

    builder = StateGraph(SkincareState)

    # Register nodes
    builder.add_node("extract", extract)
    builder.add_node("chat", chat)
    builder.add_node("search", search_node)
    builder.add_node("recommend", recommend)

   
    builder.add_edge(START, "extract")

    # Conditional routing after extraction
    builder.add_conditional_edges(
        "extract",
        route_after_extraction,
        {
            "chat": "chat",
            "search": "search",
        }
    )

    # Fixed edges
    builder.add_edge("chat", END)
    builder.add_edge("search", "recommend")
    builder.add_edge("recommend", END)

    return builder.compile()
