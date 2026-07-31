import json
import re

from google import genai
from google.genai import types
from langchain_core.messages import HumanMessage, AIMessage
from duckduckgo_search import DDGS

from core.config import settings
from graph.state import SkincareState




def make_model(api_key: str, temperature: float = 0.7):
    """Configure Gemini and return a GenerativeModel instance."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )
    )


def call_llm(api_key: str, system: str, user: str, temperature: float = 0.7) -> str:
    print("MODEL =", settings.GEMINI_MODEL, flush=True)

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=2048,
        ),
    )

    return response.text.strip()




def parse_json(text: str) -> dict:
    """Robust JSON parser — strips markdown fences, finds first {...} block."""
    text = text.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group()
        candidate = re.sub(r",\s*\}", "}", candidate)
        candidate = re.sub(r",\s*\]", "]", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    print(f"FAILED TO PARSE JSON: {text[:200]}...")
    return {}


def merge_profile(existing: dict, new_data: dict) -> dict:
    """Merge extracted entities into running skin profile (set union for lists)."""
    updated = dict(existing)
    if new_data.get("skin_type"):
        updated["skin_type"] = new_data["skin_type"]
    if new_data.get("budget"):
        updated["budget"] = new_data["budget"]
    for field in ["conditions", "problem_areas", "sensitivities", "concerns"]:
        new_vals = new_data.get(field) or []
        if new_vals:
            existing_set = set(updated.get(field, []))
            updated[field] = list(existing_set | set(new_vals))
    return updated


def profile_ready(profile: dict) -> bool:
    """True when skin_type + at least one concern/condition is present."""
    has_type = bool(profile.get("skin_type"))
    has_concern = bool(
        profile.get("conditions") or
        profile.get("concerns") or
        profile.get("problem_areas")
    )
    return has_type and has_concern


def get_last_human_message(messages: list) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def build_history_text(messages: list) -> str:
    lines = []
    for msg in messages[:-1]:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)




def extract_entities_node(state: SkincareState, api_key: str) -> SkincareState:
    print("--- NODE: extract_entities ---")
    last_message = get_last_human_message(state["messages"])

    system = """You are a skincare NLP extractor.
Return ONLY valid JSON — no markdown, no extra text, no explanation:
{
  "skin_type": "dry" or "oily" or "combination" or "normal" or "sensitive" or null,
  "conditions": [],
  "problem_areas": [],
  "sensitivities": [],
  "budget": "drugstore" or "mid-range" or "luxury" or null,
  "concerns": []
}"""

    try:
        result = call_llm(api_key, system, last_message, temperature=0.1)
        print(f"Extraction result: {result}")
        extracted = parse_json(result)
    except Exception as e:
        print(f"Extraction error: {e}")
        extracted = {}

    updated_profile = merge_profile(state.get("skin_profile", {}), extracted)
    print(f"Updated profile: {updated_profile}")
    return {**state, "skin_profile": updated_profile}




def chat_node(state: SkincareState, api_key: str) -> SkincareState:
    print("--- NODE: chat ---")
    last_message = get_last_human_message(state["messages"])
    history_text = build_history_text(state["messages"])
    profile_str = json.dumps(state.get("skin_profile", {}), indent=2)

    system = f"""You are GlowAI ✨, a warm and knowledgeable skincare expert.
Current skin profile collected so far: {profile_str}

Rules:
- Ask ONE short follow-up question to gather the most important missing info.
- Priority order: skin type → conditions → concerns → budget.
- Be concise, warm, and encouraging.
- Do NOT recommend products yet."""

    user = f"{history_text}\nUser: {last_message}" if history_text else last_message

    try:
        reply = call_llm(api_key, system, user, temperature=0.7)
    except Exception as e:
        reply = f"I'm having a little trouble right now. Could you try again? Error: {str(e)}"

    return {**state, "response_type": "chat", "final_message": reply}




def search_node(state: SkincareState) -> SkincareState:
    print("--- NODE: search ---")
    profile = state.get("skin_profile", {})
    skin_type = profile.get("skin_type", "")
    conditions = ", ".join(profile.get("conditions", []))
    concerns = ", ".join(profile.get("concerns", []))

    queries = [
        f"best cleanser for {skin_type} skin {conditions} dermatologist recommended 2024",
        f"best moisturizer {skin_type} skin {concerns} top reviews",
    ]

    all_results = []
    ddgs = DDGS()
    for query in queries:
        try:
            results = ddgs.text(query, max_results=5)
            if results:
                snippets = [f"- {r.get('title','')}: {r.get('body','')}" for r in results]
                all_results.append(f"Query: {query}\n" + "\n".join(snippets))
        except Exception as e:
            print(f"Search error: {e}")

    combined = "\n\n".join(all_results)
    print(f"Search context length: {len(combined)}")
    return {**state, "search_results": combined[:5000]}




def recommend_node(state: SkincareState, api_key: str) -> SkincareState:
    print("--- NODE: recommend ---")

    search_context = state.get("search_results", "").strip()
    fallback_note = ""
    if not search_context or len(search_context) < 100:
        fallback_note = "No web results found — use your expert skincare knowledge."

    system = """You are a skincare product recommendation engine.
Return ONLY valid JSON — no markdown, no extra text whatsoever:
{
  "message": "warm intro sentence",
  "skin_analysis": {
    "profile_summary": "brief summary of their skin situation",
    "good_ingredients": ["niacinamide", "hyaluronic acid"],
    "avoid_ingredients": ["alcohol", "fragrance"]
  },
  "products": [
    {
      "name": "Product Name",
      "brand": "Brand",
      "category": "cleanser",
      "price_range": "$10-$20",
      "merits": ["benefit 1", "benefit 2"],
      "demerits": ["downside 1"],
      "buy_links": [{"store": "Amazon", "url": "https://amazon.com/s?k=product+name"}]
    }
  ]
}
Always recommend exactly 3 real products."""

    user = f"""Skin profile:
{json.dumps(state.get("skin_profile", {}), indent=2)}

Search context:
{search_context or "None available."}
{fallback_note}

Recommend 3 products for this skin profile."""

    try:
        result = call_llm(api_key, system, user, temperature=0.4)
        print(f"Recommendation raw: {result[:300]}...")
        parsed = parse_json(result)
    except Exception as e:
        print(f"Recommendation error: {e}")
        parsed = {
            "message": f"Error generating recommendations: {str(e)}",
            "products": [],
            "skin_analysis": None,
        }

    return {
        **state,
        "response_type": "products",
        "final_message": parsed.get("message", "Here are your personalized recommendations!"),
        "products": parsed.get("products", []),
        "skin_analysis": parsed.get("skin_analysis"),
    }




def route_after_extraction(state: SkincareState) -> str:
    if profile_ready(state.get("skin_profile", {})):
        return "search"
    return "chat"
