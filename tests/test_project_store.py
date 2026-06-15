from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Skills.codex_builder import approve_standard, build_codex, load_standards
from Skills.llm_settings import get_settings, save_settings, validate_settings
from Skills.project_store import (
    analyze_change,
    apply_change,
    apply_numerical_operations,
    list_stable_projects,
    migrate_legacy_projects,
    normalize_numerical_operations,
    rollback_project,
)


def write_project(path: Path, name: str, marker: str) -> None:
    path.mkdir(parents=True)
    (path / "project_meta.json").write_text(
        json.dumps({"system_name": name}, ensure_ascii=False), encoding="utf-8"
    )
    (path / "system_design_detail.md").write_text(
        f"# {name} - 系统详细设计案\n\n## 核心规则\n{marker}\n", encoding="utf-8"
    )
    (path / "tech_blueprint.md").write_text(
        f"# {name} - 程序开发蓝图\n\n## 接口定义\nPOST /api/{name}\n", encoding="utf-8"
    )
    (path / "system_numerical_data.json").write_text(
        json.dumps({"item_table": [{"id": 1, "value": marker}]}, ensure_ascii=False), encoding="utf-8"
    )


class ProjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "projects").mkdir()
        (self.root / "Knowledge").mkdir()
        (self.root / "Excel").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_migrates_six_legacy_folders_into_five_systems(self):
        names = ["背包系统", "背包系统", "邮件系统", "活动大厅", "全品类美术图鉴", "未命名系统"]
        for index, name in enumerate(names):
            write_project(self.root / "projects" / f"{name}_2026060{index + 1}_120000", name, str(index))

        result = migrate_legacy_projects(self.root)
        projects = list_stable_projects(self.root)

        self.assertEqual(result["project_count"], 5)
        self.assertEqual(len(projects), 5)
        bag = next(project for project in projects if project["system_name"] == "背包系统")
        self.assertEqual(bag["history_count"], 1)
        bag_detail = self.root / "projects" / bag["system_id"] / "current" / "system_design_detail.md"
        self.assertIn("1", bag_detail.read_text(encoding="utf-8"))

    def test_incremental_change_appends_and_rolls_back(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)
        original_path = self.root / "projects" / "背包系统" / "current" / "system_design_detail.md"
        original = original_path.read_bytes()
        excel_path = self.root / "Excel" / "item_table.json"
        excel_path.write_text(
            json.dumps({"_metadata": {"module": "item_table", "fields": {}}, "data": [{"id": 1, "value": "original"}]}),
            encoding="utf-8",
        )

        analysis = analyze_change(self.root, "背包系统", "修改背包容量，并调整数值表")
        result = apply_change(
            self.root,
            "背包系统",
            analysis["change_id"],
            text_changes=[{
                "file": "system_design_detail.md",
                "anchor": "核心规则",
                "content": "背包容量调整为可扩展。",
                "deprecated": "旧固定容量规则已废弃。",
            }],
            numerical_operations=[{
                "action": "update_rows",
                "table": "item_table",
                "match": {"id": 1},
                "values": {"value": "updated"},
            }],
        )

        changed = original_path.read_bytes()
        self.assertTrue(changed.startswith(original))
        self.assertIn("[新]", changed.decode("utf-8"))
        numerical = json.loads(
            (self.root / "projects" / "背包系统" / "current" / "system_numerical_data.json").read_text(encoding="utf-8")
        )
        self.assertEqual(numerical["item_table"][0]["value"], "updated")
        excel = json.loads(excel_path.read_text(encoding="utf-8"))
        self.assertEqual(excel["data"][0]["value"], "updated")

        rollback = rollback_project(self.root, "背包系统", result["history_id"])
        self.assertEqual(original_path.read_bytes(), original)
        excel = json.loads(excel_path.read_text(encoding="utf-8"))
        self.assertEqual(excel["data"][0]["value"], "original")
        manifest = json.loads((self.root / "projects" / "背包系统" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(rollback["revision"], 1)
        self.assertEqual(manifest["revision"], 1)
        self.assertFalse(any(item.get("kind") == "pre_rollback" for item in manifest["history"]))
        project_meta = json.loads(
            (self.root / "projects" / "背包系统" / "current" / "project_meta.json").read_text(encoding="utf-8")
        )
        self.assertEqual(project_meta["version"], "r1")

    def test_rollback_reports_missing_snapshot(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)
        analysis = analyze_change(self.root, "背包系统", "修改规则")
        result = apply_change(
            self.root,
            "背包系统",
            analysis["change_id"],
            text_changes=[{"file": "system_design_detail.md", "content": "修改规则"}],
        )
        snapshot = self.root / "projects" / "背包系统" / "_history" / result["history_id"] / "snapshot"
        shutil.rmtree(snapshot)

        with self.assertRaisesRegex(FileNotFoundError, "历史版本快照已丢失"):
            rollback_project(self.root, "背包系统", result["history_id"])

    def test_project_list_repairs_legacy_incrementing_rollback_manifest(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)
        analysis = analyze_change(self.root, "背包系统", "修改规则")
        result = apply_change(
            self.root,
            "背包系统",
            analysis["change_id"],
            text_changes=[{"file": "system_design_detail.md", "content": "修改规则"}],
        )
        project_dir = self.root / "projects" / "背包系统"
        manifest_path = project_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["revision"] = 3
        manifest["latest_change"] = f"rollback:{result['history_id']}"
        manifest["history"].append({"id": "r0002_legacy_pre_rollback", "revision": 2, "kind": "pre_rollback"})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

        project = list_stable_projects(self.root)[0]

        self.assertEqual(project["revision"], 1)
        self.assertEqual(project["latest_change"], f"restored:{result['history_id']}")
        self.assertEqual(project["history_count"], 0)

    def test_selected_document_and_change_type_define_iteration_scope(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)

        analysis = analyze_change(
            self.root,
            "背包系统",
            "补充错误码和超时策略",
            selected_document="tech_blueprint.md",
            change_type="new_feature",
        )

        self.assertEqual(analysis["selected_document"], "tech_blueprint.md")
        self.assertEqual(analysis["change_type"], "new_feature")
        self.assertEqual(analysis["affected_files"], ["tech_blueprint.md"])
        self.assertEqual(analysis["writable_files"], ["tech_blueprint.md"])
        self.assertEqual(analysis["reference_files"], [])
        self.assertEqual(analysis["affected_agents"], ["tech_architect"])

        projects = list_stable_projects(self.root)
        self.assertIn("tech_blueprint.md", projects[0]["iterable_files"])
        self.assertNotIn("project_meta.json", projects[0]["iterable_files"])

        with self.assertRaises(ValueError):
            analyze_change(
                self.root,
                "背包系统",
                "修改元数据",
                selected_document="project_meta.json",
                change_type="existing_feature",
            )
        with self.assertRaises(ValueError):
            analyze_change(
                self.root,
                "背包系统",
                "补充错误码",
                selected_document="tech_blueprint.md",
                change_type="unclear",
            )

    def test_data_bearing_requirements_and_feedback_include_numerical_scope(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)

        for requirement in ("新增道具出售功能", "调整抽奖概率", "修改技能冷却时长"):
            scoped = analyze_change(
                self.root,
                "背包系统",
                requirement,
                selected_document="system_design_detail.md",
                change_type="new_feature",
            )
            self.assertIn("system_numerical_data.json", scoped["writable_files"])
            self.assertIn("numerical_planner", scoped["affected_agents"])

        first = analyze_change(
            self.root,
            "背包系统",
            "新增道具出售功能",
            selected_document="system_design_detail.md",
            change_type="new_feature",
        )
        second = analyze_change(
            self.root,
            "背包系统",
            "新增道具出售功能",
            selected_document="system_design_detail.md",
            change_type="new_feature",
            analysis_feedback="遗漏数值配置，需要为每个道具增加出售价格字段。",
            previous_change_id=first["change_id"],
        )
        self.assertEqual(second["analysis_feedback"], "遗漏数值配置，需要为每个道具增加出售价格字段。")
        self.assertEqual(second["previous_change_id"], first["change_id"])
        self.assertEqual([item["kind"] for item in second["discussion"]], ["requirement", "feedback"])
        pending = self.root / "projects" / "背包系统" / "_pending"
        self.assertFalse((pending / f"{first['change_id']}.json").exists())
        self.assertTrue((pending / f"{second['change_id']}.json").exists())

    def test_negated_impact_scope_does_not_force_numerical_changes(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)

        text_only = analyze_change(
            self.root,
            "背包系统",
            "补充接口超时说明，不涉及数值配置。",
            selected_document="tech_blueprint.md",
            change_type="existing_feature",
        )
        self.assertNotIn("system_numerical_data.json", text_only["writable_files"])
        self.assertNotIn("numerical_planner", text_only["affected_agents"])

        positive = analyze_change(
            self.root,
            "背包系统",
            "补充接口说明，但不要遗漏数值配置。",
            selected_document="tech_blueprint.md",
            change_type="existing_feature",
        )
        self.assertIn("system_numerical_data.json", positive["writable_files"])
        self.assertIn("numerical_planner", positive["affected_agents"])

    def test_generated_proposal_uses_writable_files_and_read_only_references(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)
        current = self.root / "projects" / "背包系统" / "current"
        (current / "system_schema.json").write_text("{}", encoding="utf-8")
        model_output = """以下是局部修改方案：
```json
{"text_changes":[{"file":"tech_blueprint.md","anchor":"接口定义","content":"新增超时错误码。","deprecated":""},{"file":"system_schema.json","anchor":"","content":"不应直接修改。","deprecated":""}],"numerical_operations":[]}
```"""

        with patch("Skills.llm_client.ask_llm", return_value=model_output) as mocked:
            analysis = analyze_change(
                self.root,
                "背包系统",
                "新增接口超时错误码",
                generate_proposal=True,
                selected_document="tech_blueprint.md",
                change_type="new_feature",
            )

        self.assertEqual(analysis["writable_files"], ["tech_blueprint.md"])
        self.assertEqual(analysis["reference_files"], ["system_schema.json"])
        self.assertEqual(analysis["proposal"]["text_changes"][0]["file"], "tech_blueprint.md")
        self.assertEqual(len(analysis["proposal"]["text_changes"]), 1)
        self.assertIn("system_schema.json", analysis["proposal_warnings"][0])
        self.assertEqual(mocked.call_args.kwargs["max_retries"], 1)
        self.assertEqual(mocked.call_args.kwargs["timeout_seconds"], 90)

    def test_missing_required_numerical_operations_marks_proposal_incomplete(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "original")
        migrate_legacy_projects(self.root)
        model_output = json.dumps({
            "text_changes": [{
                "file": "system_design_detail.md",
                "anchor": "核心规则",
                "content": "新增道具出售流程。",
                "deprecated": "",
            }],
            "numerical_operations": [{"action": "add_column", "table": "item_table"}],
        }, ensure_ascii=False)

        with patch("Skills.llm_client.ask_llm", return_value=model_output):
            analysis = analyze_change(
                self.root,
                "背包系统",
                "新增道具出售功能",
                generate_proposal=True,
                selected_document="system_design_detail.md",
                change_type="new_feature",
            )

        self.assertTrue(analysis["proposal_incomplete"])
        self.assertTrue(any("缺少 column" in warning for warning in analysis["proposal_warnings"]))
        with self.assertRaisesRegex(ValueError, "已知遗漏"):
            apply_change(self.root, "背包系统", analysis["change_id"])

    def test_all_numerical_operation_types(self):
        data = {"old": [{"id": 1, "value": 10}]}
        result = apply_numerical_operations(data, [
            {"action": "create_table", "table": "new", "rows": [{"id": 2}]},
            {"action": "add_column", "table": "old", "column": "enabled", "default": True},
            {"action": "add_rows", "table": "old", "rows": [{"id": 3, "value": 30}]},
            {"action": "update_rows", "table": "old", "match": {"id": 1}, "values": {"value": 20}},
            {"action": "delete_rows", "table": "old", "match": {"id": 3}},
            {"action": "delete_column", "table": "old", "column": "enabled"},
        ])
        self.assertEqual(len(result), 6)
        self.assertEqual(data["old"], [{"id": 1, "value": 20}])
        self.assertEqual(data["new"], [{"id": 2}])

    def test_numerical_operation_aliases_and_incomplete_operations(self):
        normalized, errors = normalize_numerical_operations([
            {"operation": "add_column", "table_name": "item_table", "field": "price", "default_value": 0},
        ])
        self.assertEqual(errors, [])
        self.assertEqual(normalized[0]["column"], "price")
        self.assertEqual(normalized[0]["default"], 0)

        normalized, errors = normalize_numerical_operations([
            {"action": "add_column", "table": "item_table", "columns": [{"name": "price", "default": 0}]},
        ])
        self.assertEqual(errors, [])
        self.assertEqual(normalized[0]["column"], "price")

        normalized, errors = normalize_numerical_operations([
            {"action": "add_column", "table": "item_table"},
        ])
        self.assertEqual(normalized, [])
        self.assertIn("缺少 column", errors[0])

    def test_codex_uses_stable_projects_and_approved_standards(self):
        write_project(self.root / "projects" / "背包系统_20260601_120000", "背包系统", "a")
        write_project(self.root / "projects" / "邮件系统_20260602_120000", "邮件系统", "b")
        build_codex(self.root)
        standards = load_standards(self.root)
        self.assertTrue(standards["candidates"])
        candidate_id = standards["candidates"][0]["id"]
        approve_standard(self.root, candidate_id, True)
        result = build_codex(self.root)
        codex = (self.root / "Knowledge" / "project_codex.md").read_text(encoding="utf-8")
        self.assertEqual(result["systems"], 2)
        self.assertIn("背包系统", codex)
        self.assertIn("已批准项目规范", codex)

    def test_llm_settings_are_masked_and_http_is_local_only(self):
        saved = save_settings(self.root, {
            "provider": "deepseek",
            "api_key": "sk-1234567890abcdef",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        })
        self.assertTrue(saved["configured"])
        self.assertNotIn("1234567890", saved["api_key_masked"])
        self.assertNotIn("api_key", get_settings(self.root))
        with self.assertRaises(ValueError):
            validate_settings({
                "provider": "custom",
                "api_key": "x",
                "base_url": "http://example.com/v1",
                "model": "test",
            })
        local = validate_settings({
            "provider": "ollama",
            "api_key": "",
            "base_url": "http://localhost:11434/v1",
            "model": "qwen2.5",
        })
        self.assertEqual(local["api_key"], "")


if __name__ == "__main__":
    unittest.main()
