# 背包系统 - 程序开发蓝图

## 一、 整体架构概述

背包系统是一个**纯客户端-服务端强一致**的仓储工具型模块。核心性能瓶颈在于**道具列表的频繁增删改查**以及**堆叠逻辑的实时计算**。系统不涉及实时同步（如帧同步），所有操作通过 HTTP/WebSocket 请求-响应模式完成。服务端作为权威数据源，负责所有道具数量、堆叠、扩容的校验与持久化；客户端负责UI渲染、交互反馈与表现层动画。

## 二、 前端模块划分 (Client)

### UI 组件层
- **`BagMainPanel`**：全屏背包主界面，半透明毛玻璃背景（`UI_BG_COLOR: #1A1A2ECC`），网格4列布局，道具图标统一 `ICON_SIZE: 80x80` 像素。
- **`CategoryTabBar`**：顶部一级分类标签栏，固定顺序“材料”、“礼物”、“消耗品”、“任务道具”、“其他”，对应 `item_category_id` 1~5。
- **`SortDropdown`**：排序下拉按钮，选项为“不排序”、“稀有度升序”、“稀有度降序”，对应 `current_sort_order` 0/1/2。
- **`ItemGrid`**：道具网格列表，支持垂直滑动，滑动条细窄样式。根据 `current_bag_category_id` 和 `current_sort_order` 动态渲染。
- **`ItemDetailPopup`**：道具详情浮窗，半透明毛玻璃背景，淡入淡出动画。包含图标、名称、描述、稀有度标签、持有数量、来源说明。
- **`ConfirmDialog`**：二次确认弹窗，用于“使用”和“丢弃”操作，包含确认/取消按钮。
- **`ExpandPanel`**：底部扩容面板，显示当前容量（`occupied_slots` / `bag_max_slots`）和“扩容”按钮。
- **`ExpandSelectionPopup`**：扩容方式选择弹窗，提供“消耗扩容券”和“消耗付费货币”两种选项，显示当前持有数量。
- **`EmptyStatePlaceholder`**：空分类占位图，灰色半透明背景 + 空箱子图标 + 文字“该分类暂无道具”。
- **`LoadingOverlay`**：数据加载中动画遮罩。
- **`ErrorRetryPanel`**：数据加载失败提示面板，包含“数据加载失败，请稍后重试”文字和“刷新”按钮。

### 表现层控制器
- **`BagAnimationController`**：管理所有UI动画，包括弹窗淡入淡出、飘字动画（“-1”绿色/红色）、扩容成功飘字（“+10”）。
- **`ItemIconAnimator`**：道具图标上的数量更新动画，以及使用/丢弃后的消失动画。
- **`NetworkRetryHandler`**：数据加载失败时，按 `RETRY_INTERVAL`（5秒）自动重试，最多 `MAX_RETRY_COUNT`（3次）。重试失败后显示 `ErrorRetryPanel`，并提供刷新按钮。
- **`ConcurrentClickGuard`**：防止并发点击，在弹窗动画播放期间忽略中间操作，仅响应最后一次点击。

## 三、 后端逻辑划分 (Server)

### 持久化数据 (DB)
- **`player_bag` 表**：
  - `player_id` (主键)
  - `bag_item_list` (JSON数组)：存储所有道具条目，每个条目包含 `item_id`, `item_count`, `current_stack_size`。
  - `current_bag_category_id` (int)：当前选中分类，默认0。
  - `current_sort_order` (int)：当前排序规则，默认0。
  - `bag_max_slots` (int)：背包最大格子数，初始值 `INITIAL_BAG_CAPACITY` (50)。
  - `occupied_slots` (int)：当前已占用格子数，等于 `bag_item_list` 长度。
- **`item_config_table` 表**：全局道具配置表，包含所有道具的 `id`, `name`, `description`, `rarity`, `category_id`, `usable_flag`, `discardable_flag`, `source_description`, `effect_description` 等字段。服务端和客户端同步维护。

