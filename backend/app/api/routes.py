import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.settings import get_settings
from app.schemas import ChatRequest, ChatResponse
from app.services.finance_agent import FinanceAgent
from app.services.tts_service import TTSService

router = APIRouter()
settings = get_settings()
agent = FinanceAgent(settings)
tts_service = TTSService(settings)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = await agent.handle_message(req.session_id, req.message)
        audio_url = None
        tts_failed = False

        if req.mode == "voice":
            audio_url, tts_failed = tts_service.synthesize(result["reply"])

        return ChatResponse(
            reply=result["reply"],
            used_tool=result["used_tool"],
            tool_name=result["tool_name"],
            mode=req.mode,
            audio_url=audio_url,
            tts_failed=tts_failed,
            meta=result["meta"],
        )
    except Exception as exc:
        logging.exception("Unhandled error in /chat")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    audio_path = Path(settings.audio_dir) / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    media_type = "audio/mpeg" if audio_path.suffix == ".mp3" else "audio/wav"
    return FileResponse(audio_path, media_type=media_type, filename=filename)


@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
