"""Stable project archive, incremental changes, and rollback support."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ARCHIVE_FILES = {
    "project_meta.json",
    "concept_brief.md",
    "system_design_draft.md",
    "system_design_detail.md",
    "task_plan.md",
    "system_schema.json",
    "system_numerical_data.json",
    "system_numerical_docs.json",
    "tech_blueprint.md",
    "ui_interaction_blueprint.md",
    "audit_feedback.json",
    "audit_trace_log.md",
    "final_audit_report.md",
}

TEXT_TARGETS = {
    "concept_brief.md": "lead_planner",
    "system_design_draft.md": "lead_planner",
    "system_design_detail.md": "system_planner",
    "task_plan.md": "task_planner",
    "tech_blueprint.md": "tech_architect",
    "ui_interaction_blueprint.md": "ux_agent",
}

NUMERICAL_OPERATIONS = {
    "create_table",
    "add_column",
    "add_rows",
    "update_rows",
    "delete_rows",
    "delete_column",
}

CHANGE_TYPES = {"new_feature", "existing_feature"}
NUMERICAL_DOC_TARGET = "system_numerical_docs.json"
WRITABLE_INCREMENTAL_TARGETS = set(TEXT_TARGETS) | {"system_numerical_data.json", NUMERICAL_DOC_TARGET}
ITERABLE_TARGETS = set(WRITABLE_INCREMENTAL_TARGETS)

AGENT_BY_FILE = {
    **TEXT_TARGETS,
    "system_numerical_data.json": "numerical_planner",
    NUMERICAL_DOC_TARGET: "numerical_planner",
    "system_schema.json": "schema_translator",
}

FILE_ORDER = [
    "concept_brief.md",
    "system_design_draft.md",
    "system_design_detail.md",
    "ui_interaction_blueprint.md",
    "system_numerical_data.json",
    NUMERICAL_DOC_TARGET,
    "tech_blueprint.md",
    "system_schema.json",
    "task_plan.md",
]

LEGACY_PATTERN = re.compile(r"^(?P<name>.+)_(?P<timestamp>\d{8}_\d{6})$")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _revision_name(revision: int) -> str:
    return f"r{revision:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def slugify_system_id(name: str) -> str:
    """Create a stable readable id while preserving Chinese system names."""
    value = re.sub(r'[\\/*?:"<>|\s]+', "-", (name or "未命名系统").strip())
    value = re.sub(r"-+", "-", value).strip("-._")
    return value[:64] or "未命名系统"


def _unique_system_id(projects_dir: Path, preferred: str) -> str:
    if not (projects_dir / preferred).exists():
        return preferred
    index = 2
    while (projects_dir / f"{preferred}-{index}").exists():
        index += 1
    return f"{preferred}-{index}"


def _manifest_path(project_dir: Path) -> Path:
    return project_dir / "manifest.json"


def _current_dir(project_dir: Path) -> Path:
    return project_dir / "current"


def _history_dir(project_dir: Path) -> Path:
    return project_dir / "_history"


def _pending_dir(project_dir: Path) -> Path:
    return project_dir / "_pending"


def _copy_artifacts(source: Path, destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for filename in sorted(ARCHIVE_FILES):
        src = source / filename
        if src.is_file():
            shutil.copy2(src, destination / filename)
            copied.append(filename)
    return copied


def _load_name_from_dir(source: Path, fallback: str) -> str:
    meta = _read_json(source / "project_meta.json", {})
    if isinstance(meta, dict) and meta.get("system_name"):
        return str(meta["system_name"]).strip()
    detail = _read_text(source / "system_design_detail.md")
    match = re.search(r"^#\s*(.+?)(?:\s*[-—]\s*.+)?$", detail, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _new_manifest(system_id: str, name: str) -> dict[str, Any]:
    timestamp = _now()
    return {
        "schema_version": 1,
        "system_id": system_id,
        "system_name": name,
        "lifecycle": "active",
        "revision": 0,
        "created_at": timestamp,
        "updated_at": timestamp,
        "dependencies": [],
        "public_interfaces": [],
        "latest_change": None,
        "history": [],
    }


def migrate_legacy_projects(data_dir: str | Path) -> dict[str, Any]:
    """Merge legacy timestamp folders into stable project directories."""
    projects_dir = Path(data_dir) / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    legacy: list[tuple[Path, str, str]] = []
    for child in projects_dir.iterdir():
        if not child.is_dir() or child.name.startswith("."):
            continue
        if _manifest_path(child).is_file():
            continue
        match = LEGACY_PATTERN.match(child.name)
        if match:
            legacy.append((child, match.group("name"), match.group("timestamp")))

    groups: dict[str, list[tuple[Path, str]]] = {}
    for path, fallback, timestamp in legacy:
        name = _load_name_from_dir(path, fallback)
        groups.setdefault(name, []).append((path, timestamp))

    migrated: list[dict[str, Any]] = []
    for name, entries in groups.items():
        entries.sort(key=lambda item: item[1])
        preferred_id = slugify_system_id(name)
        existing = projects_dir / preferred_id
        if existing.is_dir() and _manifest_path(existing).is_file():
            project_dir = existing
            manifest = _read_json(_manifest_path(project_dir), _new_manifest(preferred_id, name))
        else:
            system_id = _unique_system_id(projects_dir, preferred_id)
            project_dir = projects_dir / system_id
            project_dir.mkdir(parents=True, exist_ok=True)
            manifest = _new_manifest(system_id, name)

        for index, (legacy_dir, legacy_timestamp) in enumerate(entries):
            is_latest = index == len(entries) - 1
            if is_latest:
                current = _current_dir(project_dir)
                if current.exists():
                    shutil.rmtree(current)
                _copy_artifacts(legacy_dir, current)
            else:
                revision = int(manifest.get("revision", 0)) + 1
                history_name = f"legacy_r{revision:04d}_{legacy_timestamp}"
                destination = _history_dir(project_dir) / history_name / "snapshot"
                copied = _copy_artifacts(legacy_dir, destination)
                manifest["revision"] = revision
                manifest["history"].append({
                    "revision": revision,
                    "id": history_name,
                    "timestamp": legacy_timestamp,
                    "kind": "legacy_import",
                    "files": copied,
                })

        current_meta = _read_json(_current_dir(project_dir) / "project_meta.json", {})
        if not isinstance(current_meta, dict):
            current_meta = {}
        current_meta.update({
            "system_id": manifest["system_id"],
            "system_name": name,
            "version": f"r{int(manifest.get('revision', 0)) + 1}",
        })
        _write_json(_current_dir(project_dir) / "project_meta.json", current_meta)
        manifest["revision"] = int(manifest.get("revision", 0)) + 1
        manifest["updated_at"] = _now()
        manifest["latest_change"] = "legacy_migration"
        _write_json(_manifest_path(project_dir), manifest)

        for legacy_dir, _timestamp in entries:
            shutil.rmtree(legacy_dir)
        migrated.append({
            "system_id": manifest["system_id"],
            "system_name": name,
            "legacy_folders": len(entries),
        })

    return {"migrated": migrated, "project_count": len(list_stable_projects(data_dir))}


def list_stable_projects(data_dir: str | Path) -> list[dict[str, Any]]:
    projects_dir = Path(data_dir) / "projects"
    if not projects_dir.is_dir():
        return []
    result: list[dict[str, Any]] = []
    for project_dir in projects_dir.iterdir():
        manifest = _read_json(_manifest_path(project_dir), None)
        if not isinstance(manifest, dict):
            continue
        manifest = _repair_legacy_rollback_manifest(project_dir, manifest)
        files = sorted(path.name for path in _current_dir(project_dir).iterdir()) if _current_dir(project_dir).is_dir() else []
        item = dict(manifest)
        item["files"] = files
        item["iterable_files"] = sorted(filename for filename in files if filename in ITERABLE_TARGETS)
        item["history_count"] = len(manifest.get("history", []))
        result.append(item)
    return sorted(result, key=lambda item: item.get("updated_at", ""), reverse=True)


def _repair_legacy_rollback_manifest(project_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    latest_change = str(manifest.get("latest_change", ""))
    if not latest_change.startswith("rollback:"):
        return manifest
    target_id = latest_change.removeprefix("rollback:")
    target = next((entry for entry in manifest.get("history", []) if entry.get("id") == target_id), None)
    if not isinstance(target, dict) or not (_history_dir(project_dir) / target_id / "snapshot").is_dir():
        return manifest
    target_revision = int(target.get("revision", 0))
    project_meta = _read_json(_current_dir(project_dir) / "project_meta.json", {})
    if not isinstance(project_meta, dict) or project_meta.get("version") != f"r{target_revision}":
        return manifest
    manifest["revision"] = target_revision
    manifest["latest_change"] = f"restored:{target_id}"
    manifest["history"] = [
        entry for entry in manifest.get("history", [])
        if int(entry.get("revision", 0)) < target_revision
    ]
    _write_json(_manifest_path(project_dir), manifest)
    return manifest


def get_project(data_dir: str | Path, system_id: str) -> tuple[Path, dict[str, Any]]:
    projects_dir = Path(data_dir) / "projects"
    project_dir = (projects_dir / system_id).resolve()
    if projects_dir.resolve() not in project_dir.parents:
        raise ValueError("Invalid system_id")
    manifest = _read_json(_manifest_path(project_dir), None)
    if not isinstance(manifest, dict):
        raise FileNotFoundError(f"Project not found: {system_id}")
    return project_dir, manifest


def _snapshot_current(project_dir: Path, manifest: dict[str, Any], kind: str, metadata: dict[str, Any]) -> dict[str, Any]:
    revision = int(manifest.get("revision", 0))
    history_id = _revision_name(revision)
    destination = _history_dir(project_dir) / history_id
    copied = _copy_artifacts(_current_dir(project_dir), destination / "snapshot")
    entry = {
        "revision": revision,
        "id": history_id,
        "timestamp": _now(),
        "kind": kind,
        "files": copied,
        **metadata,
    }
    _write_json(destination / "change.json", entry)
    manifest.setdefault("history", []).append(entry)
    return entry


def archive_workspace(data_dir: str | Path, workspace_dir: str | Path) -> dict[str, Any]:
    """Archive a workspace into a stable project and preserve the previous revision."""
    migrate_legacy_projects(data_dir)
    projects_dir = Path(data_dir) / "projects"
    source = Path(workspace_dir)
    meta = _read_json(source / "project_meta.json", {})
    name = str(meta.get("system_name", "未命名系统")) if isinstance(meta, dict) else "未命名系统"
    requested_id = str(meta.get("system_id", "")) if isinstance(meta, dict) else ""
    system_id = slugify_system_id(requested_id or name)
    project_dir = projects_dir / system_id

    if _manifest_path(project_dir).is_file():
        manifest = _read_json(_manifest_path(project_dir), _new_manifest(system_id, name))
        if _current_dir(project_dir).is_dir():
            _snapshot_current(project_dir, manifest, "archive_replace", {"requirement": "Workspace archive"})
    else:
        if project_dir.exists():
            system_id = _unique_system_id(projects_dir, system_id)
            project_dir = projects_dir / system_id
        project_dir.mkdir(parents=True, exist_ok=True)
        manifest = _new_manifest(system_id, name)

    staging = Path(tempfile.mkdtemp(prefix=".archive-", dir=project_dir))
    try:
        copied = _copy_artifacts(source, staging)
        project_meta = _read_json(staging / "project_meta.json", {})
        if not isinstance(project_meta, dict):
            project_meta = {}
        next_revision = int(manifest.get("revision", 0)) + 1
        project_meta.update({"system_id": system_id, "system_name": name, "version": f"r{next_revision}"})
        _write_json(staging / "project_meta.json", project_meta)
        _validate_project(staging)

        current = _current_dir(project_dir)
        old_current = project_dir / ".current-old"
        if old_current.exists():
            shutil.rmtree(old_current)
        if current.exists():
            os.replace(current, old_current)
        os.replace(staging, current)
        if old_current.exists():
            shutil.rmtree(old_current)

        manifest.update({
            "system_id": system_id,
            "system_name": name,
            "revision": next_revision,
            "updated_at": _now(),
            "latest_change": "archive",
        })
        _write_json(_manifest_path(project_dir), manifest)
        return {"ok": True, "system_id": system_id, "path": str(current), "files": copied, "revision": next_revision}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _headings(path: Path) -> list[str]:
    return [match.group(2).strip() for match in HEADING_PATTERN.finditer(_read_text(path))]


NEGATED_IMPACT_MARKERS = (
    "不涉及", "无需", "无须", "不需要", "不用", "不修改", "不调整",
    "不改", "不包含", "不影响", "排除", "禁止", "不得", "避免",
)
POSITIVE_NEGATION_OVERRIDES = ("不要遗漏", "不得遗漏", "不能遗漏", "不可遗漏")


def _has_positive_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    for keyword in keywords:
        start = 0
        while True:
            index = text.find(keyword, start)
            if index < 0:
                break
            prefix = text[max(0, index - 10):index]
            negated = any(marker in prefix for marker in NEGATED_IMPACT_MARKERS)
            overridden = any(marker in prefix for marker in POSITIVE_NEGATION_OVERRIDES)
            if not negated or overridden:
                return True
            start = index + len(keyword)
    return False


def _ordered_files(files: set[str] | list[str]) -> list[str]:
    known = [filename for filename in FILE_ORDER if filename in files]
    extra = sorted(filename for filename in files if filename not in FILE_ORDER)
    return known + extra


def _plan_entry(
    filename: str,
    reason: str,
    *,
    required: bool = True,
    writable: bool | None = None,
    agent: str | None = None,
    source: str = "rules",
) -> dict[str, Any]:
    return {
        "file": filename,
        "reason": reason,
        "agent": agent or AGENT_BY_FILE.get(filename, "pm_supervisor"),
        "required": bool(required),
        "writable": filename in WRITABLE_INCREMENTAL_TARGETS if writable is None else bool(writable),
        "source": source,
    }


def _merge_plan_entries(entries: list[dict[str, Any]], current: Path) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in entries:
        filename = str(item.get("file", "")).strip()
        if not filename:
            continue
        if not (current / filename).is_file() and filename not in WRITABLE_INCREMENTAL_TARGETS:
            continue
        existing = merged.get(filename)
        if existing is None:
            normalized = _plan_entry(
                filename,
                str(item.get("reason") or "监管影响分析"),
                required=bool(item.get("required", True)),
                writable=bool(item.get("writable", filename in WRITABLE_INCREMENTAL_TARGETS)),
                agent=str(item.get("agent") or AGENT_BY_FILE.get(filename, "pm_supervisor")),
                source=str(item.get("source") or "supervisor"),
            )
            if filename not in WRITABLE_INCREMENTAL_TARGETS:
                normalized["writable"] = False
            merged[filename] = normalized
            continue
        reasons = {existing.get("reason", "")}
        if item.get("reason"):
            reasons.add(str(item["reason"]))
        existing["reason"] = "；".join(reason for reason in reasons if reason)
        existing["required"] = bool(existing.get("required")) or bool(item.get("required", True))
        existing["writable"] = bool(existing.get("writable")) or (
            bool(item.get("writable")) and filename in WRITABLE_INCREMENTAL_TARGETS
        )
        sources = {str(existing.get("source") or "supervisor"), str(item.get("source") or "supervisor")}
        existing["source"] = "+".join(sorted(sources))
    return [merged[filename] for filename in _ordered_files(set(merged))]


def _build_rule_supervisor_entries(
    requirement: str,
    current: Path,
    selected_document: str | None,
    change_type: str,
    analysis_feedback: str = "",
) -> tuple[list[dict[str, Any]], list[str]]:
    text = f"{requirement}\n{analysis_feedback}".lower()
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []

    if selected_document:
        if selected_document not in ITERABLE_TARGETS:
            raise ValueError(f"Document does not support incremental iteration: {selected_document}")
        if not (current / selected_document).is_file():
            raise FileNotFoundError(f"Selected document not found: {selected_document}")
        entries.append(_plan_entry(selected_document, "用户选中的需求入口文档", source="selected_document"))
    else:
        entries.append(_plan_entry("system_design_detail.md", "未选择入口文档，默认从系统详细案承接需求"))

    functional_keywords = ("功能", "玩法", "流程", "模式", "规则", "出售", "购买", "兑换", "使用")
    if change_type == "new_feature" and (
        selected_document == "system_design_draft.md"
        or _has_positive_keyword(text, functional_keywords)
    ):
        entries.append(_plan_entry("system_design_draft.md", "新增功能需要补充系统大纲"))
        entries.append(_plan_entry("system_design_detail.md", "新增功能需要补充系统详细规则"))

    numerical_keywords = (
        "数值", "配置", "参数", "字段", "列", "表", "价格", "定价", "成本", "收益",
        "奖励", "概率", "几率", "权重", "掉落", "产出", "消耗", "货币", "兑换",
        "购买", "买入", "出售", "卖出", "售价", "容量", "上限", "数量", "倍率",
        "成长", "属性", "冷却", "时长",
    )
    if _has_positive_keyword(text, numerical_keywords):
        entries.append(_plan_entry("system_numerical_data.json", "需求涉及数值配置或字段变更"))
        entries.append(_plan_entry(NUMERICAL_DOC_TARGET, "数值字段或参数变更必须同步补充说明"))

    ui_keywords = ("ui", "界面", "交互", "弹窗", "按钮", "表现", "点击", "预览", "选择", "勾选", "展示")
    if _has_positive_keyword(text, ui_keywords):
        entries.append(_plan_entry("ui_interaction_blueprint.md", "需求涉及界面或交互表现"))

    tech_keywords = ("接口", "协议", "schema", "程序", "技术", "服务端", "客户端", "错误码", "超时")
    if _has_positive_keyword(text, tech_keywords):
        entries.append(_plan_entry("tech_blueprint.md", "需求涉及技术实现或接口行为"))
        entries.append(_plan_entry("system_schema.json", "接口或字段可能影响结构定义，作为一致性参考", required=False, writable=False))

    if _has_positive_keyword(text, ("排期", "任务", "工期", "里程碑")):
        entries.append(_plan_entry("task_plan.md", "需求涉及执行计划或里程碑"))

    numerical = _read_json(current / "system_numerical_data.json", {})
    if isinstance(numerical, dict):
        for table in numerical:
            if str(table).lower() in text:
                entries.append(_plan_entry("system_numerical_data.json", f"需求点名数值表 {table}"))
                entries.append(_plan_entry(NUMERICAL_DOC_TARGET, f"数值表 {table} 变更需同步说明"))

    entries = _merge_plan_entries(entries, current)
    if not entries:
        warnings.append("监管规则未命中具体文档，已默认要求系统详细案")
        entries = _merge_plan_entries([_plan_entry("system_design_detail.md", "默认承接需求")], current)
    return entries, warnings


def _llm_supervisor_entries(
    requirement: str,
    current: Path,
    selected_document: str | None,
    change_type: str,
    discussion: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    from Skills.llm_client import ask_llm, safe_extract_json

    available = []
    for filename in FILE_ORDER:
        path = current / filename
        if not path.is_file():
            continue
        headings = _headings(path)[:12] if path.suffix == ".md" else []
        available.append({
            "file": filename,
            "agent": AGENT_BY_FILE.get(filename, "reference"),
            "writable": filename in WRITABLE_INCREMENTAL_TARGETS,
            "headings": headings,
        })
    prompt = f"""你是游戏项目归档迭代的监管方 PM Agent。你的职责是判断一个需求会影响哪些下属功能 Agent 和文档。
