import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.supervisor_agent import route_request
from rag.retriever import retrieve_context
from services.llm_service import generate_response
from api.upload import router as kb_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Enterprise AI Service Desk",
    description="AI-powered enterprise service desk backend using multi-agent architecture.",
    version="0.1.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all HTTP headers
)

app.include_router(kb_router)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Enterprise AI Service Desk API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        routing = route_request(request.message)
        intent = routing["intent"]

        if intent in {"HR_POLICY", "IT_SUPPORT", "COMPANY_POLICY"}:
            context = retrieve_context(request.message)
            ai_response = generate_response(request.message, context)
        else:
            ai_response = generate_response(request.message)

        return {
            "status": "success",
            "intent": intent,
            "assigned_agent": routing["assigned_agent"],
            "response": ai_response,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
