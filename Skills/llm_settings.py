"""Local LLM settings management with masked reads and atomic writes."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4.1-mini"},
    "dashscope": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen2.5:7b"},
    "custom": {"base_url": "", "model": ""},
}


def env_path(data_dir: str | Path) -> Path:
    return Path(data_dir) / ".env"


def _parse_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:3]}{'*' * min(12, len(value) - 7)}{value[-4:]}"


def _is_local_url(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def validate_settings(settings: dict) -> dict[str, str]:
    provider = str(settings.get("provider", "custom")).strip().lower()
    if provider not in PROVIDERS:
        raise ValueError("不支持的模型供应商")
    defaults = PROVIDERS[provider]
    base_url = str(settings.get("base_url") or defaults["base_url"]).strip().rstrip("/")
    model = str(settings.get("model") or defaults["model"]).strip()
    api_key = str(settings.get("api_key", "")).strip()
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("API 接口地址必须是完整的 HTTP(S) URL")
    if parsed.scheme != "https" and not _is_local_url(base_url):
        raise ValueError("非本地 API 接口必须使用 HTTPS")
    if not api_key and not _is_local_url(base_url):
        raise ValueError("非本地 API 接口必须填写 API Key")
    if not model:
        raise ValueError("模型名不能为空")
    return {"provider": provider, "base_url": base_url, "model": model, "api_key": api_key}


def get_settings(data_dir: str | Path) -> dict:
    values = _parse_env(env_path(data_dir))
    base_url = values.get("LLM_BASE_URL", "")
    provider = values.get("LLM_PROVIDER", "custom")
    if provider == "custom":
        for name, defaults in PROVIDERS.items():
            if name != "custom" and defaults["base_url"] == base_url:
                provider = name
                break
    api_key = values.get("LLM_API_KEY", "")
    model = values.get("LLM_MODEL") or PROVIDERS.get(provider, PROVIDERS["custom"])["model"]
    return {
        "configured": bool(base_url and model and (api_key or _is_local_url(base_url))),
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "api_key_masked": _mask(api_key),
        "allows_empty_key": _is_local_url(base_url) if base_url else False,
    }


def save_settings(data_dir: str | Path, settings: dict) -> dict:
    path = env_path(data_dir)
    existing = _parse_env(path)
    submitted = dict(settings)
    if not str(submitted.get("api_key", "")).strip() and existing.get("LLM_API_KEY"):
        submitted["api_key"] = existing["LLM_API_KEY"]
    validated = validate_settings(submitted)
    existing.update({
        "LLM_PROVIDER": validated["provider"],
        "LLM_API_KEY": validated["api_key"],
        "LLM_BASE_URL": validated["base_url"],
        "LLM_MODEL": validated["model"],
    })
    lines = [f'{key}="{value}"' for key, value in sorted(existing.items())]
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".env-", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    for key, value in {
        "LLM_PROVIDER": validated["provider"],
        "LLM_API_KEY": validated["api_key"],
        "LLM_BASE_URL": validated["base_url"],
        "LLM_MODEL": validated["model"],
    }.items():
        os.environ[key] = value
    return get_settings(data_dir)


def test_settings(settings: dict) -> dict:
    from openai import OpenAI

    validated = validate_settings(settings)
    client = OpenAI(api_key=validated["api_key"] or "local-no-key", base_url=validated["base_url"])
    response = client.chat.completions.create(
        model=validated["model"],
        messages=[{"role": "user", "content": "Reply with OK only."}],
        temperature=0,
        max_tokens=8,
        timeout=20,
    )
    content = response.choices[0].message.content or ""
    return {"ok": True, "message": content.strip()[:80] or "连接成功"}
