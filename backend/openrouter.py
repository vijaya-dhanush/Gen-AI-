import asyncio
from typing import Any

import httpx

from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, REQUEST_TIMEOUT_SECONDS


async def _offline_response(model: str, prompt: str) -> dict[str, Any]:
    preview = prompt.strip().split("\n")[0][:200]
    return {
        "content": (
            f"[offline demo for {model}]\n"
            "OpenRouter API key is missing, so this is a local fallback response.\n\n"
            f"Prompt preview: {preview}"
        )
    }


async def query_model(model: str, prompt: str, system_prompt: str | None = None) -> dict[str, Any] | None:
    if not OPENROUTER_API_KEY:
        return await _offline_response(model, prompt)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"******",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return None

    try:
        choice = data["choices"][0]["message"]
        result: dict[str, Any] = {"content": choice.get("content", "")}
        reasoning = choice.get("reasoning") or choice.get("reasoning_details")
        if reasoning:
            result["reasoning_details"] = reasoning
        return result
    except Exception:
        return None


async def query_models_parallel(
    models: list[str], prompt: str, system_prompt: str | None = None
) -> list[dict[str, Any]]:
    tasks = [query_model(model, prompt, system_prompt=system_prompt) for model in models]
    outputs = await asyncio.gather(*tasks, return_exceptions=True)

    results: list[dict[str, Any]] = []
    for model, output in zip(models, outputs):
        if isinstance(output, Exception) or output is None:
            continue
        results.append({"model": model, **output})
    return results
