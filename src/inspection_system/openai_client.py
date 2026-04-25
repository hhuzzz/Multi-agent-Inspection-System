from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel


ParsedModel = TypeVar("ParsedModel", bound=BaseModel)


class OpenAIClient:
    """Minimal OpenAI Structured Outputs wrapper."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install dependencies first: pip install -e .") from exc

        self.model = model or os.getenv("MODEL_ID") or os.getenv("OPENAI_MODEL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.timeout = timeout or float(os.getenv("OPENAI_TIMEOUT", "60"))

        if not self.model:
            raise RuntimeError("Missing model id. Set MODEL_ID in .env.")
        if not self.api_key:
            raise RuntimeError("Missing API key. Set OPENAI_API_KEY in .env.")

        client_kwargs: dict[str, Any] = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client: Any = OpenAI(**client_kwargs)

    def parse(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: type[ParsedModel],
        image_paths: list[str] | None = None,
    ) -> ParsedModel:
        schema = json.dumps(output_model.model_json_schema(), ensure_ascii=False, indent=2)
        messages = [
            {
                "role": "system",
                "content": (
                    f"{system_prompt}\n\n"
                    "你必须只返回一个 JSON 对象，不要返回 Markdown，不要使用 ```json 代码块。\n"
                    f"JSON Schema:\n{schema}"
                ),
            },
            {"role": "user", "content": _build_user_content(user_prompt, image_paths or [])},
        ]

        try:
            print(system_prompt)
            print("大模型推理开始。", flush=True)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=1200,
            )
            print("大模型推理完成。", flush=True)
        except Exception as exc:
            raise RuntimeError(
                "OpenAI-compatible chat completion request failed. "
                f"model={self.model}, base_url={self.base_url or 'OpenAI default'}, "
                f"timeout={self.timeout}s. Original error: {exc}"
            ) from exc

        content = response.choices[0].message.content or "{}"
        return output_model.model_validate_json(_extract_json_object(content))


def _extract_json_object(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    return text[start : end + 1]


def _build_user_content(user_prompt: str, image_paths: list[str]) -> str | list[dict[str, Any]]:
    if not image_paths:
        return user_prompt

    content: list[dict[str, Any]] = [{"type": "text", "text": user_prompt}]
    for image_path in image_paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _to_image_url(image_path)},
            }
        )
    return content


def _to_image_url(image_path: str) -> str:
    if image_path.startswith(("http://", "https://", "data:image/")):
        return image_path

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
