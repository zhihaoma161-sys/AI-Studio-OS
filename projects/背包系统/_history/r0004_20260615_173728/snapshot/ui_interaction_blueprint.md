# 背包系统 - UI 交互蓝图与生图清单

---

## 界面一：背包主界面（全屏列表）

### 1. 核心交互需求表 (Functional Checklist)
- **【前台可见数据】**：
  - 道具网格列表（固定4列），每个道具显示：图标、名称、稀有度标签（N/R/SR/SSR对应颜色）、当前持有数量
  - 顶部五个一级分类标签：“材料”、“礼物”、“消耗品”、“任务道具”、“其他”（固定顺序，不可拖动）
  - 每个一级标签下可展开/折叠的子分类列表（如“材料”下分“突破材料”、“技能材料”）
  - 排序按钮（按稀有度升序/降序切换）
  - 底部背包容量指示器：当前已占用格数 / 总容量格数（如 “23/50”）
  - 底部“扩容”按钮
- **【必须包含的操作】**：
  - 点击一级分类标签 → 筛选并刷新列表
  - 点击子分类标签 → 进一步筛选（可选，若子分类存在）
  - 点击排序按钮 → 切换排序方式（升序/降序/默认）
  - 点击任意道具图标 → 打开详情浮窗
  - 垂直滑动列表 → 浏览更多道具
  - 点击“扩容”按钮 → 打开扩容选择弹窗
- **【状态流转与兜底】**：
  - **正常状态** → 网格列表展示道具，底部容量指示器正常显示
  - **空状态（当前分类无道具）** → 显示占位图（灰色半透明背景 + 空箱子图标）+ 文字“该分类暂无道具” `[UX 自动补全]`
  - **加载状态（数据加载中）** → 显示骨架屏（灰色方块占位）+ 转圈动画 `[UX 自动补全]`
  - **加载失败（网络异常）** → 显示“数据加载失败，请稍后重试”提示 + “刷新”按钮 `[UX 自动补全]`
  - **背包已满（容量达到上限）** → 底部容量指示器变为红色警告色，扩容按钮高亮闪烁 `[UX 自动补全]`
  - **扩容达到硬上限** → “扩容”按钮置灰，提示“背包容量已达上限” `[UX 自动补全]`

### 2. 结构化生图 Prompt (Layout Inspiration)
- **Prompt (English)**:
  - **Type**: Mobile Game UI
  - **Style**: Sci-fi, clean flat design, dark mode, high contrast, semi-transparent frosted glass background
  - **Layout**: Full-screen grid layout, top horizontal filter tabs, bottom fixed status bar with capacity indicator and expand button
  - **Key Components**: “5 Filter Tabs (Materials, Gifts, Consumables, Quest Items, Other)”, “4-column Item Grid”, “Sort Button (top-right)”, “Capacity Bar (bottom-left)”, “Expand Button (bottom-right)”
  - **Keywords**: UI/UX, user interface architecture, wireframe layout, clean hierarchy, figma layout, mobile inventory screen
- **布局意图解析 (中文)**：采用全屏网格布局最大化道具展示密度，顶部固定筛选标签便于快速切换分类，底部固定状态栏确保容量信息始终可见。4列网格在移动端可提供良好的视觉平衡，避免单行过长或过短。

---

## 界面二：道具详情浮窗（弹窗）

### 1. 核心交互需求表 (Functional Checklist)
- **【前台可见数据】**：
  - 道具图标（高精度2D插画）
  - 道具名称
  - 道具描述文本
  - 稀有度标签（N/R/SR/SSR对应颜色）
  - 当前持有数量
  - 来源说明（如“来源：关卡掉落”）
- **【必须包含的操作】**：
  - 点击浮窗外任意区域 → 关闭浮窗
  - 点击关闭按钮（X）→ 关闭浮窗
  - 若道具可被使用（消耗品）→ 显示“使用”按钮（蓝色高亮）
  - 若道具可被丢弃 → 显示“丢弃”按钮（红色警告色）
  - 若道具不可使用 → “使用”按钮置灰，悬停提示“该道具不可使用”
  - 若道具不可丢弃 → “丢弃”按钮置灰，悬停提示“该道具不可丢弃”
- **【状态流转与兜底】**：
  - **正常状态** → 浮窗淡入显示，内容完整
  - **配置缺失（道具信息异常）** → 显示“道具信息异常”提示 + “联系客服”按钮 `[UX 自动补全]`
  - **并发点击保护** → 浮窗动画播放期间，忽略后续点击 `[UX 自动补全]`
  - **关闭状态** → 点击外部或关闭按钮，浮窗淡出消失

