"""
LLM Client (大模型底层通道)
职责：整个 AI Studio OS 中所有 Agent 调用大模型思考的唯一入口。
基于 openai 库 + python-dotenv，支持 DeepSeek 等兼容 API。
"""

import os
import re
import time
import json
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# ---- 加载 .env ----
_data_dir = os.environ.get("AI_STUDIO_DATA_DIR")
if _data_dir:
    _env_path = Path(_data_dir) / ".env"
else:
    _env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# ---- 配置 ----
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 8192
MAX_RETRIES = 3
RETRY_DELAY = 2  # 重试等待秒数（指数递增）


def ask_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_seconds: float = 120.0,
    max_retries: int = MAX_RETRIES,
) -> str:
    """
    所有 Agent 调用大模型的唯一底层通道。

    参数:
        system_prompt: 系统角色提示词（设定人设与铁律）
        user_prompt:   用户级提示词（具体任务内容）
        model:         模型名（默认 deepseek-chat）
        temperature:   生成温度（默认 0.3，保证输出稳定性）
        max_tokens:    最大输出 token 数

    返回:
        LLM 响应的文本内容（已去除首尾空白）

    异常:
        连续尝试 max_retries 次后仍失败则抛出 RuntimeError
    """
    load_dotenv(dotenv_path=_env_path, override=True)
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1").strip()
    actual_model = model if model != DEFAULT_MODEL else os.getenv("LLM_MODEL", DEFAULT_MODEL)
    is_local = any(host in base_url for host in ("localhost", "127.0.0.1", "[::1]"))
    if not api_key and not is_local:
        raise RuntimeError(f"未找到 LLM_API_KEY，请在 Web 配置向导或 {_env_path} 中完成配置")
    client = OpenAI(api_key=api_key or "local-no-key", base_url=base_url)
    last_error = None

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    if max_retries < 1:
        raise ValueError("max_retries must be at least one")

    for attempt in range(1, max_retries + 1):
        started = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=actual_model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=httpx.Timeout(timeout_seconds, connect=min(10.0, timeout_seconds)),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content or ""
            try:
                usage = getattr(response, "usage", None)
                usage_path = Path(os.environ.get("AI_STUDIO_DATA_DIR", str(_env_path.parent))) / ".agent_workspace" / "llm_usage.jsonl"
                usage_path.parent.mkdir(parents=True, exist_ok=True)
                entry = {
                    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "model": actual_model,
                    "base_url": base_url,
                    "attempt": attempt,
                    "duration_ms": round((time.perf_counter() - started) * 1000),
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                    "prompt_chars": len(system_prompt) + len(user_prompt),
                    "completion_chars": len(content),
                }
                with usage_path.open("a", encoding="utf-8") as file:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass
            return content.strip()

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = RETRY_DELAY * attempt
                print(
                    f"[LLM Client] 第 {attempt} 次调用失败: {e}，"
                    f"{wait} 秒后重试 (共 {max_retries} 次)..."
                )
                time.sleep(wait)
            else:
                print(f"[LLM Client] 已尝试 {max_retries} 次，全部失败。")

    # 所有重试耗尽
    raise RuntimeError(
        f"LLM 调用失败，已尝试 {max_retries} 次。"
        f"最后错误: {last_error}"
    )


def safe_extract_json(raw_text: str, agent_label: str = "LLM") -> tuple[str | None, str]:
    """
    万能 JSON 剥壳器：从大模型原始返回中鲁棒提取纯 JSON 文本。
    
    策略（按优先级）：
    1. 校验并提取 Markdown JSON 代码块
    2. 使用 JSONDecoder 从任意对象/数组起点解析首个有效 JSON
    
    返回 (json_string, error_message) — 成功时 error_message 为空。
    """
    if not raw_text or not raw_text.strip():
        return None, "[safe_extract_json] 输入文本为空"

    # 策略1: 尝试 ```json ... ``` 代码块
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text, re.DOTALL)
    if match:
        extracted = match.group(1).strip()
        try:
            json.loads(extracted)
            print(f"[{agent_label}] 代码块命中: 提取 JSON ({len(extracted)} 字符)")
            return extracted, ""
        except json.JSONDecodeError:
            pass

    # 策略2: 从任意对象/数组起点尝试 JSONDecoder，避免贪婪正则把多个对象粘在一起。
    decoder = json.JSONDecoder()
    for match in re.finditer(r"[\{\[]", raw_text):
        try:
            _value, end = decoder.raw_decode(raw_text[match.start():])
            extracted = raw_text[match.start():match.start() + end].strip()
            print(f"[{agent_label}] JSONDecoder 命中: 提取 JSON ({len(extracted)} 字符)")
            return extracted, ""
        except json.JSONDecodeError:
            continue

    return None, f"[{agent_label}] 返回内容中未找到有效 JSON"
