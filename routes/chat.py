import asyncio
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from models.schemas import ChatRequest, ChatResponse, SkinAnalysis, ProductCard
from graph.workflow import build_graph
from core.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])

_graph_cache: dict = {}


def get_graph(api_key: str):
    if api_key not in _graph_cache:
        _graph_cache[api_key] = build_graph(api_key)
    return _graph_cache[api_key]


@router.post("/", response_model=ChatResponse, summary="Chat with GlowAI")
async def chat(request: ChatRequest):
    # Use Gemini API key from request or fallback to config
    api_key = request.api_key or settings.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is required. Set GEMINI_API_KEY in config.py or pass 'api_key' in the request."
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
            parsed = []
            for p in raw_products:
                if isinstance(p, dict):
                    try:
                        parsed.append(ProductCard(**p))
                    except Exception as e:
                        print(f"ProductCard parse error: {e}")
            if parsed:
                response.products = parsed

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
