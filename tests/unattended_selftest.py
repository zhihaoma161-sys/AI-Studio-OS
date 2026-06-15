from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Skills.project_store import (
    analyze_change,
    apply_change,
    migrate_legacy_projects,
    rollback_project,
)


CLIENT_VERSION = "20260615.5"


class SelfTest:
    def __init__(self, *, real_llm: bool, real_scenario: str, keep_data: bool, port: int) -> None:
        self.real_llm = real_llm
        self.real_scenario = real_scenario
        self.keep_data = keep_data
        self.port = port
        self.started = time.perf_counter()
        self.results: list[dict[str, Any]] = []
        self.root = Path(tempfile.mkdtemp(prefix="ai-studio-selftest-"))
        self.server: subprocess.Popen[str] | None = None
        self.server_log = None
        self.server_log_path = self.root / "selftest_server.log"
        self.base_url = f"http://127.0.0.1:{port}"
        self.system_id = "selftest-item-system"

    def record(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append({"name": name, "ok": ok, "detail": detail})
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}{': ' + detail if detail else ''}", flush=True)

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.record(name, condition, detail)
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    def setup(self) -> None:
        for dirname in ("projects", "Knowledge", "Excel", ".agent_workspace"):
            (self.root / dirname).mkdir(parents=True, exist_ok=True)
        source_env = REPO_ROOT / ".env"
        if source_env.is_file():
            shutil.copy2(source_env, self.root / ".env")

        legacy = self.root / "projects" / "selftest-item-system_20260615_120000"
        legacy.mkdir()
        (legacy / "project_meta.json").write_text(
            json.dumps({"system_name": "无人值守测试道具系统"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (legacy / "system_design_detail.md").write_text(
            "# 无人值守测试道具系统\n\n"
            "## 道具使用\n"
            "玩家可以消耗道具，当前没有出售和冷却机制。\n",
            encoding="utf-8",
        )
        (legacy / "tech_blueprint.md").write_text(
            "# 技术蓝图\n\n## 接口\nPOST /api/items/use\n",
            encoding="utf-8",
        )
        (legacy / "ui_interaction_blueprint.md").write_text(
            "# 交互蓝图\n\n## 道具详情\n显示使用按钮。\n",
            encoding="utf-8",
        )
        numerical = {
            "item_table": [
                {"item_id": 1001, "name": "测试药水", "stack_limit": 99},
                {"item_id": 1002, "name": "测试钥匙", "stack_limit": 1},
            ]
        }
        (legacy / "system_numerical_data.json").write_text(
            json.dumps(numerical, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (legacy / "system_numerical_docs.json").write_text(
            json.dumps({"item_table": "测试道具配置表，主键 item_id"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.root / "Excel" / "item_table.json").write_text(
            json.dumps(
                {
                    "_metadata": {"module": "item_table", "fields": {}},
                    "data": numerical["item_table"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        migrate_legacy_projects(self.root)

    def start_server(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AI_STUDIO_DATA_DIR": str(self.root),
                "AI_STUDIO_PORT": str(self.port),
                "AI_STUDIO_OPEN_BROWSER": "0",
                "PYTHONUNBUFFERED": "1",
            }
        )
        self.server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(self.port)],
            cwd=REPO_ROOT,
            env=env,
            stdout=self.server_log_path.open("w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        deadline = time.time() + 20
        while time.time() < deadline:
            if self.server.poll() is not None:
                output = self.server_log_path.read_text(encoding="utf-8", errors="replace")
                raise RuntimeError(f"Isolated server exited early: {output[-2000:]}")
            try:
                response = httpx.get(f"{self.base_url}/api/projects", timeout=1)
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        raise TimeoutError("Isolated server did not start within 20 seconds")

    def api_json(self, method: str, path: str, payload: dict[str, Any] | None = None, timeout: float = 120) -> dict:
        content = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers = {"Content-Type": "application/json"} if content is not None else None
        response = httpx.request(
            method,
            f"{self.base_url}{path}",
            content=content,
            headers=headers,
            timeout=timeout,
            trust_env=False,
        )
        try:
            value = response.json()
        except ValueError as exc:
            log_tail = ""
            if self.server_log_path.is_file():
                log_tail = self.server_log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
            raise AssertionError(
                f"{path} returned non-JSON HTTP {response.status_code}: "
                f"{response.text[:1000]}\nSERVER LOG:\n{log_tail}"
            ) from exc
        if response.status_code >= 400:
            raise AssertionError(f"{path} failed HTTP {response.status_code}: {value}")
        return value

    def test_isolation(self) -> None:
        projects = self.api_json("GET", "/api/projects")["projects"]
        self.check("隔离服务只看到合成项目", len(projects) == 1, str([item["system_id"] for item in projects]))
        self.system_id = projects[0]["system_id"]

    def test_deterministic_failures(self) -> None:
        current = self.root / "projects" / self.system_id / "current"
        detail_before = (current / "system_design_detail.md").read_bytes()
        numerical_before = (current / "system_numerical_data.json").read_bytes()
        analysis = analyze_change(
            self.root,
            self.system_id,
            "新增道具出售功能",
            selected_document="system_design_detail.md",
            change_type="new_feature",
        )
        try:
            apply_change(
                self.root,
                self.system_id,
                analysis["change_id"],
                text_changes=[{"file": "system_design_detail.md", "content": "新增出售流程"}],
                numerical_operations=[{"action": "add_column", "table": "item_table"}],
            )
        except ValueError as exc:
            self.check("缺少 add_column.column 时拒绝写入", "column" in str(exc), str(exc))
            self.check(
                "错误数值操作不会修改归档",
                detail_before == (current / "system_design_detail.md").read_bytes()
                and numerical_before == (current / "system_numerical_data.json").read_bytes(),
            )
        else:
            self.check("缺少 add_column.column 时拒绝写入", False, "invalid operation was applied")

    def test_real_iteration(self) -> None:
        if not self.real_llm or self.real_scenario not in {"all", "sale"}:
            self.record("真实 LLM 出售与数值迭代", True, "skipped")
            return
        current = self.root / "projects" / self.system_id / "current"
        detail_path = current / "system_design_detail.md"
        original = detail_path.read_bytes()
        first = self.api_json(
            "POST",
            "/api/changes/analyze",
            {
                "client_version": CLIENT_VERSION,
                "system_id": self.system_id,
                "selected_document": "system_design_detail.md",
                "change_type": "new_feature",
                "requirement": "新增道具出售功能，玩家可以在道具详情页出售可出售道具。",
            },
        )
        self.check("首次需求进入讨论日志", [item["kind"] for item in first["discussion"]] == ["requirement"])

        second = self.api_json(
            "POST",
            "/api/changes/analyze",
            {
                "client_version": CLIENT_VERSION,
                "system_id": self.system_id,
                "selected_document": "system_design_detail.md",
                "change_type": "new_feature",
                "requirement": first["requirement"],
                "analysis_feedback": "分析遗漏了数值配置：请为每个道具增加出售价格和是否可出售字段。",
                "previous_change_id": first["change_id"],
            },
        )
        self.check(
            "补充意见保留完整讨论日志",
            [item["kind"] for item in second["discussion"]] == ["requirement", "feedback"],
        )
        operations = second.get("proposal", {}).get("numerical_operations", [])
        self.check("补充意见后包含数值操作", bool(operations), json.dumps(operations, ensure_ascii=False))
        self.check(
            "数值操作均具有完整关键字段",
            all(
                item.get("table")
                and item.get("action")
                and (item.get("action") not in {"add_column", "delete_column"} or item.get("column"))
                for item in operations
            ),
            json.dumps(operations, ensure_ascii=False),
        )

        applied = self.api_json(
            "POST",
            "/api/changes/apply",
            {"system_id": self.system_id, "change_id": second["change_id"]},
        )
        changed = detail_path.read_bytes()
        self.check("文本修改只追加不重写", changed.startswith(original) and len(changed) > len(original))
        numerical = json.loads((current / "system_numerical_data.json").read_text(encoding="utf-8"))
        item_rows = numerical["item_table"]
        self.check(
            "数值变更落到道具表",
            any("price" in str(key).lower() or "sell" in str(key).lower() or "出售" in str(key) for key in item_rows[0]),
            json.dumps(item_rows[0], ensure_ascii=False),
        )

        rollback = self.api_json(
            "POST",
            f"/api/projects/{self.system_id}/rollback",
            {"history_id": applied["history_id"]},
        )
        self.check("回滚恢复上一版编号", rollback["revision"] == 1, str(rollback))
        self.check("回滚恢复原始文档字节", detail_path.read_bytes() == original)

        missing = analyze_change(
            self.root,
            self.system_id,
            "补充一条测试规则",
            selected_document="system_design_detail.md",
            change_type="existing_feature",
        )
        missing_result = apply_change(
            self.root,
            self.system_id,
            missing["change_id"],
            text_changes=[{"file": "system_design_detail.md", "content": "测试规则"}],
        )
        snapshot = self.root / "projects" / self.system_id / "_history" / missing_result["history_id"] / "snapshot"
        shutil.rmtree(snapshot)
        revision_before = json.loads(
            (self.root / "projects" / self.system_id / "manifest.json").read_text(encoding="utf-8")
        )["revision"]
        try:
            rollback_project(self.root, self.system_id, missing_result["history_id"])
        except FileNotFoundError as exc:
            revision_after = json.loads(
                (self.root / "projects" / self.system_id / "manifest.json").read_text(encoding="utf-8")
            )["revision"]
            self.check("快照丢失时回滚报错且版本不变", revision_after == revision_before, str(exc))
        else:
            self.check("快照丢失时回滚报错且版本不变", False, "rollback unexpectedly succeeded")

    def test_real_text_iteration(self) -> None:
        if not self.real_llm or self.real_scenario not in {"all", "text"}:
            self.record("真实 LLM 老功能纯文本迭代", True, "skipped")
            return
        current = self.root / "projects" / self.system_id / "current"
        tech_path = current / "tech_blueprint.md"
        original = tech_path.read_bytes()
        analysis = self.api_json(
            "POST",
            "/api/changes/analyze",
            {
                "client_version": CLIENT_VERSION,
                "system_id": self.system_id,
                "selected_document": "tech_blueprint.md",
                "change_type": "existing_feature",
                "requirement": "补充道具使用接口的超时错误码和重试说明，不涉及数值配置。",
            },
        )
        self.check("老功能纯文本分析不修改数值", not analysis["proposal"]["numerical_operations"])
        result = self.api_json(
            "POST",
            "/api/changes/apply",
            {"system_id": self.system_id, "change_id": analysis["change_id"]},
        )
        self.check(
            "老功能纯文本修改只追加指定文档",
            tech_path.read_bytes().startswith(original)
            and result["text_files"] == ["tech_blueprint.md"]
            and not result["numerical_changes"],
            str(result),
        )

    def test_ui(self, playwright_module: str, edge_path: str) -> None:
        if not playwright_module:
            self.record("Playwright 页面点击流程", True, "skipped: no --playwright-module")
            return
        env = os.environ.copy()
        env.update(
            {
                "AI_STUDIO_SELFTEST_URL": self.base_url,
                "AI_STUDIO_PLAYWRIGHT_MODULE": playwright_module,
                "AI_STUDIO_EDGE_PATH": edge_path,
            }
        )
        result = subprocess.run(
            ["node", str(REPO_ROOT / "tests" / "unattended_ui_selftest.cjs")],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        detail = (result.stdout + "\n" + result.stderr).strip()[-3000:]
        self.check("Playwright 页面点击流程", result.returncode == 0, detail)

    def report(self) -> int:
        usage_path = self.root / ".agent_workspace" / "llm_usage.jsonl"
        usage = []
        if usage_path.is_file():
            usage = [
                json.loads(line)
                for line in usage_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        report = {
            "ok": all(item["ok"] for item in self.results),
            "duration_seconds": round(time.perf_counter() - self.started, 2),
            "llm_calls": len(usage),
            "total_tokens": sum(item.get("total_tokens") or 0 for item in usage),
            "data_root": str(self.root) if self.keep_data else "cleaned",
            "results": self.results,
        }
        print("\nSELFTEST_REPORT=" + json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        return 0 if report["ok"] else 1

    def close(self) -> None:
        if self.server and self.server.poll() is None:
            self.server.terminate()
            try:
                self.server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server.kill()
        if self.keep_data:
            print(f"Self-test data retained at: {self.root}", flush=True)
        else:
            shutil.rmtree(self.root, ignore_errors=True)

    def run(self, playwright_module: str, edge_path: str) -> int:
        try:
            self.setup()
            self.start_server()
            self.test_isolation()
            self.test_deterministic_failures()
            self.test_real_iteration()
            self.test_real_text_iteration()
            self.test_ui(playwright_module, edge_path)
            return self.report()
        except Exception as exc:
            self.record("无人值守自测执行", False, str(exc)[-3000:])
            return self.report()
        finally:
            self.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run isolated unattended incremental-change self-test.")
    parser.add_argument("--no-real-llm", action="store_true", help="Skip real LLM analyze/apply scenarios.")
    parser.add_argument("--real-scenario", choices=("all", "sale", "text"), default="all")
    parser.add_argument("--keep-data", action="store_true", help="Keep temporary test data for debugging.")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--playwright-module", default="", help="Absolute path to a temporary playwright module.")
    parser.add_argument(
        "--edge-path",
        default=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        help="Browser executable used by Playwright.",
    )
    args = parser.parse_args()
    return SelfTest(
        real_llm=not args.no_real_llm,
        real_scenario=args.real_scenario,
        keep_data=args.keep_data,
        port=args.port,
    ).run(
        args.playwright_module,
        args.edge_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
