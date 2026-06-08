# WBS 任务拆解计划：时装染色系统

## 1. 任务分解

### 1.1 Schema Translator (格式翻译)
- **任务**：将终审通过的 MD 草案翻译为结构化 JSON Schema
- **输入文件**：终审通过的设计草案（当前文档）
- **产出文件**：`schema/dye_system_schema.json`
- **具体产出内容**：
  - 染色分区定义 Schema
  - 调色板数据结构 Schema
  - 染色方案存储 Schema
  - 材料消耗 Schema
  - 时装扩展字段 Schema
  - 角色数据扩展字段 Schema

### 1.2 Numerical Planner (数值策划)
- **任务**：生成染色系统数值表
- **输入文件**：`schema/dye_system_schema.json`
- **产出文件**：`numerical/dye_system_numerical.json`
- **具体产出内容**：
  - 染色材料消耗表（基础/高级）
  - 分区解锁券价格表
  - 免费产出数值表（日常/周常/好感度）
  - 付费礼包定价表
  - 预设方案数量上限（初始/付费扩展）
  - 预览精度分级参数

### 1.3 Code Agent (程序执行)
- **任务**：将校验通过的 JSON 翻译为 GDScript 代码
- **输入文件**：`schema/dye_system_schema.json`、`numerical/dye_system_numerical.json`
- **产出文件**：`scripts/dye_system.gd`
- **具体产出内容**：
  - 染色分区管理类
  - HSV 调色板计算类
  - 染色方案存储/加载类
  - 材料消耗逻辑
  - 实时预览渲染逻辑
  - 焕新展示动画触发逻辑
  - 预设方案管理类

### 1.4 UI Agent (UX/UI 设计)
- **任务**：设计染色系统前端界面
- **输入文件**：`schema/dye_system_schema.json`
- **产出文件**：`ui/dye_system_ui_design.md`
- **具体产出内容**：
  - 染色主界面布局（半屏模型 + 半屏调色面板）
  - 调色板交互设计（色相环、饱和度/明度滑块）
  - 分区选择交互（点击模型分区高亮）
  - 预设方案管理界面
  - 焕新展示动画 UI 控制
  - 快捷购买弹窗设计
  - 预览精度选项 UI

### 1.5 Audit Agent (审查官)
- **任务**：数值平衡性审查
- **输入文件**：`numerical/dye_system_numerical.json`
- **产出文件**：`audit/dye_system_audit_report.md`
- **具体产出内容**：
  - 免费产出与付费消耗比例审查
  - 材料消耗合理性审查
  - 预设方案扩展定价合理性审查
  - 分区解锁券定价合理性审查
  - 整体经济循环闭环审查

### 1.6 Combat Agent (战斗策划)
- **任务**：确认染色系统与战斗系统的交互边界
- **输入文件**：`schema/dye_system_schema.json`
- **产出文件**：`combat/dye_system_combat_interface.md`
- **具体产出内容**：
  - 确认染色系统不涉及战斗属性修改
  - 确认战斗场景中染色效果渲染性能要求
  - 确认战斗模型加载时染色方案读取逻辑
  - 确认战斗回放中染色效果显示

### 1.7 System Planner (系统策划) - 最终集成
- **任务**：集成所有子模块产出，生成最终可执行方案
- **输入文件**：所有下游 Agent 产出文件
- **产出文件**：`final/dye_system_implementation_plan.md`
- **具体产出内容**：
  - 开发排期建议
  - 测试用例清单
  - 上线灰度策略
  - 后续迭代路线图

## 2. 执行顺序与依赖

### 2.1 串行阶段
```
阶段1: Schema Translator → 产出 dye_system_schema.json
    ↓
阶段2: 并行执行以下任务
    ├── Numerical Planner → 产出 dye_system_numerical.json
    ├── UI Agent → 产出 dye_system_ui_design.md
    └── Combat Agent → 产出 dye_system_combat_interface.md
    ↓
阶段3: Audit Agent → 产出 dye_system_audit_report.md
    ↓
阶段4: Code Agent → 产出 dye_system.gd
    ↓
阶段5: System Planner → 产出 dye_system_implementation_plan.md
```

### 2.2 并行任务
- **阶段2 可并行执行**：
  - Numerical Planner
  - UI Agent
  - Combat Agent
- **阶段3 与阶段4 可部分并行**：
  - Audit Agent 审查数值时，Code Agent 可开始编写不依赖数值的框架代码

### 2.3 关键依赖关系
| 任务 | 依赖 | 产出文件 |
|------|------|----------|
| Numerical Planner | dye_system_schema.json | dye_system_numerical.json |
| UI Agent | dye_system_schema.json | dye_system_ui_design.md |
| Combat Agent | dye_system_schema.json | dye_system_combat_interface.md |
| Audit Agent | dye_system_numerical.json | dye_system_audit_report.md |
| Code Agent | dye_system_schema.json, dye_system_numerical.json | dye_system.gd |
| System Planner | 所有产出 | dye_system_implementation_plan.md |

## 3. 风险提示

### 3.1 阻塞点
| 风险 | 影响范围 | 缓解措施 |
|------|----------|----------|
| **Schema 定义不完整** | 所有下游 Agent 阻塞 | Schema Translator 需与 System Planner 确认所有字段，输出前进行内部评审 |
| **数值策划与 UI 设计冲突** | Numerical Planner 与 UI Agent 产出不一致 | 在阶段2 并行执行前，System Planner 提供明确的数值-UI 映射规则 |
| **性能风险未解决** | Code Agent 实现受阻 | 在阶段1 中，Schema Translator 需包含预览精度分级参数，为性能降级预留接口 |
| **后端数据存储方案未确认** | Code Agent 染色方案存储逻辑阻塞 | 在阶段1 中，Schema Translator 需与后端确认 `outfit_dye_data` 的 JSON 结构 |
| **美术蒙版生产延迟** | 染色分区功能无法上线 | 在阶段5 中，System Planner 需制定“首批仅支持基础时装”的灰度策略 |

### 3.2 跨团队依赖冲突
| 冲突 | 涉及团队 | 协调建议 |
|------|----------|----------|
| **染色材料道具注册** | 系统策划 vs 后端 | 在阶段1 中，Schema Translator 需明确 `use_effect_id` 的命名规范 |
| **商城商品分类新增** | 系统策划 vs 运营 | 在阶段5 中，System Planner 需与运营确认商品定价策略 |
| **拍照模式数据读取** | 系统策划 vs 前端 | 在阶段2 中，Combat Agent 需与前端确认 `outfit_dye_data` 的读取接口 |
| **云端同步方案** | 系统策划 vs 后端 | 在阶段1 中，Schema Translator 需与后端确认数据量级与同步策略 |

### 3.3 时间线建议
| 阶段 | 预计工时 | 关键里程碑 |
|------|----------|------------|
| 阶段1 | 1 天 | Schema 内部评审通过 |
| 阶段2 | 2 天 | 数值/UI/战斗接口并行产出 |
| 阶段3 | 0.5 天 | 审计报告通过 |
| 阶段4 | 3 天 | 代码实现完成 |
| 阶段5 | 0.5 天 | 最终方案评审通过 |
| **总计** | **7 天** | - |