选中文档只是需求入口，不是修改边界。必须找出所有必改文档和只读参考文档。

需求：{requirement}
迭代类型：{"新增功能" if change_type == "new_feature" else "老功能迭代"}
入口文档：{selected_document or "未指定"}
需求日志：{json.dumps(discussion, ensure_ascii=False)}
可用文档：{json.dumps(available, ensure_ascii=False)}

硬性要求：
- 新增功能若影响系统大纲，必须同时要求系统详细案。
- 涉及界面、交互、按钮、弹窗、预览时，必须要求 UX 蓝图。
- 涉及数值表、字段、价格、货币、概率、冷却等时，必须要求数值数据和数值说明。
- 只读参考文档可列出，但不要标记 writable。

输出纯 JSON：
{{"files":[{{"file":"文件名","reason":"为什么受影响","agent":"负责 Agent","required":true,"writable":true}}]}}"""
    try:
        raw = ask_llm(
            "你是严谨的项目影响范围监管方，只输出 JSON。",
            prompt,
            max_tokens=2048,
            timeout_seconds=45,
            max_retries=1,
        )
        json_text, error = safe_extract_json(raw, "SupervisorImpact")
        if error or not json_text:
            return [], [error or "监管 Agent 未返回有效 JSON，已使用规则兜底"]
        result = json.loads(json_text)
    except Exception as exc:
        return [], [f"监管 Agent 调用失败，已使用规则兜底：{exc}"]
    if not isinstance(result, dict) or not isinstance(result.get("files"), list):
        return [], ["监管 Agent 输出缺少 files，已使用规则兜底"]
    entries = []
    for item in result["files"]:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("file", "")).strip()
        if not filename:
            continue
        entries.append(_plan_entry(
            filename,
            str(item.get("reason") or "监管 Agent 判断受影响"),
            required=bool(item.get("required", True)),
            writable=bool(item.get("writable", filename in WRITABLE_INCREMENTAL_TARGETS)),
            agent=str(item.get("agent") or AGENT_BY_FILE.get(filename, "pm_supervisor")),
            source="llm_supervisor",
        ))
    return _merge_plan_entries(entries, current), []


def _build_supervisor_plan(
    requirement: str,
    current: Path,
    selected_document: str | None,
    change_type: str,
    discussion: list[dict[str, Any]],
    analysis_feedback: str = "",
    previous_analysis: dict[str, Any] | None = None,
    reuse_previous: bool = False,
    use_llm: bool = True,
) -> dict[str, Any]:
    if reuse_previous and isinstance(previous_analysis, dict) and isinstance(previous_analysis.get("supervisor_plan"), dict):
        plan = dict(previous_analysis["supervisor_plan"])
        plan["reused_from"] = previous_analysis.get("change_id")
        return plan
    rule_entries, warnings = _build_rule_supervisor_entries(
        requirement,
        current,
        selected_document,
        change_type,
        analysis_feedback,
    )
    llm_entries: list[dict[str, Any]] = []
    llm_warnings: list[str] = []
    if use_llm:
        llm_entries, llm_warnings = _llm_supervisor_entries(
            requirement,
            current,
            selected_document,
            change_type,
            discussion,
        )
    files = _merge_plan_entries([*llm_entries, *rule_entries], current)
    required_files = [item["file"] for item in files if item.get("required")]
    writable_files = [item["file"] for item in files if item.get("writable")]
    reference_files = [item["file"] for item in files if not item.get("writable")]
    return {
        "agent": "pm_supervisor",
        "source": "llm_supervisor+rules" if use_llm else "rules",
        "requires_confirmation": True,
        "files": files,
        "required_files": required_files,
        "writable_files": writable_files,
        "reference_files": reference_files,
        "warnings": warnings + llm_warnings,
    }


def _targets_from_supervisor_plan(plan: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    files = [
        str(item.get("file", "")).strip()
        for item in plan.get("files", [])
        if isinstance(item, dict) and item.get("file")
    ]
    affected_files = _ordered_files(set(files))
    agents = sorted({
        str(item.get("agent") or AGENT_BY_FILE.get(str(item.get("file", "")), "pm_supervisor"))
        for item in plan.get("files", [])
        if isinstance(item, dict)
    })
    return affected_files, agents, []


def _select_targets(
    requirement: str,
    current: Path,
    selected_document: str | None = None,
    analysis_feedback: str = "",
) -> tuple[list[str], list[str], list[str]]:
    entries, _warnings = _build_rule_supervisor_entries(
        requirement,
        current,
        selected_document,
        "existing_feature",
        analysis_feedback,
    )
    return _targets_from_supervisor_plan({"files": entries})


def _dependency_graph(data_dir: str | Path) -> dict[str, list[str]]:
    projects = list_stable_projects(data_dir)
    names = {item["system_id"]: item.get("system_name", item["system_id"]) for item in projects}
    graph: dict[str, list[str]] = {system_id: [] for system_id in names}
    for project in projects:
        source_id = project["system_id"]
        current = Path(data_dir) / "projects" / source_id / "current"
        corpus = "\n".join(_read_text(path) for path in current.glob("*.md"))
        for target_id, target_name in names.items():
            if target_id != source_id and target_name and target_name in corpus:
                graph[source_id].append(target_id)
    return graph


def analyze_change(
    data_dir: str | Path,
    system_id: str,
    requirement: str,
    generate_proposal: bool = False,
    selected_document: str | None = None,
    change_type: str = "existing_feature",
    analysis_feedback: str = "",
    previous_change_id: str = "",
    impact_confirmed: bool = False,
) -> dict[str, Any]:
    project_dir, manifest = get_project(data_dir, system_id)
    if manifest.get("lifecycle") == "deleted":
        raise ValueError("Deleted projects cannot be modified")
    requirement = requirement.strip()
    if not requirement:
        raise ValueError("Requirement is empty")
    if change_type not in CHANGE_TYPES:
        raise ValueError("Change type must be new_feature or existing_feature")

    analysis_feedback = analysis_feedback.strip()
    previous_analysis = None
    if previous_change_id:
        if not re.fullmatch(r"chg_[A-Za-z0-9_]+", previous_change_id):
            raise ValueError("Invalid previous change id")
        previous_analysis = _read_json(_pending_dir(project_dir) / f"{previous_change_id}.json", None)
        if not isinstance(previous_analysis, dict):
            raise FileNotFoundError(f"上一轮分析记录已丢失: {previous_change_id}")

    if isinstance(previous_analysis, dict) and isinstance(previous_analysis.get("discussion"), list):
        discussion = list(previous_analysis["discussion"])
    else:
        discussion = [{"kind": "requirement", "content": requirement, "created_at": _now()}]
    if analysis_feedback:
        discussion.append({"kind": "feedback", "content": analysis_feedback, "created_at": _now()})

    supervisor_plan = _build_supervisor_plan(
        requirement,
        _current_dir(project_dir),
        selected_document,
        change_type,
        discussion,
        analysis_feedback,
        previous_analysis if isinstance(previous_analysis, dict) else None,
        reuse_previous=bool(impact_confirmed and previous_analysis and not analysis_feedback),
        use_llm=bool(generate_proposal),
    )
    targets, agents, tables = _targets_from_supervisor_plan(supervisor_plan)
    anchors = {
        target: _headings(_current_dir(project_dir) / target)[:30]
        for target in targets if target.endswith(".md")
    }
    graph = _dependency_graph(data_dir)
    dependents = sorted(source for source, deps in graph.items() if system_id in deps)
    change_id = f"chg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    analysis = {
        "change_id": change_id,
        "system_id": system_id,
        "system_name": manifest.get("system_name", system_id),
        "requirement": requirement,
        "analysis_feedback": analysis_feedback,
        "discussion": discussion,
        "previous_change_id": previous_change_id or None,
        "previous_preview": previous_analysis.get("preview") if isinstance(previous_analysis, dict) else None,
        "change_type": change_type,
        "selected_document": selected_document,
        "impact_confirmed": bool(impact_confirmed),
        "requires_impact_confirmation": bool(generate_proposal and not impact_confirmed),
        "created_at": _now(),
        "affected_files": targets,
        "writable_files": list(supervisor_plan.get("writable_files", [target for target in targets if target in WRITABLE_INCREMENTAL_TARGETS])),
        "reference_files": list(supervisor_plan.get("reference_files", [target for target in targets if target not in WRITABLE_INCREMENTAL_TARGETS])),
        "affected_tables": tables,
        "affected_agents": agents,
        "supervisor_plan": supervisor_plan,
        "anchors": anchors,
        "dependent_systems": dependents,
        "final_audit_required": True,
    }
    if generate_proposal and impact_confirmed:
        text_changes, numerical_operations, numerical_doc_changes = _generate_change_proposal(_current_dir(project_dir), analysis)
        analysis["proposal"] = {
            "text_changes": text_changes,
            "numerical_operations": numerical_operations,
            "numerical_doc_changes": numerical_doc_changes,
        }
        analysis["preview"] = {
            "text_changes": [
                {
                    "file": item.get("file"),
                    "anchor": item.get("anchor"),
                    "content": str(item.get("content", ""))[:500],
                    "deprecated": str(item.get("deprecated", ""))[:300],
                }
                for item in text_changes
            ],
            "numerical_operations": numerical_operations,
            "numerical_doc_changes": numerical_doc_changes,
        }
    _write_json(_pending_dir(project_dir) / f"{change_id}.json", analysis)
    if previous_change_id and previous_change_id != change_id:
        previous_path = _pending_dir(project_dir) / f"{previous_change_id}.json"
        if previous_path.exists():
            previous_path.unlink()
    return analysis


def _append_change_section(path: Path, change_id: str, requirement: str, anchor: str, content: str, deprecated: str = "") -> None:
    original = _read_text(path)
    title = requirement.strip().splitlines()[0][:80] or "系统修改"
    section = [
        "",
        "",
        f"## [新][{_date()}] {title}",
        f"> 变更编号：{change_id}；原始需求：{requirement.strip()}；影响原章节：{anchor or '由影响分析定位'}",
        "",
        "### 新增或修改内容",
        content.strip() or requirement.strip(),
    ]
    if deprecated.strip():
        section.extend(["", "### 废弃内容", deprecated.strip()])
    path.write_text(original + "\n".join(section) + "\n", encoding="utf-8")


def _records_for_table(data: dict[str, Any], table: str, create: bool = False) -> list[dict[str, Any]]:
    if table not in data:
        if not create:
            raise ValueError(f"Table not found: {table}")
        data[table] = []
    value = data[table]
    if isinstance(value, list):
        if not all(isinstance(row, dict) for row in value):
            raise ValueError(f"Table {table} is not a record list")
        return value
    if isinstance(value, dict):
        if all(isinstance(row, dict) for row in value.values()):
            rows = list(value.values())
            data[table] = rows
            return rows
        data[table] = [value]
        return data[table]
    raise ValueError(f"Table {table} cannot accept row operations")


def _match_row(row: dict[str, Any], match: dict[str, Any]) -> bool:
    return all(row.get(key) == value for key, value in match.items())


GLOBAL_NUMERICAL_TABLE_ALIASES = {
    "system_numerical_data",
    "system_numerical_data.json",
    "global",
    "globals",
    "parameters",
    "params",
}


def _is_global_numerical_table(table: str) -> bool:
    return table.strip().lower() in GLOBAL_NUMERICAL_TABLE_ALIASES


def normalize_numerical_operations(operations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    expanded_operations: list[Any] = []
    for raw in operations:
        action = raw.get("action") or raw.get("operation") or raw.get("type") if isinstance(raw, dict) else None
        columns = raw.get("columns") if isinstance(raw, dict) else None
        if action == "add_column" and isinstance(columns, list) and columns and not raw.get("column"):
            for column in columns:
                expanded = {key: value for key, value in raw.items() if key != "columns"}
                if isinstance(column, dict):
                    expanded["column"] = column.get("column") or column.get("name") or column.get("field")
                    if "default" in column:
                        expanded["default"] = column["default"]
                else:
                    expanded["column"] = column
                expanded_operations.append(expanded)
        else:
            expanded_operations.append(raw)

    for index, raw in enumerate(expanded_operations):
        if not isinstance(raw, dict):
            errors.append(f"第 {index + 1} 个数值操作必须是对象")
            continue
        operation = dict(raw)
        operation["action"] = operation.get("action") or operation.get("operation") or operation.get("type")
        operation["table"] = operation.get("table") or operation.get("table_name") or operation.get("module")
        action = operation.get("action")

        if action in {"add_column", "delete_column"}:
            operation["column"] = (
                operation.get("column")
                or operation.get("column_name")
                or operation.get("field")
                or operation.get("field_name")
                or operation.get("name")
            )
            if "default" not in operation and "default_value" in operation:
                operation["default"] = operation["default_value"]
        elif action in {"create_table", "add_rows"} and "rows" not in operation:
            operation["rows"] = operation.get("data", [])
        elif action == "update_rows":
            operation["match"] = operation.get("match") or operation.get("where")
            operation["values"] = operation.get("values") or operation.get("set")
        elif action == "delete_rows":
            operation["match"] = operation.get("match") or operation.get("where")

        label = f"第 {index + 1} 个数值操作"
        table = str(operation.get("table", "")).strip()
        column = str(operation.get("column") or "").strip()
        if action not in NUMERICAL_OPERATIONS:
            errors.append(f"{label}的 action 无效")
        elif not table:
            errors.append(f"{label}缺少 table")
        elif action in {"add_column", "delete_column"} and not column:
            errors.append(f"{label}缺少 column")
        elif action in {"create_table", "add_rows"} and (
            not isinstance(operation.get("rows"), list)
            or not all(isinstance(row, dict) for row in operation["rows"])
        ):
            errors.append(f"{label}的 rows 必须是对象数组")
        elif action == "update_rows" and (
            not isinstance(operation.get("match"), dict)
            or not operation["match"]
            or not isinstance(operation.get("values"), dict)
        ):
            errors.append(f"{label}需要非空 match 和对象 values")
        elif action == "delete_rows" and (
            not isinstance(operation.get("match"), dict) or not operation["match"]
        ):
            errors.append(f"{label}需要非空 match")
        else:
            operation["table"] = table
            if action in {"add_column", "delete_column"}:
                operation["column"] = column
            normalized.append(operation)
    return normalized, errors


def apply_numerical_operations(data: dict[str, Any], operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for operation in operations:
        action = operation.get("action")
        table = str(operation.get("table", "")).strip()
        if action not in NUMERICAL_OPERATIONS or not table:
            raise ValueError(f"Invalid numerical operation: {operation}")

        count = 0
        if _is_global_numerical_table(table):
            if action == "add_column":
                column = str(operation.get("column", "")).strip()
                if not column:
                    raise ValueError("add_column requires column")
                if column not in data:
                    data[column] = operation.get("default")
                    count = 1
            elif action == "delete_column":
                column = str(operation.get("column", "")).strip()
                if column in data:
                    del data[column]
                    count = 1
            elif action == "update_rows":
                values = operation.get("values", {})
                if not isinstance(values, dict) or not values:
                    raise ValueError("global update_rows requires object values")
                data.update(values)
                count = len(values)
            else:
                raise ValueError(f"{action} cannot target global numerical parameters")
        elif action == "create_table":
            if table in data:
                raise ValueError(f"Table already exists: {table}")
            rows = operation.get("rows", [])
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise ValueError("create_table rows must be a list of objects")
            data[table] = rows
            count = len(rows)
        elif action == "add_column":
            column = str(operation.get("column", "")).strip()
            if not column:
                raise ValueError("add_column requires column")
            for row in _records_for_table(data, table):
                if column not in row:
                    row[column] = operation.get("default")
                    count += 1
        elif action == "delete_column":
            column = str(operation.get("column", "")).strip()
            for row in _records_for_table(data, table):
                if column in row:
                    del row[column]
                    count += 1
        elif action == "add_rows":
            rows = operation.get("rows", [])
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise ValueError("add_rows rows must be a list of objects")
            _records_for_table(data, table).extend(rows)
            count = len(rows)
        elif action == "update_rows":
            match = operation.get("match", {})
            values = operation.get("values", {})
            if not isinstance(match, dict) or not isinstance(values, dict) or not match:
                raise ValueError("update_rows requires non-empty match and values")
            for row in _records_for_table(data, table):
                if _match_row(row, match):
                    row.update(values)
                    count += 1
        elif action == "delete_rows":
            match = operation.get("match", {})
            if not isinstance(match, dict) or not match:
                raise ValueError("delete_rows requires non-empty match")
            rows = _records_for_table(data, table)
            kept = [row for row in rows if not _match_row(row, match)]
            count = len(rows) - len(kept)
            data[table] = kept
        results.append({"action": action, "table": table, "count": count})
    return results


def apply_numerical_doc_changes(docs: dict[str, Any], changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError("numerical_doc_changes entries must be objects")
        table = str(change.get("table") or change.get("scope") or "").strip()
        field = str(
            change.get("field")
            or change.get("column")
            or change.get("parameter")
            or change.get("name")
            or ""
        ).strip()
        description = str(
            change.get("description")
            or change.get("content")
            or change.get("comment")
            or ""
        ).strip()
        if not field and not description:
            raise ValueError("numerical_doc_changes requires field or description")
        key = "global_parameters" if not table or _is_global_numerical_table(table) else table
        existing = docs.get(key)
        if isinstance(existing, dict):
            section = existing
        elif isinstance(existing, str):
            section = {"description": existing}
            docs[key] = section
        elif existing is None:
            section = {}
            docs[key] = section
        else:
            section = {"description": str(existing)}
            docs[key] = section
        if field:
            section[field] = description or field
        else:
            notes = section.setdefault("_notes", [])
            if not isinstance(notes, list):
                notes = [str(notes)]
                section["_notes"] = notes
            notes.append(description)
        results.append({"table": key, "field": field or "_notes"})
    return results


def _compact_context(content: str, limit: int) -> str:
    if len(content) <= limit:
        return content
    head = int(limit * 0.65)
    tail = limit - head
    return content[:head] + "\n\n...[中间内容已省略，禁止据此重写全文]...\n\n" + content[-tail:]


def _generate_change_proposal(current: Path, analysis: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Ask the affected roles for a scoped patch proposal, never a full-document rewrite."""
    from Skills.llm_client import ask_llm, safe_extract_json

    context_parts: list[str] = []
    remaining_budget = 36000
    selected_document = analysis.get("selected_document")
    for filename in analysis.get("affected_files", []):
        if remaining_budget <= 0:
            break
        path = current / filename
        if path.suffix == ".md":
            content = _read_text(path)
        else:
            value = _read_json(path, {})
            content = json.dumps(value, ensure_ascii=False, indent=2)
        per_file_limit = 14000 if filename == selected_document else 7000
        per_file_limit = min(per_file_limit, remaining_budget)
        compacted = _compact_context(content, per_file_limit)
        context_parts.append(f"<{filename}>\n{compacted}\n</{filename}>")
        remaining_budget -= len(compacted)

    system_prompt = """你是游戏研发项目的增量修改协调器。
你必须只针对批准的影响范围生成局部变更，禁止重写全文。
文本修改只输出要追加到原文末尾的新增/修改内容与废弃说明。
数值操作只能使用 create_table、add_column、add_rows、update_rows、delete_rows、delete_column。
删除文本内容时写入 deprecated；删除数值时使用 delete_rows 或 delete_column。
只允许修改“可写文件”，只读参考文件仅用于判断依赖和一致性，禁止出现在修改方案中。
用户选中的主文档必须出现在修改方案中。
如果可写文件包含 system_numerical_data.json，必须根据需求输出至少一个格式完整的 numerical_operations 操作。
如果可写文件包含 system_numerical_docs.json，且数值操作新增/删除/修改了表、字段或顶层参数，必须输出 numerical_doc_changes 同步说明。
监管方标记为必改的 Markdown 文档必须都出现在 text_changes 中。
输出纯 JSON，不要 Markdown 代码块。"""
    user_prompt = f"""修改需求：
{analysis['requirement']}

需求与补充意见日志：{json.dumps(analysis.get("discussion", []), ensure_ascii=False)}
上一轮变更预览：{json.dumps(analysis.get("previous_preview"), ensure_ascii=False) if analysis.get("previous_preview") else "无"}
迭代类型：{"新增功能" if analysis.get("change_type") == "new_feature" else "老功能迭代"}
用户选中的主文档：{analysis.get("selected_document") or "未指定"}
受影响 Agent：{', '.join(analysis.get('affected_agents', []))}
可写文件：{', '.join(analysis.get('writable_files', []))}
只读参考文件：{', '.join(analysis.get('reference_files', [])) or "无"}
监管拆分结果：{json.dumps(analysis.get('supervisor_plan', {}), ensure_ascii=False)}
定位到的章节：{json.dumps(analysis.get('anchors', {}), ensure_ascii=False)}

当前内容：
{chr(10).join(context_parts)}

输出格式：
{{
  "text_changes": [
    {{"file": "批准的Markdown文件", "anchor": "原章节标题", "content": "仅新增或修改内容", "deprecated": "需要废弃的旧内容说明，可空"}}
  ],
  "numerical_operations": [
    {{"action": "六种操作之一", "table": "表名", "...": "该操作需要的字段"}}
  ],
  "numerical_doc_changes": [
    {{"table": "表名或 system_numerical_data", "field": "字段/参数名", "description": "字段含义、类型、默认值、配置规则"}}
  ]
}}"""
    raw = ask_llm(
        system_prompt,
        user_prompt,
        max_tokens=4096,
        timeout_seconds=90,
        max_retries=1,
    )
    json_text, error = safe_extract_json(raw, "IncrementalChange")
    if error or not json_text:
        raise ValueError(error or "AI 未生成有效的增量修改方案")
    try:
        proposal = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI 返回的修改方案不是有效 JSON，请重试分析: {exc.msg}") from exc
    if not isinstance(proposal, dict):
        raise ValueError("AI 增量修改方案必须是 JSON 对象")
    text_changes = proposal.get("text_changes", [])
    numerical_operations = proposal.get("numerical_operations", [])
    numerical_doc_changes = proposal.get("numerical_doc_changes", [])
    if not isinstance(text_changes, list) or not isinstance(numerical_operations, list) or not isinstance(numerical_doc_changes, list):
        raise ValueError("AI 增量修改方案字段格式错误")
    approved_files = set(analysis.get("writable_files", analysis.get("affected_files", [])))
    proposal_warnings: list[str] = []
    numerical_operations, numerical_errors = normalize_numerical_operations(numerical_operations)
    if numerical_errors:
        proposal_warnings.extend(f"数值方案不完整：{error}" for error in numerical_errors)
    approved_text_changes: list[dict[str, Any]] = []
    for item in text_changes:
        filename = str(item.get("file", "")).strip() if isinstance(item, dict) else ""
        if filename not in TEXT_TARGETS or filename not in approved_files:
            proposal_warnings.append(f"已忽略未批准的文本修改: {filename or '未知文件'}")
            continue
        approved_text_changes.append(item)
    text_changes = approved_text_changes
    if numerical_operations and "system_numerical_data.json" not in approved_files:
        proposal_warnings.append("已忽略未批准的数值修改")
        numerical_operations = []
    if "system_numerical_data.json" in approved_files and not numerical_operations:
        proposal_warnings.append("影响范围包含数值配置，但模型未生成数值操作；请补充分析意见后重新分析")
        analysis["proposal_incomplete"] = True
    approved_doc_changes: list[dict[str, Any]] = []
    for item in numerical_doc_changes:
        if isinstance(item, dict):
            approved_doc_changes.append(item)
        else:
            proposal_warnings.append("已忽略格式错误的数值说明修改")
    numerical_doc_changes = approved_doc_changes
    if numerical_doc_changes and NUMERICAL_DOC_TARGET not in approved_files:
        proposal_warnings.append("已忽略未批准的数值说明修改")
        numerical_doc_changes = []
    if numerical_operations and NUMERICAL_DOC_TARGET in approved_files and not numerical_doc_changes:
        proposal_warnings.append("数值数据存在变更，但模型未同步补充数值说明")
        analysis["proposal_incomplete"] = True
    if proposal_warnings:
        analysis["proposal_warnings"] = proposal_warnings

    required_text_files = [
        item.get("file")
        for item in analysis.get("supervisor_plan", {}).get("files", [])
        if isinstance(item, dict) and item.get("required") and item.get("file") in TEXT_TARGETS
    ]
    for filename in required_text_files:
        if not any(isinstance(item, dict) and item.get("file") == filename for item in text_changes):
            proposal_warnings.append(f"必改文档缺少文本变更: {filename}")
            analysis["proposal_incomplete"] = True
    if selected_document == "system_numerical_data.json" and not numerical_operations:
        analysis["proposal_incomplete"] = True
    if proposal_warnings:
        analysis["proposal_warnings"] = proposal_warnings
    return text_changes, numerical_operations, numerical_doc_changes


