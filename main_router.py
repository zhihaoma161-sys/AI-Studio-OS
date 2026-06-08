"""
Main Router (核心中枢 / 24h 常驻守护进程)
职责：基于状态机轮询 task_status.json 调度所有子 Agent 和 Guards。

状态流转（V3 线性 HITL 审批 / 严格单向 / 杜绝循环）：
  idle --> pending_classification
    |--> (skill) pending_design --> pending_schema_approval --> pending_execution
    |         --> pending_validation --> pending_audit --> pending_data_approval
    |         --> pending_assets --> completed --> idle
    |
    |--> (system) system_visionary --> clarifying_requirements
              --> pending_design_approval --> pending_plan_approval
              --> pending_system_design --> pending_system_approval
              --> pending_schema_translate --> pending_numerical --> pending_numerical_approval
              --> pending_tech_design --> pending_tech_approval
              --> pending_final_audit(全自动纠错回环) --> completed(归档) --> idle
"""

import json
import os
import re
import subprocess
import sys
import time

# ---- Windows 控制台 UTF-8 适配 ----
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---- Web GUI 模式：将 input/print 透传到 web_io 桥梁 ----
import builtins
if os.environ.get("AI_STUDIO_WEB_MODE") == "1":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from Skills.web_io import web_print, web_input
    _original_print = builtins.print
    _original_input = builtins.input
    builtins.print = web_print
    builtins.input = web_input

# 确保项目根目录在 sys.path 中，方便引入 Guards 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Guards.schema_validator import SchemaValidator
from Guards.qa_auditor import QAAuditor

# ---- 配置 ----
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(os.environ.get("AI_STUDIO_DATA_DIR", ROOT_DIR), ".agent_workspace")
STATUS_FILE = os.path.join(WORKSPACE_DIR, "task_status.json")
RESULT_FILE = os.path.join(WORKSPACE_DIR, "current_result.json")
SCHEMA_FILE = os.path.join(WORKSPACE_DIR, "active_schema.json")
CONCEPT_FILE = os.path.join(WORKSPACE_DIR, "concept_brief.md")
AUDIT_FILE = os.path.join(WORKSPACE_DIR, "audit_feedback.json")
ROUTE_FILE = os.path.join(WORKSPACE_DIR, "task_route.json")
BOSS_FEEDBACK_FILE = os.path.join(WORKSPACE_DIR, "boss_feedback.txt")
PROJECT_DB_DIR = os.path.join(WORKSPACE_DIR, "project_db")
CONCEPT_CACHE_FILE = os.path.join(WORKSPACE_DIR, ".concept_brief_cache.txt")
DRAFT_CACHE_FILE = os.path.join(WORKSPACE_DIR, ".draft_cache.md")
RETRY_COUNT_FILE = os.path.join(WORKSPACE_DIR, ".retry_count.json")
POLL_INTERVAL = 2

YEL_COLOR = "\033[93m"
GRN_COLOR = "\033[92m"
RED_COLOR = "\033[91m"
RESET_CLR = "\033[0m"


def read_state() -> str:
    data = read_state_raw()
    return data.get("current_state", "idle")


def read_state_raw() -> dict:
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Router][错误] 文件不存在，尝试读取路径: {STATUS_FILE}")
        return {"current_state": "idle"}
    except json.JSONDecodeError as e:
        print(f"[Router][错误] JSON 解析失败，文件路径: {STATUS_FILE}")
        print(f"[Router][错误] 详细原因: {e}")
        return {"current_state": "idle"}


def write_state(state: str, **extra):
    try:
        data = {"current_state": state}
        data.update(extra)
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[Router][警告] 无法写入状态文件: {STATUS_FILE}")
        print(f"[Router][警告] 详细原因: {e}")


