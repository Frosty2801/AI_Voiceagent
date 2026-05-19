import logging
import subprocess
import wave
from pathlib import Path
from uuid import uuid4

from app.core.settings import Settings
from app.services.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


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
            audio_id = uuid4().hex
            wav_path = self.audio_dir / f"{audio_id}.wav"
            mp3_path = self.audio_dir / f"{audio_id}.mp3"
            clean_text = self._prepare_text(text)
            model.tts_to_file(text=clean_text, file_path=str(wav_path))
            if not self._has_audible_signal(wav_path):
                logger.warning("Coqui generated an invalid or silent audio file: %s", wav_path)
                wav_path.unlink(missing_ok=True)
                return None, self.settings.tts_fallback_enabled

            if self._convert_to_mp3(wav_path, mp3_path):
                wav_path.unlink(missing_ok=True)
                return f"/audio/{mp3_path.name}", False

            return f"/audio/{wav_path.name}", False
        except Exception:
            logger.exception("Coqui TTS failed; browser fallback will be used when enabled.")
            return None, self.settings.tts_fallback_enabled

    def _get_model(self):
        if self._model is None:
            from TTS.api import TTS

            logger.info("Loading Coqui TTS model: %s", self.settings.coqui_tts_model)
            self._model = TTS(model_name=self.settings.coqui_tts_model, progress_bar=False)
        return self._model

    @staticmethod
    def _prepare_text(text: str) -> str:
        return ResponseFormatter.for_speech(text, max_length=500)

    @staticmethod
    def _convert_to_mp3(source: Path, target: Path) -> bool:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-af",
            "loudnorm",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(target),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        except Exception:
            logger.exception("Could not convert TTS WAV to MP3; serving WAV instead.")
            return False

        return target.exists() and target.stat().st_size > 1024

    @staticmethod
    def _has_audible_signal(path: Path) -> bool:
        if not path.exists() or path.stat().st_size < 1024:
            return False

        try:
            with wave.open(str(path), "rb") as wav_file:
                frame_count = wav_file.getnframes()
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                if frame_count == 0 or sample_width not in {1, 2, 4}:
                    return False

                raw = wav_file.readframes(frame_count)
        except wave.Error:
            return path.stat().st_size > 4096

        if not raw:
            return False

        peak = 0
        step = sample_width
        for index in range(0, len(raw) - step + 1, step):
            sample = int.from_bytes(raw[index : index + step], byteorder="little", signed=True)
            peak = max(peak, abs(sample))

        max_peak = float(2 ** (8 * sample_width - 1))
        normalized_peak = peak / max_peak
        return channels > 0 and normalized_peak > 0.002