def _has_required_proposal_changes(
    analysis: dict[str, Any],
    text_changes: list[dict[str, Any]],
    numerical_operations: list[dict[str, Any]],
    numerical_doc_changes: list[dict[str, Any]] | None = None,
) -> bool:
    numerical_doc_changes = numerical_doc_changes or []
    if not text_changes and not numerical_operations:
        return False
    selected_document = str(analysis.get("selected_document") or "")
    for item in analysis.get("supervisor_plan", {}).get("files", []):
        if not isinstance(item, dict) or not item.get("required"):
            continue
        filename = str(item.get("file", ""))
        if filename in TEXT_TARGETS and not any(
            isinstance(change, dict) and change.get("file") == filename
            for change in text_changes
        ):
            return False
    writable_files = set(analysis.get("writable_files", analysis.get("affected_files", [])))
    if "system_numerical_data.json" in writable_files and not numerical_operations:
        return False
    if numerical_operations and NUMERICAL_DOC_TARGET in writable_files and not numerical_doc_changes:
        return False
    if selected_document == "system_numerical_data.json" and not numerical_operations:
        return False
    return True


def _duplicate_ids(value: Any, path: str = "$") -> list[str]:
    issues: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            issues.extend(_duplicate_ids(child, f"{path}.{key}"))
    elif isinstance(value, list):
        values: list[Any] = []
        for child in value:
            if isinstance(child, dict):
                id_key = next((key for key in child if key == "id" or key.endswith("_id")), None)
                if id_key is not None:
                    values.append(child[id_key])
            issues.extend(_duplicate_ids(child, path))
        duplicates = [item for item, count in Counter(values).items() if count > 1]
        issues.extend(f"{path}: duplicate id {item}" for item in duplicates)
    return issues


