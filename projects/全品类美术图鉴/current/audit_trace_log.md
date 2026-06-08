# 全品类美术图鉴 - 审查修改日志


--- 审查时间: 2026-05-30 21:56:59 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 表 2: player_gallery_progress
- 问题描述: 程序蓝图中的 `player_gallery_progress` 表将 `all_categories_unlocked_count` 和 `all_categories_total_count` 作为字段存储在该表中，但该表的主键是 `(player_id, category_id)`，这意味着每个分类记录都会冗余存储全局总数，且当全局数据更新时，需要更新所有6条记录，存在数据一致性和并发写入的严重风险。
- 修改建议: 建议将全局进度数据（`all_categories_unlocked_count`, `all_categories_total_count`, `total_progress`）独立为一张新表 `player_gallery_total_progress`，主键为 `player_id`，避免冗余存储和并发更新问题。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 表 1: player_gallery_entry
- 问题描述: 程序蓝图中的 `player_gallery_entry` 表将 `entry_name`, `rarity`, `acquisition_hint`, `is_obsolete` 等条目静态属性存储在玩家维度的表中，导致数据严重冗余。如果全局配置（如条目名称修改、稀有度调整）发生变化，需要全量更新所有玩家的记录，存在数据一致性和性能风险。
- 修改建议: 建议将条目的静态属性（`entry_name`, `rarity`, `acquisition_hint`, `is_obsolete`）独立为全局配置表 `gallery_entry_definition`，玩家表 `player_gallery_entry` 仅存储 `player_id`, `entry_id`, `unlock_status`, `unlock_time` 等玩家私有数据。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接)
- 问题描述: 系统策划案中明确描述了排序与筛选功能（2.3.3节），但程序蓝图中的 `Gallery_GetCategoryDetail` 接口返回参数中，`sort_filter` 字段仅返回了单个排序/筛选配置，而非支持客户端提交排序和筛选参数。这导致客户端无法实现多维度叠加筛选（如“已解锁 + SSR + 天启阵营”），核心功能缺失。
- 修改建议: 修改 `Gallery_GetCategoryDetail` 接口，在请求参数中增加 `sort_dimension`, `filter_dimensions`（数组）和 `filter_values`（数组）字段，服务端根据参数排序和筛选后返回条目列表。
### Issue 4 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.2 奖励节点
- 问题描述: 系统策划案中定义了单品类里程碑节点为10%/25%/50%/75%/100%共5个节点，但数值配表 `milestone_reward` 中仅定义了每个分类的5个里程碑奖励，缺少总进度里程碑的奖励内容定义。总进度里程碑（`total_milestone_1` 到 `total_milestone_5`）在数值配表中存在，但系统策划案未明确总进度里程碑的奖励内容是否由数值策划定义，存在需求断链。
- 修改建议: 系统策划需在2.2.2节中明确总进度里程碑的奖励内容由数值策划定义，并补充说明奖励内容需与核心商业化循环对齐。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 3.2 核心校验逻辑
- 问题描述: 程序蓝图中的里程碑奖励发放逻辑仅检查 `claim_status` 是否为 `false`，但未检查当前进度是否真正达到里程碑阈值。如果由于数据异常或并发问题导致 `claim_status` 为 `false` 但进度未达标，系统仍会错误发放奖励。
- 修改建议: 在发放奖励前，增加进度阈值校验：根据 `milestone_id` 解析对应的 `category_id` 或 `total`，从 `player_gallery_progress` 或 `player_gallery_total_progress` 中读取当前进度，确认达到阈值后再发放奖励。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 21:59:29 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心校验逻辑 - 里程碑奖励发放校验
- 问题描述: 程序蓝图中的里程碑奖励发放校验逻辑存在逻辑死胡同：校验条件要求当前进度必须大于等于里程碑节点对应的阈值（如10%），但数值配表 `category_progress` 和 `total_progress` 中并未提供任何字段来存储或映射 `milestone_level` 到具体百分比阈值（如1→10%）。后端无法知道每个 `milestone_id` 对应的进度阈值是多少，导致奖励发放条件永远无法满足或可能错误触发。
- 修改建议: 需要在 `milestone_reward` 表或 `category_progress`/`total_progress` 表中增加一个字段（如 `threshold_percent`），明确存储每个里程碑节点对应的进度百分比阈值（如10, 25, 50, 75, 100），供后端校验逻辑读取。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口 - GetCategoryEntries
- 问题描述: 程序蓝图中的 `GetCategoryEntries` 接口返回参数缺少 `unlock_time` 字段，但系统策划案（2.3.3节）明确要求支持按解锁时间排序，且数值配表 `entry_unlock` 中定义了 `unlock_time`。前端无法获取该字段来实现默认的“最新解锁优先”排序。
- 修改建议: 在 `GetCategoryEntries` 接口的返回参数 `entry_list` 中增加 `unlock_time` (int) 字段，确保前端能获取到解锁时间戳用于排序。
### Issue 3 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.2 奖励节点 - 总进度里程碑
- 问题描述: 系统策划案（2.2.2节）明确要求总进度里程碑奖励内容由数值策划在 `NP-01` 任务中定义，但数值配表 `milestone_reward` 中已直接配置了 `total_milestone_1` 至 `total_milestone_5` 的奖励内容（如限定抽卡券、头像框）。这导致系统策划案中的责任归属声明与数值配表的实际配置存在矛盾，可能引发开发阶段的职责混乱。
- 修改建议: 要么在系统策划案中删除关于 `NP-01` 任务的责任归属声明，明确奖励内容已由数值配表定义；要么在数值配表中移除 `total_milestone` 相关记录，等待 `NP-01` 任务输出。
### Issue 4 [严重级别: 中]
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - category_progress
- 问题描述: 数值说明书中的 `category_progress` 字段定义为【浮点数】，但系统策划案（2.2.1节）明确要求进度精确到整数百分比且向下取整。数据类型定义（float）与业务逻辑（int）不匹配，可能导致前端展示或后端计算时出现精度问题或逻辑歧义。
- 修改建议: 将 `category_progress` 和 `total_progress` 的字段类型从【浮点数】改为【整数】，并在数值说明书中明确其取值范围为 0 到 100，且计算时采用向下取整。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心校验逻辑 - 绝版内容校验
- 问题描述: 程序蓝图中的绝版内容校验逻辑仅描述了前端展示逻辑（显示“已绝版”），但未定义后端如何处理活动结束后的 `is_obsolete` 字段更新机制。系统策划案（2.5节）要求活动结束后条目永久不可解锁，但未明确由谁、在何时、通过何种方式触发 `is_obsolete` 字段的批量更新。这可能导致活动结束后，未解锁条目仍显示旧的获取途径提示。
- 修改建议: 在程序蓝图中增加一个由运营后台或定时任务触发的批量更新接口/脚本，用于在活动结束后统一将对应 `entry_display` 记录的 `is_obsolete` 字段更新为 `true`，并明确触发时机（如活动结束次日凌晨）。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 22:02:11 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 持久化数据 (DB) - player_collection_data 表
- 问题描述: 程序蓝图中的 `player_collection_data` 表将 `category_progress`、`total_progress`、`entry_unlocks`、`milestone_rewards` 全部存储为 JSON 字段，但数值说明书中的 `category_progress`、`total_progress`、`entry_unlock`、`milestone_reward` 均为独立的结构化表（含外键关系）。这种设计将导致后端无法高效地进行 SQL 查询（如按 `unlock_status` 筛选、按 `unlock_time` 排序），且违背了数值说明书中的外键约束设计。
- 修改建议: 建议将 `player_collection_data` 表拆分为多个关系型表（如 `player_category_progress`、`player_entry_unlock`、`player_milestone_reward`），以支持高效的 SQL 查询和索引，并确保外键约束的完整性。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心校验逻辑 - 绝版内容校验
- 问题描述: 程序蓝图描述活动结束后，后端通过定时任务批量更新 `entry_display` 表中的 `is_obsolete` 字段。但 `entry_display` 在程序蓝图中被定义为静态配置表（`EntryDisplayTable`），静态配置表通常不应在运行时被动态修改。这种设计矛盾会导致数据不一致：静态表被修改后，下次热更新或重启时可能被覆盖。
- 修改建议: 建议将 `is_obsolete` 和 `acquisition_hint` 字段从静态配置表移至玩家数据表（如 `player_entry_display`），或设计一个独立的“条目状态表”来存储每个玩家的绝版状态，避免修改全局静态配置。
### Issue 3 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2.2 奖励节点 - 总进度里程碑
- 问题描述: 系统策划案中描述了总进度里程碑奖励的边界与异常兜底逻辑（邮箱满、离线、作弊），但未定义 `[MAIL_RETENTION_DAYS]` 的具体值或取值范围。这导致程序蓝图无法实现邮件保留天数的逻辑，属于字段遗漏。
- 修改建议: 请在系统策划案中补充 `[MAIL_RETENTION_DAYS]` 的具体数值或取值范围，或将其定义为数值配表中的字段。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 前后端通信协议 - [UNLOCK_EVENT]
- 问题描述: 程序蓝图中的 `[UNLOCK_EVENT]` API 请求参数包含 `source_system`（字符串），但数值说明书中的 `system_linkage` 表定义了 `source_system` 的枚举值（如 `character_acquisition`）。程序蓝图未说明后端是否需要根据 `system_linkage` 表校验 `source_system` 的合法性，存在校验缺失风险。
- 修改建议: 建议在 `[UNLOCK_EVENT]` 的后端处理逻辑中，增加对 `source_system` 和 `trigger_event` 的合法性校验，拒绝非法来源的解锁事件，并记录错误日志。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3.2 未解锁条目
- 问题描述: 系统策划案中描述了未解锁条目的获取途径提示，并提到“若获取途径涉及多个条件，仅展示主要条件”。但未定义“主要条件”的判定规则或优先级，这会导致前端实现时产生歧义，不同开发人员可能实现不同的展示逻辑。
- 修改建议: 建议在系统策划案中补充“主要条件”的判定规则（如按条件类型优先级：系统来源 > 关卡 > 等级），或由数值策划在 `entry_display` 表中直接配置最终显示的提示文本。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 22:04:45 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - [UNLOCK_EVENT]
- 问题描述: 系统策划案中定义了多个解锁事件（如 on_character_acquired、on_first_encounter_enemy、on_first_watch_cg 等），但程序蓝图中的 [UNLOCK_EVENT] API 仅定义了 entry_id、source_system、trigger_event 三个参数，缺少了系统策划案中明确要求的解锁事件类型标识（如 on_character_acquired 等）。这会导致后端无法区分不同来源的解锁事件，进而无法正确执行对应的解锁逻辑（如角色解锁需检查角色系统，敌人解锁需检查战斗系统）。
- 修改建议: 在 [UNLOCK_EVENT] 请求参数中增加一个字段（如 unlock_event_type），用于明确标识具体的事件类型（如 on_character_acquired、on_first_encounter_enemy 等），并确保后端能根据该字段执行对应的校验逻辑。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 系统策划案 2.2.3 节明确要求“达到节点后自动发放至邮箱”，但程序蓝图中的 player_milestone_reward 表仅记录了 claim_status（是否已领取），缺少了奖励发放方式（如是否已发送至邮箱）以及发放状态的记录。这会导致后端无法判断奖励是否已成功发送至邮箱，也无法处理邮箱满时的重试逻辑。
- 修改建议: 在 player_milestone_reward 表中增加字段，如 reward_sent_status（奖励是否已发送至邮箱）和 retry_count（重试次数），以支持邮箱发放的完整流程。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - [GET_CATEGORY_ENTRIES]
- 问题描述: 系统策划案 2.3.3 节定义了排序维度包括“按阵营（角色/武器）”和“按版本”，筛选维度包括“按阵营”、“按版本”和“按二级分类”。但程序蓝图中的 [GET_CATEGORY_ENTRIES] API 的请求参数中，sort_dimension 和 filter_dimension 的枚举值并未明确包含“camp”、“version”和“sub_category”，仅从字段名推断可能支持，但未在文档中明确定义。这会导致前端无法正确传递这些排序/筛选条件，后端也无法正确处理。
- 修改建议: 在 [GET_CATEGORY_ENTRIES] API 的文档中，明确列出 sort_dimension 和 filter_dimension 所有支持的枚举值（包括 camp、version、sub_category 等），并确保后端能根据这些值进行正确的数据查询。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 二、前端模块划分 (Client) - UI 组件层 - 条目详情页 (EntryDetailPanel)
- 问题描述: 系统策划案 2.5.1 节提到角色图鉴子页面“若已解锁该角色的专属剧情片段，显示‘剧情回放’按钮”，但程序蓝图中未定义该按钮的交互逻辑、数据来源（如何判断是否有专属剧情片段）以及对应的 API 接口。这会导致该功能无法实现。
- 修改建议: 在程序蓝图中增加“剧情回放”按钮的交互定义，明确其数据来源（如通过 entry_id 关联剧情系统），并定义对应的 API 接口（如 [GET_CHARACTER_STORY_CLIP]）以获取剧情片段数据。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 二、前端模块划分 (Client) - 表现层控制器 - 资源缓存策略
- 问题描述: 系统策划案 2.3.2 节详细定义了未解锁条目的“获取途径提示规则”，包括“主要条件”的手动标记、优先级选择、活动绝版后的自动切换等复杂逻辑。但程序蓝图中的资源缓存策略仅提到“未解锁条目仅缓存剪影/锁图标与文本信息”，未提及如何缓存和处理这些复杂的获取途径提示逻辑（如 is_obsolete 字段的自动切换）。这会导致前端在展示未解锁条目时，无法正确显示获取途径提示。
- 修改建议: 在程序蓝图中明确未解锁条目获取途径提示的缓存策略，包括如何缓存 acquisition_hint 字段、如何处理 is_obsolete 字段的自动切换（如通过定时任务或事件驱动），以及如何展示“该内容已绝版”等特殊文本。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 22:07:18 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - [GetCategoryDetail]
- 问题描述: 系统策划案（2.3.2节）定义了未解锁条目展示逻辑依赖 `acquisition_hint` 和 `is_obsolete` 两个字段，且前端需根据 `is_obsolete` 决定显示内容。但程序蓝图中的 [GetCategoryDetail] API 返回参数仅指定了 `entry_display` 列表，未明确说明该列表是否包含 `acquisition_hint` 和 `is_obsolete` 字段。同时，程序蓝图（二、前端模块划分 - 模型预览控制器）中描述未解锁条目缓存策略时，明确提到了依赖 `acquisition_hint` 和 `is_obsolete`，但API定义缺失导致数据链路断裂，前端无法获取这两个关键字段，将导致未解锁条目展示逻辑无法实现。
- 修改建议: 在 [GetCategoryDetail] API 的返回参数中，明确 `entry_display` 列表的每个元素必须包含 `acquisition_hint` (string) 和 `is_obsolete` (bool) 字段，并确保服务端在返回数据时从配置表中正确读取这些字段。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 系统策划案（2.2.3节）规定里程碑奖励达到节点后自动发放至邮箱，并在图鉴界面显示已领取状态。但程序蓝图中的 `player_album_data` 表结构仅存储了 `milestone_reward_claims` 的领取状态，未设计存储奖励发放记录（如邮件ID、发放时间等）的字段。这导致服务端无法追踪奖励是否已成功通过邮件系统发放，若邮件系统发送失败，无法进行重试或状态回滚，可能导致玩家永远丢失奖励。
- 修改建议: 在 `player_album_data` 表中增加一个字段，例如 `milestone_reward_sent` (JSON)，用于记录每个里程碑奖励的邮件发送状态（如 pending/sent/failed），并设计对应的重试机制。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - [UnlockEntry]
- 问题描述: 系统策划案（5.1-5.4节）定义了多个解锁事件（如 `on_character_acquired`, `on_first_encounter_enemy` 等），但程序蓝图中的 [UnlockEntry] API 仅是一个通用的推送接口，未定义服务端如何根据不同的来源系统事件（如角色获取 vs 首次遭遇敌人）来映射到对应的 `entry_id`。虽然蓝图（五、数值与配置表挂载）提到了 `SystemLinkageTable`，但API层面没有明确说明服务端在收到外部事件后，应通过该配置表查询 `linked_entry_id` 并调用 [UnlockEntry] 推送的逻辑流程。这可能导致服务端实现时遗漏事件到条目的映射逻辑，造成解锁功能失效。
- 修改建议: 在程序蓝图（三、后端逻辑划分）中，明确增加一个“事件路由与映射”模块，描述服务端如何监听外部系统事件，通过 `SystemLinkageTable` 查找对应的 `entry_id`，然后执行解锁逻辑并推送 [UnlockEntry]。
### Issue 4 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3.2 未解锁条目 - 获取途径提示规则
- 问题描述: 系统策划案详细描述了“主要条件”的手动标记规则和异常兜底（如字段为空显示“待定”），但未定义当 `is_obsolete` 字段为 `true` 时，`acquisition_hint` 字段是否仍应保留原文本。数值说明书（`entry_display` 字段定义）中 `acquisition_hint` 的默认值为空字符串，而 `is_obsolete` 为 `true` 时，前端逻辑（根据程序蓝图）会直接显示“该内容已绝版”，忽略 `acquisition_hint`。这可能导致数据冗余或歧义：当 `is_obsolete` 为 `true` 时，`acquisition_hint` 字段是否应该被清空或保留原值？缺少明确约定。
- 修改建议: 在系统策划案中补充一条规则：当 `is_obsolete` 字段被标记为 `true` 时，`acquisition_hint` 字段应被清空或设置为空字符串，以避免数据冗余和潜在的展示逻辑冲突。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 二、前端模块划分 (Client) - 模型预览控制器
- 问题描述: 程序蓝图描述了模型预览控制器的资源缓存策略，其中提到“根据设备性能（通过API获取设备等级标识）决定缓存策略”。但该API（获取设备等级标识）在前后端通信协议中未定义，也未说明该标识是前端本地获取还是通过服务端接口获取。这导致前端开发时无法确定如何实现设备分级逻辑，可能阻塞P2阶段的开发。
- 修改建议: 在程序蓝图（四、前后端通信协议）中增加一个API，例如 [GetDeviceConfig] 或类似接口，用于服务端根据客户端上报的设备信息返回设备等级标识（如 high/mid/low），或者明确说明该标识由前端本地通过特定SDK或硬编码规则获取。
**当前审查总计问题:** 5 个
