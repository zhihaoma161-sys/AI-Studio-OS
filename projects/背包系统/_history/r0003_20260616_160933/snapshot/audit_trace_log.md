
--- 审查时间: 2026-06-08 15:50:32 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 核心接口
- 问题描述: 蓝图定义了 `Bag_UpdateSortFilter` 接口，但系统策划案和数值说明书中均未定义该接口的请求参数 `category_id` 和 `sort_order` 的数据类型。系统案中 `current_bag_category_id` 和 `current_sort_order` 是客户端本地状态，策划案并未要求每次切换分类/排序时都调用后端接口。该接口的存在会导致前后端数据不一致（后端存储了客户端本地状态），且无任何业务逻辑支撑，属于逻辑死胡同。
- 修改建议: 移除 `Bag_UpdateSortFilter` 接口，将分类筛选与排序逻辑完全放在客户端本地执行，无需同步到后端。后端 `Bag_GetData` 返回的 `current_bag_category_id` 和 `current_sort_order` 字段也应移除，或作为客户端初始默认值下发。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) -> 核心校验逻辑 -> `expand_capacity(method)`
- 问题描述: 蓝图中的 `expand_capacity` 接口参数为 `method: "item" | "currency"`，但系统策划案中明确要求扩容操作需要消耗具体道具（`EXPAND_ITEM_ID`）或具体货币（`PREMIUM_CURRENCY`）。蓝图没有定义如何传递消耗的具体道具ID或货币类型，且未说明当 `method` 为 `"item"` 时，是否默认使用 `EXPAND_ITEM_ID`。这会导致后端无法正确校验消耗品，属于字段遗漏。
- 修改建议: 修改 `Bag_ExpandCapacity` 接口的请求参数，增加 `item_id`（可选）和 `currency_type`（可选）字段，或明确约定当 `method` 为 `"item"` 时，固定消耗 `EXPAND_ITEM_ID`（10001），当 `method` 为 `"currency"` 时，固定消耗 `PREMIUM_CURRENCY`。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 核心接口
- 问题描述: 系统策划案中多处提到需要调用 `check_bag_space(item_id, count)` 接口（如商城购买前预检），但蓝图中的 `Bag_CheckSpace` 接口的请求参数只包含了 `item_id, count`，没有包含 `player_id`。这是一个明显的参数遗漏，会导致后端无法确定是哪个玩家的背包。
- 修改建议: 在 `Bag_CheckSpace` 接口的请求参数中增加 `player_id` 字段，或明确说明该接口通过会话/Token隐式获取玩家ID。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) -> 核心校验逻辑 -> `use_item(item_id, count)`
- 问题描述: 系统策划案中 `use_item` 接口的返回参数包含 `effect_result`（如调用体力系统后的结果），但蓝图中的 `Bag_UseItem` 接口返回参数只定义了 `{ success: bool, error_code?: int, effect_result?: object }`，没有定义 `effect_result` 的具体结构。这会导致客户端无法处理道具使用后的效果反馈（如体力值变化），属于数据类型断裂。
- 修改建议: 在蓝图或API文档中明确定义 `effect_result` 的结构，例如 `{ stamina_added: int, current_stamina: int }`，或约定客户端在调用 `use_item` 后，主动调用体力系统的接口获取最新数据。
### Issue 5 [严重级别: 中]
- 责任方: ux_agent
- 目标文件: ui_interaction_blueprint.md
- 锚点: 界面一：背包主界面（全屏列表） -> 1. 核心交互需求表 -> 【状态流转与兜底】
- 问题描述: UX 蓝图在【状态流转与兜底】中补全了“背包已满状态 → 底部容量指示变红/警告色，提示文字‘背包已满’”，但系统策划案中并未定义背包已满时底部容量指示的视觉反馈（变红/警告色）。虽然这属于纯前端表现，但系统案中明确写了“当 occupied_slots 等于 bag_max_slots 时，玩家无法获得任何新道具”，并未要求UI有特殊颜色反馈。此补全可能误导UI开发，导致与策划案意图不符。
- 修改建议: 移除“底部容量指示变红/警告色”的补全，或与 System Planner 确认是否真的需要此视觉反馈。如果确认需要，应在系统策划案中补充该表现层需求。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-08 15:53:21 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案中明确要求了 `check_bag_space(item_id, count)` 接口用于商城系统预检背包空间，但程序蓝图中缺少该 API 的定义。这会导致商城购买流程无法实现预检逻辑，可能造成货币扣除后因背包满而回滚的糟糕体验。
- 修改建议: 在 API 协议列表中新增 `Bag_CheckSpace` 接口，定义请求参数 `{ item_id: int, count: int }` 和返回 `{ has_space: bool, error_code?: int }`。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - use_item
- 问题描述: 系统策划案中 `use_item` 接口在效果执行失败时需要回滚 `remove_item` 操作，但程序蓝图中的 `use_item` 逻辑描述为“若效果执行失败，回滚 `remove_item` 操作”，这缺少了实现回滚所需的具体机制（如事务或补偿操作）。这是一个逻辑死胡同，开发者无法仅凭此描述实现安全的回滚。
- 修改建议: 明确 `use_item` 的实现方式：使用数据库事务包裹 `remove_item` 和效果执行逻辑，或定义明确的补偿操作（如 `add_item`）在失败时调用。需在蓝图中补充事务或补偿机制的具体设计。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案中 `expand_capacity` 接口需要根据扩容方式（道具券或付费货币）扣除不同的资源，但程序蓝图中的 API `Bag_ExpandCapacity` 只接收 `expand_type: string`，没有定义如何校验和扣除对应资源。这导致扩容逻辑的实现不完整，缺少关键的校验和扣除步骤。
- 修改建议: 在 `Bag_ExpandCapacity` 的后端逻辑中补充：根据 `expand_type` 的值（如 "item" 或 "premium"），分别调用 `remove_item` 扣除扩容券或调用货币系统接口扣除付费货币。同时需在 API 文档中明确 `expand_type` 的枚举值及其对应的资源扣除逻辑。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 系统策划案中 `bag_item_list` 的每个条目包含 `current_stack_size` 字段，用于堆叠逻辑。但程序蓝图中的 `player_bag` 表定义中，`bag_item_list` 的 JSON 结构只提到了 `{item_id, item_count, current_stack_size}`，没有明确 `item_count` 和 `current_stack_size` 的关系。这可能导致数据模型歧义：`item_count` 是总数量还是单个堆叠的数量？`current_stack_size` 是否冗余？
- 修改建议: 明确 `bag_item_list` 中每个条目的数据模型：建议移除 `item_count`，仅保留 `current_stack_size` 表示该堆叠的数量，总数量由服务端计算或客户端累加。或者在蓝图中明确说明 `item_count` 是总数量，`current_stack_size` 是当前堆叠数量，并解释两者关系。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 核心校验逻辑
- 问题描述: 系统策划案中 `discard_item` 接口需要校验 `item_discardable_flag`，但程序蓝图中的 `discard_item` 逻辑描述为“校验 `item_discardable_flag == true`”，这缺少了从 `item_config_table` 获取该标志位的具体步骤。虽然这是一个实现细节，但考虑到这是一个关键的安全校验（防止误删重要道具），蓝图应明确说明校验的数据来源。
- 修改建议: 在 `discard_item` 的逻辑描述中补充：从服务端内存中的 `item_config_table` 字典中，根据 `item_id` 获取对应的 `discardable_flag` 字段进行校验。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-08 15:55:57 ---
### Issue 1 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案中定义了 `check_bag_space(item_id, count)` 预检接口，用于商城系统在购买前检查背包空间。程序蓝图中虽然定义了 `C2S_CheckBagSpace` API，但该 API 的返回参数 `{ has_space, error_code }` 缺少 `error_code` 的具体枚举值定义。系统策划案中 `ERROR_BAG_FULL` 错误码为 1001，但 `check_bag_space` 接口在空间不足时返回的 `error_code` 是否复用该错误码，或使用新的错误码，未在蓝图或数值表中定义，导致商城系统无法准确判断预检失败原因。
- 修改建议: 在 `C2S_CheckBagSpace` 的返回参数中明确 `error_code` 的枚举值，例如：空间充足时返回 `error_code: 0`，空间不足时返回 `error_code: 1001 (ERROR_BAG_FULL)`。同时，在数值说明书或蓝图中补充该枚举定义。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 系统策划案中多次提到 `item_config_table` 是道具配置表，用于查询道具的完整信息（名称、描述、稀有度、分类、可用性、可丢弃性等）。程序蓝图在“五、 数值与配置表挂载”中声明了从 `system_numerical_data.json` 加载 `item_config_table`。然而，数值配表 `data.json` 中的 `item_config_table` 字段包含了 `effect_description`，但程序蓝图中的 `use_item` 校验逻辑并未提及需要读取或使用 `effect_description` 字段。虽然这不构成致命错误，但 `effect_description` 字段在客户端详情浮窗中用于显示使用效果，蓝图未明确客户端如何获取该字段，存在客户端渲染数据源缺失的风险。
- 修改建议: 在程序蓝图的“五、 数值与配置表挂载”中，明确客户端也需要加载 `item_config_table` 到内存，并说明 `effect_description` 字段用于道具详情浮窗的“使用效果描述”显示。或者，在 `C2S_GetBagData` 的返回参数中，增加 `item_config_table` 的完整数据，或提供一个单独的 `C2S_GetItemConfig` API 供客户端按需查询。
### Issue 3 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - C2S_ExpandCapacity
- 问题描述: 系统策划案中，扩容操作支持两种方式：使用道具（扩容券）和使用付费货币。程序蓝图中的 `C2S_ExpandCapacity` API 请求参数为 `{ expand_type (0=道具券, 1=付费货币) }`。但是，蓝图没有定义当 `expand_type` 为 0（使用道具券）时，服务端如何扣除道具。蓝图中的 `expand_capacity 校验` 逻辑提到“若使用扩容券：校验 `EXPAND_ITEM_ID` 的 `item_count` 是否 >= 1”，但未说明扣除操作的具体实现（是调用 `remove_item` 还是直接在 `expand_capacity` 内部处理）。这可能导致实现时出现逻辑遗漏或重复扣减。
- 修改建议: 在 `expand_capacity` 校验逻辑中，明确说明：当 `expand_type` 为 0 时，服务端应调用 `remove_item(player_id, EXPAND_ITEM_ID, 1)` 来扣除扩容券，并处理其返回的错误码。如果 `remove_item` 返回 `ERROR_ITEM_NOT_ENOUGH`，则 `expand_capacity` 应返回相应的错误码。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - S2C_BagDataUpdate
- 问题描述: 系统策划案中，道具使用/丢弃成功后，客户端需要播放“-1”飘字动画，并在道具归零时从列表中移除该条目。程序蓝图定义了 `S2C_BagDataUpdate` 推送，但该推送的返回参数 `{ updated_bag_item_list, bag_max_slots, occupied_slots }` 中，`updated_bag_item_list` 是完整的道具列表。对于频繁的单次使用/丢弃操作，推送整个列表会造成不必要的网络开销。虽然这不影响功能正确性，但在高并发场景下可能成为性能瓶颈。更优的做法是推送增量更新（如 `{ removed_item_ids, updated_item_stacks }`）。
- 修改建议: 建议将 `S2C_BagDataUpdate` 的推送参数改为增量更新格式，例如：`{ removed_item_ids: [item_id1, ...], updated_item_stacks: [{item_id, new_count, new_stack_size}, ...], bag_max_slots, occupied_slots }`，以减少网络传输量。或者，在蓝图注释中说明当前全量推送方案是阶段一实现，后续可优化为增量推送。
### Issue 5 [严重级别: 低]
- 责任方: ux_agent
- 目标文件: ui_interaction_blueprint.md
- 锚点: 界面一：背包主界面（全屏列表） - 状态流转与兜底
- 问题描述: UX 蓝图在“背包满状态”下，自动补全了“底部容量指示器显示红色警告样式”。系统策划案中并未明确要求背包满时容量指示器变红，仅提到“当 `occupied_slots` 等于 `bag_max_slots` 时，玩家无法获得任何新道具”。虽然这是一个合理的 UX 增强，但属于 [UX 自动补全] 的纯前端表现，根据审查法则，应予以放行。然而，该补全内容与系统策划案中“背包满时弹出提示”的边界处理逻辑存在轻微不一致（系统案强调弹窗提示，UX 案强调视觉警告）。建议确认是否两者都需要实现，还是仅保留弹窗提示。
- 修改建议: 建议 System Planner 或 UX Agent 确认：背包满时，是仅通过弹窗提示（如系统策划案所述），还是同时需要底部容量条变红的视觉警告（如 UX 蓝图所述）。如果两者都需要，请在系统策划案或 UX 蓝图中明确说明。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-08 15:58:22 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案中明确要求了 `check_bag_space(item_id, count)` 接口用于商城系统预检，但程序蓝图中定义的 `C2S_CheckBagSpace` 接口返回参数缺少 `has_space` 字段，仅返回 `error_code`，导致商城系统无法判断是否有空间。
- 修改建议: 在 `C2S_CheckBagSpace` 的返回参数中补充 `has_space` 布尔字段，明确指示是否有足够空间容纳新道具。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 核心校验逻辑
- 问题描述: 系统策划案中道具使用流程要求：若效果逻辑执行失败（如体力已满），需回滚 `item_count` 的减少操作。但程序蓝图中的 `use_item` 校验逻辑仅描述了“若失败则回滚道具扣除”，未定义如何回滚以及回滚的触发条件（如调用 `add_stamina` 返回错误码时的处理），存在逻辑死胡同。
- 修改建议: 在 `use_item` 逻辑中明确：先执行效果逻辑（如调用 `add_stamina`），若效果逻辑返回失败，则不扣除道具，直接返回错误码；若效果逻辑成功，再扣除道具。避免先扣道具再回滚的复杂操作。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - S2C_BagDataUpdate
- 问题描述: 系统策划案中道具使用/丢弃成功后，客户端需要播放“-1”飘字动画。但 `S2C_BagDataUpdate` 推送的增量数据中，`updated_item_stacks` 仅包含 `item_id, item_count, current_stack_size`，缺少 `delta_count`（本次变更数量）字段，客户端无法得知具体减少了多少数量，无法准确播放飘字动画（如使用多个道具时需显示“-3”）。
- 修改建议: 在 `S2C_BagDataUpdate` 的 `updated_item_stacks` 中增加 `delta_count` 字段，表示本次变更的净数量（正数为增加，负数为减少），供客户端飘字动画使用。
### Issue 4 [严重级别: 中]
- 责任方: ux_agent
- 目标文件: ui_interaction_blueprint.md
- 锚点: 界面二：道具详情浮窗（Modal） - 核心交互需求表
- 问题描述: 系统策划案中明确要求：若 `item_config_table` 中未找到该 `item_id`，浮窗显示“道具信息异常”提示，并提供“联系客服”按钮（调用客服系统接口）。但 UX 蓝图中的配置缺失状态仅描述了显示“道具信息异常”提示 + “联系客服”按钮，未提及需要调用客服系统接口，缺少后端接口定义。
- 修改建议: 在 UX 蓝图中补充说明：点击“联系客服”按钮需调用客服系统接口（如 `C2S_ContactCustomerService`），并确保该接口在程序蓝图中已定义。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 核心校验逻辑
- 问题描述: 系统策划案中扩容操作支持两种方式：消耗道具（扩容券）和消耗付费货币。但程序蓝图中的 `expand_capacity` 校验逻辑仅描述了校验 `EXPAND_ITEM_ID` 和 `premium_currency`，未定义如何根据 `expand_type` 参数选择对应的扣除逻辑，且 `C2S_ExpandCapacity` 接口的请求参数 `expand_type` 未在蓝图中的 API 定义中明确枚举值。
- 修改建议: 在 `C2S_ExpandCapacity` 的请求参数中明确 `expand_type` 的枚举值（0=道具，1=付费货币），并在后端校验逻辑中根据 `expand_type` 分支处理对应的扣除操作。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-08 16:00:56 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: API 接口列表中缺少 `C2S_SetCategoryFilter` 和 `C2S_SetSortOrder` 的返回数据结构定义。系统策划案和数值表均定义了 `current_bag_category_id` 和 `current_sort_order` 字段，且蓝图在“后端逻辑划分”中提到了服务端会更新这两个字段，但在API协议部分，这两个接口仅声明了“返回成功状态”，未定义返回的完整数据包结构（例如是否需要返回更新后的 `current_bag_category_id` 或 `current_sort_order` 给客户端确认）。这会导致前后端数据状态不同步的风险。
- 修改建议: 在 `C2S_SetCategoryFilter` 和 `C2S_SetSortOrder` 的接口描述中，明确返回的数据结构，建议返回更新后的 `current_bag_category_id` 或 `current_sort_order` 字段，以便客户端进行状态同步校验。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - expand_capacity 校验
- 问题描述: 蓝图中的 `expand_capacity` 校验逻辑缺少对 `expand_type` 参数的枚举值定义和校验。系统策划案中明确提到了两种扩容方式（消耗扩容券和消耗付费货币），蓝图也提到了 `expand_type` 参数，但未在文档中定义 `expand_type` 的合法枚举值（如1和2）以及非法值的处理逻辑。这会导致接口调用方（客户端）传入非法值时，服务端行为不可预期。
- 修改建议: 在 `expand_capacity` 校验逻辑中，明确 `expand_type` 参数的枚举值定义（例如：1=消耗扩容券, 2=消耗付费货币），并添加对非法 `expand_type` 值的错误处理逻辑（如返回错误码或忽略请求）。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - S2C_BagUpdate
- 问题描述: 蓝图定义了 `S2C_BagUpdate` 推送消息，但未明确该推送的触发条件和推送范围。系统策划案中涉及多个可能改变背包数据的操作（使用、丢弃、扩容、外部系统调用 add_item/remove_item），但蓝图未说明哪些操作会触发 `S2C_BagUpdate` 推送，以及推送是全局广播还是仅推送给当前玩家。这会导致客户端数据更新不及时或收到无关推送。
- 修改建议: 在 `S2C_BagUpdate` 的描述中，明确其触发条件（例如：任何导致 `bag_item_list`、`occupied_slots` 或 `bag_max_slots` 变化的操作），并明确推送范围（仅推送给当前玩家）。
### Issue 4 [严重级别: 中]
- 责任方: ux_agent
- 目标文件: ui_interaction_blueprint.md
- 锚点: 界面三：二次确认弹窗 - 状态流转与兜底
- 问题描述: UX 蓝图在“二次确认弹窗”的“状态流转与兜底”中，为“使用”和“丢弃”操作定义了不同的点击外部关闭行为（使用可点击外部关闭，丢弃不可）。系统策划案中并未区分这两种操作的关闭行为，且这种差异化的交互设计增加了实现复杂度，且可能让用户感到困惑。这属于 UX Agent 的越权补全，引入了不必要的逻辑差异。
- 修改建议: 统一“使用”和“丢弃”二次确认弹窗的关闭行为，建议均不允许点击外部关闭，以强化确认操作的严肃性，避免误操作。移除 UX 蓝图中关于“丢弃操作建议仅通过按钮关闭”的描述。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.4 堆叠 - 边界与异常兜底
- 问题描述: 系统策划案中描述了堆叠逻辑，但未定义当 `add_item` 调用时，如果 `item_id` 在 `bag_item_list` 中存在但所有堆叠都已满，且 `occupied_slots` 未达到 `bag_max_slots` 时，创建新堆叠的具体规则。例如，新堆叠的 `current_stack_size` 初始值是多少？是等于 `count` 还是等于 `min(count, MAX_STACK_SIZE)`？这会导致程序实现时出现歧义。
- 修改建议: 在系统策划案中明确新创建堆叠的 `current_stack_size` 初始值规则，建议为 `min(count, MAX_STACK_SIZE)`，并说明当 `count` 超过 `MAX_STACK_SIZE` 时需要创建多个堆叠。
**当前审查总计问题:** 5 个
