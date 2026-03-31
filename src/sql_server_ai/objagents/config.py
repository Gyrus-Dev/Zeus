import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Provider selection ────────────────────────────────────────────────────────
# Set MODEL_PROVIDER to "google" (default), "anthropic", or "openai"
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "google").lower()
IS_GOOGLE_MODEL = MODEL_PROVIDER == "google"
USE_SKILLS = os.environ.get("USE_SKILLS", "true").lower() != "false"

# ── Model resolution ──────────────────────────────────────────────────────────
if MODEL_PROVIDER == "anthropic":
    from google.adk.models.lite_llm import LiteLlm

    _primary = os.environ.get("MODEL_PRIMARY", "anthropic/claude-3-5-haiku-20241022")
    _thinking = os.environ.get("MODEL_THINKING", "anthropic/claude-3-5-sonnet-20241022")

    PRIMARY_MODEL = LiteLlm(model=_primary)
    THINKING_MODEL = LiteLlm(model=_thinking)

elif MODEL_PROVIDER == "openai":
    from google.adk.models.lite_llm import LiteLlm

    _primary = os.environ.get("MODEL_PRIMARY", "openai/gpt-4o-mini")
    _thinking = os.environ.get("MODEL_THINKING", "openai/gpt-4o")

    PRIMARY_MODEL = LiteLlm(model=_primary)
    THINKING_MODEL = LiteLlm(model=_thinking)

else:  # google (default)
    PRIMARY_MODEL = os.environ.get("PRIMARY_MODEL", "gemini-2.5-flash")
    THINKING_MODEL = os.environ.get("THINKING_MODEL", "gemini-2.5-pro")

_primary_label = getattr(PRIMARY_MODEL, "model", PRIMARY_MODEL)
_thinking_label = getattr(THINKING_MODEL, "model", THINKING_MODEL)
logger.info("Model provider: %s | primary: %s | thinking: %s", MODEL_PROVIDER, _primary_label, _thinking_label)
print(f"[config] provider={MODEL_PROVIDER}  primary={_primary_label}  thinking={_thinking_label}")


# ── Planner factory ───────────────────────────────────────────────────────────
def get_planner(thinking_budget: int = 512) -> Optional[object]:
    """Returns a BuiltInPlanner for Google models, None for all other providers.

    BuiltInPlanner / ThinkingConfig are Gemini-specific features and are not
    supported by Anthropic or OpenAI models via LiteLLM.
    """
    if not IS_GOOGLE_MODEL:
        return None
    from google.adk.planners import BuiltInPlanner
    from google.genai import types

    return BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=thinking_budget,
        )
    )
