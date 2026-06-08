"""
ConfigTable Bridge Server — 配表工具桥接服务
监听 localhost:8081，接收 AI Studio OS 的配表请求
独立运行在 ConfigTable/ 目录下，隔离于主项目
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.environ.get("AI_STUDIO_DATA_DIR", os.path.dirname(ROOT_DIR))
EXCEL_DIR = os.path.join(PROJECT_ROOT, "Excel")
GAMEDATA_DIR = os.path.join(ROOT_DIR, "knowledge", "gamedata")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
SESSION_FILE = os.path.join(ROOT_DIR, ".session_state.json")
MODIFIED_FILE = os.path.join(ROOT_DIR, ".modified_files.json")
HFSM_SERVER_DIR = os.path.join(ROOT_DIR, "references", "scripts", "server")
HFSM_CORE_DIR = os.path.join(ROOT_DIR, "references", "scripts", "core")

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

for path in (HFSM_SERVER_DIR, HFSM_CORE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from hfsm_controller import TaskStatus, get_controller, reset_controller

app = FastAPI()
_allowed_origins = [
    origin.strip()
    for origin in os.environ.get(
        "AI_STUDIO_ALLOWED_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

session_log = []
modified_files = set()
active_task = False
CONTROLLER_ID = "ai-studio-os"


def _safe_child(base_dir: str, relative_path: str) -> str | None:
    base = os.path.realpath(base_dir)
    candidate = os.path.realpath(os.path.join(base, relative_path))
    try:
        if os.path.commonpath([base, candidate]) != base:
            return None
    except ValueError:
        return None
    return candidate


def _reply_callback(_user_id, message, card_data=None):
    global active_task
    timestamp = datetime.now().strftime("%H:%M:%S")
    session_log.append(f"[{timestamp}] {message}")
    if card_data:
        session_log.append(f"[{timestamp}] 等待确认: {card_data.get('title', '')}")
    ctrl = get_controller(CONTROLLER_ID)
    active_task = ctrl.status in (TaskStatus.RUNNING, TaskStatus.WAITING_USER)
    save_session()


def _controller():
    return get_controller(CONTROLLER_ID, _reply_callback)


def _scan_files() -> list[dict]:
    files = []
    roots = (("Excel", EXCEL_DIR), ("output", OUTPUT_DIR))
    for label, base_dir in roots:
        if not os.path.isdir(base_dir):
            continue
        for root, _dirs, filenames in os.walk(base_dir):
            for filename in sorted(filenames):
                if not filename.lower().endswith((".json", ".xlsx", ".xls", ".txt", ".md")):
                    continue
                fp = os.path.join(root, filename)
                rel = os.path.relpath(fp, base_dir).replace("\\", "/")
                files.append({
                    "name": f"{label}/{rel}",
                    "size": os.path.getsize(fp),
                    "mtime": os.path.getmtime(fp),
                })
    files.sort(key=lambda x: x["name"])
    return files


def _has_gamedata() -> bool:
    if not os.path.isdir(GAMEDATA_DIR):
        return False
    return any(
        filename.lower().endswith((".xlsx", ".xls"))
        for _root, _dirs, filenames in os.walk(GAMEDATA_DIR)
        for filename in filenames
        if not filename.startswith("~$")
    )


def load_session():
    global session_log, modified_files, active_task
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            session_log = d.get("log", [])
            modified_files = set(d.get("modified", []))
            active_task = d.get("active", False)
        except Exception:
            pass


def save_session():
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "log": session_log[-200:],
                "modified": sorted(modified_files),
                "active": active_task,
            }, f, ensure_ascii=False)
    except Exception:
        pass


load_session()


@app.get("/status")
def api_status():
    ctrl = _controller()
    status = ctrl.get_status()
    current = {f["name"]: f["mtime"] for f in _scan_files()}
    previous = getattr(api_status, "_snapshot", {})
    modified_files.update(name for name, mtime in current.items() if previous and previous.get(name) != mtime)
    api_status._snapshot = current
    save_session()
    return JSONResponse({
        "active": status["status"] in ("running", "waiting_user"),
        "waiting": status["waiting"],
        "ready": _has_gamedata(),
        "controller": status,
        "log": session_log[-80:],
    })


@app.get("/files")
def api_files():
    """返回 Excel/ 下所有 JSON/XLSX/XLS/TXT 文件（含子目录）"""
    return JSONResponse({"files": _scan_files(), "modified": sorted(modified_files)})


@app.post("/open_file")
async def api_open_file(data: dict):
    fname = data.get("file", "")
    prefix, _, rel = fname.partition("/")
    base = EXCEL_DIR if prefix == "Excel" else OUTPUT_DIR if prefix == "output" else None
    fp = _safe_child(base, rel) if base else None
    if not fp or not os.path.isfile(fp):
        return JSONResponse({"ok": False, "error": "文件不在允许目录内"}, status_code=400)
    abs_path = os.path.abspath(fp)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])
    return JSONResponse({"ok": True})


@app.post("/design")
async def api_design(data: dict):
    """提交需求到真实 HFSM 配表工作流。"""
    global active_task, session_log
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "需求文本为空"})
    if not _has_gamedata():
        return JSONResponse({
            "ok": False,
            "error": "ConfigTable/knowledge/gamedata 中没有 Excel 源表，请先导入配置表",
        }, status_code=409)

    ctrl = _controller()
    if ctrl.status == TaskStatus.WAITING_USER:
        ctrl.resume(text)
        active_task = True
        save_session()
        return JSONResponse({"ok": True, "submitted": "resume", "controller": ctrl.get_status()})
    if ctrl.status == TaskStatus.RUNNING:
        return JSONResponse({"ok": False, "error": "已有配表任务正在执行"}, status_code=409)

    ctrl.submit(text)
    active_task = True
    timestamp = datetime.now().strftime("%H:%M:%S")
    session_log.append(f"[{timestamp}] 已提交到 HFSM 配表工作流: {text[:100]}")
    save_session()
    return JSONResponse({"ok": True, "submitted": "design", "controller": ctrl.get_status()})


@app.post("/quick")
async def api_quick(data: dict):
    """快速修改使用真实工作流，并明确标记快速模式约束。"""
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "需求文本为空"})

    return await api_design({"text": f"[S_Express 快速修改] {text}"})


@app.post("/resume")
async def api_resume(data: dict):
    text = data.get("text", "").strip()
    ctrl = _controller()
    if not text or ctrl.status != TaskStatus.WAITING_USER:
        return JSONResponse({"ok": False, "error": "当前没有等待回复的配表任务"}, status_code=409)
    ctrl.resume(text)
    return JSONResponse({"ok": True, "controller": ctrl.get_status()})


@app.post("/cancel")
def api_cancel():
    global active_task
    _controller().reset()
    active_task = False
    session_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 任务已取消")
    save_session()
    return JSONResponse({"ok": True})


@app.post("/clear_session")
def api_clear_session():
    global session_log, modified_files
    reset_controller(CONTROLLER_ID)
    session_log = []
    modified_files = set()
    save_session()
    return JSONResponse({"ok": True})


@app.post("/reload_settings")
def api_reload_settings():
    """Reload local .env values for controllers created after this request."""
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)
    ctrl = _controller()
    if ctrl.status not in (TaskStatus.RUNNING, TaskStatus.WAITING_USER):
        reset_controller(CONTROLLER_ID)
    return JSONResponse({"ok": True})


if __name__ == "__main__":
    import uvicorn
    print(f"ConfigTable Bridge Server -> http://localhost:8081")
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level="warning")
