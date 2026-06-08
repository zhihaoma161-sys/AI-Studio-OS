# 活动大厅 - 审查修改日志


--- 审查时间: 2026-05-30 23:55:41 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 接口定义
- 问题描述: 程序蓝图定义了 `DoRetroactive` 接口，请求参数为 `{ target_day: int }`，但系统策划案 2.4.3 节描述补签逻辑时，提到补签价格是根据漏签天数计算（`retroactive_cost_per_day * missed_days_count`），且服务器校验时需检查玩家付费货币是否足够。然而，接口请求参数中并未包含用于计算总价的 `missed_days_count` 或 `total_cost` 字段，导致服务器无法在单次请求中完成价格校验。这是一个逻辑死胡同：服务器无法仅凭 `target_day` 得知玩家要补签多少天，从而无法计算总价并校验货币。
- 修改建议: 在 `DoRetroactive` 接口的请求参数中增加 `missed_days_count` (整数) 字段，或改为传递一个 `target_days` (整数数组) 字段，以便服务器明确知晓本次补签涉及的天数，从而正确计算总价并进行货币校验。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 接口定义
- 问题描述: 系统策划案 2.3.1 节描述了红点上报机制：活动子系统调用红点系统的 `report_reddot_status(activity_id, is_active)` 接口。但程序蓝图 4.1 节只定义了服务端向客户端推送红点状态的 `PushReddotUpdate` 接口，完全没有定义活动子系统向红点系统上报红点状态的内部接口。这导致红点系统的数据来源缺失，红点推送功能无法实现。
- 修改建议: 在程序蓝图的后端逻辑部分，增加一个内部接口定义，例如 `ReportReddotStatus` (S->S)，用于活动子系统向红点系统上报红点状态变化。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 3.2 核心校验逻辑
- 问题描述: 系统策划案 2.4.3 节和数值配表 `global_params` 中定义了补签价格相关的字段：`retroactive_cost_per_day`、`retroactive_cost_base`、`retroactive_cost_max`。系统策划案 2.4.3 节描述补签价格是“根据漏签天数计算”，且 4.2 节提到“补签价格随漏签天数递增（如第1天 `[RETROACTIVE_COST_BASE]`，第2天 `[RETROACTIVE_COST_BASE] * 2`，以此类推，上限为 `[RETROACTIVE_COST_MAX]`）”。然而，程序蓝图 3.2 节的补签校验逻辑中，只写了校验货币是否 >= `retroactive_cost_per_day * 漏签天数`，这与系统策划案中描述的递增价格模型完全矛盾。程序蓝图使用了错误的、固定的单价计算方式，会导致补签定价逻辑与设计意图不符。
- 修改建议: 修改程序蓝图 3.2 节补签校验逻辑中的价格计算公式，使其符合系统策划案 4.2 节描述的递增价格模型（第N天价格 = min(retroactive_cost_base * N, retroactive_cost_max)），并累加所有漏签天数的价格得到总价。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 系统策划案 5.5 节和数值说明书 `check_bag_space` 字段明确提到，奖励发放前需要调用背包系统的 `check_bag_space` 接口检查空间。但程序蓝图 3.2 节的奖励发放校验逻辑中，只写了“若空间不足则调用 send_mail 补发”，并未定义或提及如何调用 `check_bag_space` 接口。这导致奖励发放流程中缺少关键的前置检查步骤，是一个流程断裂。
- 修改建议: 在程序蓝图 3.2 节的奖励发放校验逻辑中，明确增加调用 `check_bag_space` 接口的步骤，并说明其返回值（布尔值）如何影响后续流程（空间充足则直接发放，不足则触发邮件补发）。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.1 状态初始化
- 问题描述: 系统策划案 2.2.1 节描述了状态初始化的判定树，其中判定1根据当前服务器时间与 `start_time`、`end_time` 的比较，将状态设为 `未激活`（时间未到）或 `已结束`（时间已过）。但判定树中并未明确区分“时间未到”和“时间已过”这两种情况，而是笼统地归为 `未激活` 或 `已结束`。然而，2.2.1 节的表现层反馈中又提到“未激活的活动页签...显示倒计时（若时间未到）”，这说明客户端需要知道具体是“时间未到”还是“条件未满足”才能正确显示。当前的状态机定义（只有 `inactive`、`active`、`ended` 三个状态）无法区分“时间未到”和“条件未满足”这两种不同的 `未激活` 子状态，导致客户端无法准确显示倒计时或锁图标。
- 修改建议: 建议在 `current_status` 枚举中增加一个子状态，例如 `inactive_time`（时间未到）和 `inactive_condition`（条件未满足），或者为 `inactive` 状态增加一个 `reason` 字段（如 `time`、`level`、`chapter`），以便客户端根据具体原因显示不同的 UI 元素（倒计时或锁图标）。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 23:58:15 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 接口定义
- 问题描述: 接口 `DoRetroactive` 和 `DoAccelerate` 的返回参数中缺少 `new_consecutive_days` 字段。系统策划案（2.2.3节）和数值说明书（`consecutive_signin_days` 字段）均明确要求补签和加速操作后需要更新并返回连续签到天数，但蓝图中的这两个接口返回参数列表中没有该字段，导致前端无法更新连续签到进度条。
- 修改建议: 在 `DoRetroactive` 和 `DoAccelerate` 的返回参数中增加 `new_consecutive_days`（整数）字段，用于返回操作后的最新连续签到天数。
### Issue 2 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.4 状态流转（玩家条件变化触发）
- 问题描述: 系统策划案描述了玩家条件变化（如升级、通关）后，对应系统向活动大厅发送条件变更事件，但未定义该事件的接口协议（事件名称、参数格式）。程序蓝图（tech_blueprint.md）中也未定义此事件的推送接口，导致跨系统通信链路断裂。
- 修改建议: 在系统策划案中明确定义条件变更事件的接口协议（如事件名 `PlayerConditionChanged`，参数包含 `changed_field` 和 `new_value`），并在程序蓝图的API定义中补充该推送接口。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 接口定义
- 问题描述: 接口 `DoSignIn` 的返回参数中缺少 `new_consecutive_days` 字段。系统策划案（2.2.3节）和数值说明书（`consecutive_signin_days` 字段）均明确要求签到后需要更新并返回连续签到天数，但蓝图中的该接口返回参数列表中没有该字段，导致前端无法更新连续签到进度条。
- 修改建议: 在 `DoSignIn` 的返回参数中增加 `new_consecutive_days`（整数）字段，用于返回签到后的最新连续签到天数。
### Issue 4 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.1 状态初始化
- 问题描述: 系统策划案中定义了 `TIME_SYNC_TOLERANCE` 变量用于服务器与客户端时间偏差容忍度，但该变量在数值说明书（`system_numerical_docs.json`）和数值配表（`data.json`）中均未定义，导致程序无法确定具体容忍阈值。
- 修改建议: 在数值说明书或数值配表中新增 `time_sync_tolerance`（整数，单位秒）字段，并赋予默认值（如300秒）。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 接口定义
- 问题描述: 接口 `DoRetroactive` 的请求参数中缺少 `target_day` 字段的详细取值范围说明。虽然蓝图标注了取值范围为1-`month_max_days`，但未明确说明当 `target_day` 超出该范围时的服务端处理逻辑（如返回错误码或忽略请求），可能导致边界情况下的未定义行为。
- 修改建议: 在接口定义中补充 `target_day` 参数的边界处理逻辑：若超出1-`month_max_days` 范围，服务端应返回错误码（如 `err_invalid_target_day`）并拒绝处理。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-31 00:01:27 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 接口 `DoRetroactive` 的返回参数中提到了错误码 `err_invalid_target_day` (1004)，但在系统策划案和数值说明书的 `错误码` 枚举中均未定义此错误码。这会导致客户端无法正确解析该错误场景，可能引发程序崩溃或逻辑死循环。
- 修改建议: 在数值说明书 `relations_and_enums` 的 `错误码` 枚举中增加 `err_invalid_target_day: 1004` 的定义，或在 `DoRetroactive` 接口中移除对该错误码的引用，改用现有错误码（如 `err_already_retroactive`）进行覆盖处理。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 系统策划案 2.2.1 节描述了活动状态判定逻辑需要读取 `player_level` 和 `player_main_story_chapter`，但 `GetActivityHallData` 接口的返回参数中未包含这两个字段。客户端无法直接从该接口获取玩家等级和主线进度，导致状态判定逻辑无法在客户端本地进行预判或校验。
- 修改建议: 在 `GetActivityHallData` 接口的返回参数中增加 `player_level` (整数) 和 `player_main_story_chapter` (整数) 字段，或明确说明客户端应通过其他独立接口（如 `GetPlayerInfo`）获取这些数据，并在文档中注明依赖关系。
### Issue 3 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.1 状态初始化 - 边界与异常兜底
- 问题描述: 系统策划案中提到了 `[TIME_SYNC_TOLERANCE]` 变量用于处理时间同步偏差，但在数值说明书和数值配表中均未定义该变量的具体数值。这导致程序无法实现该时间同步容忍度逻辑，可能引发客户端与服务端状态不一致。
- 修改建议: 在数值配表的 `global_params` 节点中增加 `time_sync_tolerance` (整数，单位秒) 字段，并赋予一个合理的默认值（如 60 秒）。同时，在系统策划案中明确该变量的取值范围和默认值。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 系统策划案 5.3 节提到奖励发放失败时通过邮件系统 `send_mail()` 接口补发，但程序蓝图中的签到、补签、加速等接口（`DoSignin`, `DoRetroactive`, `DoAccelerate`）的返回参数中，均未包含邮件补发状态或邮件ID等字段。客户端无法得知奖励是否通过邮件补发，也无法进行后续的邮件提示。
- 修改建议: 在 `DoSignin`, `DoRetroactive`, `DoAccelerate` 接口的返回参数中增加 `mail_sent` (布尔) 字段，表示是否因背包满而通过邮件补发奖励。如果为 `true`，客户端可提示玩家“奖励已通过邮件发放”。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 系统策划案 2.1 节提到服务器定时推送状态变更通知，程序蓝图定义了 `PushActivityStatusChange` 推送接口。但系统策划案 2.2.1 节提到“若玩家在打开大厅的同时收到服务器推送通知，系统以最后一次刷新结果为准”，然而 `GetActivityHallData` 接口的返回参数中未包含时间戳或版本号字段，客户端无法判断推送通知与接口返回数据哪个是最新的，可能导致状态冲突。
- 修改建议: 在 `GetActivityHallData` 接口的返回参数中增加 `server_timestamp` (整数，Unix秒级时间戳) 字段，并在 `PushActivityStatusChange` 推送参数中也增加 `server_timestamp` 字段。客户端在收到推送时，比较时间戳，仅当推送时间戳晚于接口返回时间戳时才更新本地状态。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-31 00:03:51 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 接口 `GetActivityHallData` 的返回参数中包含了 `activity_tab_list`，但该列表的生成逻辑（遍历活动配置表、判断状态、排序）在蓝图中被描述为客户端行为（见 2.2.1 状态初始化）。这导致数据流向矛盾：若由服务端生成并返回列表，则客户端无需自行计算；若由客户端计算，则服务端不应返回该字段。蓝图未明确服务端是否承担此计算职责，导致前后端职责冲突。
- 修改建议: 明确 `activity_tab_list` 的生成方。若由服务端生成，则需在蓝图后端逻辑部分补充服务端遍历 `activity_config`、判定状态、排序并返回列表的逻辑；若由客户端生成，则 `GetActivityHallData` 接口应返回完整的 `activity_config` 列表（或增量更新）以及服务器时间戳，由客户端自行计算 `activity_tab_list`。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 接口 `GetActivityHallData` 的返回参数中包含了 `data_version`，且蓝图在阶段二提到客户端需根据 `push_data_version` 与本地缓存的 `data_version` 比较以处理推送通知。但蓝图未定义 `data_version` 的生成规则（如基于活动配置表内容的哈希值、时间戳或递增ID），也未说明客户端首次获取数据时如何获取该版本号。这会导致版本比较逻辑无法实现。
- 修改建议: 在蓝图或系统策划案中补充 `data_version` 的生成规则（例如：每次活动配置表变更时，由运营后台生成一个递增的版本号或基于配置表内容的MD5值），并明确客户端首次加载时通过 `GetActivityHallData` 接口获取该版本号。
### Issue 3 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.1 状态初始化 - 边界与异常兜底
- 问题描述: 系统策划案中描述了时间同步失败时的处理逻辑（使用本地时间并记录日志），但未定义 `[TIME_SYNC_TOLERANCE]` 和 `[TIME_SYNC_RETRY_INTERVAL]` 这两个关键参数的具体值或取值范围。这导致程序蓝图无法实现该逻辑，属于未定义的占位符。
- 修改建议: 在系统策划案中明确 `[TIME_SYNC_TOLERANCE]` 和 `[TIME_SYNC_RETRY_INTERVAL]` 的具体数值（例如：`[TIME_SYNC_TOLERANCE]` = 120秒，`[TIME_SYNC_RETRY_INTERVAL]` = 30秒），或将其定义为可由数值配置表控制的参数，并在数值配表中添加相应字段。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 接口定义
- 问题描述: 蓝图定义了 `PushActivityStatusChange` 推送接口，但未定义客户端如何处理推送与手动刷新（`GetActivityHallData`）之间的并发冲突。系统策划案 2.2.1 中提到“以最后一次操作为准”，但蓝图未实现该逻辑的具体机制（例如：使用序列号或时间戳判断先后顺序）。
- 修改建议: 在蓝图中补充推送与手动刷新的冲突处理机制。例如：为每次 `GetActivityHallData` 请求分配一个递增的请求序列号，客户端在收到推送时，比较推送中的序列号与本地最后一次请求的序列号，仅当推送序列号更新时才处理推送。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 蓝图定义了 `player_signin_data` 表的 `last_signin_date` 字段用于连续签到判定，但未定义该字段在跨月时的处理逻辑。例如：玩家在1月31日签到，2月1日再次签到，连续签到是否中断？系统策划案仅提到“每月1日重置”，但未明确连续签到是否跨月计算。这会导致实现歧义。
- 修改建议: 在系统策划案或蓝图中明确连续签到的跨月规则。例如：连续签到仅在当月内有效，每月1日重置为0；或连续签到可跨月计算，但需考虑月份天数差异（如1月31日与2月1日是否算连续）。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-31 00:06:22 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案（第五章）和数值说明书均明确要求活动大厅在奖励发放前调用 `check_bag_space` 接口检查背包空间，若空间不足则调用 `send_mail` 接口补发奖励。但程序蓝图中定义的 `DoSignin`、`DoRetroactiveSignin`、`DoAccelerateSignin` 三个API的返回结果中，均未提及任何关于背包空间检查失败或邮件补发的处理逻辑与返回值定义。这导致奖励发放流程存在逻辑死胡同：背包满时，系统无法决定是直接失败还是触发邮件补发。
- 修改建议: 在 `DoSignin`、`DoRetroactiveSignin`、`DoAccelerateSignin` 的API描述中，增加对背包空间检查的说明，并定义当空间不足时，系统应自动调用邮件系统补发奖励，并返回一个特定的状态码（如 `reward_mailed`）以告知客户端奖励已通过邮件发送。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案（2.2.1节）详细描述了时间同步失败时的客户端重试机制，包括重试间隔 `TIME_SYNC_RETRY_INTERVAL` 和最大重试次数 `TIME_SYNC_MAX_RETRIES`。然而，数值说明书和数值配表中均未定义这两个关键参数。程序蓝图虽然提到了重试机制，但缺少具体的数值配置来源，导致该逻辑无法实现或只能使用硬编码的魔数。
- 修改建议: 在数值配表的 `global_params` 中增加 `time_sync_retry_interval`（重试间隔，单位秒）和 `time_sync_max_retries`（最大重试次数）两个字段，并赋予默认值。同时，在程序蓝图的 `TimeSyncManager` 描述中明确引用这两个数值配置。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案（第五章）和数值说明书均定义了 `reddot_update` 事件，用于红点系统向活动大厅推送状态变更。程序蓝图也提到了 `ReddotObserver` 监听此事件。但是，程序蓝图中的API列表里，`PushReddotUpdate` 的推送参数为 `activity_id` 和 `is_active`，而数值说明书中的 `reddot_update` 事件定义携带的参数是 `activity_id` 和 `is_active`（布尔值）。这里存在数据类型不一致的风险：`is_active` 在数值说明书中定义为布尔值，但在程序蓝图中未明确其数据类型，可能导致前后端解析错误。
- 修改建议: 在程序蓝图 `PushReddotUpdate` 的API描述中，明确 `is_active` 参数的数据类型为布尔值（`boolean`），与数值说明书保持一致。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server)
- 问题描述: 系统策划案（2.3节）和数值说明书均定义了 `player_signin_data` 记录玩家签到数据，其中包含 `consecutive_signin_days` 字段。程序蓝图也提到了该字段，并描述了跨月连续签到的处理逻辑。然而，数值说明书中的 `consecutive_signin_days` 字段定义在 `field_dictionary` 中，但并未出现在 `player_signin_data` 的子字段定义中（`player_signin_data.current_month`, `player_signin_data.signed_days_bitmask`, `player_signin_data.claimed_reward_tiers`）。这导致数据模型定义不完整，`consecutive_signin_days` 字段在数据存储层面缺少明确的归属和类型定义。
- 修改建议: 在数值说明书的 `field_dictionary` 中，将 `consecutive_signin_days` 明确列为 `player_signin_data` 的子字段，例如 `player_signin_data.consecutive_signin_days`，并补充其取值范围和默认值。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 六、 待确认风险与追问
- 问题描述: 系统策划案（6.3节）提出了限制活动页签数量上限的建议（如8个），但数值配表中的 `max_tab_count` 被设置为10。虽然根据最高裁决法则，数值表拥有定价权，但系统策划案中明确将此列为风险点并给出了具体建议值（8个），而最终数值表采用了不同的值（10个）。这本身不构成错误，但表明系统策划案与数值表在页签数量上限这一设计决策上存在分歧，可能意味着策划案中的风险分析未被采纳或未被充分讨论。
- 修改建议: 系统策划应与数值策划对齐 `max_tab_count` 的最终值，并在系统策划案中更新或删除此风险点，或明确说明已评估并接受10个页签的性能风险。
**当前审查总计问题:** 5 个
