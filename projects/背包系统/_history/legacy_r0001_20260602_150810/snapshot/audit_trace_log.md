
--- 审查时间: 2026-06-02 14:49:49 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 4.1 核心接口 - add_item
- 问题描述: 系统策划案和数值配表中，`add_item` 接口的参数为 `item_id`（道具实例ID），但程序蓝图中该接口的参数写成了 `item_definition_id`（道具模板ID）。这是数据类型/语义的致命断裂：调用方无法知道传入的是实例ID还是模板ID，且后端无法根据模板ID创建实例（缺少实例ID生成逻辑）。
- 修改建议: 请统一接口参数命名：要么全部使用 `item_definition_id` 并明确后端自动生成实例ID，要么全部使用 `item_id` 并明确调用方需传入已存在的实例ID。当前混用会导致开发阻塞。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 4.1 核心接口 - get_inventory
- 问题描述: 系统策划案中 `get_inventory` 的 filter 参数包含 `category`、`tags`、`quality` 等字段，但程序蓝图中的 filter 对象缺少 `category` 字段，多出了 `type` 字段。同时返回参数中缺少系统策划案明确要求的 `item_card_info` 对象（包含 icon, name, quality, quantity, expire_time 等），而是直接返回了零散字段。这会导致前端渲染组件 `ItemCardGrid` 无法获取完整数据。
- 修改建议: 请对齐 filter 参数：使用 `category` 而非 `type`（或明确两者等价并统一命名）。返回参数中应包含一个 `item_card_info` 对象或确保所有 `item_card_info` 所需的字段（icon, name, quality, quantity, expire_time）都在返回列表中。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 5.1 常量配置加载
- 问题描述: 程序蓝图中的常量配置加载路径存在多处错误：`batch_operation_limit` 引用了 `batch_sell.batch_operation_limit`，但数值配表中该值位于 `item_use.batch_operation_limit` 和 `item_sell.batch_operation_limit` 下；`expiry_warning_days` 引用了 `health_recover.expiry_warning_days`，但实际路径是 `expiry_management.expiry_warning_days`；`base_currency` 和 `event_token` 引用了 `sell_price.base_currency` 和 `sell_price.event_token`，但实际路径是 `item_sell.base_currency` 和 `item_sell.event_token`。这些错误的路径引用会导致程序启动时配置加载失败。
- 修改建议: 请根据数值配表 `system_numerical_data.json` 的实际 JSON 路径修正所有配置加载路径，确保程序能正确读取到配置值。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 5.2 错误码枚举加载
- 问题描述: 程序蓝图中的错误码枚举加载路径写的是 `error_codes.SUCCESS_CODE` 等，但数值配表中错误码定义在 `relations_and_enums.status_code_enum` 下，且数值配表中根本没有 `error_codes` 这个顶层键。这会导致所有错误码加载失败，整个系统的错误处理机制瘫痪。
- 修改建议: 请将错误码加载路径修正为 `relations_and_enums.status_code_enum.SUCCESS_CODE` 等，或要求数值策划在 JSON 中增加 `error_codes` 顶层键。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 4.5 扩容接口 - use_expansion_card
- 问题描述: 系统策划案和数值配表中均未定义 `use_expansion_card` 这个 API 接口。系统策划案仅在 2.5.1 节描述了扩容卡的使用逻辑，但未在 6.1 节接口定义中列出该接口。程序蓝图新增了此接口，但系统策划案中缺少对应的接口定义，属于接口定义遗漏。
- 修改建议: 请在系统策划案 6.1 节中补充 `use_expansion_card` 接口的定义，包括参数、返回值和错误码，以确保文档一致性。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 14:52:22 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - use_item
- 问题描述: 系统策划案中定义了 `batch_use_items` 和 `batch_sell_items` 接口，但程序蓝图中的 `use_item` 接口参数 `quantity` 为 int，而系统案中批量使用是独立接口。更严重的是，蓝图中的 `use_item` 返回参数缺少 `fail_reasons` 字段，但系统案中批量使用失败时需要返回失败原因列表。这会导致批量使用失败时前端无法展示具体失败原因。
- 修改建议: 在 `use_item` 接口的返回参数中增加 `fail_reasons` 字段（字符串数组），用于在批量使用失败时返回具体原因。或者，明确区分单次使用和批量使用的接口返回结构。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - sell_item
- 问题描述: 系统策划案中定义了 `batch_sell_items` 接口，参数为 `item_ids_with_quantities`（键值对列表），但程序蓝图中的 `batch_sell_items` 接口参数 `items` 为 `[{ item_id: string, quantity: int }]`，类型一致。然而，蓝图中的 `sell_item` 接口（单次出售）返回参数中缺少 `fail_reasons` 字段，而系统案中批量出售失败时需要返回失败原因列表。这会导致批量出售失败时前端无法展示具体失败原因。
- 修改建议: 在 `sell_item` 接口的返回参数中增加 `fail_reasons` 字段（字符串数组），用于在批量出售失败时返回具体原因。或者，明确区分单次出售和批量出售的接口返回结构。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 系统策划案中 `inventory` 表的主键为 `(player_id, item_id)`，但程序蓝图中的 `inventory` 表主键也是 `(player_id, item_id)`，类型为 `VARCHAR(64)`。然而，数值配表中的 `item_id` 字段定义为字符串，但系统策划案中 `item_id` 的示例为 `ASCENSION_STONE_001`，而程序蓝图中的 `item_id` 字段类型为 `VARCHAR(64)`，两者一致。但系统策划案中 `item_id` 字段在 `field_dictionary` 中定义为“道具实例的唯一标识”，而程序蓝图中的 `item_id` 字段在 `inventory` 表中也作为主键，但数值配表中的 `item_definition` 模块中，道具定义的主键是 `item_definition_id`（如 `ASCENSION_STONE_001`），而 `inventory` 表中的 `item_id` 是道具实例的唯一标识，两者概念不同。程序蓝图中的 `inventory` 表缺少 `item_definition_id` 字段，导致无法关联到道具定义表。
- 修改建议: 在 `inventory` 表中增加 `item_definition_id` 字段（VARCHAR(64)），作为外键引用 `item_definition` 表，并确保 `item_id` 是道具实例的唯一标识，`item_definition_id` 是道具模板的标识。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - get_inventory
- 问题描述: 系统策划案中 `get_inventory` 接口的 `filter` 参数包含 `type`, `tags`, `quality`, `search_keyword`, `sort_order`, `view_mode` 等字段，但程序蓝图中的 `get_inventory` 接口的 `filter` 参数缺少 `view_mode` 字段。虽然 `view_mode` 是前端表现层参数，但后端返回数据时可能需要根据 `view_mode` 决定返回字段的详细程度（如列表模式返回更多字段，网格模式返回较少字段）。缺少该字段可能导致前端无法正确渲染不同视图模式。
- 修改建议: 在 `get_inventory` 接口的 `filter` 参数中增加 `view_mode` 字段（字符串，可选 "list" 或 "grid"），后端根据该字段决定返回数据的详细程度。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - open_inventory_for_selection
- 问题描述: 系统策划案中定义了 `open_inventory_for_selection(selection_filter)` 接口，返回选中道具的ID及数量。但程序蓝图中的 `open_inventory_for_selection` 接口返回参数中缺少 `quantity` 字段，只返回了 `item_id`。这会导致外部系统无法知道选中道具的具体数量。
- 修改建议: 在 `open_inventory_for_selection` 接口的返回参数中，将 `items` 字段改为 `[{ item_id: string, quantity: int }]`，确保返回选中道具的ID和数量。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 14:55:00 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - use_expansion_card
- 问题描述: 程序蓝图新增了 `use_expansion_card` API，但系统策划案和数值配表中均未定义此接口。系统策划案仅提到“玩家可通过使用扩容卡永久增加背包容量上限”，但未定义该操作的接口、参数和返回值。这是一个未定义级致命 Bug，会导致扩容卡功能无法实现。
- 修改建议: 请 System Planner 在系统策划案中补充扩容卡使用的详细流程和接口定义，或由 Tech Architect 在蓝图中移除该 API 并改用通用道具使用流程实现扩容效果。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - inventory 表
- 问题描述: 程序蓝图中的 `inventory` 表将 `item_definition_id` 定义为字符串类型，但数值配表 `field_dictionary` 中 `item_definition_id` 定义为“【字符串】关联 item_definition 表的外键”，而 `item_id` 也定义为字符串。系统策划案中道具实例的 `item_id` 与 `item_definition_id` 关系模糊，且蓝图将 `item_id` 作为主键之一，可能导致数据冗余和引用混乱。
- 修改建议: 请 Tech Architect 明确 `inventory` 表的主键设计：是使用 `(player_id, item_id)` 还是 `(player_id, item_definition_id)`？建议统一使用 `item_definition_id` 作为外键，避免 `item_id` 与 `item_definition_id` 混淆。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - inventory 表
- 问题描述: 程序蓝图中的 `inventory` 表包含了大量从 `item_definition` 表冗余存储的字段（如 `name`, `icon`, `quality`, `type`, `sellable`, `usable`, `batch_usable`, `use_condition`, `sell_currency_type`, `sell_price`, `use_effect_id`）。系统策划案明确指出“道具定义变更后，背包中已有道具的标签字段需同步更新”，但蓝图未提供任何同步机制。这种冗余设计会导致数据不一致，且增加维护成本。
- 修改建议: 请 Tech Architect 重构 `inventory` 表，仅存储 `player_id`, `item_definition_id`, `quantity`, `tags`, `expire_time` 等实例特有字段，道具模板属性通过 JOIN `item_definition` 表获取。
### Issue 4 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.2 使用流程 - 步骤5
- 问题描述: 系统策划案中道具使用流程第5步描述“若道具数量为0，自动从背包中移除该道具条目”，但未定义移除后该道具实例的 `item_id` 是否可被复用，以及移除操作是否记录日志。这可能导致后续数据追踪困难。
- 修改建议: 请 System Planner 补充道具移除后的数据保留策略（如软删除、日志记录），并明确 `item_id` 的复用规则。
### Issue 5 [严重级别: 中]
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - player_id
- 问题描述: 数值说明书 `field_dictionary` 中 `player_id` 定义为“【字符串】玩家唯一标识”，但程序蓝图 `inventory` 表和 `inventory_capacity` 表中 `player_id` 也定义为字符串。然而，系统策划案中所有接口参数均使用 `player_id`，但未明确其数据类型。虽然目前一致，但若后续系统统一使用整数 ID，可能导致类型断裂。
- 修改建议: 请 Numerical Planner 与 System Planner 确认 `player_id` 的最终数据类型（字符串或整数），并在所有文档中统一声明。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 14:57:46 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - add_item
- 问题描述: 系统策划案和数值说明书中 `add_item` 接口的参数包含 `tags[]` 数组，用于在添加道具时指定动态标签。但程序蓝图中的 `add_item` 接口请求参数只有 `{ player_id, item_definition_id, quantity }`，缺少 `tags` 参数，导致动态标签无法在道具创建时附加，与系统案中标签系统（2.1.2节）的“动态标签”功能断链。
- 修改建议: 在 `add_item` 接口的请求参数中增加可选的 `tags: string[]` 字段，并在后端逻辑中处理该字段，将传入的标签合并到道具实例的 `tags` 数组中。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - inventory 表
- 问题描述: 数值说明书 `field_dictionary` 中 `player_id` 字段明确建议“统一为整数ID以兼容后续系统升级”，但程序蓝图中的 `inventory` 表将 `player_id` 定义为 `VARCHAR(64)`，与数值策划的明确建议冲突，可能导致后续系统升级时出现类型不兼容问题。
- 修改建议: 将 `inventory` 表（以及所有相关表）的 `player_id` 字段类型从 `VARCHAR(64)` 改为 `BIGINT` 或 `INT`，并在接口层做类型转换适配，以符合数值策划的升级建议。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 - 常量配置
- 问题描述: 程序蓝图中的 `EXPANSION_CARD_CAPACITY_INCREASE` 默认值写为 10，但数值配表 `inventory_capacity` 中 `expansion_card_capacity_increase` 的值为 50，两者不一致。虽然数值表拥有最终定价权，但蓝图中的默认值应同步为 50 以避免开发时使用错误常量。
- 修改建议: 将 `EXPANSION_CARD_CAPACITY_INCREASE` 的默认值从 10 改为 50，以匹配数值配表中的配置。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 - 常量配置
- 问题描述: 程序蓝图中的 `MAIL_RETENTION_DAYS` 默认值写为 30，但数值配表 `mail_system` 中 `mail_retention_days` 的值为 7，两者不一致。蓝图默认值应同步为 7 以避免溢出邮件保留时间过长。
- 修改建议: 将 `MAIL_RETENTION_DAYS` 的默认值从 30 改为 7，以匹配数值配表中的配置。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 错误码
- 问题描述: 系统策划案（6.2节）和数值配表 `error_codes` 中定义了 8 个错误码（如 `ERROR_ITEM_NOT_USABLE`、`ERROR_ITEM_NOT_SELLABLE`、`ERROR_USE_CONDITION_NOT_MET`、`ERROR_INTERNAL_SERVER`），但程序蓝图中的错误码枚举只定义了 4 个（`ERROR_CODE_INVENTORY_FULL`、`ERROR_CODE_ITEM_NOT_FOUND`、`ERROR_CODE_NETWORK_FAILURE`、`ERROR_CODE_INSUFFICIENT_ITEMS`），缺少道具不可使用、不可出售、使用条件不满足、服务器内部错误等关键错误码，导致前端无法正确处理这些错误场景。
- 修改建议: 在程序蓝图的错误码枚举中补充 `ERROR_CODE_ITEM_NOT_USABLE`、`ERROR_CODE_ITEM_NOT_SELLABLE`、`ERROR_CODE_USE_CONDITION_NOT_MET`、`ERROR_CODE_INTERNAL_SERVER` 等错误码，并分配对应的数值编码。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 15:00:28 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 核心接口
- 问题描述: 系统策划案 2.2.2 节明确要求使用道具后需记录操作日志，包含 `item_id`、`quantity_before`、`quantity_after`、`operation_type`、`timestamp`、`player_id`。程序蓝图在 3.1 节定义了 `operation_log` 表，但在 4.1 节的核心接口列表中，`use_item` 和 `sell_item` 接口的返回值中均未包含 `operation_log_id` 或类似字段，导致前端无法确认日志记录是否成功，存在日志丢失风险。
- 修改建议: 在 `use_item` 和 `sell_item` 接口的响应结构中增加 `operation_log_id` (字符串) 字段，用于返回本次操作生成的日志记录ID，以便前端进行后续的日志确认或错误追踪。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) -> 3.1 持久化数据 (DB)
- 问题描述: 系统策划案 2.4.1 节提到 `inventory_capacity_max` 记录当前背包容量上限，且 2.4.2 节提到扩容卡使用后该值增加。程序蓝图在 3.1 节定义了 `inventory_capacity` 表，但该表只存储了 `inventory_capacity_max` 字段。系统策划案 2.4.1 节还要求显示“当前容量/最大容量”，其中“当前容量”需要实时计算背包中所有道具实例的总数。程序蓝图缺少一个用于快速获取当前道具总数的字段或索引，在 `add_item` 和 `remove_item` 时，每次都需要全表扫描 `inventory` 表计算 `item_count`，在高并发下可能导致性能瓶颈。
- 修改建议: 在 `inventory_capacity` 表中增加一个 `current_item_count` (整数) 字段，用于实时记录当前背包中的道具实例总数。在 `add_item` 和 `remove_item` 操作成功后，同步更新该字段，避免每次查询都进行全表扫描。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 核心接口
- 问题描述: 系统策划案 2.3.2 节描述出售流程时，提到“系统计算出售价格（根据道具定义中的 `sell_price` 字段）”，并且出售成功后“增加对应货币（基础货币/活动代币）”。程序蓝图中的 `sell_item` 接口返回值 `currency_gained` 只包含了 `type` 和 `amount`，但没有明确指出货币增加的具体来源（是基础货币还是活动代币）。这会导致前端在展示货币增加动画时，无法准确区分货币类型，可能造成UI显示错误。
- 修改建议: 在 `sell_item` 接口的 `currency_gained` 对象中，明确 `type` 字段的取值范围，并确保其与 `item_definition` 表中的 `sell_currency_type` 字段一致。同时，在接口文档中注明，前端应根据 `type` 字段的值（如 `BASE_CURRENCY` 或 `EVENT_TOKEN`）来播放对应的货币增加动画。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) -> 3.2 核心校验逻辑
- 问题描述: 系统策划案 2.2.2 节提到，使用道具时“系统读取道具定义中的 `use_effect_id`，匹配对应的使用效果配置”。程序蓝图在 5.2 节提到“运行时动态读取 `use_effect` 表”，但在 3.2 节的核心校验逻辑中，并未包含对 `use_effect_id` 是否存在且有效的校验。如果 `use_effect_id` 配置错误或指向一个不存在的效果，会导致使用道具时服务器内部错误，且无法回滚。
- 修改建议: 在 `use_item` 接口的核心校验逻辑中，增加对 `use_effect_id` 的校验步骤：读取 `item_definition` 中的 `use_effect_id`，并在 `use_effect` 表中查询该ID是否存在。如果不存在，则返回 `ERROR_INTERNAL_SERVER` 错误码，并记录错误日志。
### Issue 5 [严重级别: 中]
- 责任方: ux_agent
- 目标文件: ui_interaction_blueprint.md
- 锚点: 二、表现层控制器 -> 批量操作进度条
- 问题描述: 系统策划案 2.2.3 节和 2.3.3 节提到批量操作时，若中间某次失败，已成功部分不回溯。程序蓝图 2.1 节定义了 `BatchProgressBar` 组件。但 UX Agent 在补全 `BatchProgressBar` 时，如果添加了“失败时自动重试”或“一键跳过失败项”等需要后端支持的高级逻辑，则属于逻辑污染。当前文档未提供 `ui_interaction_blueprint.md` 的具体内容，但根据审查法则，需指出如果存在此类补全，则必须移除。
- 修改建议: 移除 `BatchProgressBar` 中任何关于“失败重试”或“跳过失败项”的复杂逻辑，仅保留纯前端的进度显示功能。批量操作失败的处理应由后端返回错误码，前端根据错误码显示提示信息，不进行自动重试。
**当前审查总计问题:** 5 个