def _save_draft_snapshot():
    """保存 system_design_draft.md 的快照副本，用于后续智能剪裁比对。"""
    draft_path = os.path.join(WORKSPACE_DIR, "system_design_draft.md")
    if os.path.exists(draft_path):
        try:
            with open(draft_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(DRAFT_CACHE_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print("[Router] 已保存草案快照 (.draft_cache.md)")
        except Exception as e:
            print(f"[Router][警告] 无法保存草案快照: {e}")


def _extract_section(md_text: str, section_title: str) -> str:
    """从 Markdown 文本中提取指定标题的章节内容。"""
    import re
    pattern = rf"^#+\s*{re.escape(section_title)}.*$"
    match = re.search(pattern, md_text, re.MULTILINE)
    if not match:
        return ""
    start = match.start()
    # 从该节之后找下一个同级或更高级标题
    level = len(re.match(r"^#+", md_text[start:]).group())
    remaining = md_text[start + len(match.group()):]
    next_match = re.search(rf"^#{{{1,{level}}}}\s", remaining, re.MULTILINE)
    if next_match:
        return md_text[start:start + len(match.group()) + next_match.start()]
    else:
        return md_text[start:]


def _trim_open_questions_if_unchanged():
    """
    智能剪裁：如果"六、待确认风险与疑点"未被人工修改，则删除该节及之后内容。
    返回是否执行了剪裁。
    """
    draft_path = os.path.join(WORKSPACE_DIR, "system_design_draft.md")
    if not os.path.exists(draft_path) or not os.path.exists(DRAFT_CACHE_FILE):
        print("[Router] 缺少草案或快照文件，跳过智能剪裁")
        return False

    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            current_text = f.read()
        with open(DRAFT_CACHE_FILE, "r", encoding="utf-8") as f:
            snapshot_text = f.read()
    except Exception as e:
        print(f"[Router][警告] 读取草案/快照失败: {e}")
        return False

    section_title = "六、待确认风险与疑点"
    current_section = _extract_section(current_text, section_title)
    snapshot_section = _extract_section(snapshot_text, section_title)

    if not current_section:
        print("[Router] 草案中未找到疑点章节，无需剪裁")
        return False

    # 比对：标准化（去空格）后判断是否一致
    current_norm = "".join(current_section.split())
    snapshot_norm = "".join(snapshot_section.split())

    # 相似度阈值：差异小于 5% 视为未修改
    max_len = max(len(current_norm), len(snapshot_norm)) or 1
    similarity = 1.0 - (abs(len(current_norm) - len(snapshot_norm)) / max_len)

    if similarity > 0.95:
        # 老板未修改 → 删除疑点节及之后所有内容
        import re
        pattern = rf"^#+\s*{re.escape(section_title)}.*$"
        match = re.search(pattern, current_text, re.MULTILINE)
        if match:
            trimmed = current_text[:match.start()].rstrip() + "\n"
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(trimmed)
            print("\033[93m[智能剪裁] 疑点章节未修改，已自动擦除，保护下游数据纯净。\033[0m")
            return True
    else:
        print("\033[92m[智能剪裁] 检测到疑点章节已被人工修改，予以保留。\033[0m")

    return False


def _save_retry_count(agent: str, count: int):
    """保存指定 Agent 的重试计数。"""
    try:
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        with open(RETRY_COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump({"agent": agent, "count": count}, f)
    except Exception:
        pass


def _get_retry_count(agent: str) -> int:
    """读取指定 Agent 的重试计数，如果不是同一 Agent 则归零。"""
    if not os.path.exists(RETRY_COUNT_FILE):
        return 0
    try:
        with open(RETRY_COUNT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("agent") == agent:
            return data.get("count", 0)
        return 0
    except Exception:
        return 0


def _clear_retry_count():
    """清除重试计数。"""
    if os.path.exists(RETRY_COUNT_FILE):
        try:
            os.remove(RETRY_COUNT_FILE)
        except Exception:
            pass


def _get_agent_script(agent_name: str) -> str | None:
    """根据 responsible_agent 名称返回 Agent 脚本路径。"""
    mapping = {
        "system_planner": "Agents/system_planner.py",
        "numerical_planner": "Agents/numerical_planner.py",
        "numerical_agent": "Agents/numerical_agent.py",
        "tech_architect": "Agents/tech_architect.py",
        "combat_agent": "Agents/combat_agent.py",
        "lead_planner": "Agents/lead_planner.py",
        "schema_translator": "Agents/schema_translator.py",
        "ux_agent": "Agents/ux_agent.py",
    }
    return mapping.get(agent_name)


def _generate_final_audit_report(rounds: int):
    """合并设计文档与审计追踪日志，生成终极审计报告。"""
    report_path = os.path.join(WORKSPACE_DIR, "final_audit_report.md")
    lines = ["# 终极审计报告", ""]
    lines.append(f"> 审计轮次: {rounds} | 结论: 通过")
    lines.append("")

    trace_path = os.path.join(WORKSPACE_DIR, "audit_trace_log.md")
    if os.path.exists(trace_path):
        lines.append("## 审计追踪日志")
        lines.append("")
        with open(trace_path, "r", encoding="utf-8") as f:
            lines.append(f.read())
    else:
        lines.append("## 审计追踪日志")
        lines.append("")
        lines.append("（无问题记录）")

    lines.append("")
    lines.append("## 最终交付物清单")
    for fname in sorted(os.listdir(WORKSPACE_DIR)):
        fpath = os.path.join(WORKSPACE_DIR, fname)
        if os.path.isfile(fpath) and not fname.startswith("."):
            size_kb = os.path.getsize(fpath) / 1024
            lines.append(f"- {fname} ({size_kb:.1f} KB)")

    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def require_human_approval(agent_name: str, artifact_paths: list[str],
                           next_state: str, reject_state: str) -> str:
    """
    通用 HITL 审批函数：阻塞等待老板验收 Agent 产物。
    返回 next_state（通过）或 reject_state（打回）。
    """
    print("\033[93m" + "=" * 60 + "\033[0m")
    print(f"\033[93m[审批节点] 等待老板验收 {agent_name} 的产物:\033[0m")
    for p in artifact_paths:
        print(f"[审批节点]   - {p}")
    print("\033[93m" + "=" * 60 + "\033[0m")

    user_input = input("[审批节点] 输入 'y' 通过，或输入修改意见打回: ").strip()

    if user_input.lower() == "y":
        print(f"\033[92m[审批节点] 老板放行！{agent_name} 产物已验收。\033[0m")
        return next_state
    else:
        print(f"\033[91m[审批节点] 老板打回！意见: {user_input}\033[0m")
        try:
            with open(BOSS_FEEDBACK_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{agent_name}] {user_input}\n")
            print(f"[审批节点] 修改意见已追加至: {BOSS_FEEDBACK_FILE}")
        except Exception as e:
            print(f"[审批节点][警告] 无法保存反馈: {e}")
        return reject_state


def _upsert_archive(workspace_dir: str, db_dir: str):
    """
    读取 system_numerical_data.json → 按顶级模块拆分 → Upsert 到 project_db/
    同名模块深合并：同 ID 覆盖，新 ID 追加。
    """
    data_file = os.path.join(workspace_dir, "system_numerical_data.json")
    if not os.path.exists(data_file):
        print("[Router][警告] system_numerical_data.json 不存在，跳过归档")
        return

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Router][警告] 无法读取 {data_file}: {e}")
        return

    if not isinstance(data, dict):
        print("[Router][警告] 数据格式非 dict，跳过归档")
        return

    os.makedirs(db_dir, exist_ok=True)
    merged_count = 0
    new_count = 0

    for module_name, module_data in data.items():
        if not isinstance(module_data, dict):
            continue

        module_file = os.path.join(db_dir, f"{module_name}.json")

        # 将嵌套结构展平为记录列表（处理 discrete_milestones 等层级）
        records = _flatten_records(module_data)

        if not records:
            continue

        # 加载旧数据
        old_records = []
        if os.path.exists(module_file):
            try:
                with open(module_file, "r", encoding="utf-8") as f:
                    old_records = json.load(f)
                if not isinstance(old_records, list):
                    old_records = []
            except Exception:
                old_records = []

        # 建立旧数据 ID 索引
        old_index = {}
        for i, rec in enumerate(old_records):
            pid = _get_primary_id(rec)
            if pid is not None:
                old_index[pid] = i

        # 合并：同 ID 覆盖，新 ID 追加
        for rec in records:
            pid = _get_primary_id(rec)
            if pid is not None and pid in old_index:
                old_records[old_index[pid]] = rec
                merged_count += 1
            else:
                old_records.append(rec)
                new_count += 1

        # 落盘
        with open(module_file, "w", encoding="utf-8") as f:
            json.dump(old_records, f, ensure_ascii=False, indent=2)

        print(f"[Router]   {module_name}.json: 更新 {merged_count} 条, 新增 {new_count} 条 -> {module_file}")

    print(f"[Router] 归档完成: {merged_count} 条更新, {new_count} 条新增")


def _flatten_records(data: dict) -> list[dict]:
    """将嵌套的模块数据展平为记录列表。自动穿透 discrete_milestones 等中间层。"""
    # 如果包含 discrete_milestones 子键，钻入
    if "discrete_milestones" in data and isinstance(data["discrete_milestones"], dict):
        return list(data["discrete_milestones"].values())

    # 如果 value 全是 dict 且至少有一个含 _id 字段，视为记录集
    if all(isinstance(v, dict) for v in data.values()):
        has_ids = any(_get_primary_id(v) is not None for v in data.values())
        if has_ids:
            return list(data.values())

    # 兜底：尝试展平一层
    result = []
    for v in data.values():
        if isinstance(v, dict):
            result.append(v)
    return result if result else [data]


def _get_primary_id(record: dict):
    """从记录中提取主键 ID 值（优先 _id 结尾的字段）。"""
    if not isinstance(record, dict):
        return None
    # 优先匹配 *_id 结尾
    for key, value in record.items():
        if key.endswith("_id") and isinstance(value, (str, int)):
            return value
    # 兜底：id 字段
    for key in ("id", "_id"):
        if key in record and isinstance(record[key], (str, int)):
            return record[key]
    return None


def main():
    print("[Router] AI Studio OS 调度中枢已启动（常驻守护模式）...")
    print(f"[Router] 监听文件: {STATUS_FILE}")
    print(f"[Router] 轮询间隔: {POLL_INTERVAL} 秒")
    print("[Router] 按 Ctrl+C 可停止调度中枢")

    os.makedirs(PROJECT_DB_DIR, exist_ok=True)
    print(f"[Router] 归档仓库已就绪: {PROJECT_DB_DIR}\n")

    validator = SchemaValidator()

    # ---- 基于内容的缓存机制 ----
    concept_current = ""
    try:
        with open(CONCEPT_FILE, "r", encoding="utf-8") as f:
            concept_current = f.read().strip()
    except FileNotFoundError:
        pass

    concept_cache = ""
    try:
        with open(CONCEPT_CACHE_FILE, "r", encoding="utf-8") as f:
            concept_cache = f.read().strip()
    except FileNotFoundError:
        pass

    if concept_current:
        print(f"[Router] 概念简案已就绪: {CONCEPT_FILE} ({len(concept_current)} 字符)")
        if concept_current == concept_cache:
            print("[Router] 内容与缓存一致（旧需求/已处理），保持 idle 监听。\n")
        else:
            print("[Router] 检测到新需求（内容与缓存不一致）。\n")
    else:
        print(f"[Router] 概念简案为空，等待老板编写: {CONCEPT_FILE}\n")

    # ---- 开机恢复 / 清理 ----
    previous_state = read_state()
    recovering = previous_state != "idle"
    if recovering:
        current_state = previous_state
        print(f"[Router] 检测到中断任务，保留工作区并从状态继续: {previous_state}")
    else:
        print("[Router] 当前无中断任务，正在执行开机清理...")
        write_state("idle")
        current_state = "idle"

    # 仅在空闲启动时清理上一轮旧文件（严禁触碰 project_db/）
    files_to_clean = [
        "task_route.json",
        "system_schema.json",
        "system_flow.mmd",
        "system_numerical_docs.json",
        "system_numerical_data.json",
        "audit_feedback.json",
        "audit_trace_log.md",
        "ui_interaction_blueprint.md",
        "guild_design_data.json",
    ]
    if not recovering:
        for f in files_to_clean:
            filepath = os.path.join(WORKSPACE_DIR, f)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[Router] 已清理历史遗留文件: {f}")

    print("[Router] AI Studio OS 调度中枢已就绪（等待修改概念简案）...\n")

    last_printed_state = None  # 去重心跳：状态不变时不重复打印

    while True:
        # ===== 0. 每次循环从硬盘读取概念简案内容 =====
        try:
            with open(CONCEPT_FILE, "r", encoding="utf-8") as f:
                concept_current = f.read().strip()
        except FileNotFoundError:
            concept_current = ""

        # ===== 0.5 基于内容的严格比对 =====
        concept_changed = (concept_current and concept_current != concept_cache)

        if concept_changed:
            print("\033[93m[Router]\033[0m 检测到老板更新了《概念简案》内容！自动触发分发器...")
            # 立即更新缓存快照，防止重启误触发
            try:
                with open(CONCEPT_CACHE_FILE, "w", encoding="utf-8") as f:
                    f.write(concept_current)
                concept_cache = concept_current
            except Exception as e:
                print(f"[Router][警告] 无法更新缓存: {e}")
            # 清理旧轮次文件
            for f in [AUDIT_FILE, ROUTE_FILE, BOSS_FEEDBACK_FILE,
                      os.path.join(WORKSPACE_DIR, "system_design_draft.md"),
                      os.path.join(WORKSPACE_DIR, "system_design_detail.md"),
                      os.path.join(WORKSPACE_DIR, "task_plan.md")]:
                if os.path.exists(f):
                    os.remove(f)
                    print(f"[Router] 已清理旧文件: {os.path.basename(f)}")
            write_state("pending_classification")
            current_state = "pending_classification"
        else:
            current_state = read_state()

        # 去重心跳：idle 不打印，状态不变不重复
        if current_state != "idle" and current_state != last_printed_state:
            print(f"[Router][心跳] 当前状态: {current_state}")
            last_printed_state = current_state

        # ============================== 分类 ==============================
        if current_state == "idle":
            pass

        elif current_state == "pending_classification":
            print("[Router] 正在调用前置分类器判断需求类别...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "classifier_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                if not os.path.exists(ROUTE_FILE):
                    print("\033[91m[Router][错误] 路由文件未生成\033[0m")
                    write_state("idle")
                else:
                    with open(ROUTE_FILE, "r", encoding="utf-8") as f:
                        route_data = json.load(f)
                    task_type = route_data.get("task_type", "unknown")
                    reason = route_data.get("reason", "未提供")
                    print(f"[Router] 需求类别判定: {task_type} | {reason}")

                    # ---- 构建全局项目记忆 (Project Codex) ----
                    print("[Router] 正在唤醒档案管理员，构建全局项目记忆 (Project Codex)...")
                    try:
                        subprocess.run(
                            [sys.executable, os.path.join(ROOT_DIR, "Skills", "build_memory_codex.py")],
                            check=True, cwd=ROOT_DIR,
                        )
                        print("[Router] 项目记忆 Codex 构建完成。")
                    except subprocess.CalledProcessError as e:
                        print(f"\033[91m[Router][警告] Codex 构建失败（{e.returncode}），继续执行\033[0m")
                    except FileNotFoundError:
                        print("\033[91m[Router][警告] 找不到 build_memory_codex.py，跳过\033[0m")

                    if task_type == "skill":
                        print("[Router] \U0001f3af 识别为单体技能需求，进入技能管线。")
                        write_state("pending_design")
                    elif task_type == "system":
                        print("[Router] 🏗️ 识别为玩法系统需求，进入知识驱动管线。")
                        try:
                            subprocess.run(
                                [sys.executable, os.path.join(ROOT_DIR, "Skills", "system_visionary.py")],
                                stdout=sys.stdout, stderr=sys.stdout,
                                cwd=ROOT_DIR,
                            )
                            print("[Router] Visionary Agent 执行完毕。")
                        except Exception as e:
                            print(f"\033[91m[Router] Visionary 失败: {e}\033[0m")
                            write_state("idle")
                    else:
                        print(f"\033[91m[Router] 非法类别: '{task_type}'\033[0m")
                        write_state("idle")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] Classifier 失败（{e.returncode}）\033[0m")
                write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 classifier_agent.py\033[0m")
                write_state("idle")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"\033[91m[Router] 路由解析失败: {e}\033[0m")
                write_state("idle")

        # ============================== 技能管线 ==============================
        elif current_state == "pending_design":
            print("[Router] 正在唤醒主策划 Agent...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "lead_planner.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] 主策划 Agent 执行完毕，进入 Schema 审批。")
                write_state("pending_schema_approval")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] LeadPlanner 失败（{e.returncode}）\033[0m")
                continue
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 lead_planner.py\033[0m")
                continue

        elif current_state == "pending_schema_approval":
            # HITL: 主策划 Schema 验收
            result = require_human_approval(
                agent_name="LeadPlanner (主策划 Schema)",
                artifact_paths=[SCHEMA_FILE, os.path.join(WORKSPACE_DIR, "review_board.md")],
                next_state="pending_execution",
                reject_state="pending_design",
            )
            write_state(result)

        elif current_state == "pending_execution":
            print("[Router] 正在唤醒战斗数值策划 Agent...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "combat_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] Combat Agent 执行完毕，等待校验。")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] CombatAgent 失败（{e.returncode}）\033[0m")
                continue
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 combat_agent.py\033[0m")
                continue

        elif current_state == "pending_validation":
            print("[Router] 正在执行 JSON Schema 强校验...")
            try:
                with open(RESULT_FILE, "r", encoding="utf-8") as f:
                    business_data = json.load(f)
                with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                payload = business_data.get("payload", business_data)
                passed, errors = validator.validate(payload, schema_data)
                if passed:
                    print("\033[92m[安检通过] 数据完美符合契约！\033[0m")
                    write_state("pending_audit")
                else:
                    print("\033[91m[安检拦截]\033[0m")
                    for err in errors:
                        print(f"\033[91m  -> {err}\033[0m")
                    print("\033[91m[安检] 已回滚至 pending_execution，触发自动重试...\033[0m")
                    write_state("pending_execution")
            except FileNotFoundError as e:
                print(f"\033[91m[安检拦截] 文件不存在: {e}\033[0m")
                write_state("pending_execution")
            except json.JSONDecodeError as e:
                print(f"\033[91m[安检拦截] JSON 解析失败: {e}\033[0m")
                write_state("pending_execution")
            except ValueError as e:
                print(f"\033[91m[安检拦截] 校验异常: {e}\033[0m")
                write_state("pending_execution")

        elif current_state == "pending_audit":
            print("[Router] 正在交由主编进行数值逻辑审查...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "audit_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                if not os.path.exists(AUDIT_FILE):
                    print("\033[91m[Router] 审查文件未生成\033[0m")
                    write_state("idle")
                else:
                    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                        audit_data = json.load(f)
                    is_pass = audit_data.get("is_pass", False)
                    critique = audit_data.get("critique", "")
                    if is_pass:
                        print(f"\033[92m[主编放行] {critique}\033[0m")
                        write_state("pending_data_approval")
                    else:
                        print(f"\033[91m[主编打回] {critique}\033[0m")
                        write_state("pending_execution")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] AuditAgent 失败（{e.returncode}）\033[0m")
                write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 audit_agent.py\033[0m")
                write_state("idle")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"\033[91m[Router] 审查解析失败: {e}\033[0m")
                write_state("idle")

        elif current_state == "pending_data_approval":
            # HITL: 战斗数值验收
            result = require_human_approval(
                agent_name="CombatAgent + Audit (数值与审查)",
                artifact_paths=[RESULT_FILE, AUDIT_FILE],
                next_state="pending_assets",
                reject_state="pending_execution",
            )
            write_state(result)

        elif current_state == "pending_assets":
            print("[Router] 正在同时唤醒 Code Agent 和 UI Agent...")
            code_ok = False
            ui_ok = False
            print("[Router] --- [1/2] Code Agent ---")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "code_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] [OK] Code Agent 执行成功。")
                code_ok = True
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] CodeAgent 失败（{e.returncode}）\033[0m")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 code_agent.py\033[0m")
            print("[Router] --- [2/2] UI Agent ---")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "ux_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] [OK] UI Agent 执行成功。")
                ui_ok = True
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] UIAgent 失败（{e.returncode}）\033[0m")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 ux_agent.py\033[0m")
            if code_ok and ui_ok:
                print("[Router] Code + UI 均已完成，流水线终结。")
                write_state("completed")
            else:
                print("\033[91m[Router] 资产生成失败，打回 idle。\033[0m")
                write_state("idle")

        # ============================== 系统管线 (三重状态机) ==============================
        elif current_state == "clarifying_requirements":
            """
            追问闭环：Visionary 判断需求是否完备。
            读 task_status.json 判断 Vionary 结果，不再解析 stdout。
            """
            print("[Router] 正在运行 Visionary 审核需求...")
            try:
                result = subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Skills", "system_visionary.py")],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", cwd=ROOT_DIR,
                )
                output = (result.stdout or "") + (result.stderr or "")
                if output:
                    print(output, end="")

                # 读 task_status.json 判断 Visionary 写了哪个状态
                current_state = read_state()
                if current_state == "pending_design_approval":
                    # Visionary 写了 draft_ready → 直接推进
                    print(f"{GRN_COLOR}[Router] 需求已完备，设计草案已生成！{RESET_CLR}")
                elif current_state == "clarifying_requirements":
                    # Visionary 写了 need_info → 从 stdout 尾部提取问询文本
                    # 取最后一行合法 JSON {"status":"need_info","question":"..."}
                    question = "无法解析追问内容"
                    for line in output.strip().split("\n"):
                        line = line.strip()
                        if line.startswith('{"status"') and "need_info" in line:
                            try:
                                qd = json.loads(line)
                                if qd.get("status") == "need_info":
                                    question = qd.get("question", question)
                            except json.JSONDecodeError:
                                pass
                    user_reply = input(f"[主策追问]\n{question}\n").strip()
                    if user_reply:
                        try:
                            qa_block = (
                                f"\n\n> [主策追问] {question}\n"
                                f"> [老板指示] {user_reply}\n"
                            )
                            with open(CONCEPT_FILE, "a", encoding="utf-8") as f:
                                f.write(qa_block)
                            print(f"[Router] 已将问答对追加至概念简案。")
                            with open(CONCEPT_FILE, "r", encoding="utf-8") as f:
                                new_content = f.read().strip()
                            with open(CONCEPT_CACHE_FILE, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            concept_cache = new_content
                        except Exception as e:
                            print(f"[Router][警告] 无法追加/更新缓存: {e}")
                    write_state("clarifying_requirements")
                else:
                    # Visionary 失败或返回意外状态 → 重试
                    print(f"\033[91m[Router] Visionary 返回非预期状态: {current_state}，重试\033[0m")
                    write_state("clarifying_requirements")

            except Exception as e:
                print(f"\033[91m[Router] Visionary 执行异常: {e}\033[0m")
                write_state("idle")
            except Exception as e:
                print(f"\033[91m[Router] Visionary 执行异常: {e}\033[0m")
                write_state("idle")

        elif current_state == "pending_design_approval":
            """
            草案审查黑板：审阅 system_design_draft.md → 通过后进入 PM 排期
            """
            draft_path = os.path.join(WORKSPACE_DIR, "system_design_draft.md")

            print("\033[93m" + "=" * 60 + "\033[0m")
            print(f"\033[93m[草案审查] 设计草案已生成于: {draft_path}\033[0m")
            print("[草案审查] 您可以直接修改该文件，或在下方输入修改意见打回。若确认无误，请输入 'y' 进入任务拆解：")
            print("\033[93m" + "=" * 60 + "\033[0m")

            user_input = input("[草案审查] 请输入: ").strip()

            if user_input.lower() == "y" or "已手动修改" in user_input:
                print(f"\033[92m[草案审查] 老板放行！设计草案已确认。\033[0m")
                # ---- MD 智能阅卷与剪裁 ----
                _trim_open_questions_if_unchanged()
                # ---- 进入 PM 任务拆解 ----
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(ROOT_DIR, "Skills", "task_planner.py")],
                        check=True, cwd=ROOT_DIR,
                    )
                    print("[Router] Task Planner 执行完毕。")
                    # task_planner 内部已写 pending_plan_approval
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[Router] TaskPlanner 失败（{e.returncode}）\033[0m")
                    write_state("idle")
                except FileNotFoundError:
                    print("\033[91m[Router] 找不到 Skills/task_planner.py\033[0m")
                    write_state("idle")
            else:
                print(f"\033[91m[草案审查] 老板打回！意见: {user_input}\033[0m")
                try:
                    with open(BOSS_FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        f.write(user_input)
                except Exception as e:
                    print(f"[草案审查][警告] 无法保存反馈: {e}")
                # 打回 Visionary 重写 MD
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(ROOT_DIR, "Skills", "system_visionary.py")],
                        check=True, cwd=ROOT_DIR,
                    )
                    print("[Router] Visionary 已根据反馈重新生成草案。")
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[Router] Visionary 重试失败（{e.returncode}）\033[0m")
                    write_state("idle")
                except FileNotFoundError:
                    print("\033[91m[Router] 找不到 system_visionary.py\033[0m")
                    write_state("idle")

        elif current_state == "pending_plan_approval":
            """
            计划审查黑板：审阅 task_plan.md → 通过后进入执行阶段
            """
            plan_path = os.path.join(WORKSPACE_DIR, "task_plan.md")

            print("\033[93m" + "=" * 60 + "\033[0m")
            print(f"\033[93m[计划审查] 任务拆解计划已生成于: {plan_path}\033[0m")
            print("[计划审查] 输入修改意见重新排期，或输入 'y' 正式派发给子 Agent 团队执行：")
            print("\033[93m" + "=" * 60 + "\033[0m")

            user_input = input("[计划审查] 请输入: ").strip()

            if user_input.lower() == "y":
                print(f"\033[92m[计划审查] 老板放行！进入系统策划详细设计阶段。\033[0m")
                write_state("pending_system_design")
            else:
                print(f"\033[91m[计划审查] 老板打回！意见: {user_input}\033[0m")
                try:
                    with open(BOSS_FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        f.write(user_input)
                except Exception as e:
                    print(f"[计划审查][警告] 无法保存反馈: {e}")
                # 打回 Task Planner 重新排期
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(ROOT_DIR, "Skills", "task_planner.py")],
                        check=True, cwd=ROOT_DIR,
                    )
                    print("[Router] Task Planner 已重新排期。")
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[Router] TaskPlanner 重试失败（{e.returncode}）\033[0m")
                    write_state("idle")
                except FileNotFoundError:
                    print("\033[91m[Router] 找不到 task_planner.py\033[0m")
                    write_state("idle")

        elif current_state == "pending_system_design":
            """
            系统策划执行：调用 System Planner 生成详细玩法规则 MD。
            不输出 WBS / PM 派单指令，只负责把玩法规则讲透。
            """
            print("[Router] 正在调用 System Planner 生成详细设计草案...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "system_planner.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] System Planner 执行完毕，生成系统详细设计 MD。")
                # system_planner 内部已写 pending_system_approval
            except subprocess.CalledProcessError as e:
                if e.returncode == 2 and _get_retry_count("system_planner") < 2:
                    c = _get_retry_count("system_planner") + 1
                    _save_retry_count("system_planner", c)
                    print(f"\033[93m[Router] SystemPlanner 重试 ({c}/2)...\033[0m")
                else:
                    _clear_retry_count()
                    print(f"\033[91m[Router] SystemPlanner 失败（{e.returncode}）\033[0m")
                    write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 system_planner.py\033[0m")
                write_state("idle")

        elif current_state == "pending_system_approval":
            """
            V3 系统设计最终验收：老板审阅 System Planner 详细设计 → 放行进入 JSON 翻译。
            """
            draft_path = os.path.join(WORKSPACE_DIR, "system_design_detail.md")
            plan_path = os.path.join(WORKSPACE_DIR, "task_plan.md")

            print("\033[93m" + "=" * 60 + "\033[0m")
            print("\033[93m[系统验收] 系统策划已完成详细玩法规则设计。\033[0m")
            if os.path.exists(draft_path):
                print(f"[系统验收] 详细设计 MD: {draft_path} ({os.path.getsize(draft_path)} 字节)")
            if os.path.exists(plan_path):
                print(f"[系统验收] 任务拆解: {plan_path} ({os.path.getsize(plan_path)} 字节)")
            print("[系统验收] 输入修改意见打回系统策划重设计；或输入 'y' 批准，进入 Schema 翻译与数值配置阶段：")
            print("\033[93m" + "=" * 60 + "\033[0m")

            user_input = input("[系统验收] 请输入: ").strip()

            if user_input.lower() == "y":
                print(f"\033[92m[系统验收] 老板批准！进入 Schema 翻译与数值配置阶段。\033[0m")
                write_state("pending_schema_translate")
            else:
                print(f"\033[91m[系统验收] 老板打回！意见: {user_input}\033[0m")
                try:
                    with open(BOSS_FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        f.write(user_input)
                except Exception as e:
                    print(f"[系统验收][警告] 无法保存反馈: {e}")
                # V3: 打回至系统策划重做，非 Visionary
                write_state("pending_system_design")

        elif current_state == "pending_schema_translate":
            retry_count = _get_retry_count("schema_translator")
            print(f"[Router] 正在调用 Schema Translator 将 MD 翻译为结构化 JSON... (第 {retry_count + 1} 次)")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "schema_translator.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] Schema 翻译完毕，静默流转至 UX 交互设计。")
                _clear_retry_count()
                write_state("pending_ux_design")
            except subprocess.CalledProcessError as e:
                if e.returncode == 2 and retry_count < 2:
                    retry_count += 1
                    _save_retry_count("schema_translator", retry_count)
                    print(f"\033[93m[Router] SchemaTranslator JSON 被截断，自动重试 ({retry_count}/2)...\033[0m")
                elif e.returncode == 2 and retry_count >= 2:
                    _clear_retry_count()
                    print(f"\033[91m[Router] SchemaTranslator 重试 {retry_count} 次仍失败\033[0m")
                    user_input = input("[Router] Schema 翻译失败（可能因内容过长）。按 'y' 重试，按 'n' 回 idle: ").strip()
                    if user_input.lower() == "y":
                        write_state("pending_schema_translate")
                    else:
                        write_state("idle")
                else:
                    _clear_retry_count()
                    print(f"\033[91m[Router] SchemaTranslator 失败（{e.returncode}）\033[0m")
                    write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 schema_translator.py\033[0m")
                write_state("idle")

        elif current_state == "pending_ux_design":
            """
            UX 交互蓝图：读取系统策划详细案 → 输出 ui_interaction_blueprint.md
            在 Schema 翻译之后、数值填表之前执行。
            """
            print("[Router] 正在唤醒 UX Agent 进行表现层脱水与交互蓝图提炼...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "ux_agent.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] UX Agent 执行完毕，交互蓝图已生成。")
                write_state("pending_ux_approval")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] UX Agent 失败（{e.returncode}）\033[0m")
                write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 ux_agent.py\033[0m")
                write_state("idle")

        elif current_state == "pending_ux_approval":
            """
            UX 蓝图审批：老板审阅 ui_interaction_blueprint.md → 放行进入数值填表。
            """
            blueprint_path = os.path.join(WORKSPACE_DIR, "ui_interaction_blueprint.md")
            print("\033[93m" + "=" * 60 + "\033[0m")
            print("\033[93m[UX 审批] UX Agent 已完成交互蓝图提炼。\033[0m")
            if os.path.exists(blueprint_path):
                print(f"[UX 审批] 蓝图文件: {blueprint_path} ({os.path.getsize(blueprint_path)} 字节)")
            else:
                print("[UX 审批] 警告: 蓝图文件未找到，仍可放行或打回。")
            print("[UX 审批] 输入 'y' 批准，进入数值填表阶段；输入其他意见打回 UX 重做：")
            print("\033[93m" + "=" * 60 + "\033[0m")

            user_input = input("[UX 审批] 请输入: ").strip()
            if user_input.lower() == "y":
                print(f"\033[92m[UX 审批] 老板批准！进入数值填表阶段。\033[0m")
                write_state("pending_numerical")
            else:
                print(f"\033[91m[UX 审批] 老板打回！意见: {user_input}\033[0m")
                try:
                    with open(BOSS_FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        f.write(user_input)
                except Exception:
                    pass
                write_state("pending_ux_design")

        elif current_state == "pending_numerical":
            retry_count = _get_retry_count("numerical_planner")
            print(f"[Router] 正在唤醒 Numerical Planner 进行数值曲线推演... (第 {retry_count + 1} 次)")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "numerical_planner.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] 数值推演完毕，进入数值审批。")
                _clear_retry_count()
                write_state("pending_numerical_approval")
            except subprocess.CalledProcessError as e:
                if e.returncode == 2 and retry_count < 2:
                    retry_count += 1
                    _save_retry_count("numerical_planner", retry_count)
                    print(f"\033[93m[Router] NumericalPlanner JSON 被截断，自动重试 ({retry_count}/2)...\033[0m")
                elif e.returncode == 2 and retry_count >= 2:
                    _clear_retry_count()
                    print(f"\033[91m[Router] NumericalPlanner 重试 {retry_count} 次仍失败（JSON 截断）\033[0m")
                    user_input = input("[Router] 数值策划生成数据表失败（可能因为内容过长）。按 'y' 再次重试，或按 'n' 打回至主策划重新拆解: ").strip()
                    if user_input.lower() == "y":
                        write_state("pending_numerical")
                    else:
                        write_state("pending_schema_translate")
                else:
                    _clear_retry_count()
                    print(f"\033[91m[Router] NumericalPlanner 失败（{e.returncode}）\033[0m")
                    write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 numerical_planner.py\033[0m")
                write_state("idle")

        elif current_state == "pending_numerical_approval":
            # HITL: 数值成长表验收
            result = require_human_approval(
                agent_name="NumericalPlanner (数值成长表)",
                artifact_paths=[
                    os.path.join(WORKSPACE_DIR, "system_numerical_data.json"),
                    os.path.join(WORKSPACE_DIR, "system_numerical_docs.json"),
                ],
                next_state="pending_tech_design",
                reject_state="pending_numerical",
            )

            if result == "pending_tech_design":
                _upsert_archive(WORKSPACE_DIR, PROJECT_DB_DIR)
                print(f"\033[92m[Router] 核心数据已永久归档至 Project DB！\033[0m")
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(ROOT_DIR, "Skills", "build_memory_codex.py")],
                        check=True, cwd=ROOT_DIR,
                    )
                    print("[Router] 全局记忆库 (Codex + Registry) 已刷新。")
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[Router][警告] Codex 构建失败（{e.returncode}）\033[0m")
                except FileNotFoundError:
                    print("\033[91m[Router][警告] 找不到 build_memory_codex.py，跳过\033[0m")

            write_state(result)

        # ============================== 终态 ==============================
        elif current_state == "pending_tech_design":
            """
            主程架构：调用 Tech Architect 生成程序开发蓝图。
            """
            print("[Router] 正在调用 Tech Architect 生成程序开发蓝图...")
            try:
                subprocess.run(
                    [sys.executable, os.path.join(ROOT_DIR, "Agents", "tech_architect.py")],
                    check=True, cwd=ROOT_DIR,
                )
                print("[Router] Tech Architect 执行完毕，进入架构审批。")
                write_state("pending_tech_approval")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[Router] TechArchitect 失败（{e.returncode}）\033[0m")
                write_state("idle")
            except FileNotFoundError:
                print("\033[91m[Router] 找不到 tech_architect.py\033[0m")
                write_state("idle")

        elif current_state == "pending_tech_approval":
            """
            架构验收：审阅主程的 tech_blueprint.md → 通过后进入终态。
            """
            blueprint_path = os.path.join(WORKSPACE_DIR, "tech_blueprint.md")

            print("\033[93m" + "=" * 60 + "\033[0m")
            print(f"\033[93m[架构验收] 主程已完成程序开发蓝图: {blueprint_path}\033[0m")
            print("[架构验收] 请输入修改意见打回重做；或输入 'y' 确认最终定稿：")
            print("\033[93m" + "=" * 60 + "\033[0m")

            user_input = input("[架构验收] 请输入: ").strip()

            if user_input.lower() == "y":
                print(f"\033[92m[架构验收] 老板批准！进入最终自动审计纠错回环。\033[0m")
                write_state("pending_final_audit")
            else:
                print(f"\033[91m[架构验收] 老板打回！意见: {user_input}\033[0m")
                try:
                    with open(BOSS_FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        f.write(user_input)
                except Exception as e:
                    print(f"[架构验收][警告] 无法保存反馈: {e}")
                write_state("pending_tech_design")

        elif current_state == "pending_final_audit":
            """
            全自动纠错回环：
              1. 调用 Audit Agent 审查 → status: pass 或 reject + issues
              2. 若 reject → 遍历 issues，静默唤醒对应 Agent 修正 → 再次审计
              3. 循环至 pass → 生成 final_audit_report.md → HITL 确认结项
            """
            max_loops = 4
            loop_count = _get_retry_count("final_audit")
            print(f"[Router] 正在执行全自动审计纠错回环... (第 {loop_count + 1} 轮)")

            # 1. 先执行确定性 QA，结构正确后再调用 LLM 做语义审计。
            deterministic_issues = QAAuditor().audit_workspace(WORKSPACE_DIR)
            if deterministic_issues:
                print(f"\033[91m[确定性 QA] 发现 {len(deterministic_issues)} 个结构问题，跳过本轮 LLM 审计。\033[0m")
                audit_data = {"status": "reject", "issues": deterministic_issues}
                with open(AUDIT_FILE, "w", encoding="utf-8") as f:
                    json.dump(audit_data, f, ensure_ascii=False, indent=2)
            else:
                print("\033[92m[确定性 QA] 结构检查通过，进入 LLM 一致性审计。\033[0m")
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(ROOT_DIR, "Agents", "audit_agent.py")],
                        check=True, cwd=ROOT_DIR,
                    )
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[Router] AuditAgent 失败（{e.returncode}）\033[0m")
                    write_state("idle")
                    return
                except FileNotFoundError:
                    print("\033[91m[Router] 找不到 audit_agent.py\033[0m")
                    write_state("idle")
                    return

                if not os.path.exists(AUDIT_FILE):
                    print("\033[91m[Router] 审计文件未生成\033[0m")
                    write_state("idle")
                    return

                with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                    audit_data = json.load(f)

            status = audit_data.get("status", "reject")
            issues = audit_data.get("issues", [])

            if status == "pass":
                _clear_retry_count()
                print(f"\033[92m[审计通过] 所有内部 Bug 已修复，共经过 {loop_count + 1} 轮审计。\033[0m")
                # 生成终极报告
                try:
                    _generate_final_audit_report(loop_count + 1)
                except Exception as e:
                    print(f"[Router][警告] 报告生成失败: {e}")
                report_path = os.path.join(WORKSPACE_DIR, "final_audit_report.md")
                print(f"[Router] 终极审计报告已生成: {report_path}")
                user_input = input("[审计通过] 所有内部 Bug 已修复，详见 final_audit_report.md。输入 'y' 确认项目结项: ").strip()
                if user_input.lower() == "y":
                    print(f"\033[92m[Router] 老板确认结项！项目建设完毕。\033[0m")
                    write_state("completed")
                else:
                    print("[Router] 待老板确认后重新触发结项。")
                    # 保持 pending_final_audit
            else:
                # 有 issues → 自动纠错
                if loop_count >= max_loops:
                    _clear_retry_count()
                    print(f"\033[91m[Router] 审计纠错已达最大轮次 ({max_loops})，仍有 {len(issues)} 个问题未解决\033[0m")
                    user_input = input("[Router] 请老板人工介入。输入 'y' 忽略问题结项，或按其他键回 idle: ").strip()
                    if user_input.lower() == "y":
                        write_state("completed")
                    else:
                        write_state("idle")
                    continue

                print(f"\033[93m[审计打回] 发现 {len(issues)} 个问题，静默唤醒对应 Agent 修正...\033[0m")
                corrected_any = False
                for issue in issues:
                    agent = issue.get("responsible_agent", "")
                    anchor = issue.get("anchor", "")
                    desc = issue.get("problem_description", "")
                    suggestion = issue.get("fix_suggestion", "")

                    # 将 issue 数据写入临时修复指令文件，供 Agent 读取
                    fix_cmd = {
                        "correction_mode": True,
                        "anchor": anchor,
                        "problem": desc,
                        "suggestion": suggestion,
                    }
                    fix_cmd_path = os.path.join(WORKSPACE_DIR, ".fix_correction.json")
                    with open(fix_cmd_path, "w", encoding="utf-8") as f:
                        json.dump(fix_cmd, f, ensure_ascii=False)

                    agent_script = _get_agent_script(agent)
                    if agent_script:
                        print(f"[Router]   修正 {agent}: {anchor} — {desc[:60]}...")
                        try:
                            subprocess.run(
                                [sys.executable, os.path.join(ROOT_DIR, agent_script)],
                                check=True, cwd=ROOT_DIR,
                            )
                            corrected_any = True
                        except subprocess.CalledProcessError as e:
                            print(f"\033[91m[Router]   {agent} 修正失败（{e.returncode}）\033[0m")
                        except FileNotFoundError:
                            print(f"\033[91m[Router]   找不到 {agent_script}\033[0m")
                    else:
                        print(f"\033[91m[Router]   未知 Agent: {agent}，跳过\033[0m")

                # 清理修正指令
                if os.path.exists(fix_cmd_path):
                    os.remove(fix_cmd_path)

                # 递增循环计数，下一轮心跳自动再次审计
                loop_count += 1
                _save_retry_count("final_audit", loop_count)
                print(f"[Router] 本轮修正完毕，下一轮心跳重新审计 ({loop_count}/{max_loops})")
                write_state("pending_final_audit")

        elif current_state == "ui_done":
            print("[Router] UX 交互蓝图已完成，工作流结束。")
            write_state("completed")

        elif current_state == "completed":
            print("[Router] 本次流水线任务全部完成，进入待机摸鱼模式...")
            write_state("idle")

        else:
            print(f"[Router][警告] 遇到未知状态: '{current_state}'，重置为 idle")
            write_state("idle")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