def _validate_project(current: Path) -> dict[str, Any]:
    issues: list[str] = []
    for path in current.glob("*.json"):
        value = _read_json(path, None)
        if value is None:
            issues.append(f"{path.name}: invalid JSON")
        elif path.name == "system_numerical_data.json":
            issues.extend(_duplicate_ids(value))
    if not (current / "system_design_detail.md").is_file():
        issues.append("system_design_detail.md is required")
    if issues:
        raise ValueError("Final audit failed: " + "; ".join(issues))
    return {"ok": True, "issues": [], "audited_at": _now(), "source": "deterministic_final_audit"}


def _llm_final_audit(current: Path, analysis: dict[str, Any]) -> dict[str, Any]:
    from Skills.llm_client import ask_llm, safe_extract_json

    context: list[str] = []
    for filename in analysis.get("affected_files", []):
        path = current / filename
        content = _read_text(path) if path.suffix == ".md" else json.dumps(_read_json(path, {}), ensure_ascii=False, indent=2)
        context.append(f"<{filename}>\n{content[:16000]}\n</{filename}>")
    prompt = f"""原始修改需求：
{analysis['requirement']}

用户补充的分析意见：{analysis.get("analysis_feedback") or "无"}
迭代类型：{"新增功能" if analysis.get("change_type") == "new_feature" else "老功能迭代"}
用户选中的主文档：{analysis.get("selected_document") or "未指定"}
请只检查以下修改后文件是否满足原始需求、是否跨文档矛盾、是否出现字段或接口断链。
{chr(10).join(context)}

输出纯 JSON：
{{"status":"pass 或 reject","issues":[{{"file":"文件名","problem":"问题","suggestion":"修复建议"}}]}}"""
    raw = ask_llm("你是最终一致性审计官。不得扩写需求，只判断局部修改是否一致且可执行。", prompt, max_tokens=4096)
    json_text, error = safe_extract_json(raw, "IncrementalFinalAudit")
    if error or not json_text:
        raise ValueError(error or "LLM 终审未返回有效结果")
    result = json.loads(json_text)
    if not isinstance(result, dict) or result.get("status") != "pass":
        raise ValueError("LLM final audit failed: " + json.dumps(result.get("issues", []), ensure_ascii=False))
    return {"ok": True, "issues": [], "audited_at": _now(), "source": "llm_cross_document_final_audit"}


