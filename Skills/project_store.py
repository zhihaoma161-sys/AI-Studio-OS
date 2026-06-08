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
        files = sorted(path.name for path in _current_dir(project_dir).iterdir()) if _current_dir(project_dir).is_dir() else []
        item = dict(manifest)
        item["files"] = files
        item["history_count"] = len(manifest.get("history", []))
        result.append(item)
    return sorted(result, key=lambda item: item.get("updated_at", ""), reverse=True)


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


def _select_targets(requirement: str, current: Path) -> tuple[list[str], list[str], list[str]]:
    text = requirement.lower()
    targets: set[str] = {"system_design_detail.md"}
    agents: set[str] = {"system_planner"}
    tables: set[str] = set()

    keyword_targets = {
        "数值": ({"system_numerical_data.json", "system_numerical_docs.json"}, {"numerical_planner"}),
        "配置": ({"system_numerical_data.json", "system_numerical_docs.json"}, {"numerical_planner"}),
        "表": ({"system_numerical_data.json", "system_numerical_docs.json"}, {"numerical_planner"}),
        "接口": ({"system_schema.json", "tech_blueprint.md"}, {"schema_translator", "tech_architect"}),
        "程序": ({"tech_blueprint.md"}, {"tech_architect"}),
        "技术": ({"tech_blueprint.md"}, {"tech_architect"}),
        "ui": ({"ui_interaction_blueprint.md"}, {"ux_agent"}),
        "界面": ({"ui_interaction_blueprint.md"}, {"ux_agent"}),
        "交互": ({"ui_interaction_blueprint.md"}, {"ux_agent"}),
        "排期": ({"task_plan.md"}, {"task_planner"}),
    }
    for keyword, (files, owners) in keyword_targets.items():
        if keyword in text:
            targets.update(files)
            agents.update(owners)

    numerical = _read_json(current / "system_numerical_data.json", {})
    if isinstance(numerical, dict):
        for table in numerical:
            if str(table).lower() in text:
                tables.add(str(table))
                targets.update({"system_numerical_data.json", "system_numerical_docs.json"})
                agents.add("numerical_planner")

    existing_targets = [target for target in sorted(targets) if (current / target).is_file()]
    return existing_targets, sorted(agents), sorted(tables)


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
) -> dict[str, Any]:
    project_dir, manifest = get_project(data_dir, system_id)
    if manifest.get("lifecycle") == "deleted":
        raise ValueError("Deleted projects cannot be modified")
    requirement = requirement.strip()
    if not requirement:
        raise ValueError("Requirement is empty")

    targets, agents, tables = _select_targets(requirement, _current_dir(project_dir))
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
        "created_at": _now(),
        "affected_files": targets,
        "affected_tables": tables,
        "affected_agents": agents,
        "anchors": anchors,
        "dependent_systems": dependents,
        "final_audit_required": True,
    }
    if generate_proposal:
        text_changes, numerical_operations = _generate_change_proposal(_current_dir(project_dir), analysis)
        analysis["proposal"] = {
            "text_changes": text_changes,
            "numerical_operations": numerical_operations,
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
        }
    _write_json(_pending_dir(project_dir) / f"{change_id}.json", analysis)
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


