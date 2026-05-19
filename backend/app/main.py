from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from .agent import Agent

app = FastAPI(title="VoiceAgent Backend - Stub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str = "text"  # or "voice"


class ChatResponse(BaseModel):
    reply: str
    used_tool: bool = False
    tool_name: str | None = None
    meta: Dict[str, Any] = {}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        reply, used_tool, tool_name = await agent.handle_message(
            req.session_id, req.message
        )
        return ChatResponse(reply=reply, used_tool=used_tool, tool_name=tool_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
