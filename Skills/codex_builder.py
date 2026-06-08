"""Build project memory from stable archives and manage project standards."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from Skills.project_store import list_stable_projects, migrate_legacy_projects


HEADING_PATTERN = re.compile(r"^(#{2,4})\s+(.+?)\s*$", re.MULTILINE)
INTERFACE_PATTERN = re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+(/[A-Za-z0-9_./{}:-]+)")
TERM_PATTERN = re.compile(r"(?:名词|术语|定义|概念)")


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def standards_path(data_dir: str | Path) -> Path:
    return Path(data_dir) / "Knowledge" / "project_standards.json"


def load_standards(data_dir: str | Path) -> dict[str, list[dict[str, Any]]]:
    value = _read_json(standards_path(data_dir), {})
    if not isinstance(value, dict):
        value = {}
    value.setdefault("approved", [])
    value.setdefault("candidates", [])
    value.setdefault("rejected_ids", [])
    return value


def approve_standard(data_dir: str | Path, candidate_id: str, approved: bool) -> dict[str, list[dict[str, Any]]]:
    standards = load_standards(data_dir)
    candidate = next((item for item in standards["candidates"] if item.get("id") == candidate_id), None)
    if not candidate:
        raise FileNotFoundError(f"Candidate not found: {candidate_id}")
    standards["candidates"] = [item for item in standards["candidates"] if item.get("id") != candidate_id]
    if approved:
        approved_item = dict(candidate)
        approved_item["approved_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        standards["approved"].append(approved_item)
    else:
        standards["rejected_ids"].append(candidate_id)
    _write_json(standards_path(data_dir), standards)
    return standards


def _table_summary(path: Path) -> dict[str, Any] | None:
    value = _read_json(path, None)
    if value is None:
        return None
    if isinstance(value, dict) and isinstance(value.get("data"), list):
        rows = value["data"]
    elif isinstance(value, list):
        rows = value
    elif isinstance(value, dict):
        rows = [value]
    else:
        return None
    fields: set[str] = set()
    ids: list[int | float | str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        fields.update(row.keys())
        id_key = next((key for key in row if key == "id" or key.endswith("_id")), None)
        if id_key is not None:
            ids.append(row[id_key])
    numeric_ids = [item for item in ids if isinstance(item, (int, float))]
    id_range = f"{min(numeric_ids)} ~ {max(numeric_ids)}" if numeric_ids else ""
    return {"name": path.name, "rows": len(rows), "fields": sorted(fields), "id_range": id_range}


def _generate_candidates(project_data: list[dict[str, Any]], approved_ids: set[str]) -> list[dict[str, Any]]:
    evidence: dict[str, set[str]] = defaultdict(set)
    for project in project_data:
        for heading in project["headings"]:
            normalized = re.sub(r"^[一二三四五六七八九十\d.、\s\-—]+", "", heading).strip()
            if re.search(r"(Issue|严重级别|Agent|审计|纠错|错误)", normalized, re.IGNORECASE):
                continue
            if len(normalized) >= 3:
                evidence[normalized].add(project["system_id"])
    candidates: list[dict[str, Any]] = []
    for heading, systems in sorted(evidence.items()):
        if len(systems) < 2:
            continue
        candidate_id = "heading:" + re.sub(r"\W+", "-", heading, flags=re.UNICODE).strip("-")[:50]
        if candidate_id in approved_ids:
            continue
        candidates.append({
            "id": candidate_id,
            "title": f"文档应包含“{heading}”相关章节",
            "kind": "repeated_document_pattern",
            "evidence_systems": sorted(systems),
            "status": "candidate",
        })
    return candidates[:30]


def build_codex(data_dir: str | Path) -> dict[str, Any]:
    data_dir = Path(data_dir)
    migrate_legacy_projects(data_dir)
    projects = list_stable_projects(data_dir)
    project_data: list[dict[str, Any]] = []

    for project in projects:
        current = data_dir / "projects" / project["system_id"] / "current"
        core_docs = (
            "system_design_draft.md",
            "system_design_detail.md",
            "task_plan.md",
            "tech_blueprint.md",
            "ui_interaction_blueprint.md",
        )
        markdown = "\n".join(_read_text(current / filename) for filename in core_docs)
        headings = [match.group(2).strip() for match in HEADING_PATTERN.finditer(markdown)]
        interfaces = sorted(set(INTERFACE_PATTERN.findall(markdown)))
        terms = sorted({heading for heading in headings if TERM_PATTERN.search(heading)})
        numerical = _read_json(current / "system_numerical_data.json", {})
        tables = sorted(
            key for key, value in numerical.items() if isinstance(value, (dict, list))
        ) if isinstance(numerical, dict) else []
        project_data.append({
            "system_id": project["system_id"],
            "system_name": project.get("system_name", project["system_id"]),
            "lifecycle": project.get("lifecycle", "active"),
            "revision": project.get("revision", 0),
            "updated_at": project.get("updated_at", ""),
            "latest_change": project.get("latest_change"),
            "dependencies": project.get("dependencies", []),
            "interfaces": interfaces,
            "terms": terms,
            "tables": tables,
            "headings": headings,
            "_corpus": markdown,
        })

    names = {project["system_id"]: project["system_name"] for project in project_data}
    for project in project_data:
        inferred = sorted(
            target_id
            for target_id, target_name in names.items()
            if target_id != project["system_id"] and target_name and target_name in project["_corpus"]
        )
        project["dependencies"] = sorted(set(project["dependencies"]) | set(inferred))
        manifest_path = data_dir / "projects" / project["system_id"] / "manifest.json"
        manifest = _read_json(manifest_path, {})
        if isinstance(manifest, dict):
            manifest["dependencies"] = project["dependencies"]
            manifest["public_interfaces"] = project["interfaces"]
            _write_json(manifest_path, manifest)

    table_summaries = []
    excel_dir = data_dir / "Excel"
    if excel_dir.is_dir():
        for path in sorted(excel_dir.glob("*.json")):
            summary = _table_summary(path)
            if summary:
                table_summaries.append(summary)

    standards = load_standards(data_dir)
    approved_ids = {item.get("id", "") for item in standards["approved"]}
    rejected_ids = set(standards["rejected_ids"])
    standards["candidates"] = [
        item for item in _generate_candidates(project_data, approved_ids)
        if item["id"] not in rejected_ids
    ]
    _write_json(standards_path(data_dir), standards)

    lines = [
        "# 项目记忆 Codex",
        "",
        "> 本文档仅从稳定归档项目与当前有效数值表生成。候选规范不会约束 Agent，只有人工批准的规范会生效。",
        "",
        "## 系统清单",
    ]
    for project in project_data:
        lines.append(
            f"- **{project['system_name']}** (`{project['system_id']}`) | "
            f"状态: {project['lifecycle']} | 修订: r{project['revision']} | "
            f"最近变更: {project['latest_change'] or '无'}"
        )
        if project["dependencies"]:
            lines.append(f"  - 依赖: {', '.join(project['dependencies'])}")
        if project["interfaces"]:
            lines.append(f"  - 公开接口: {', '.join(project['interfaces'][:12])}")
        if project["tables"]:
            lines.append(f"  - 数值表: {', '.join(project['tables'])}")
    if not project_data:
        lines.append("- （暂无稳定归档项目）")

    lines.extend(["", "## 当前有效数值表"])
    for table in table_summaries:
        id_note = f" | 主键范围: {table['id_range']}" if table["id_range"] else ""
        lines.append(
            f"- **{table['name']}** | {table['rows']} 行 | 字段: "
            f"`{', '.join(table['fields'][:20])}`{id_note}"
        )
    if not table_summaries:
        lines.append("- （暂无有效数值表）")

    lines.extend(["", "## 已批准项目规范"])
    for standard in standards["approved"]:
        lines.append(f"- {standard.get('title', standard.get('id'))} | 证据: {', '.join(standard.get('evidence_systems', []))}")
    if not standards["approved"]:
        lines.append("- （暂无，候选规范需在 Web 端人工确认）")

    lines.extend(["", "## 候选项目规范"])
    for candidate in standards["candidates"]:
        lines.append(f"- `{candidate['id']}` {candidate['title']} | 证据: {', '.join(candidate.get('evidence_systems', []))}")
    if not standards["candidates"]:
        lines.append("- （暂无跨系统重复模式）")

    codex_path = data_dir / "Knowledge" / "project_codex.md"
    codex_path.parent.mkdir(parents=True, exist_ok=True)
    codex_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "path": str(codex_path),
        "systems": len(project_data),
        "tables": len(table_summaries),
        "approved_standards": len(standards["approved"]),
        "candidate_standards": len(standards["candidates"]),
    }