def _copy_staging_to_current(project_dir: Path, staging: Path) -> None:
    current = _current_dir(project_dir)
    old_current = project_dir / ".current-old"
    if old_current.exists():
        shutil.rmtree(old_current)
    os.replace(current, old_current)
    try:
        os.replace(staging, current)
    except Exception:
        os.replace(old_current, current)
        raise
    shutil.rmtree(old_current)


def _stage_excel_operations(
    data_dir: Path,
    operations: list[dict[str, Any]],
    staging_dir: Path,
) -> list[str]:
    staged: list[str] = []
    excel_dir = data_dir / "Excel"
    staging_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        str(item.get("table", "")).strip()
        for item in operations
        if item.get("table") and not _is_global_numerical_table(str(item.get("table", "")).strip())
    }
    for table in sorted(tables):
        source = excel_dir / f"{table}.json"
        existing = _read_json(source, {})
        if isinstance(existing, dict) and isinstance(existing.get("data"), list):
            wrapper = {table: existing["data"]}
            metadata = existing.get("_metadata", {"module": table, "fields": {}})
            output_wrapped = True
        else:
            wrapper = {table: existing} if existing else {}
            metadata = {"module": table, "fields": {}}
            output_wrapped = False
        table_operations = [item for item in operations if str(item.get("table", "")).strip() == table]
        apply_numerical_operations(wrapper, table_operations)
        output = {"_metadata": metadata, "data": wrapper[table]}
        _write_json(staging_dir / f"{table}.json", output)
        staged.append(table)
    return staged


