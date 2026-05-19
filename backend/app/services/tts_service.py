import re
from pathlib import Path
from uuid import uuid4

from app.core.settings import Settings


class TTSService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.audio_dir = Path(settings.audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self._model = None

    def synthesize(self, text: str) -> tuple[str | None, bool]:
        if not self.settings.enable_coqui_tts:
            return None, True

        try:
            model = self._get_model()
            filename = f"{uuid4().hex}.wav"
            output_path = self.audio_dir / filename
            clean_text = self._prepare_text(text)
            model.tts_to_file(text=clean_text, file_path=str(output_path))
            return f"/audio/{filename}", False
        except Exception:
            return None, self.settings.tts_fallback_enabled

    def _get_model(self):
        if self._model is None:
            from TTS.api import TTS

            self._model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        return self._model

    @staticmethod
    def _prepare_text(text: str) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        return clean[:800]
