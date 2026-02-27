"""Local ternary model provider for zero-cost on-device inference.

Loads a ternary-quantized LLM from disk and runs inference locally
via PyTorch. Implements the same BaseProvider interface as cloud
providers (OpenAI, Google, Anthropic), enabling seamless swapping.

The model is loaded lazily on first call and cached in memory.
"""

import json
import logging
import time
from typing import Optional

from backend.providers.base import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)

# Global model cache (loaded once, reused across requests)
_model_cache: dict = {}


def _get_or_load_model(model_path: str):
    """Load and cache the ternary model + tokenizer."""
    if model_path in _model_cache:
        return _model_cache[model_path]

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    logger.info(f"Loading local ternary model from {model_path}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load the fine-tuned model
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float32
    )
    model.eval()

    # Try to apply ternary quantization if not already applied
    try:
        import sys
        from pathlib import Path
        # Add Ternary-SD to path if available
        ternary_sd_path = Path(__file__).resolve().parent.parent.parent / "Ternary-SD"
        if ternary_sd_path.exists():
            sys.path.insert(0, str(ternary_sd_path))
        from models.ternary_llm import convert_llm_to_ternary
        model = convert_llm_to_ternary(model)
        logger.info("Applied ternary quantization to local model")
    except ImportError:
        logger.info("Ternary-SD not found, using model as-is")

    elapsed = time.time() - t0
    param_count = sum(p.numel() for p in model.parameters())
    logger.info(
        f"Local model loaded in {elapsed:.1f}s "
        f"({param_count:,} params)"
    )

    _model_cache[model_path] = (model, tokenizer)
    return model, tokenizer


class LocalTernaryProvider(BaseProvider):
    """Provider that runs a ternary-quantized LLM locally."""

    def __init__(self, model_path: str):
        super().__init__(name="local-ternary")
        self.model_path = model_path

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        system_prompt: Optional[str] = None,
    ) -> ProviderResponse:
        import torch

        t0 = time.time()
        model_obj, tokenizer = _get_or_load_model(self.model_path)

        # Build prompt from messages
        parts = []
        if system_prompt:
            parts.append(f"<|system|>\n{system_prompt}")
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"<|{role}|>\n{content}")
        parts.append("<|assistant|>\n")
        prompt = "\n".join(parts)

        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        input_len = inputs["input_ids"].shape[1]

        # Generate
        with torch.no_grad():
            outputs = model_obj.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=max(temperature, 0.01),
                do_sample=temperature > 0,
                pad_token_id=tokenizer.pad_token_id,
            )

        # Decode only the new tokens
        new_tokens = outputs[0][input_len:]
        response_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        output_len = len(new_tokens)

        latency = (time.time() - t0) * 1000

        return ProviderResponse(
            content=response_text,
            model=f"local-ternary:{model}",
            input_tokens=input_len,
            output_tokens=output_len,
            latency_ms=latency,
            cost_usd=0.0,  # Zero cost — local inference
        )
