"""Local ternary model provider for zero-cost on-device inference.

Loads a Triton-trained TernaryCreditRiskNet from disk and runs
classification locally. Implements the same BaseProvider interface
as cloud providers (OpenAI, Google, Anthropic), enabling seamless
swapping in the Lead Ranking Pipeline.

The model is loaded lazily on first call and cached in memory.
All inference is zero-cost (no API calls).

Two model backends are supported:
  1. Triton TernaryCreditRiskNet (lightweight classifier, preferred)
  2. HuggingFace generative LLM with ternary quantization (fallback)
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from backend.providers.base import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)

# Global model cache (loaded once, reused across requests)
_model_cache: dict = {}


def _find_triton_path() -> Optional[Path]:
    """Locate the Triton repo (env var first, then relative paths)."""
    candidates = [
        # Explicit env var (Docker / production)
        Path(os.getenv("TRITON_PATH", "")) if os.getenv("TRITON_PATH") else None,
        # Relative to AI Portal (local dev)
        Path(__file__).resolve().parent.parent.parent / "Triton",
        Path(__file__).resolve().parent.parent.parent.parent / "Triton",
    ]
    for p in candidates:
        if p and p.exists() and (p / "backend" / "pytorch" / "ternary_tensor.py").exists():
            return p
    return None


def _load_triton_model(checkpoint_path: str, tokenizer_path: str):
    """Load Triton TernaryCreditRiskNet + tokenizer."""
    import torch

    triton_path = _find_triton_path()
    if triton_path is None:
        raise ImportError("Triton repo not found. Set TRITON_PATH env var.")

    # Add Triton to Python path
    sys.path.insert(0, str(triton_path))

    from models.credit_risk.ternary_credit_risk import (
        TernaryCreditRiskNet,
        CreditRiskTokenizer,
    )

    logger.info(f"Loading Triton credit risk model from {checkpoint_path}...")
    t0 = time.time()

    # Load tokenizer
    tokenizer = CreditRiskTokenizer.load(tokenizer_path)

    # Load checkpoint
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(checkpoint_path, map_location=device)
    vocab_size = ckpt.get("vocab_size", tokenizer.vocab_size)

    # Build model
    model = TernaryCreditRiskNet(vocab_size=vocab_size)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    elapsed = time.time() - t0
    param_count = sum(p.numel() for p in model.parameters())
    ternary_count = sum(
        p.numel() for n, p in model.named_parameters()
        if "fc" in n and "weight" in n
    )
    logger.info(
        f"Triton model loaded in {elapsed:.1f}s "
        f"({param_count:,} params, {ternary_count:,} ternary, "
        f"~{ternary_count * 2.5 / 8 / 1024:.1f} KB ternary size)"
    )

    return model, tokenizer, device


def _get_or_load_model(model_path: str):
    """Load and cache the ternary model + tokenizer.

    Tries Triton classifier first, falls back to HuggingFace LLM.
    """
    if model_path in _model_cache:
        return _model_cache[model_path]

    path = Path(model_path)

    # Strategy 1: Triton checkpoint (preferred)
    checkpoint_file = None
    tokenizer_file = None

    # Check for Triton-style checkpoint
    if path.is_dir():
        for name in ["credit_risk_best.pth", "credit_risk_latest.pth"]:
            if (path / name).exists():
                checkpoint_file = str(path / name)
                break
        if (path / "tokenizer.json").exists():
            tokenizer_file = str(path / "tokenizer.json")
    elif path.suffix == ".pth" and path.exists():
        checkpoint_file = str(path)
        tokenizer_file = str(path.parent / "tokenizer.json")

    if checkpoint_file and tokenizer_file and Path(tokenizer_file).exists():
        try:
            model, tokenizer, device = _load_triton_model(
                checkpoint_file, tokenizer_file
            )
            _model_cache[model_path] = {
                "type": "triton",
                "model": model,
                "tokenizer": tokenizer,
                "device": device,
            }
            return _model_cache[model_path]
        except Exception as e:
            logger.warning(f"Failed to load Triton model: {e}")

    # Strategy 2: HuggingFace generative LLM (fallback)
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(f"Loading HuggingFace model from {model_path}...")
        t0 = time.time()

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=torch.float32
        )
        model.eval()

        elapsed = time.time() - t0
        param_count = sum(p.numel() for p in model.parameters())
        logger.info(
            f"HuggingFace model loaded in {elapsed:.1f}s ({param_count:,} params)"
        )

        _model_cache[model_path] = {
            "type": "huggingface",
            "model": model,
            "tokenizer": tokenizer,
        }
        return _model_cache[model_path]
    except Exception as e:
        raise RuntimeError(
            f"Could not load ternary model from {model_path}: {e}"
        )


class LocalTernaryProvider(BaseProvider):
    """Provider that runs a ternary-quantized model locally.

    Supports two model backends:
      - Triton TernaryCreditRiskNet: Lightweight classifier (~500 KB).
        Returns structured {Risk_Flag, Audit_Memo} with zero latency.
      - HuggingFace LLM: Generative model for free-form responses.
        Heavier but more flexible.
    """

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
        t0 = time.time()
        cached = _get_or_load_model(self.model_path)

        if cached["type"] == "triton":
            return await self._triton_inference(
                cached, messages, t0
            )
        else:
            return await self._huggingface_inference(
                cached, messages, model, temperature, max_tokens, system_prompt, t0
            )

    async def _triton_inference(
        self, cached: dict, messages: list[dict], t0: float
    ) -> ProviderResponse:
        """Run Triton classifier inference."""
        import torch

        model_obj = cached["model"]
        tokenizer = cached["tokenizer"]
        device = cached["device"]

        # Extract borrower notes from last user message
        text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                raw_content = msg.get("content", "")
                if isinstance(raw_content, list):
                    # Rich content array — extract text blocks, ignore images
                    text = " ".join(
                        block["text"] for block in raw_content
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                else:
                    text = raw_content
                break

        # Tokenize and predict
        input_ids = tokenizer.encode(text).unsqueeze(0).to(device)
        results = model_obj.predict(input_ids)
        result = results[0]

        # Format as JSON response (matches Gemini output format)
        response_text = json.dumps({
            "Risk_Flag": result["Risk_Flag"],
            "Audit_Memo": result["Audit_Memo"],
        })

        latency = (time.time() - t0) * 1000
        token_estimate = len(text.split())

        return ProviderResponse(
            content=response_text,
            model="triton-ternary-credit-risk",
            input_tokens=token_estimate,
            output_tokens=len(response_text.split()),
            latency_ms=latency,
            cost_usd=0.0,  # Zero cost -- local inference
        )

    async def _huggingface_inference(
        self,
        cached: dict,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str],
        t0: float,
    ) -> ProviderResponse:
        """Run HuggingFace generative LLM inference."""
        import torch

        model_obj = cached["model"]
        tokenizer = cached["tokenizer"]

        # Build prompt
        parts = []
        if system_prompt:
            parts.append(f"<|system|>\n{system_prompt}")
        for msg in messages:
            role = msg.get("role", "user")
            raw_content = msg.get("content", "")
            if isinstance(raw_content, list):
                content = " ".join(
                    block["text"] for block in raw_content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            else:
                content = raw_content
            parts.append(f"<|{role}|>\n{content}")
        parts.append("<|assistant|>\n")
        prompt = "\n".join(parts)

        # Tokenize
        inputs = tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=512
        )
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

        new_tokens = outputs[0][input_len:]
        response_text = tokenizer.decode(
            new_tokens, skip_special_tokens=True
        ).strip()
        output_len = len(new_tokens)

        latency = (time.time() - t0) * 1000

        return ProviderResponse(
            content=response_text,
            model=f"local-ternary:{model}",
            input_tokens=input_len,
            output_tokens=output_len,
            latency_ms=latency,
            cost_usd=0.0,  # Zero cost -- local inference
        )