def apply_numerical_operations(data: dict[str, Any], operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for operation in operations:
        action = operation.get("action")
        table = str(operation.get("table", "")).strip()
        if action not in NUMERICAL_OPERATIONS or not table:
            raise ValueError(f"Invalid numerical operation: {operation}")

        count = 0
        if action == "create_table":
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


def _generate_change_proposal(current: Path, analysis: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Ask the affected roles for a scoped patch proposal, never a full-document rewrite."""
    from Skills.llm_client import ask_llm, safe_extract_json

    context_parts: list[str] = []
    for filename in analysis.get("affected_files", []):
        path = current / filename
        if path.suffix == ".md":
            content = _read_text(path)
        else:
            value = _read_json(path, {})
            content = json.dumps(value, ensure_ascii=False, indent=2)
        context_parts.append(f"<{filename}>\n{content[:18000]}\n</{filename}>")

    system_prompt = """你是游戏研发项目的增量修改协调器。
你必须只针对批准的影响范围生成局部变更，禁止重写全文。
文本修改只输出要追加到原文末尾的新增/修改内容与废弃说明。
数值操作只能使用 create_table、add_column、add_rows、update_rows、delete_rows、delete_column。
删除文本内容时写入 deprecated；删除数值时使用 delete_rows 或 delete_column。
输出纯 JSON，不要 Markdown 代码块。"""
    user_prompt = f"""修改需求：
{analysis['requirement']}

受影响 Agent：{', '.join(analysis.get('affected_agents', []))}
批准修改的文件：{', '.join(analysis.get('affected_files', []))}
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
  ]
}}"""
    raw = ask_llm(system_prompt, user_prompt, max_tokens=8192)
    json_text, error = safe_extract_json(raw, "IncrementalChange")
    if error or not json_text:
        raise ValueError(error or "AI 未生成有效的增量修改方案")
    proposal = json.loads(json_text)
    if not isinstance(proposal, dict):
        raise ValueError("AI 增量修改方案必须是 JSON 对象")
    text_changes = proposal.get("text_changes", [])
    numerical_operations = proposal.get("numerical_operations", [])
    if not isinstance(text_changes, list) or not isinstance(numerical_operations, list):
        raise ValueError("AI 增量修改方案字段格式错误")
    return text_changes, numerical_operations


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
    for table in sorted({str(item.get("table", "")).strip() for item in operations if item.get("table")}):
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
) -> dict[str, Any]:
    project_dir, manifest = get_project(data_dir, system_id)
    analysis = _read_json(_pending_dir(project_dir) / f"{change_id}.json", None)
    if not isinstance(analysis, dict):
        raise FileNotFoundError(f"Pending change not found: {change_id}")

    text_changes = text_changes or []
    numerical_operations = numerical_operations or []
    if not text_changes and not numerical_operations:
        proposal = analysis.get("proposal", {})
        text_changes = proposal.get("text_changes", []) if isinstance(proposal, dict) else []
        numerical_operations = proposal.get("numerical_operations", []) if isinstance(proposal, dict) else []
    if not text_changes and not numerical_operations:
        text_changes, numerical_operations = _generate_change_proposal(_current_dir(project_dir), analysis)
    if numerical_operations and "system_numerical_data.json" not in analysis.get("affected_files", []):
        raise ValueError("Numerical operations are outside the approved impact scope")

    staging = Path(tempfile.mkdtemp(prefix=".change-", dir=project_dir))
    excel_staging = Path(tempfile.mkdtemp(prefix=".excel-change-", dir=project_dir))
    started = time.perf_counter()
    try:
        _copy_artifacts(_current_dir(project_dir), staging)
        applied_text: list[str] = []
        for change in text_changes:
            filename = str(change.get("file", "")).strip()
            if filename not in TEXT_TARGETS or filename not in analysis.get("affected_files", []):
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
        staged_tables = _stage_excel_operations(Path(data_dir), numerical_operations, excel_staging) if numerical_operations else []

        deterministic_audit = _validate_project(staging)
        audit = {
            "deterministic": deterministic_audit,
            "semantic": _llm_final_audit(staging, analysis) if analysis.get("proposal") else None,
        }
        history_entry = _snapshot_current(project_dir, manifest, "incremental_change", {
            "change_id": change_id,
            "requirement": analysis["requirement"],
            "affected_files": analysis.get("affected_files", []),
            "affected_agents": analysis.get("affected_agents", []),
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
            "text_files": applied_text,
            "numerical_changes": numerical_results,
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
    snapshot = _history_dir(project_dir) / history_id / "snapshot"
    if not snapshot.is_dir():
        raise FileNotFoundError(f"History snapshot not found: {history_id}")
    staging = Path(tempfile.mkdtemp(prefix=".rollback-", dir=project_dir))
    try:
        _copy_artifacts(snapshot, staging)
        audit = _validate_project(staging)
        _snapshot_current(project_dir, manifest, "pre_rollback", {"rollback_target": history_id})
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
        manifest.update({
            "revision": int(manifest.get("revision", 0)) + 1,
            "updated_at": _now(),
            "latest_change": f"rollback:{history_id}",
        })
        _write_json(_manifest_path(project_dir), manifest)
        return {"ok": True, "revision": manifest["revision"], "restored": history_id, "audit": audit}
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