### 核心校验逻辑
- **`add_item(item_id, count)` 校验**：
  1. 校验 `item_id` 是否存在于 `item_config_table`。
  2. 遍历 `bag_item_list`，查找相同 `item_id` 且 `current_stack_size < MAX_STACK_SIZE` 的堆叠，优先填充。
  3. 若所有堆叠已满或未找到，检查 `occupied_slots < bag_max_slots`，若满足则创建新堆叠；否则返回 `ERROR_BAG_FULL` (1001)。
  4. 更新 `item_count` 和 `current_stack_size`，确保不超过 `MAX_STACK_SIZE` (999)。
- **`remove_item(item_id, count)` 校验**：
  1. 校验 `item_id` 是否存在于 `bag_item_list`。
  2. 检查对应条目的 `item_count >= count`，若不满足返回 `ERROR_ITEM_NOT_ENOUGH` (1002)。
  3. 扣除后若 `item_count` 归零，从 `bag_item_list` 中移除该条目，更新 `occupied_slots`。
- **`use_item(item_id, count)` 校验**：
  1. 校验 `item_usable_flag` 为 `true`。
  2. 调用 `remove_item` 逻辑扣除道具。
  3. 触发道具效果（如调用体力系统 `add_stamina(STAMINA_RECOVER_VALUE)`）。
  4. 若效果执行失败，回滚 `remove_item` 操作。
- **`discard_item(item_id, count)` 校验**：
  1. 校验 `item_discardable_flag` 为 `true`。
  2. 调用 `remove_item` 逻辑永久移除道具。
- **`expand_capacity(expand_type)` 校验**：
  1. 校验 `bag_max_slots < BAG_CAPACITY_HARD_CAP` (500)，若已达到返回错误。
  2. 根据 `expand_type` 参数选择扣除逻辑：
     - **`expand_type = 1`（消耗扩容券）**：校验 `EXPAND_ITEM_ID` (10001) 的 `item_count >= 1`，调用 `remove_item(EXPAND_ITEM_ID, 1)` 扣除。
     - **`expand_type = 2`（消耗付费货币）**：校验 `premium_currency` 余额 >= `EXPAND_COST_CURRENCY` (100)，调用货币系统扣除。
  3. 校验通过后，`bag_max_slots` 增加 `EXPAND_SLOTS_PER_USE` (10)。
- **`check_bag_space(item_id, count)` 预检**：
  1. 模拟 `add_item` 逻辑，计算新道具是否能被容纳（通过堆叠或空位）。
  2. 返回布尔值，供商城等系统在购买前调用。

## 四、 前后端通信协议 (API & 数据对接)

- **`C2S_GetBagData`**: C->S / 无参数 / 返回 `bag_item_list`, `current_bag_category_id`, `current_sort_order`, `bag_max_slots`, `occupied_slots`。
- **`C2S_SetCategoryFilter`**: C->S / `category_id` (int) / 返回成功状态。服务端更新 `current_bag_category_id`。
- **`C2S_SetSortOrder`**: C->S / `sort_order` (int, 0/1/2) / 返回成功状态。服务端更新 `current_sort_order`。
- **`C2S_UseItem`**: C->S / `item_id` (int), `count` (int) / 返回成功状态或错误码 (`ERROR_ITEM_NOT_ENOUGH`)。服务端执行 `use_item` 逻辑。
- **`C2S_DiscardItem`**: C->S / `item_id` (int), `count` (int) / 返回成功状态或错误码 (`ERROR_ITEM_NOT_ENOUGH`)。服务端执行 `discard_item` 逻辑。
- **`C2S_ExpandCapacity`**: C->S / `expand_type` (int, 枚举值: 1=消耗扩容券, 2=消耗付费货币) / 返回成功状态或错误码（如“扩容券不足”、“货币不足”、“已达上限”）。服务端执行 `expand_capacity` 逻辑。
- **`C2S_AddItem`**: 内部接口，供战斗、邮件、商城等系统调用。C->S / `item_id` (int), `count` (int) / 返回成功状态或错误码 (`ERROR_BAG_FULL`)。
- **`C2S_RemoveItem`**: 内部接口，供消耗系统调用。C->S / `item_id` (int), `count` (int) / 返回成功状态或错误码 (`ERROR_ITEM_NOT_ENOUGH`)。
- **`C2S_CheckBagSpace`**: 内部接口，供商城系统调用。C->S / `item_id` (int), `count` (int) / 返回布尔值 `has_space`。
- **`S2C_BagUpdate`**: S->C / 推送消息，当背包数据发生变化时（如道具增减、扩容），服务端主动推送更新后的 `bag_item_list`, `occupied_slots`, `bag_max_slots` 等字段。

