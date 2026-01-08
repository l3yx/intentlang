import os
from pathlib import Path

from .intent import Intent
from .models import IntentIO
from .engines import (
    LLMConfig,
    LLMEngineFactory,
)

_env_vars_to_check = ["OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL_NAME"]
if not any(os.getenv(v) for v in _env_vars_to_check):
    _dotenv_path = Path.cwd() / ".env"
    if _dotenv_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(_dotenv_path)
        except ImportError:
            pass


__all__ = [
    "Intent",
    "IntentIO",
    "LLMConfig", "LLMEngineFactory"
]