### 2. 结构化生图 Prompt (Layout Inspiration)
- **Prompt (English)**:
  - **Type**: Mobile Game Popup Modal
  - **Style**: Sci-fi, clean flat design, dark mode, frosted glass background, semi-transparent overlay
  - **Layout**: Centered modal with rounded corners, top area for item icon, middle area for name/description/rarity, bottom area for action buttons (Use/Discard)
  - **Key Components**: “Large Item Icon (center-top)”, “Item Name & Rarity Badge”, “Item Description Text”, “Quantity Display”, “Source Info”, “Use Button (blue)”, “Discard Button (red)”, “Close Button (top-right)”
  - **Keywords**: UI/UX, user interface architecture, wireframe layout, clean hierarchy, figma layout, modal popup
- **布局意图解析 (中文)**：采用居中弹窗设计，不遮挡主界面角色展示（符合项目宪法红线）。信息层级从上到下依次为图标、名称/稀有度、描述、来源，底部放置操作按钮，符合用户阅读习惯。

---

## 界面三：二次确认弹窗（使用/丢弃确认）

### 1. 核心交互需求表 (Functional Checklist)
- **【前台可见数据】**：
  - 道具图标
  - 道具名称
  - 操作类型说明（如“使用”或“丢弃”）
  - 使用效果描述（如“恢复体力”）（仅使用操作）
  - 警告文字（仅丢弃操作：“确定要丢弃该道具吗？丢弃后不可恢复。”）
- **【必须包含的操作】**：
  - 点击“确认”按钮 → 执行操作（使用或丢弃）
  - 点击“取消”按钮 → 关闭弹窗，不执行操作
  - 点击弹窗外区域 → 关闭弹窗（仅使用操作可；丢弃操作建议仅通过按钮关闭以强调警告性） `[UX 自动补全]`
- **【状态流转与兜底】**：
  - **正常状态** → 弹窗淡入显示
  - **操作成功** → 弹窗关闭，道具图标上显示“-1”飘字动画（使用为蓝色，丢弃为红色）
  - **操作失败（数量不足）** → 弹窗显示“道具数量不足”提示，自动关闭 `[UX 自动补全]`
  - **操作失败（效果执行失败）** → 弹窗显示“使用失败：[具体原因]”提示 `[UX 自动补全]`
  - **网络中断** → 弹窗显示“网络异常，请重试”提示，不扣除道具 `[UX 自动补全]`

### 2. 结构化生图 Prompt (Layout Inspiration)
- **Prompt (English)**:
  - **Type**: Mobile Game Confirmation Popup
  - **Style**: Sci-fi, clean flat design, dark mode, high contrast warning (for discard), semi-transparent overlay
  - **Layout**: Centered modal with rounded corners, top area for warning icon (discard) or item icon (use), middle area for description text, bottom area for two buttons (Confirm/Cancel)
  - **Key Components**: “Warning Icon (discard only)”, “Item Icon”, “Confirmation Text”, “Confirm Button (blue for use, red for discard)”, “Cancel Button (gray)”
  - **Keywords**: UI/UX, user interface architecture, wireframe layout, clean hierarchy, figma layout, confirmation modal
- **布局意图解析 (中文)**：采用标准二次确认弹窗布局，使用和丢弃共用同一模板但颜色区分（使用为蓝色，丢弃为红色），确保玩家在操作前能清晰识别操作类型。丢弃操作增加警告图标以强化风险提示。

---

## 界面四：扩容选择弹窗

### 1. 核心交互需求表 (Functional Checklist)
- **【前台可见数据】**：
  - 当前背包容量（已占用/总容量）
  - 扩容后容量预览（如“扩容后：50 → 60”）
  - 两种扩容方式选项：
    - 使用“背包扩容券”：显示当前持有数量（如“背包扩容券 x 3”）
    - 使用付费货币：显示所需货币数量及当前余额
- **【必须包含的操作】**：
  - 点击任一扩容方式选项 → 选中该方式（高亮）
  - 点击“确认扩容”按钮 → 执行扩容操作
  - 点击“取消”按钮 → 关闭弹窗
  - 若扩容券不足 → 对应选项置灰，提示“背包扩容券不足，请前往活动或商城获取”
  - 若付费货币不足 → 对应选项置灰，提示“货币不足，请前往充值”，并提供“前往充值”跳转链接
  - 若背包容量已达硬上限 → 弹窗不弹出，主界面扩容按钮已置灰 `[UX 自动补全]`
