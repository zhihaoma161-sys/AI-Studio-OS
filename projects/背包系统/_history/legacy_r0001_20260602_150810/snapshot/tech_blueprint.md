# 背包系统 - 程序开发蓝图

## 一、 整体架构概述

背包系统是一个**强数据一致性、弱实时性**的全局数据容器模块。其核心定位为所有道具操作的唯一数据源与校验中心，不承担任何角色展示或动画职责。性能瓶颈主要集中于高频的批量操作（使用/出售）时的数据库事务处理，以及每日首次打开背包时的过期道具批量扫描。系统采用**客户端-服务器架构**，所有数据变更必须经过服务端校验，客户端仅负责UI渲染与操作发起。

## 二、 前端模块划分 (Client)

### 2.1 UI 组件层
- **背包主界面 (InventoryMainPanel)**：包含分类标签栏（`category_tabs`）、搜索框（`search_keyword`）、排序下拉菜单（`sort_order`）、视图切换按钮（`view_mode`）、容量指示器（当前容量/最大容量）。
- **道具卡片 (ItemCard)**：显示 `item_card_info` 中的图标、名称、数量、品质边框、过期倒计时（若有）。支持点击、长按、多选状态。
- **筛选面板 (FilterPanel)**：按 `type`、`quality`、`tags` 等维度筛选，支持多选。
- **使用/出售确认弹窗 (ConfirmDialog)**：二次确认弹窗，包含道具信息、数量选择器（支持滑动条）、确认/取消按钮。扩容卡使用时需额外提示“容量立即生效且不可逆”。
- **批量操作进度条 (BatchProgressBar)**：显示批量使用/出售的当前进度。
- **空状态提示 (EmptyStateHint)**：筛选结果为空时显示“暂无道具”。

### 2.2 表现层控制器
- **纯功能型反馈**：所有操作反馈仅限标准UI反馈（弹窗、飘字、高亮、图标移除动画），**严禁调用角色模型、动画或语音**。
- **道具图标加载器**：从 `item_definition` 读取 `icon` 路径，加载失败时显示默认占位图。
- **过期倒计时控制器**：根据 `expire_time` 计算剩余时间，在道具卡片上显示倒计时，剩余 `expiry_warning_days` 天时显示红色标记。
- **货币增加动画**：出售成功后，在货币栏播放短暂的数值增加动画。

## 三、 后端逻辑划分 (Server)

### 3.1 持久化数据 (DB)
- **inventory 表**：
  - `player_id` (整数，主键之一)
  - `item_id` (字符串，主键之一，格式如 `ASCENSION_STONE_001`)
  - `quantity` (整数，默认1)
  - `tags` (字符串数组，默认空数组)
  - `expire_time` (整数，Unix秒，0表示永久)
  - `item_definition_id` (字符串，外键引用 `item_definition.id`)
- **inventory_capacity 表**：
  - `player_id` (整数，主键)
  - `inventory_capacity_max` (整数，初始值 `initial_capacity`)
- **overflow_mail 表**：
  - `mail_id` (字符串，主键，自动生成)
  - `player_id` (整数)
  - `item_id` (字符串)
  - `quantity` (整数)
  - `mail_title` (字符串，默认值)
  - `mail_content` (字符串，默认值)
  - `expire_time` (整数，邮件过期时间)
- **operation_log 表**（审计日志）：
  - `log_id` (自增主键)
  - `player_id` (整数)
  - `item_id` (字符串)
  - `quantity_before` (整数)
  - `quantity_after` (整数)
  - `operation_type` (字符串，如 `USE`, `SELL`, `ADD`, `REMOVE`)
  - `timestamp` (整数，Unix秒)

### 3.2 核心校验逻辑
- **道具存在性校验**：`item_id` 必须在 `inventory` 表中存在且属于该 `player_id`。
- **数量校验**：操作数量不得超过当前 `quantity`，且 `quantity` 不得为负数。
- **容量校验**：`add_item` 时，当前 `item_count` + 新增数量不得超过 `inventory_capacity_max`。
- **使用条件校验**：读取 `item_definition` 中的 `usable` 和 `use_condition`，校验玩家等级、任务阶段等条件。
- **出售条件校验**：读取 `item_definition` 中的 `sellable`，校验道具是否可出售。
- **批量操作上限校验**：单次批量操作数量不得超过 `batch_operation_limit`。
- **扩容卡校验**：使用扩容卡时，校验道具 `item_definition_id` 是否为 `expansion_card_item_id`，且数量足够。
- **过期校验**：每日首次打开背包时，扫描所有 `expire_time` 非0且小于当前时间戳的道具，自动删除并触发邮件通知。

## 四、 前后端通信协议 (API & 数据对接)

### 4.1 核心接口

