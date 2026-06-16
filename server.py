"""
AI Studio OS - FastAPI Backend
WebSocket + REST API hybrid architecture
"""

import json
import os
import sys
import shutil
import subprocess
import time
import asyncio
import threading
import uuid
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from Skills.llm_settings import get_settings, save_settings, test_settings
from Skills.codex_builder import approve_standard, build_codex, load_standards
from Skills.project_store import (
    analyze_change,
    apply_change,
    archive_workspace,
    get_project,
    list_stable_projects,
    migrate_legacy_projects,
    rollback_project,
    set_lifecycle,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = ROOT_DIR
DATA_DIR = os.path.abspath(os.environ.get("AI_STUDIO_DATA_DIR", ROOT_DIR))

WS_DIR = os.path.join(DATA_DIR, ".agent_workspace")
KNOWLEDGE_DIR = os.path.join(DATA_DIR, "Knowledge")
BEST_DIR = os.path.join(KNOWLEDGE_DIR, "best_practices")
ANTI_DIR = os.path.join(KNOWLEDGE_DIR, "anti_patterns")
STATUS_FILE = os.path.join(WS_DIR, "task_status.json")
CONCEPT_FILE = os.path.join(WS_DIR, "concept_brief.md")
PROMPT_FILE = os.path.join(WS_DIR, ".web_prompt.json")
RESPONSE_FILE = os.path.join(WS_DIR, ".web_response.json")
LOG_FILE = os.path.join(WS_DIR, ".web_log.jsonl")
CHANGE_ANALYSIS_LOG = os.path.join(WS_DIR, "change_analysis_log.jsonl")

FRAMEWORK_FILES = {
    "blueprint.json", "active_schema.json", "current_result.json",
    "task_status.json", "review_board.md", "task_route.json",
    "boss_feedback.txt", "project_meta.json", "concept_brief.md",
}

HOST = os.environ.get("AI_STUDIO_HOST", "127.0.0.1")
PORT = int(os.environ.get("AI_STUDIO_PORT", "8080"))
WEB_CLIENT_VERSION = "20260616.2"
_default_origins = f"http://localhost:{PORT},http://127.0.0.1:{PORT}"
ALLOWED_ORIGINS = {
    origin.strip()
    for origin in os.environ.get("AI_STUDIO_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

router_proc = None
engine_start_ts = 0
active_ws: WebSocket | None = None


def _refresh_codex():
    script = os.path.join(BUNDLE_DIR, "Skills", "build_memory_codex.py")
    if not os.path.isfile(script):
        return
    env = os.environ.copy()
    env["AI_STUDIO_DATA_DIR"] = DATA_DIR
    subprocess.run([sys.executable, script], cwd=BUNDLE_DIR, env=env, capture_output=True, timeout=60)


def _safe_child(base_dir: str, *parts: str) -> str | None:
    base = os.path.realpath(base_dir)
    candidate = os.path.realpath(os.path.join(base, *parts))
    try:
        if os.path.commonpath([base, candidate]) != base:
            return None
    except ValueError:
        return None
    return candidate


def _log_change_analysis(event: str, trace_id: str, **data):
    try:
        os.makedirs(WS_DIR, exist_ok=True)
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "event": event,
            "trace_id": trace_id,
            **data,
        }
        with open(CHANGE_ANALYSIS_LOG, "a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _change_error_response(exc: Exception, trace_id: str) -> JSONResponse:
    detail = str(exc) or exc.__class__.__name__
    lowered = detail.lower()
    if "timeout" in lowered or "timed out" in lowered:
        message = "模型响应超时，请缩小需求范围后重试，或检查 API 服务状态。"
        status_code = 504
    elif isinstance(exc, (ValueError, FileNotFoundError)):
        message = detail
        status_code = 400
    elif "json" in lowered:
        message = "模型返回的修改方案格式不完整，请重新分析。"
        status_code = 502
    else:
        message = "增量修改方案生成失败，请根据详细错误检查 API 配置或需求范围。"
        status_code = 502
    return JSONResponse({
        "ok": False,
        "error": message,
        "detail": detail[:1000],
        "trace_id": trace_id,
    }, status_code=status_code)


# ==================== REST API ====================

# ---- ConfigTable 桥接 ----
import httpx

TABLE_BRIDGE = "http://127.0.0.1:8081"

async def _proxy_table(method: str, path: str, data: dict = None):
    """代理请求到 ConfigTable 子服务"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                r = await client.get(f"{TABLE_BRIDGE}{path}")
            else:
                r = await client.post(f"{TABLE_BRIDGE}{path}", json=data or {})
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception:
        return JSONResponse({"ok": False, "error": "ConfigTable 服务未启动 (8081)"}, 503)


@app.get("/api/table/status")
async def api_table_status():
    return await _proxy_table("GET", "/status")

@app.get("/api/table/files")
async def api_table_files():
    return await _proxy_table("GET", "/files")

@app.post("/api/table/open_file")
async def api_table_open_file(data: dict):
    return await _proxy_table("POST", "/open_file", data)

@app.post("/api/table/design")
async def api_table_design(data: dict):
    return await _proxy_table("POST", "/design", data)

@app.post("/api/table/quick")
async def api_table_quick(data: dict):
    return await _proxy_table("POST", "/quick", data)

@app.post("/api/table/resume")
async def api_table_resume(data: dict):
    return await _proxy_table("POST", "/resume", data)

@app.post("/api/table/cancel")
async def api_table_cancel():
    return await _proxy_table("POST", "/cancel")

@app.post("/api/table/clear")
async def api_table_clear():
    return await _proxy_table("POST", "/clear_session")

@app.get("/api/status")
def api_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            state = json.load(f).get("current_state", "idle")
    except Exception:
        state = "idle"
    return JSONResponse({"state": state, "llm_configured": get_settings(DATA_DIR)["configured"]})


@app.get("/api/settings/llm")
def api_get_llm_settings():
    return JSONResponse(get_settings(DATA_DIR))


@app.post("/api/settings/llm/test")
def api_test_llm_settings(data: dict):
    try:
        return JSONResponse(test_settings(data))
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/settings/llm")
async def api_save_llm_settings(data: dict):
    try:
        result = save_settings(DATA_DIR, data)
        await _proxy_table("POST", "/reload_settings")
        return JSONResponse({"ok": True, **result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.get("/api/files")
def api_files():
    if not os.path.exists(WS_DIR):
        return JSONResponse({"files": []})

    files = []
    for f in os.listdir(WS_DIR):
        fp = os.path.join(WS_DIR, f)
        # 只取直接文件，排除子目录（如 project_db/）
        if not os.path.isfile(fp) or f.startswith("."):
            continue
        if f in FRAMEWORK_FILES:
            continue
        mtime = os.path.getmtime(fp)
        if mtime < engine_start_ts:
            continue
        if os.path.getsize(fp) < 10:
            continue
        files.append({
            "name": f,
            "path": f".agent_workspace/{f}",
            "mtime": mtime,
            "size": os.path.getsize(fp),
        })
    files.sort(key=lambda x: x["mtime"])
    return JSONResponse({"files": files})


@app.post("/api/open_file")
async def api_open_file(data: dict):
    fp = _safe_child(WS_DIR, data.get("file", ""))
    if not fp or not os.path.isfile(fp):
        return JSONResponse({"ok": False, "error": "文件不在当前工作区内"}, status_code=400)
    abs_path = os.path.abspath(fp)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])
    return JSONResponse({"ok": True})


@app.post("/api/open_knowledge")
async def api_open_knowledge(data: dict):
    d = BEST_DIR if data.get("type") == "best" else ANTI_DIR
    fp = _safe_child(d, data.get("file", ""))
    if not fp or not os.path.isfile(fp):
        return JSONResponse({"ok": False, "error": "知识文件不在允许目录内"}, status_code=400)
    abs_path = os.path.abspath(fp)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])
    return JSONResponse({"ok": True})


@app.post("/api/concept")
async def api_concept(data: dict):
    text = data.get("text", "")
    if text.strip():
        os.makedirs(WS_DIR, exist_ok=True)
        with open(CONCEPT_FILE, "w", encoding="utf-8") as f:
            f.write(text.strip())
    return JSONResponse({"ok": True})


@app.get("/api/knowledge")
def api_knowledge(type: str = "best"):
    d = BEST_DIR if type == "best" else ANTI_DIR
    files = sorted(os.listdir(d)) if os.path.exists(d) else []
    return JSONResponse({"files": files})


@app.post("/api/archive")
async def api_archive(data: dict):
    doc_path = _safe_child(WS_DIR, data.get("doc", ""))
    if not doc_path or not os.path.isfile(doc_path):
        return JSONResponse({"ok": False, "error": "只能归档当前工作区内的文件"}, status_code=400)
    python_exe = sys.executable
    cmd = [python_exe,
           os.path.join(BUNDLE_DIR, "Agents", "archivist_agent.py"),
           doc_path, "all", data.get("type", "red"),
           data.get("comment", "") or "（无评语）",
           data.get("agent", "系统")]
    try:
        env = os.environ.copy()
        env["AI_STUDIO_DATA_DIR"] = DATA_DIR
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=BUNDLE_DIR, env=env)
        return JSONResponse({"ok": r.returncode == 0, "error": r.stderr[-300:] if r.returncode else ""})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})


@app.post("/api/archive_project")
def api_archive_project():
    """Archive the workspace into the stable project store."""
    try:
        result = archive_workspace(DATA_DIR, WS_DIR)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    try:
        splitter = os.path.join(BUNDLE_DIR, "Skills", "config_splitter.py")
        if os.path.exists(splitter):
            python_exe = sys.executable
            env = os.environ.copy()
            env["AI_STUDIO_DATA_DIR"] = DATA_DIR
            subprocess.run(
                [python_exe, splitter],
                cwd=ROOT_DIR, env=env,
                capture_output=True, timeout=30,
            )
    except Exception:
        pass

    _refresh_codex()
    return JSONResponse(result)


@app.get("/api/projects")
def api_projects():
    migrate_legacy_projects(DATA_DIR)
    return JSONResponse({"projects": list_stable_projects(DATA_DIR)})


@app.post("/api/open_project_file")
async def api_open_project_file(data: dict):
    folder = data.get("system_id") or data.get("folder", "")
    filename = data.get("file", "")
    fp = _safe_child(os.path.join(DATA_DIR, "projects"), folder, "current", filename)
    if not fp or not os.path.isfile(fp):
        return JSONResponse({"ok": False, "error": "项目文件不在允许目录内"}, status_code=400)
    abs_path = os.path.abspath(fp)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])
    return JSONResponse({"ok": True})


@app.post("/api/open_project_folder")
async def api_open_project_folder(data: dict):
    try:
        system_id = str(data.get("system_id", "")).strip()
        project_dir, _manifest = get_project(DATA_DIR, system_id)
        current = project_dir / "current"
        if not current.is_dir():
            return JSONResponse({"ok": False, "error": "项目当前文档目录不存在"}, status_code=404)
        abs_path = str(current.resolve())
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.call(["open", abs_path])
        else:
            subprocess.call(["xdg-open", abs_path])
        return JSONResponse({"ok": True, "path": abs_path})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/changes/analyze")
def api_analyze_change(data: dict):
    trace_id = f"ana_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    started = time.perf_counter()
    system_id = str(data.get("system_id", ""))
    selected_document = str(
        data.get("selected_document")
        or data.get("document")
        or data.get("filename")
        or data.get("file")
        or ""
    ).strip()
    change_type = str(data.get("change_type") or data.get("iteration_type") or "").strip()
    client_version = str(data.get("client_version", "")).strip()
    requirement = str(data.get("requirement", ""))
    analysis_feedback = str(data.get("analysis_feedback", "")).strip()
    previous_change_id = str(data.get("previous_change_id", "")).strip()
    raw_impact_confirmed = data.get("impact_confirmed", False)
    impact_confirmed = raw_impact_confirmed is True or str(raw_impact_confirmed).lower() in {"1", "true", "yes", "y"}
    _log_change_analysis(
        "started",
        trace_id,
        system_id=system_id,
        selected_document=selected_document,
        change_type=change_type,
        client_version=client_version,
        payload_keys=sorted(str(key) for key in data.keys()),
        requirement_chars=len(requirement),
        feedback_chars=len(analysis_feedback),
        previous_change_id=previous_change_id,
        impact_confirmed=impact_confirmed,
    )
    try:
        if client_version and client_version != WEB_CLIENT_VERSION:
            raise ValueError(
                f"当前页面版本为 {client_version}，服务端版本为 {WEB_CLIENT_VERSION}。"
                "请刷新浏览器页面后重新选择文档。"
            )
        if not client_version and not selected_document and not change_type:
            raise ValueError("当前页面版本过旧，未发送文档和迭代类型。请刷新浏览器页面后重新选择文档。")
        if not selected_document:
            raise ValueError("请先选择要迭代的归档文档")
        if not change_type:
            raise ValueError("请说明本次需求是新增功能还是老功能迭代")
        result = analyze_change(
            DATA_DIR,
            system_id,
            requirement,
            generate_proposal=True,
            selected_document=selected_document,
            change_type=change_type,
            analysis_feedback=analysis_feedback,
            previous_change_id=previous_change_id,
            impact_confirmed=impact_confirmed,
        )
        duration_ms = round((time.perf_counter() - started) * 1000)
        _log_change_analysis(
            "completed",
            trace_id,
            duration_ms=duration_ms,
            affected_files=result.get("affected_files", []),
            writable_files=result.get("writable_files", []),
            impact_confirmed=result.get("impact_confirmed"),
        )
        return JSONResponse({"ok": True, "trace_id": trace_id, "duration_ms": duration_ms, **result})
    except Exception as exc:
        _log_change_analysis(
            "failed",
            trace_id,
            duration_ms=round((time.perf_counter() - started) * 1000),
            error_type=exc.__class__.__name__,
            error=str(exc)[:2000],
        )
        return _change_error_response(exc, trace_id)


@app.post("/api/changes/apply")
def api_apply_change(data: dict):
    try:
        result = apply_change(
            DATA_DIR,
            str(data.get("system_id", "")),
            str(data.get("change_id", "")),
            data.get("text_changes"),
            data.get("numerical_operations"),
            data.get("numerical_doc_changes"),
        )
        _refresh_codex()
        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/projects/{system_id}/rollback")
def api_rollback_project(system_id: str, data: dict):
    try:
        result = rollback_project(DATA_DIR, system_id, str(data.get("history_id", "")))
        _refresh_codex()
        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/projects/{system_id}/lifecycle")
def api_project_lifecycle(system_id: str, data: dict):
    try:
        result = set_lifecycle(DATA_DIR, system_id, str(data.get("lifecycle", "")))
        _refresh_codex()
        return JSONResponse({"ok": True, "project": result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.get("/api/standards")
def api_standards():
    return JSONResponse(load_standards(DATA_DIR))


@app.post("/api/standards/{candidate_id}/decision")
def api_standard_decision(candidate_id: str, data: dict):
    try:
        standards = approve_standard(DATA_DIR, candidate_id, bool(data.get("approved")))
        build_codex(DATA_DIR)
        return JSONResponse({"ok": True, **standards})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


# ==================== WebSocket ====================

def get_prompt_data():
    if not os.path.exists(PROMPT_FILE):
        return None
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("answered"):
            return None
        return d.get("prompt", "")
    except Exception:
        return None


def submit_answer(ans: str):
    try:
        os.makedirs(WS_DIR, exist_ok=True)
        with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
            json.dump({"answer": ans, "ts": time.time()}, f)
    except Exception:
        pass


@app.websocket("/ws/terminal")
async def ws_terminal(websocket: WebSocket):
    global router_proc, engine_start_ts, active_ws

    origin = websocket.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    await websocket.accept()

    if not get_settings(DATA_DIR)["configured"]:
        await websocket.send_json({"type": "error", "msg": "请先在 Web 的 API 配置向导中完成大模型配置"})
        await websocket.close()
        return

    if active_ws is not None:
        await websocket.send_json({"type": "error", "msg": "控制台已在另一个窗口运行中"})
        await websocket.close()
        return

    active_ws = websocket
    engine_start_ts = time.time()

    # Preserve the concept cache while resuming an interrupted task so the
    # router does not mistake a restart for a new requirement.
    CACHE_FILE = os.path.join(WS_DIR, ".concept_brief_cache.txt")
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            preserve_cache = json.load(f).get("current_state", "idle") != "idle"
    except Exception:
        preserve_cache = False
    communication_files = [PROMPT_FILE, RESPONSE_FILE] + ([] if preserve_cache else [CACHE_FILE])
    for f in communication_files:
        if os.path.exists(f):
            os.remove(f)
    os.makedirs(WS_DIR, exist_ok=True)
    open(LOG_FILE, "w", encoding="utf-8").close()

    env = os.environ.copy()
    env["AI_STUDIO_WEB_MODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["AI_STUDIO_DATA_DIR"] = DATA_DIR

    try:
        python_cmd = sys.executable
        router_proc = subprocess.Popen(
            [python_cmd, "-u", os.path.join(BUNDLE_DIR, "main_router.py")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=BUNDLE_DIR, env=env,
            bufsize=1, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        await websocket.send_json({"type": "error", "msg": f"引擎启动失败: {e}"})
        active_ws = None
        return

    # Immediately push startup confirmation
    ws_queue = asyncio.Queue()
    await ws_queue.put({"type": "log", "text": f"[GUI] 引擎已启动 (PID: {router_proc.pid})"})
    stop_flag = threading.Event()
    loop = asyncio.get_running_loop()

    # Thread: read Router stdout (strip ANSI codes)
    def stdout_reader():
        import re
        ansi_re = re.compile(r'\x1b\[[0-9;]*m')
        try:
            for line in iter(router_proc.stdout.readline, ""):
                if stop_flag.is_set():
                    break
                if line and line.strip():
                    clean = ansi_re.sub("", line.strip())
                    loop.call_soon_threadsafe(ws_queue.put_nowait, {"type": "log", "text": clean})
        except Exception:
            pass

    # Thread: poll HITL prompts  
    def hitl_poller():
        last_prompt = ""
        while not stop_flag.is_set():
            prompt = get_prompt_data()
            if prompt and prompt != last_prompt:
                last_prompt = prompt
                loop.call_soon_threadsafe(ws_queue.put_nowait, {"type": "hitl_req", "msg": prompt})
            elif not prompt:
                last_prompt = ""
            time.sleep(1)

    t1 = threading.Thread(target=stdout_reader, daemon=True)
    t2 = threading.Thread(target=hitl_poller, daemon=True)
    t1.start()
    t2.start()

    async def consumer():
        while True:
            msg = await ws_queue.get()
            if msg["type"] == "log":
                try:
                    await websocket.send_text(msg["text"])
                except Exception:
                    break
            elif msg["type"] == "hitl_req":
                try:
                    await websocket.send_json(msg)
                except Exception:
                    break
            elif msg["type"] == "engine_dead":
                try:
                    await websocket.send_json({"type": "engine_exit", "msg": msg.get("text", "引擎已退出")})
                except Exception:
                    pass
                break

    async def receiver():
        try:
            while True:
                data = await websocket.receive_text()
                submit_answer(data)
        except WebSocketDisconnect:
            stop_flag.set()
            ws_queue.put_nowait({"type": "engine_dead", "text": ""})

    async def engine_monitor():
        while not stop_flag.is_set() and router_proc.poll() is None:
            await asyncio.sleep(1)
        if stop_flag.is_set():
            return
        await asyncio.sleep(0.5)
        loop.call_soon_threadsafe(ws_queue.put_nowait, {"type": "engine_dead", "text": "[System] 引擎进程已退出"})

    try:
        await asyncio.gather(consumer(), receiver(), engine_monitor())
    except WebSocketDisconnect:
        stop_flag.set()
        if not ws_queue.full():
            ws_queue.put_nowait({"type": "engine_dead", "text": ""})
    finally:
        stop_flag.set()
        active_ws = None
        if router_proc and router_proc.poll() is None:
            router_proc.terminate()
            try:
                router_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                router_proc.kill()


# ==================== Static Files ====================

@app.get("/")
async def root():
    return FileResponse(
        os.path.join(BUNDLE_DIR, "index.html"),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-AI-Studio-Client-Version": WEB_CLIENT_VERSION,
        },
    )


# ==================== Startup ====================

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import socket
    import threading as _threading

    URL = f"http://localhost:{PORT}/?v={WEB_CLIENT_VERSION}"

    # 端口检测
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1)
        s.connect(("127.0.0.1", PORT))
        print(f"AI Studio OS — port {PORT} 已被占用，可能已在运行。")
        webbrowser.open(URL)
        input("按 Enter 退出...")
        sys.exit(0)
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    finally:
        s.close()

    print(f"AI Studio OS v2 (FastAPI + WebSocket)")
    print(f"Starting server -> {URL}")

    # 启动 ConfigTable 子服务（配表桥接，端口 8081）
    TABLE_DIR = os.path.join(BUNDLE_DIR, "ConfigTable")
    TABLE_PORT = 8081
    table_proc = None
    # 已有子服务时复用，不主动终止用户进程。
    table_port_in_use = False
    try:
        with socket.create_connection(("127.0.0.1", TABLE_PORT), timeout=0.5):
            table_port_in_use = True
            print(f"ConfigTable 已在运行 -> http://localhost:{TABLE_PORT}")
    except Exception:
        pass

    if not table_port_in_use and os.path.exists(os.path.join(TABLE_DIR, "table_server.py")):
        table_python = sys.executable
        table_env = os.environ.copy()
        table_env["AI_STUDIO_DATA_DIR"] = DATA_DIR
        table_proc = subprocess.Popen(
            [table_python, "-m", "uvicorn", "table_server:app",
             "--host", "127.0.0.1", "--port", str(TABLE_PORT), "--log-level", "warning"],
            cwd=TABLE_DIR, env=table_env, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        import time as _time; _time.sleep(1)
        if table_proc.poll() is not None:
            err = table_proc.stderr.read().decode("utf-8", errors="replace")[:500]
            print(f"[WARN] ConfigTable 子服务启动失败: {err}")
            table_proc = None
        else:
            print(f"ConfigTable 桥接服务 -> http://localhost:{TABLE_PORT}")

    def _open_browser():
        import time as _time
        _time.sleep(1.5)
        webbrowser.open(URL)

    if os.environ.get("AI_STUDIO_OPEN_BROWSER", "1") == "1":
        _threading.Thread(target=_open_browser, daemon=True).start()

    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        if table_proc and table_proc.poll() is None:
            table_proc.terminate()
            try: table_proc.wait(timeout=3)
            except: table_proc.kill()