def _commit_project_and_excel(
    data_dir: Path,
    project_dir: Path,
    project_staging: Path,
    excel_staging: Path,
) -> None:
    current = _current_dir(project_dir)
    current_backup = project_dir / ".current-old"
    excel_dir = data_dir / "Excel"
    excel_dir.mkdir(parents=True, exist_ok=True)
    excel_backups: list[tuple[Path, Path | None]] = []
    if current_backup.exists():
        shutil.rmtree(current_backup)
    os.replace(current, current_backup)
    try:
        for staged in excel_staging.glob("*.json"):
            destination = excel_dir / staged.name
            backup = excel_staging / f".{staged.name}.bak" if destination.exists() else None
            if backup:
                os.replace(destination, backup)
            excel_backups.append((destination, backup))
            os.replace(staged, destination)
        os.replace(project_staging, current)
    except Exception:
        if current.exists():
            shutil.rmtree(current)
        os.replace(current_backup, current)
        for destination, backup in reversed(excel_backups):
            if destination.exists():
                destination.unlink()
            if backup and backup.exists():
                os.replace(backup, destination)
        raise
    shutil.rmtree(current_backup)
    for _destination, backup in excel_backups:
        if backup and backup.exists():
            backup.unlink()


def apply_change(
    data_dir: str | Path,
    system_id: str,
    change_id: str,
    text_changes: list[dict[str, Any]] | None = None,
    numerical_operations: list[dict[str, Any]] | None = None,
    numerical_doc_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    project_dir, manifest = get_project(data_dir, system_id)
    analysis = _read_json(_pending_dir(project_dir) / f"{change_id}.json", None)
    if not isinstance(analysis, dict):
        raise FileNotFoundError(f"Pending change not found: {change_id}")

    text_changes = text_changes or []
    numerical_operations = numerical_operations or []
    numerical_doc_changes = numerical_doc_changes or []
    if not text_changes and not numerical_operations and not numerical_doc_changes:
        proposal = analysis.get("proposal", {})
        text_changes = proposal.get("text_changes", []) if isinstance(proposal, dict) else []
        numerical_operations = proposal.get("numerical_operations", []) if isinstance(proposal, dict) else []
        numerical_doc_changes = proposal.get("numerical_doc_changes", []) if isinstance(proposal, dict) else []
    if not text_changes and not numerical_operations and not numerical_doc_changes:
        text_changes, numerical_operations, numerical_doc_changes = _generate_change_proposal(_current_dir(project_dir), analysis)
    numerical_operations, numerical_errors = normalize_numerical_operations(numerical_operations)
    if numerical_errors:
        raise ValueError("数值变更方案不完整，请重新分析：" + "；".join(numerical_errors))
    if not _has_required_proposal_changes(
        analysis,
        text_changes,
        numerical_operations,
        numerical_doc_changes,
    ):
        raise ValueError("当前修改方案存在已知遗漏，请补充意见并重新分析后再应用")
    writable_files = analysis.get("writable_files", analysis.get("affected_files", []))
    if numerical_operations and "system_numerical_data.json" not in writable_files:
        raise ValueError("Numerical operations are outside the approved impact scope")
    if numerical_doc_changes and NUMERICAL_DOC_TARGET not in writable_files:
        raise ValueError("Numerical doc changes are outside the approved impact scope")

    staging = Path(tempfile.mkdtemp(prefix=".change-", dir=project_dir))
    excel_staging = Path(tempfile.mkdtemp(prefix=".excel-change-", dir=project_dir))
    started = time.perf_counter()
    try:
        _copy_artifacts(_current_dir(project_dir), staging)
        applied_text: list[str] = []
        for change in text_changes:
            filename = str(change.get("file", "")).strip()
            if filename not in TEXT_TARGETS or filename not in writable_files:
                raise ValueError(f"Text change is outside approved impact scope: {filename}")
            _append_change_section(
                staging / filename,
                change_id,
                analysis["requirement"],
                str(change.get("anchor", "")),
                str(change.get("content", "")),
                str(change.get("deprecated", "")),
            )
            applied_text.append(filename)

        numerical_results: list[dict[str, Any]] = []
        if numerical_operations:
            numerical_path = staging / "system_numerical_data.json"
            numerical = _read_json(numerical_path, {})
            if not isinstance(numerical, dict):
                raise ValueError("system_numerical_data.json must contain an object")
            numerical_results = apply_numerical_operations(numerical, numerical_operations)
            _write_json(numerical_path, numerical)
        numerical_doc_results: list[dict[str, Any]] = []
        if numerical_doc_changes:
            numerical_docs_path = staging / NUMERICAL_DOC_TARGET
            numerical_docs = _read_json(numerical_docs_path, {})
            if not isinstance(numerical_docs, dict):
                numerical_docs = {}
            numerical_doc_results = apply_numerical_doc_changes(numerical_docs, numerical_doc_changes)
            _write_json(numerical_docs_path, numerical_docs)
        staged_tables = _stage_excel_operations(Path(data_dir), numerical_operations, excel_staging) if numerical_operations else []

        deterministic_audit = _validate_project(staging)
        audit = {
            "deterministic": deterministic_audit,
            "semantic": _llm_final_audit(staging, analysis) if analysis.get("proposal") else None,
        }
        history_entry = _snapshot_current(project_dir, manifest, "incremental_change", {
            "change_id": change_id,
            "requirement": analysis["requirement"],
            "analysis_feedback": analysis.get("analysis_feedback", ""),
            "change_type": analysis.get("change_type", "existing_feature"),
            "selected_document": analysis.get("selected_document"),
            "affected_files": analysis.get("affected_files", []),
            "affected_agents": analysis.get("affected_agents", []),
            "supervisor_plan": analysis.get("supervisor_plan", {}),
        })
        excel_snapshot = _history_dir(project_dir) / history_entry["id"] / "excel_snapshot"
        snapshot_index: dict[str, bool] = {}
        for table in staged_tables:
            source = Path(data_dir) / "Excel" / f"{table}.json"
            snapshot_index[table] = source.is_file()
            if source.is_file():
                excel_snapshot.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, excel_snapshot / source.name)
        if staged_tables:
            _write_json(excel_snapshot / "index.json", snapshot_index)
        _commit_project_and_excel(Path(data_dir), project_dir, staging, excel_staging)

        next_revision = int(manifest.get("revision", 0)) + 1
        manifest.update({
            "revision": next_revision,
            "updated_at": _now(),
            "latest_change": change_id,
        })
        _write_json(_manifest_path(project_dir), manifest)
        result = {
            "ok": True,
            "change_id": change_id,
            "revision": next_revision,
            "change_type": analysis.get("change_type", "existing_feature"),
            "selected_document": analysis.get("selected_document"),
            "text_files": applied_text,
            "numerical_changes": numerical_results,
            "numerical_doc_changes": numerical_doc_results,
            "excel_tables": staged_tables,
            "audit": audit,
            "history_id": history_entry["id"],
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "agents": analysis.get("affected_agents", []),
            "token_usage": None,
        }
        _write_json(_history_dir(project_dir) / history_entry["id"] / "result.json", result)
        pending = _pending_dir(project_dir) / f"{change_id}.json"
        if pending.exists():
            pending.unlink()
        return result
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if excel_staging.exists():
            shutil.rmtree(excel_staging)