- **`add_item`**: C->S / `(player_id, item_id, quantity, tags[])` / `{success: bool, error_code: string, overflow_mail_id: string|null}`
- **`remove_item`**: C->S / `(player_id, item_id, quantity)` / `{success: bool, error_code: string}`
- **`get_inventory`**: C->S / `(player_id, filter[])` / `{items: ItemInstance[], total_count: int}`
- **`get_item_detail`**: C->S / `(player_id, item_id)` / `{item: ItemInstance}`
- **`use_item`**: C->S / `(player_id, item_id, quantity)` / `{success: bool, error_code: string, effects: UseEffect[]}`
- **`sell_item`**: C->S / `(player_id, item_id, quantity)` / `{success: bool, error_code: string, currency_gained: {type: string, amount: int}}`
- **`check_capacity`**: C->S / `(player_id)` / `{current_count: int, max_capacity: int, is_full: bool}`
- **`expand_capacity`**: C->S / `(player_id)` / `{success: bool, new_capacity: int, error_code: string}`
- **`batch_use_items`**: C->S / `(player_id, item_id, quantity)` / `{results: {success: bool, error_code: string}[], total_success: int}`
- **`batch_sell_items`**: C->S / `(player_id, item_ids[])` / `{results: {item_id: string, success: bool, error_code: string}[], total_currency: {type: string, amount: int}}`
- **`add_tag`**: C->S / `(player_id, item_id, tag)` / `{success: bool}`
- **`remove_tag`**: C->S / `(player_id, item_id, tag)` / `{success: bool}`
- **`get_tags`**: C->S / `(player_id, item_id)` / `{tags: string[]}`
- **`check_expired_items`**: C->S / `(player_id)` / `{expired_items: string[], warning_items: {item_id: string, days_left: int}[]}`
- **`get_expiring_items`**: C->S / `(player_id, days)` / `{items: {item_id: string, expire_time: int}[]}`

### 4.2 错误码

所有接口返回的 `error_code` 字段使用以下枚举值：

- `ERROR_INVENTORY_FULL`：背包已满
- `ERROR_ITEM_NOT_FOUND`：道具不存在
- `ERROR_ITEM_NOT_ENOUGH`：道具数量不足
- `ERROR_ITEM_NOT_USABLE`：道具不可使用
- `ERROR_ITEM_NOT_SELLABLE`：道具不可出售
- `ERROR_USE_CONDITION_NOT_MET`：使用条件不满足
- `ERROR_NETWORK_TIMEOUT`：网络超时
- `ERROR_INTERNAL_SERVER`：服务器内部错误

## 五、 数值与配置表挂载

### 5.1 启动时加载配置
程序启动时，从 `system_numerical_data.json` 中读取以下全局常量并缓存至内存：

- `initial_capacity` (整数，默认100)
- `expansion_card_capacity_increase` (整数，默认50)
- `expansion_card_item_id` (字符串)
- `expansion_card_quantity` (整数，默认1)
- `mail_retention_days` (整数，默认7)
- `batch_operation_limit` (整数，默认99)
- `expiry_warning_days` (整数，默认3)
- `health_recover_amount` (整数，默认0)

### 5.2 运行时动态读取
- `item_definition` 表：每次操作道具时，根据 `item_definition_id` 读取对应的 `name`, `icon`, `quality`, `type`, `sellable`, `usable`, `batch_usable`, `use_condition`, `sell_currency_type`, `sell_price`, `use_effect_id`。
- `use_effect` 表：使用道具时，根据 `use_effect_id` 读取使用效果配置。

### 5.3 配置变更同步
- 道具定义变更（如新增标签、修改品质）通过事件驱动机制，触发 `inventory` 表中对应 `item_definition_id` 的 `tags` 字段同步更新。
- 若道具定义被删除，背包中对应道具显示为“未知道具”，禁止任何操作。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

### 阶段一 (P0 - 底层数据与协议)
- **建表**：创建 `inventory`、`inventory_capacity`、`overflow_mail`、`operation_log` 表。
- **定义 API 协议**：完成所有接口的请求/响应格式定义，包括错误码枚举。
- **后端核心校验逻辑**：
  - 实现 `add_item`、`remove_item`、`get_inventory`、`check_capacity` 接口。
  - 实现道具存在性、数量、容量校验。
  - 实现 `operation_log` 记录。
- **配置加载**：实现 `system_numerical_data.json` 的启动加载与缓存。

### 阶段二 (P1 - 前端核心表现)
- **UI 框架搭建**：实现背包主界面、道具卡片、分类标签栏、搜索框、排序、视图切换。
- **接入后端 API**：前端调用 `get_inventory`、`check_capacity` 渲染背包列表和容量指示器。
- **核心玩法跑通**：
  - 实现 `use_item` 和 `sell_item` 的单次操作流程（含二次确认弹窗）。
  - 实现 `expand_capacity` 扩容卡使用流程。
  - 实现 `batch_use_items` 和 `batch_sell_items` 批量操作流程（含进度条）。
- **筛选与排序**：实现前端筛选面板和排序逻辑，调用后端 `get_inventory` 时传递 `filter` 参数。

### 阶段三 (P2 - 表现层打磨)
- **过期处理**：
  - 实现每日首次打开背包时的 `check_expired_items` 调用。
  - 实现道具卡片上的过期倒计时显示和红色标记。
  - 实现过期前 `expiry_warning_days` 天的邮件提醒。
- **溢出邮件**：
  - 实现 `add_item` 时容量不足自动创建 `overflow_mail`。
  - 实现邮件系统接口对接（创建邮件、领取道具）。
- **边缘异常兜底**：
  - 网络超时重试机制（`ERROR_NETWORK_TIMEOUT`）。
  - 道具图标加载失败显示默认占位图。
  - 道具定义被删除时显示“未知道具”。
- **标签系统**：
  - 实现 `add_tag`、`remove_tag`、`get_tags` 接口。
  - 实现道具定义变更时的事件驱动标签同步。
- **审计日志**：确保所有操作均记录 `operation_log`。