- **【状态流转与兜底】**：
  - **正常状态** → 两种扩容方式均可选
  - **扩容成功** → 弹窗关闭，主界面容量指示器更新，播放“+[扩容格数]”飘字动画
  - **扩容券不足** → 对应选项置灰，不可选择
  - **付费货币不足** → 对应选项置灰，不可选择，显示“前往充值”链接
  - **网络中断** → 弹窗显示“网络异常，请重试”提示，不扣除任何资源 `[UX 自动补全]`

### 2. 结构化生图 Prompt (Layout Inspiration)
- **Prompt (English)**:
  - **Type**: Mobile Game Selection Popup
  - **Style**: Sci-fi, clean flat design, dark mode, semi-transparent overlay
  - **Layout**: Centered modal with rounded corners, top area for current capacity display, middle area for two expansion options (side by side or stacked), bottom area for Confirm/Cancel buttons
  - **Key Components**: “Current Capacity Display”, “Expansion Preview Text”, “Option 1: Expansion Ticket (with count)”, “Option 2: Premium Currency (with cost)”, “Confirm Button”, “Cancel Button”
  - **Keywords**: UI/UX, user interface architecture, wireframe layout, clean hierarchy, figma layout, selection modal
- **布局意图解析 (中文)**：采用双选项布局，让玩家在两种扩容方式间直观对比。每种选项显示当前持有/余额，帮助玩家快速判断是否可行。底部确认按钮在未选择任何选项时置灰，防止误操作 `[UX 自动补全]`。

## [新][2026-06-15] 背包要新增一个出售功能，点击之后界面有点变化，从点击道具变成批量选择道具，同时可以预览出售的结果。
> 变更编号：chg_20260615_160521_588e53；原始需求：背包要新增一个出售功能，点击之后界面有点变化，从点击道具变成批量选择道具，同时可以预览出售的结果。；影响原章节：界面一：背包主界面（全屏列表）

### 新增或修改内容
### 1. 核心交互需求表 (Functional Checklist)
- **【必须包含的操作】**：
  - 新增：点击“出售”按钮 → 进入批量选择模式
  - 新增：在批量选择模式下，点击道具图标 → 切换选中/取消选中状态
  - 新增：在批量选择模式下，底部显示“已选中 X 件道具，预估总售价：YYYY”预览
  - 新增：在批量选择模式下，点击“确认出售”按钮 → 弹出二次确认弹窗
  - 新增：在批量选择模式下，点击“取消”或“返回”按钮 → 退出批量选择模式，恢复普通浏览
- **【状态流转与兜底】**：
  - **新增：批量选择模式（正常）** → 道具图标左上角出现勾选框，已选中道具高亮边框，底部显示选中数量和预估总售价
  - **新增：批量选择模式（无可出售道具）** → “出售”按钮置灰，提示“当前无可出售道具”
  - **新增：批量选择模式（选中道具后）** → “确认出售”按钮变为可点击（蓝色高亮）
  - **新增：批量选择模式（未选中任何道具）** → “确认出售”按钮置灰，提示“请先选择要出售的道具”


## [新][2026-06-15] 背包要新增一个出售功能，点击之后界面有点变化，从点击道具变成批量选择道具，同时可以预览出售的结果。
> 变更编号：chg_20260615_160521_588e53；原始需求：背包要新增一个出售功能，点击之后界面有点变化，从点击道具变成批量选择道具，同时可以预览出售的结果。；影响原章节：界面三：二次确认弹窗（使用/丢弃确认）

### 新增或修改内容
### 1. 核心交互需求表 (Functional Checklist)
- **【前台可见数据】**：
  - 新增：出售确认时，显示选中道具列表缩略（图标+名称+数量）
  - 新增：出售确认时，显示总售价预览
- **【必须包含的操作】**：
  - 新增：点击“确认出售”按钮 → 执行出售操作
  - 新增：点击“取消”按钮 → 关闭弹窗，返回批量选择模式
- **【状态流转与兜底】**：
  - **新增：出售成功** → 弹窗关闭，退出批量选择模式，主界面道具列表刷新，底部显示“出售成功，获得 YYY 货币”飘字动画
  - **新增：出售失败（网络中断）** → 弹窗显示“网络异常，请重试”提示，不扣除道具 `[UX 自动补全]`
