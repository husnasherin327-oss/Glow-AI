import asyncio
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from models.schemas import ChatRequest, ChatResponse, SkinAnalysis, ProductCard
from graph.workflow import build_graph
from core.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])

_graph_cache: dict = {}


def get_graph(api_key: str):
    """
    Return a cached compiled graph for the given API key.
    Compiling once per key avoids rebuild overhead on every request.
    """
    if api_key not in _graph_cache:
        _graph_cache[api_key] = build_graph(api_key)
    return _graph_cache[api_key]


@router.post("/", response_model=ChatResponse, summary="Chat with GlowAI")
async def chat(request: ChatRequest):
    """
    Main chat endpoint powered by LangGraph.

    The pipeline automatically:
    1. Extracts skin entities via NLP (NER)
    2. Merges into running skin profile
    3. Routes to chat (ask more) OR search → recommend (if ready)
    4. Returns structured response
    """
    api_key = request.api_key or settings.HF_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is required. Pass 'api_key' in the request body or set HF_API_KEY in your .env file."
        )

    try:
        history = []
        for msg in request.conversation_history:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))

        history.append(HumanMessage(content=request.message))

        initial_state = {
            "messages": history,
            "skin_profile": request.skin_profile or {},
            "search_results": "",
            "products": [],
            "skin_analysis": None,
            "response_type": "chat",
            "final_message": "",
        }

        graph = get_graph(api_key)

        # BUG FIX #3: asyncio.get_event_loop() is deprecated in Python 3.10+
        # and raises a DeprecationWarning (error in 3.12) when called inside
        # a running async context.  Use get_running_loop() instead.
        # OLD: loop = asyncio.get_event_loop()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, graph.invoke, initial_state)

        response = ChatResponse(
            type=result.get("response_type", "chat"),
            message=result.get("final_message", ""),
            skin_profile=result.get("skin_profile", {}),
        )

        if result.get("skin_analysis") and isinstance(result["skin_analysis"], dict):
            try:
                response.skin_analysis = SkinAnalysis(**result["skin_analysis"])
            except Exception:
                pass

        raw_products = result.get("products", [])
        if raw_products and isinstance(raw_products, list):
            print(f"DEBUG: Found {len(raw_products)} products to attach")
            parsed = []
            for p in raw_products:
                if isinstance(p, dict):
                    try:
                        parsed.append(ProductCard(**p))
                    except Exception as e:
                        print(f"DEBUG: ProductCard parsing error: {e}")
            if parsed:
                response.products = parsed

        print(f"DEBUG: Final response type={response.type}, message_len={len(response.message)}")
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
