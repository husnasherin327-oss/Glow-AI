# 🌿 GlowAI — AI Skincare Consultant

An AI-powered skincare chatbot built with **FastAPI + LangGraph + Google Gemini + Streamlit**.

## Tech Stack
- **Backend:** FastAPI, LangGraph, LangChain
- **LLM:** Google Gemini 1.5 Flash
- **RAG:** DuckDuckGo Search
- **Frontend:** Streamlit

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Add your Gemini API key in `core/config.py`
5. Run: `streamlit run streamlit_app.py`