## 五、 数值与配置表挂载

程序启动时，从 `system_numerical_data.json` 中读取以下配置并加载到内存缓存中：
- **`item_config_table`**：解析为字典，以 `item_id` 为键，包含 `name`, `description`, `rarity`, `category_id`, `usable_flag`, `discardable_flag`, `source_description`, `effect_description` 等字段。客户端和服务端均需加载。
- **常量字段**：`MAX_STACK_SIZE` (999), `INITIAL_BAG_CAPACITY` (50), `EXPAND_ITEM_ID` (10001), `EXPAND_SLOTS_PER_USE` (10), `PREMIUM_CURRENCY` ("premium_currency"), `EXPAND_COST_CURRENCY` (100), `BAG_CAPACITY_HARD_CAP` (500), `MAIL_RETENTION_DAYS` (30), `RETRY_INTERVAL` (5), `MAX_RETRY_COUNT` (3), `STAMINA_RECOVER_VALUE` (60), `ERROR_BAG_FULL` (1001), `ERROR_ITEM_NOT_ENOUGH` (1002), `UI_BG_COLOR` ("#1A1A2ECC"), `ICON_SIZE` (80), `FREE_CURRENCY` ("free_currency"), `GACHA_CURRENCY` ("gacha_currency")。
- **状态码枚举**：`current_bag_category_id` 的枚举值（0~5），`current_sort_order` 的枚举值（0~2），`item_rarity` 的枚举值（1~4），错误码枚举（1001, 1002）。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

### 阶段一 (P0 - 底层数据与协议)
1. **数据库建表**：创建 `player_bag` 表，定义 `bag_item_list` 的 JSON Schema。
2. **配置表加载**：实现 `item_config_table` 的解析与缓存逻辑。
3. **核心API定义**：完成 `C2S_AddItem`, `C2S_RemoveItem`, `C2S_CheckBagSpace`, `C2S_GetBagData` 的接口定义与基础实现。
4. **后端核心校验逻辑**：实现 `add_item`（含堆叠逻辑）、`remove_item`、`use_item`、`discard_item`、`expand_capacity` 的校验逻辑，包括 `expand_type` 枚举值的分支处理。
5. **错误码枚举**：定义并实现 `ERROR_BAG_FULL` (1001) 和 `ERROR_ITEM_NOT_ENOUGH` (1002) 的返回逻辑。

### 阶段二 (P1 - 前端核心表现)
1. **UI框架搭建**：实现 `BagMainPanel`, `CategoryTabBar`, `SortDropdown`, `ItemGrid`, `ItemDetailPopup`, `ConfirmDialog`, `ExpandPanel`, `ExpandSelectionPopup` 等UI组件。
2. **数据绑定**：前端接入 `C2S_GetBagData` 接口，实现 `bag_item_list` 的渲染与分类/排序筛选。
3. **核心玩法跑通**：实现道具使用、丢弃、扩容的完整前端流程，对接后端API，确保核心增删改查功能可用。
4. **堆叠逻辑前端展示**：道具图标上正确显示 `current_stack_size`，并在 `add_item` 后自动更新。

### 阶段三 (P2 - 表现层打磨)
1. **动画与特效接入**：实现弹窗淡入淡出、飘字动画（使用/丢弃/扩容）、按钮点击缩放等UI动画。
2. **边界与异常处理**：
   - 实现空分类占位图、数据加载失败重试逻辑（`RETRY_INTERVAL` 和 `MAX_RETRY_COUNT`）。
   - 实现背包满时的提示与跳转逻辑。
   - 实现扩容券/货币不足时的置灰与提示。
   - 实现并发点击防护。
3. **跨系统联调**：与战斗、邮件、商城系统联调，确保 `add_item` 和 `remove_item` 接口在背包满/道具不足时正确返回错误码，并触发邮件系统溢出逻辑。
4. **性能优化**：优化 `bag_item_list` 的增删改查性能，确保大量道具（接近500格）时列表滑动流畅。