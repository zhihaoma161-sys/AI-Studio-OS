# AI Studio OS

AI 驱动的游戏研发自动化工具。从概念简案出发，自动串联主策草案、系统详细案、数值推演、技术架构、UX 蓝图到最终审计纠错，闭环产出完整策划文档。

## 核心能力

- **双管线智能路由**：自动判断需求是「单体技能」还是「玩法系统」，走不同流水线
- **多 Agent 协作**：主策(Visionary)、系统策划、数值策划、技术架构、UX 表现、审计官共 11 个 Agent 接力
- **HITL 人机协同**：关键节点人工审批，其余自动执行
- **RAG 知识库**：支持按领域注入项目记忆、设计规范、红黑榜案例
- **Web GUI**：浏览器端操作，实时查看日志和产出文件

## 安装部署

### 前置条件

- Python 3.10+
- Git

### 步骤

```bash
git clone https://github.com/zhihaoma161-sys/AI-Studio-OS.git
cd AI_Studio_OS
pip install -r requirements.txt
```

### 配置 API Key

复制项目根目录的 `.env` 文件，填入你的大模型 API 信息：

```env
LLM_API_KEY="sk-your-key-here"
LLM_BASE_URL="https://api.deepseek.com/v1"
```

兼容所有 OpenAI 协议接口（DeepSeek、OpenAI、通义千问等）。

### 启动

```bash
python server.py
```

或双击 `start.bat`。启动脚本会依次探测项目 `.venv`、Windows `py -3`
和 `python` 命令；未找到 Python 时会显示明确的安装提示。
浏览器打开 `http://localhost:8080` 即可使用。

## 使用方式

1. 在输入框键入游戏概念（如「我要做一个背包系统」），按 Enter 提交
2. 点击「启动研发」，引擎自动走流水线
3. 遇到审批节点时，右侧控制栏会显示问询/审批提示，输入回复后确认
4. 生成的文件显示在右侧「下发文件」面板，点击即可打开
5. 研发完成后，点击「存档项目」将产物归档

**记忆积累**页签：可将优秀/错误案例归档至知识库，供后续 Agent 参考。

### 修改已归档系统

1. 在「设计项目」页将工作模式切换为「修改已有系统」。
2. 在「存档项目」中展开目标系统，选中指定文档并点击「启动迭代」。
3. 在独立的「文档迭代」页说明本次是「新增功能」还是「老功能迭代」，并输入具体需求。
4. 系统会生成影响文件、执行 Agent、依赖系统及局部修改预览。
5. 所有基础需求和补充意见都会逐条显示在消息日志中；使用同一个输入框继续提出纠正意见，上一轮预览会作为重新分析上下文。
6. 确认后只追加需求涉及的文档段落，数值修改同步到对应 `Excel/` 表，并执行终审。
7. 每次修改前会自动保存 `_history/` 快照；回到历史版本时直接恢复该版本号，不会额外生成新版本，快照丢失时会明确报错。

稳定项目保存在 `projects/<system_id>/current/`。同名旧时间戳目录会自动合并，最新版本作为正文，较早版本进入 `_history/`。
在「存档项目」中点击项目名称会打开对应的 `current/` 文档目录，点击「展开文档」可查看和选择具体文件。
迭代分析失败时，Web 会显示详细错误与追踪编号；完整追踪记录保存在 `.agent_workspace/change_analysis_log.jsonl`。

### Project Codex 与项目规范

`Knowledge/project_codex.md` 从全部稳定项目和当前有效数值表生成，不再依赖临时工作区。跨系统重复模式会进入候选规范，只有在 Web「记忆积累」页人工批准后才成为正式项目规范。

### 首次 API 配置

没有有效 API 配置时，Web 会自动显示配置向导并阻止 Agent 启动。支持 DeepSeek、OpenAI、通义千问、本地 Ollama 和自定义 OpenAI 兼容接口。API Key 仅保存到本机 `.env`，Web 接口只返回脱敏值。

## 项目结构

```
AI_Studio_OS/
├── Agents/           # 11 个 AI Agent 模块 + 7 个 Prompt 模板
│   └── prompts/      # 各 Agent 的角色设定 Prompt（.md）
├── Skills/           # 通用技能模块（LLM 客户端、RAG 加载器、状态机等）
├── Guards/           # 验证守卫（Schema 校验器、QA 审计器）
├── Knowledge/        # 项目知识库（设计规范、术语表、红黑榜案例）
├── ConfigTable/      # 配表子系统（端口 8081）
├── .agent_workspace/ # Agent 运行时工作目录（产出文件存放处）
├── main_router.py    # 核心路由器（状态机主循环）
├── server.py         # 唯一 Web 后端入口
├── app.py            # 旧入口兼容启动器，自动转发到 server.py
├── index.html        # Web 前端界面
├── start.bat         # 一键启动脚本
├── .env              # API Key 配置（需自行创建）
└── requirements.txt  # Python 依赖清单
```

## Agent 角色

| Agent | 职责 |
|-------|------|
| **Classifier** | 分类路由，判断技能/系统管线 |
| **Lead Planner** | 主策 Visionary：审阅需求、追问澄清、起草宏观草案 |
| **System Planner** | 系统策划：基于草案扩写极其详尽的系统详细设计案 |
| **Numerical Planner** | 数值策划：生成数值配置表和说明书 |
| **Tech Architect** | 技术架构师：输出程序开发蓝图 |
| **UX Agent** | 表现层脱水：生成 UI 交互蓝图 |
| **Schema Translator** | 结构翻译：将设计案转为结构化 Schema |
| **Audit Agent** | 审计官：跨文档一致性检查，自动纠错回环 |
| **Task Planner** | PM：拆解开发任务并排期 |
| **Combat Agent** | 战斗数据生成（技能管线） |
| **Code Agent** | 代码生成（技能管线） |
| **Archivist** | 归档员：将产出沉淀至知识库 |

## 配置

### .env 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `LLM_API_KEY` | 是 | 大模型 API Key |
| `LLM_BASE_URL` | 否 | API 地址，默认 `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 否 | 模型名，默认 `deepseek-chat` |

### 环境变量

| 变量 | 说明 |
|------|------|
| `AI_STUDIO_DATA_DIR` | 数据目录路径，默认项目根目录 |
| `AI_STUDIO_WEB_MODE` | Web GUI 模式开关（内部使用） |
| `AI_STUDIO_HOST` | Web 监听地址，默认 `127.0.0.1`；确认需要局域网访问时才改为 `0.0.0.0` |
| `AI_STUDIO_PORT` | Web 端口，默认 `8080` |
| `AI_STUDIO_ALLOWED_ORIGINS` | 允许访问 API/WebSocket 的来源列表，逗号分隔 |
| `AI_STUDIO_OPEN_BROWSER` | 是否启动时自动打开浏览器，默认 `1`；服务化运行可设为 `0` |

## 注意事项

- 当前版本直接通过源码运行，无打包版，需自行 `git clone` + `pip install`
- 配表模块已接入真实 HFSM 工作流；使用前需将 Excel 源表放入 `Excel/`
- `.agent_workspace/` 和 `Knowledge/` 中的运行时数据建议加入 `.gitignore` 或手动忽略
