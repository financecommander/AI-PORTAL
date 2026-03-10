"""Provider fallback utility — try Ollama first, fall back to cloud provider.

Enables zero-downtime model swaps: if the GPU VM running Ollama is
unreachable, pipelines gracefully degrade to cloud providers without
breaking or slowing down.
"""

import logging
from typing import Optional

from backend.providers.base import BaseProvider
from backend.providers.factory import get_provider

logger = logging.getLogger(__name__)

# Cache Ollama health status for a short period to avoid
# hammering the health endpoint on every pipeline call.
_ollama_healthy: Optional[bool] = None
_ollama_checked_at: float = 0.0
_HEALTH_CACHE_SECONDS = 30.0


async def get_provider_with_fallback(
    primary: str = "ollama",
    fallback: str = "google",
    primary_model: str = "deepseek-r1:14b",
    fallback_model: str = "gemini-2.5-flash",
) -> tuple[Optional[BaseProvider], str]:
    """Try the primary provider (Ollama) first; fall back if unreachable.

    If ``fallback_model`` is set to the sentinel ``"__skip__"``, the
    function returns ``(None, "__skip__")`` instead of instantiating a
    cloud provider — callers can check for this to skip the operation.

    Returns:
        Tuple of (provider_instance, model_id) ready for use.
    """
    import time

    global _ollama_healthy, _ollama_checked_at

    def _fallback():
        if fallback_model == "__skip__":
            return None, "__skip__"
        return get_provider(fallback), fallback_model

    now = time.monotonic()
    cache_expired = (now - _ollama_checked_at) > _HEALTH_CACHE_SECONDS

    if cache_expired:
        try:
            provider = get_provider(primary)
            healthy = await provider.is_healthy()
            _ollama_healthy = healthy
            _ollama_checked_at = now

            if healthy:
                logger.debug("Ollama is healthy — using %s/%s", primary, primary_model)
                return provider, primary_model
            else:
                logger.warning(
                    "Ollama health check failed — falling back to %s/%s",
                    fallback, fallback_model,
                )
                return _fallback()
        except Exception as e:
            logger.warning(
                "Ollama provider unavailable (%s) — falling back to %s/%s",
                e, fallback, fallback_model,
            )
            _ollama_healthy = False
            _ollama_checked_at = now
            return _fallback()
    else:
        # Use cached health status
        if _ollama_healthy:
            return get_provider(primary), primary_model
        else:
            return _fallback()