def rollback_project(data_dir: str | Path, system_id: str, history_id: str) -> dict[str, Any]:
    project_dir, manifest = get_project(data_dir, system_id)
    target_entry = next(
        (entry for entry in manifest.get("history", []) if entry.get("id") == history_id),
        None,
    )
    if not isinstance(target_entry, dict):
        raise FileNotFoundError(f"历史版本记录已丢失: {history_id}")
    snapshot = _history_dir(project_dir) / history_id / "snapshot"
    if not snapshot.is_dir():
        raise FileNotFoundError(f"历史版本快照已丢失: {history_id}")
    target_revision = int(target_entry.get("revision", 0))
    staging = Path(tempfile.mkdtemp(prefix=".rollback-", dir=project_dir))
    try:
        _copy_artifacts(snapshot, staging)
        project_meta = _read_json(staging / "project_meta.json", {})
        if isinstance(project_meta, dict):
            project_meta["version"] = f"r{target_revision}"
            _write_json(staging / "project_meta.json", project_meta)
        audit = _validate_project(staging)
        _copy_staging_to_current(project_dir, staging)
        excel_snapshot = _history_dir(project_dir) / history_id / "excel_snapshot"
        if excel_snapshot.is_dir():
            excel_dir = Path(data_dir) / "Excel"
            excel_dir.mkdir(parents=True, exist_ok=True)
            snapshot_index = _read_json(excel_snapshot / "index.json", {})
            for table, existed in snapshot_index.items():
                destination = excel_dir / f"{table}.json"
                if not existed and destination.exists():
                    destination.unlink()
            for source in excel_snapshot.glob("*.json"):
                if source.name == "index.json":
                    continue
                shutil.copy2(source, excel_dir / source.name)
        manifest["history"] = [
            entry for entry in manifest.get("history", [])
            if int(entry.get("revision", 0)) < target_revision
        ]
        manifest.update({
            "revision": target_revision,
            "updated_at": _now(),
            "latest_change": f"restored:{history_id}",
        })
        _write_json(_manifest_path(project_dir), manifest)
        return {"ok": True, "revision": target_revision, "restored": history_id, "audit": audit}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def set_lifecycle(data_dir: str | Path, system_id: str, lifecycle: str) -> dict[str, Any]:
    if lifecycle not in {"active", "deprecated", "deleted"}:
        raise ValueError("Invalid lifecycle")
    project_dir, manifest = get_project(data_dir, system_id)
    if lifecycle == "deleted":
        graph = _dependency_graph(data_dir)
        dependents = [source for source, dependencies in graph.items() if system_id in dependencies]
        if dependents:
            raise ValueError(f"Project is still referenced by: {', '.join(dependents)}")
    manifest["lifecycle"] = lifecycle
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(project_dir), manifest)
    return manifest
