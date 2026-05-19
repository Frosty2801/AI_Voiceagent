from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Finance VoiceAgent"
    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    currency_api_base_url: str = "https://open.er-api.com/v6/latest"
    enable_coqui_tts: bool = True
    tts_fallback_enabled: bool = True
    audio_dir: str = "/tmp/voiceagent-audio"
    frontend_origin: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
