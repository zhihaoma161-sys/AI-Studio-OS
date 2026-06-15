from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import server


class ChangeApiTests(unittest.TestCase):
    def test_server_honors_isolated_data_dir(self):
        with tempfile.TemporaryDirectory() as temp:
            env = os.environ.copy()
            env["AI_STUDIO_DATA_DIR"] = temp
            result = subprocess.run(
                [sys.executable, "-c", "import server; print(server.DATA_DIR)"],
                cwd=Path(__file__).resolve().parents[1],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )

        self.assertEqual(Path(result.stdout.strip()), Path(temp).resolve())

    def test_index_response_disables_cache(self):
        response = asyncio.run(server.root())

        self.assertIn("no-store", response.headers["cache-control"])
        self.assertEqual(response.headers["x-ai-studio-client-version"], server.WEB_CLIENT_VERSION)

    def test_old_client_gets_refresh_message(self):
        with patch("server._log_change_analysis"):
            response = server.api_analyze_change({
                "system_id": "背包系统",
                "requirement": "修改接口",
            })

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 400)
        self.assertIn("页面版本过旧", payload["error"])
        self.assertTrue(payload["trace_id"].startswith("ana_"))

    def test_open_project_folder_opens_current_document_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            current = project / "current"
            current.mkdir()
            with patch("server.get_project", return_value=(project, {})), patch("server.os.startfile") as startfile:
                response = asyncio.run(server.api_open_project_folder({"system_id": "背包系统"}))

        payload = json.loads(response.body)
        self.assertTrue(payload["ok"])
        startfile.assert_called_once_with(str(current.resolve()))

    def test_document_aliases_reach_change_analysis(self):
        result = {
            "change_id": "chg_test",
            "affected_files": ["tech_blueprint.md"],
            "writable_files": ["tech_blueprint.md"],
        }
        with patch("server._log_change_analysis"), patch("server.analyze_change", return_value=result) as analyze:
            response = server.api_analyze_change({
                "client_version": server.WEB_CLIENT_VERSION,
                "system_id": "背包系统",
                "document": "tech_blueprint.md",
                "iteration_type": "new_feature",
                "requirement": "新增接口",
            })

        payload = json.loads(response.body)
        self.assertTrue(payload["ok"])
        analyze.assert_called_once_with(
            server.DATA_DIR,
            "背包系统",
            "新增接口",
            generate_proposal=True,
            selected_document="tech_blueprint.md",
            change_type="new_feature",
            analysis_feedback="",
            previous_change_id="",
        )

    def test_feedback_and_previous_change_reach_analysis(self):
        result = {
            "change_id": "chg_new",
            "affected_files": ["system_design_detail.md", "system_numerical_data.json"],
            "writable_files": ["system_design_detail.md", "system_numerical_data.json"],
        }
        with patch("server._log_change_analysis"), patch("server.analyze_change", return_value=result) as analyze:
            response = server.api_analyze_change({
                "client_version": server.WEB_CLIENT_VERSION,
                "system_id": "背包系统",
                "selected_document": "system_design_detail.md",
                "change_type": "new_feature",
                "requirement": "新增道具出售功能",
                "analysis_feedback": "遗漏出售价格配置",
                "previous_change_id": "chg_old",
            })

        payload = json.loads(response.body)
        self.assertTrue(payload["ok"])
        analyze.assert_called_once_with(
            server.DATA_DIR,
            "背包系统",
            "新增道具出售功能",
            generate_proposal=True,
            selected_document="system_design_detail.md",
            change_type="new_feature",
            analysis_feedback="遗漏出售价格配置",
            previous_change_id="chg_old",
        )

    def test_validation_error_with_json_filename_is_not_reported_as_model_json_error(self):
        with patch("server._log_change_analysis"), patch(
            "server.analyze_change",
            side_effect=ValueError("Document does not support incremental iteration: project_meta.json"),
        ):
            response = server.api_analyze_change({
                "client_version": server.WEB_CLIENT_VERSION,
                "system_id": "背包系统",
                "selected_document": "project_meta.json",
                "change_type": "existing_feature",
                "requirement": "修改元数据",
            })

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 400)
        self.assertIn("project_meta.json", payload["error"])

    def test_stale_client_version_gets_refresh_message(self):
        with patch("server._log_change_analysis"), patch("server.analyze_change") as analyze:
            response = server.api_analyze_change({
                "client_version": "old-version",
                "system_id": "背包系统",
                "selected_document": "tech_blueprint.md",
                "change_type": "existing_feature",
                "requirement": "修改接口",
            })

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 400)
        self.assertIn(server.WEB_CLIENT_VERSION, payload["error"])
        analyze.assert_not_called()


if __name__ == "__main__":
    unittest.main()
