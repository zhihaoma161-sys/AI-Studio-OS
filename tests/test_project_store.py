from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Skills.codex_builder import approve_standard, build_codex, load_standards
from Skills.llm_settings import get_settings, save_settings, validate_settings
from Skills.project_store import (
    analyze_change,
    apply_change,
    apply_numerical_operations,
    list_stable_projects,
    migrate_legacy_projects,
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

        rollback_project(self.root, "背包系统", result["history_id"])
        self.assertEqual(original_path.read_bytes(), original)
        excel = json.loads(excel_path.read_text(encoding="utf-8"))
        self.assertEqual(excel["data"][0]["value"], "original")

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
