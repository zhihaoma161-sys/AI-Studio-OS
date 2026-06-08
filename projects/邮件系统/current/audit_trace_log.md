
--- 审查时间: 2026-05-27 17:15:25 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas.stats_board.pve_win_rate.base
- 问题描述: 数值配表中 `pve_win_rate` 的 `base` 值为 0.5，但数值说明书中 `pve_win_rate` 的默认值为 0.0。两者不一致。
- 修改建议: 请确认 `pve_win_rate` 的初始默认值应为 0.0 还是 0.5，并统一数值说明书和数值配表中的定义。
### Issue 2
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas.stats_board.pvp_win_rate.base
- 问题描述: 数值配表中 `pvp_win_rate` 的 `base` 值为 0.5，但数值说明书中 `pvp_win_rate` 的默认值为 0.0。两者不一致。
- 修改建议: 请确认 `pvp_win_rate` 的初始默认值应为 0.0 还是 0.5，并统一数值说明书和数值配表中的定义。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas.stats_board.character_collection_rate.base
- 问题描述: 数值配表中 `character_collection_rate` 的 `base` 值为 0.0，但数值说明书中 `character_collection_rate` 的默认值为 0.0。此字段一致。但数值配表中存在 `growth` 字段，而数值说明书中未提及收集率的增长逻辑。数值配表中的 `growth` 字段含义不明，与策划案中“收集率计算”逻辑不符。
- 修改建议: 请明确 `character_collection_rate` 的 `growth` 字段在系统中的具体作用，或将其移除，因为策划案中收集率是动态计算的，而非线性增长。
### Issue 4
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas.stats_board.weapon_collection_rate.base
- 问题描述: 数值配表中 `weapon_collection_rate` 的 `base` 值为 0.0，但数值说明书中 `weapon_collection_rate` 的默认值为 0.0。此字段一致。但数值配表中存在 `growth` 字段，而数值说明书中未提及收集率的增长逻辑。数值配表中的 `growth` 字段含义不明，与策划案中“收集率计算”逻辑不符。
- 修改建议: 请明确 `weapon_collection_rate` 的 `growth` 字段在系统中的具体作用，或将其移除，因为策划案中收集率是动态计算的，而非线性增长。
### Issue 5
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 数据统计看板模块
- 问题描述: 策划案中数据统计看板模块的【前置条件】为“玩家等级≥10级”，但数值说明书和程序蓝图中均未提及此等级限制。这可能导致低等级玩家无法访问该模块，但后端数据接口和前端组件并未对此进行限制。
- 修改建议: 请在数值说明书或程序蓝图中明确数据统计看板模块的等级解锁条件，并确保后端API和前端UI组件在玩家等级不足时进行相应处理（如隐藏或显示锁定状态）。
### Issue 6
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 历史战绩模块
- 问题描述: 策划案中历史战绩模块的【前置条件】为“玩家完成至少1场高光战绩”，但数值说明书和程序蓝图中均未提及此条件。这可能导致无高光战绩的玩家无法访问该模块，但后端数据接口和前端组件并未对此进行限制。
- 修改建议: 请在数值说明书或程序蓝图中明确历史战绩模块的解锁条件，并确保后端API和前端UI组件在玩家无高光战绩时进行相应处理（如显示占位文字）。
### Issue 7
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 社交互动模块
- 问题描述: 策划案中社交互动模块的【前置条件】为“玩家已添加至少1名好友”，但数值说明书和程序蓝图中均未提及此条件。这可能导致无好友的玩家无法访问该模块，但后端数据接口和前端组件并未对此进行限制。
- 修改建议: 请在数值说明书或程序蓝图中明确社交互动模块的解锁条件，并确保后端API和前端UI组件在玩家无好友时进行相应处理（如隐藏或显示引导文字）。
### Issue 8
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 四、 前后端通信协议 (API & 数据对接) > 4.1 核心接口定义 > 1. 获取主页数据
- 问题描述: 程序蓝图中的“获取主页数据”接口返回参数中包含了 `stats_board` 和 `battle_history` 数据，但策划案中这两个模块的数据是独立刷新或加载的（数据统计每24小时刷新，历史战绩从战斗系统读取）。此接口设计将所有数据打包返回，与策划案中模块化的数据加载逻辑不符。
- 修改建议: 请考虑将 `stats_board` 和 `battle_history` 的数据获取拆分为独立的API接口，或明确此接口在何种场景下被调用（如首次进入主页时），并确保与策划案中的数据加载逻辑一致。
### Issue 9
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 四、 前后端通信协议 (API & 数据对接) > 4.1 核心接口定义 > 1. 获取主页数据
- 问题描述: 程序蓝图中的“获取主页数据”接口返回参数中包含了 `social_interaction` 的 `messages` 字段，但策划案中留言板只显示最近20条已审核通过的留言。此接口设计返回所有留言数据，可能导致数据量过大，且未考虑审核状态过滤。
- 修改建议: 请修改接口设计，使其只返回已审核通过的留言，并限制返回条数（如20条），或增加分页参数。
### Issue 10
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 五、 数值与配置表挂载 > 5.1 配置表读取方式
- 问题描述: 程序蓝图中的配置表读取方式示例中，`main_squad` 的 `lod_memory_thresholds` 字段使用了内存阈值（如2048、1024），但策划案中【边界与异常兜底】描述的是“设备内存<2GB”和“内存<1GB”，单位不一致。
- 修改建议: 请统一内存阈值的单位，建议使用MB（兆字节）或GB（吉字节），并确保与策划案中的描述一致。
### Issue 11
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 五、 数值与配置表挂载 > 5.1 配置表读取方式
- 问题描述: 程序蓝图中的配置表读取方式示例中，`achievement_wall` 的 `max_display_order` 字段值为100，但策划案中并未提及排序数组的最大长度。此限制可能影响玩家自定义排序的体验。
- 修改建议: 请确认 `max_display_order` 的必要性，如果存在，请在策划案中补充说明，或将其移除。
### Issue 12
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 主力阵容展示模块
- 问题描述: 策划案中主力阵容展示模块的【边界与异常兜底】提到“若玩家分解了阵容中的角色，系统自动将该槽位设为‘空’”，但程序蓝图和数值说明书中均未定义当角色被分解时，后端应如何处理 `main_squad` 表中的数据。
- 修改建议: 请在程序蓝图中明确角色分解时对 `main_squad` 表的影响，例如在角色删除逻辑中增加对 `main_squad` 表的级联更新操作。
### Issue 13
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 历史战绩模块
- 问题描述: 策划案中历史战绩模块的【边界与异常兜底】提到“若某条置顶战绩因版本更新而失效，系统自动取消其置顶状态”，但程序蓝图和数值说明书中均未定义如何判断战绩是否“失效”，以及如何触发自动取消置顶的逻辑。
- 修改建议: 请在程序蓝图中明确战绩失效的判断标准（如活动ID过期）和自动取消置顶的触发机制（如每日检查或版本更新时）。
**当前审查总计问题:** 13 个

--- 审查时间: 2026-05-27 18:52:43 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas.dormitory_affection_level.formula
- 问题描述: 好感度等级公式与策划案中明确列出的里程碑数值严重冲突。策划案中等级1-10所需经验值分别为：0, 100, 200, 400, 700, 1100, 1600, 2200, 2900, 3700, 4600。而数值配表中使用的连续公式 `floor(1 + 0.5 * ln(dormitory_affection + 1))` 计算出的等级与这些里程碑数值完全不匹配。例如，当好感度为100时，公式计算结果为 `floor(1 + 0.5 * ln(101)) ≈ floor(1 + 0.5 * 4.615) = floor(3.307) = 3`，但策划案中100点应为等级2。
- 修改建议: 请数值策划重新审查好感度等级的计算逻辑。要么放弃连续公式，直接使用策划案中定义的离散里程碑表；要么调整连续公式的参数，使其计算结果与策划案中的里程碑数值对齐。
### Issue 2
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones.dormitory_affection_level
- 问题描述: 数值配表中的解锁标志与策划案不一致。1. 策划案中等级3解锁'腰部触摸区域'，配表中正确标记了 `unlocked_touch_waist`，但策划案中等级5解锁的是'居家服'，配表中标记为 `unlocked_costume_casual`，字段名不一致。2. 策划案中等级8解锁'睡衣'和'特殊组合交互'，配表中标记为 `unlocked_costume_pajama` 和 `unlocked_special_interaction`，但策划案中'特殊组合交互'的解锁条件明确为'好感度等级≥8且拥有床、枕头、被子家具'，配表中缺少对家具条件的说明。3. 策划案中等级9和10解锁的是'角色专属剧情片段1和2'以及'告白特殊互动'，配表中标记为 `unlocked_story_1`, `unlocked_story_2`, `unlocked_confession`，这些字段在数值说明书的 `field_dictionary` 中完全不存在。
- 修改建议: 请数值策划：1. 统一服装解锁标志的命名（策划案中为'居家服'，配表中为'casual'，建议统一为 `unlocked_costume_home` 或与策划案一致）。2. 在 `relations_and_enums` 中明确特殊组合交互的家具条件。3. 在 `field_dictionary` 中补充 `unlocked_story_1`, `unlocked_story_2`, `unlocked_confession` 等字段的定义。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值说明书 (system_numerical_docs.json)
- 锚点: field_dictionary.unlocked_flag
- 问题描述: 数值说明书中定义了一个泛化的 `unlocked_flag` 字段，描述为'用于affection_unlock_content_table模块'，但该字段过于笼统，无法对应到具体的解锁内容。策划案中每个解锁项（如胸部触摸、睡衣、剧情等）都有独立的 `unlocked_` 前缀字段，而数值说明书中只定义了 `unlocked_touch_chest` 和 `unlocked_costume_pajama`，缺少 `unlocked_touch_waist`, `unlocked_touch_leg`, `unlocked_costume_casual`（或 `unlocked_costume_home`）, `unlocked_story_1`, `unlocked_story_2`, `unlocked_confession`, `unlocked_special_interaction` 等字段。
- 修改建议: 请数值策划在 `field_dictionary` 中补充所有策划案中提到的解锁标志字段，并删除或明确泛化的 `unlocked_flag` 字段。
### Issue 4
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 好感度成长系统
- 问题描述: 策划案中好感度等级经验值表与数值配表中的里程碑数值存在矛盾。策划案中明确列出了10个等级的经验值：1级:100, 2级:200, 3级:400, 4级:700, 5级:1100, 6级:1600, 7级:2200, 8级:2900, 9级:3700, 10级:4600。但按照常规理解，'1级:100'通常意味着从0到100点好感度对应等级1，100到200对应等级2，以此类推。然而，数值配表中的 `required_affection` 值（0, 100, 200, 400, 700, 1100, 1600, 2200, 2900, 3700）与策划案中的经验值列表（100, 200, 400, 700, 1100, 1600, 2200, 2900, 3700, 4600）在数值上错位了一位。策划案中第10级需要4600点，但配表中最高只到3700。
- 修改建议: 请系统策划与数值策划对齐好感度等级的定义。明确'1级:100'是指'达到100点好感度时升到1级'还是'1级需要100点经验值'。如果是前者，配表中的 `required_affection` 值是正确的（0->1级, 100->2级, ...）；如果是后者，配表需要调整。同时，策划案中第10级的4600点需要确认是否遗漏。
### Issue 5
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 五、数值与配置表挂载 - 1. 好感度等级经验值表
- 问题描述: 程序蓝图直接引用了策划案中的好感度等级经验值表（level_1:100, level_2:200, ... level_10:4600），但数值配表中使用的是完全不同的连续公式。程序蓝图要求'实现为连续公式，避免硬编码枚举'，但数值配表中的连续公式与策划案中的离散值不兼容。程序将无法确定应该使用哪个数据源。
- 修改建议: 请技术架构师与数值策划协调，确定最终采用离散里程碑还是连续公式。如果采用离散里程碑，程序蓝图应直接引用数值配表中的 `discrete_milestones.dormitory_affection_level` 数据；如果采用连续公式，则需要数值策划修正公式使其与策划案对齐。
### Issue 6
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 三、后端逻辑划分 - 角色宿舍数据表
- 问题描述: 程序蓝图中的角色宿舍数据表缺少多个策划案中明确提到的字段。策划案中提到了 `last_touch_time`, `touch_count_today`, `rejected_touch_count`, `touch_cooldown`, `last_interaction_time`, `interaction_count_today`, `interaction_cooldown`, `special_interaction_unlocked`, `last_special_interaction_time` 等字段，但程序蓝图中的角色宿舍数据表只包含了 `dormitory_affection`, `dormitory_affection_level`, `unlocked_touch_chest`, `unlocked_costume_pajama`, `special_interaction_unlocked`, `last_special_interaction_time`, `room_layout`, `theme_set_active`。触摸和交互相关的冷却/计数/时间戳字段完全缺失。
- 修改建议: 请技术架构师在角色宿舍数据表中补充 `last_touch_time`, `touch_count_today`, `rejected_touch_count`, `last_interaction_time`, `interaction_count_today` 等字段。注意 `touch_cooldown` 和 `interaction_cooldown` 是运行时状态，不应持久化。
### Issue 7
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 三、后端逻辑划分 - 玩家宿舍解锁状态表
- 问题描述: 程序蓝图中的玩家宿舍解锁状态表缺少 `dormitory_pass` 字段。策划案中明确提到玩家背包中需要拥有'私人宿舍通行证'道具，且数值说明书中的 `field_dictionary` 也定义了 `dormitory_pass` 字段。程序蓝图在背包道具表中提到了 `dormitory_pass`，但在玩家宿舍解锁状态表中没有体现该道具的持有状态。
- 修改建议: 请技术架构师在玩家宿舍解锁状态表中增加 `dormitory_pass` 字段，或明确说明该字段由背包系统管理，并在核心校验逻辑中引用背包系统的接口。
### Issue 8
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 四、前后端通信协议 - Dormitory_TouchCharacter
- 问题描述: `Dormitory_TouchCharacter` 接口的返回参数中包含了 `rejected` 字段，但缺少 `rejected_touch_count` 的返回。策划案中明确提到拒绝次数超过5次后当日触摸不再增加好感度，客户端需要知道当前的拒绝次数以显示提示。
- 修改建议: 请技术架构师在 `Dormitory_TouchCharacter` 的返回参数中增加 `rejected_touch_count` 字段，以便客户端在拒绝次数达到上限时显示相应提示。
### Issue 9
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 四、前后端通信协议 - Dormitory_GetWeatherTime
- 问题描述: `Dormitory_GetWeatherTime` 接口返回了 `character_state`，但策划案中角色状态是由游戏内时间 `in_game_time` 决定的，客户端可以根据时间自行计算。服务端返回 `character_state` 可能导致客户端与服务端状态不一致（例如在时间边界附近）。
- 修改建议: 请技术架构师考虑是否由客户端根据 `in_game_time` 自行计算 `character_state`，或者服务端返回 `in_game_time` 和 `current_weather` 后，客户端根据策划案中的时间映射表自行推导角色状态。这样可以减少网络传输和状态同步问题。
### Issue 10
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 好感度解锁内容表
- 问题描述: 策划案中好感度解锁内容表与数值配表中的解锁条件存在不一致。策划案中等级2解锁'物品交互（床、沙发）'，等级4解锁'物品交互（书桌、玩偶）'，等级6解锁'物品交互（书架、窗户）'。但数值配表中的 `discrete_milestones` 没有为等级2、4、6设置任何解锁标志（`unlock_flags: []`），这意味着物品交互的解锁条件在数值配表中完全没有体现。
- 修改建议: 请系统策划与数值策划对齐，在数值配表的 `discrete_milestones` 中为等级2、4、6添加对应的物品交互解锁标志（如 `unlocked_interact_bed`, `unlocked_interact_desk` 等），或者在策划案中明确物品交互的解锁不由好感度等级控制。
### Issue 11
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 好感度成长系统
- 问题描述: 策划案中好感度每日上限为100点（所有角色共享），但触摸每日上限为50次（每次+1点），交互每日上限为30次（每次+2点）。理论上，如果玩家完成所有触摸（50点）和交互（60点），单日可获得110点好感度，超过了100点的每日上限。这会导致玩家在完成所有触摸和部分交互后，后续交互不再增加好感度，但交互次数仍被消耗，造成玩家困惑。
- 修改建议: 请系统策划调整数值：要么降低触摸或交互的每日次数上限（如触摸40次、交互25次），要么提高每日好感度上限（如150点），或者明确说明当好感度达到每日上限后，触摸和交互仍消耗次数但不增加好感度。
### Issue 12
- 责任方: numerical_planner
- 目标文件: 数值说明书 (system_numerical_docs.json)
- 锚点: field_dictionary.battle_reward_trigger
- 问题描述: 数值说明书中定义了 `battle_reward_trigger` 字段，描述为'标记战斗结算联动内容是否已触发'，但程序蓝图中使用的是 `battle_reward_triggered_count`（整数，每日上限5次）。这两个字段类型不一致（布尔 vs 整数），且策划案中明确要求每日上限5次，布尔值无法满足计数需求。
- 修改建议: 请数值策划将 `battle_reward_trigger` 的类型从布尔值改为整数，并重命名为 `battle_reward_triggered_count`，与程序蓝图保持一致。
### Issue 13
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 三、后端逻辑划分 - 核心校验逻辑 - 战斗结算联动校验
- 问题描述: 程序蓝图中的战斗结算联动校验逻辑与策划案不完全一致。策划案中明确要求'若多个角色满足条件，优先播放好感度等级最高的角色内容'，但程序蓝图中的校验逻辑只提到了'选择好感度等级最高的角色'，没有处理等级相同的情况。策划案中边界与异常兜底部分提到'多个角色等级相同：随机选择一个角色触发'。
- 修改建议: 请技术架构师在战斗结算联动校验逻辑中补充：当多个角色好感度等级相同时，随机选择一个角色触发联动内容。
### Issue 14
- 责任方: system_planner
- 目标文件: 系统策划案 (system_design_detail.md)
- 锚点: 昼夜与天气系统
- 问题描述: 策划案中天气系统描述为'每现实4小时随机切换一次天气'，但数值配表中的 `current_weather` 里程碑也设置了 `duration_hours: 4`。然而，策划案中没有说明天气切换的具体逻辑（例如，是否允许连续两次出现同一种天气？切换时是否有权重？）。此外，策划案中天气类型有5种（晴天、多云、小雨、大雨、雪天），但程序蓝图中没有提到天气切换的随机算法。
- 修改建议: 请系统策划补充天气切换的详细规则：是否允许重复？每种天气的出现概率是否相等？是否需要根据季节或地区调整？这些信息对程序实现至关重要。
### Issue 15
- 责任方: tech_architect
- 目标文件: 程序蓝图 (tech_blueprint.md)
- 锚点: 二、前端模块划分 - 表现层控制器 - CharacterDormitoryController
- 问题描述: 程序蓝图中的 `CharacterDormitoryController` 负责播放触摸反馈动作/表情/语音，但缺少对'拒绝反馈'的详细处理逻辑。策划案中明确提到当触摸不允许时触发'拒绝反馈'（角色躲闪、摇头、语音提示'不要这样'），且拒绝次数超过5次后当日所有触摸区域均视为不允许。程序蓝图中没有说明拒绝反馈的触发条件和次数限制。
- 修改建议: 请技术架构师在 `CharacterDormitoryController` 或 `TouchRaycastController` 中补充拒绝反馈的处理逻辑：当触摸区域未解锁或拒绝次数超过5次时，播放拒绝反馈动画/语音，并更新 `rejected_touch_count`。
**当前审查总计问题:** 15 个

--- 审查时间: 2026-05-28 01:59:13 ---
### Issue 1
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 个人主页（名片）系统 - 展示内容定义
- 问题描述: 策划案中【展示内容列表】提到了“动态头像框”和“特效称号”，但在【数据状态变化】中，`player_homepage_config` 表记录的字段包含了“头像框ID”，却没有“特效称号ID”。特效称号作为一个独立的展示项，其ID未被记录在主页配置中，导致数据状态变化与展示内容不一致。
- 修改建议: 建议在 `player_homepage_config` 的数据状态变化描述中，增加“特效称号ID”字段，确保所有展示项都有对应的数据记录字段。
### Issue 2
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 个人主页（名片）系统 - 展示内容定义
- 问题描述: 策划案中【展示内容列表】提到了“角色皮肤”和“角色动作”，但在【数据状态变化】中，`player_homepage_config` 表记录的字段包含了“皮肤ID”和“动作ID”。然而，在【边界与异常兜底】中，只提到了“玩家删除已装备为展示角色的角色时，系统自动将展示角色重置为默认角色”和“玩家删除已装备皮肤的角色时，系统自动将皮肤重置为默认皮肤”，却没有提及“玩家删除已装备动作的角色时，系统自动将动作重置为默认动作”。逻辑不完整。
- 修改建议: 建议在【边界与异常兜底】中补充：当玩家删除已装备动作的角色时，系统自动将动作重置为默认动作。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary
- 问题描述: 数值说明书中 `field_dictionary` 定义了 `player_homepage_config` 对象，包含 `avatar_id`, `title_id`, `signature_text`, `background_id`, `display_character_id`, `skin_id`, `action_id`, `avatar_frame_id`。但策划案中明确提到了“特效称号”是一个独立的展示项，而数值说明书中没有对应的字段（如 `effect_title_id`）来记录特效称号的ID。这导致数值说明书与策划案不一致。
- 修改建议: 建议在 `player_homepage_config` 对象中增加 `effect_title_id` 字段，并定义其类型、取值范围和默认值，以匹配策划案中的“特效称号”展示项。
### Issue 4
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary
- 问题描述: 数值说明书中 `field_dictionary` 定义了 `player_statistics` 对象，其字段包含 `main_stage`, `abyss_floor`, `character_collection_pct`, `max_constellation_count`, `max_level_count`, `login_days`, `weekly_activity`。但策划案中【成就/战绩系统 - 展示内容列表】提到的“角色收集度百分比”在数值说明书中对应 `character_collection_percentage`，而 `player_statistics` 中却使用了 `character_collection_pct`，字段命名不一致。这可能导致程序开发时引用错误。
- 修改建议: 建议统一字段命名，将 `player_statistics` 中的 `character_collection_pct` 改为 `character_collection_percentage`，以保持与 `field_dictionary` 中其他字段的命名风格一致，并匹配策划案中的描述。
### Issue 5
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: continuous_formulas
- 问题描述: 数值配表中 `continuous_formulas` 定义了 `player_statistics` 的初始值 `{"main_stage":0,"abyss_floor":0,"character_collection_pct":0.0,"max_constellation_count":0,"max_level_count":0,"login_days":0,"weekly_activity":0}`。但数值说明书 `field_dictionary` 中 `player_statistics` 的描述是“包含主线最高章节、深渊最高层数、角色收集度、满命角色数、满级角色数、累计登录天数、本周活跃度等字段”，而配表中的字段名 `character_collection_pct` 与说明书中的 `character_collection_percentage` 不一致。
- 修改建议: 建议将数值配表中 `player_statistics` 的初始值字段名 `character_collection_pct` 修改为 `character_collection_percentage`，以保持与数值说明书一致。
### Issue 6
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的API列表没有提供获取“特效称号”相关数据的接口。策划案中明确提到了“特效称号”作为个人主页的一个独立展示项，且数值说明书中也应有对应的字段。但蓝图中的 `GetHomepageConfig` 和 `SaveHomepageConfig` 接口没有包含 `effect_title_id` 参数，也没有提供获取玩家已拥有特效称号列表的接口。这导致策划案中的功能无法通过现有API实现。
- 修改建议: 建议在 `SaveHomepageConfig` 接口的请求参数中增加 `effect_title_id`，并新增一个 `GetPlayerOwnedEffectTitles` 接口，用于获取玩家已拥有的特效称号列表，以便前端进行校验和展示。
### Issue 7
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 三、 后端逻辑划分 (Server)
- 问题描述: 程序蓝图中的【核心校验逻辑】部分，对于主页配置保存的校验，只校验了 `display_character_id`, `skin_id`, `action_id` 以及 `avatar_id`, `title_id`, `background_id`, `avatar_frame_id` 是否在对应的拥有列表中。但缺少对 `effect_title_id`（特效称号）的校验。如果后续增加了特效称号功能，后端将无法防止玩家设置未拥有的特效称号。
- 修改建议: 建议在【核心校验逻辑】中增加对 `effect_title_id` 的校验，验证其是否在玩家已拥有的特效称号列表中。
### Issue 8
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 五、 数值与配置表挂载
- 问题描述: 程序蓝图中的【配置表数据结构映射】部分，定义了 `id_ranges` 包含 `avatar`, `title`, `background`, `avatar_frame`, `character`, `skin`, `action`，但没有包含 `effect_title`（特效称号）的ID范围。这会导致程序在加载配置时，无法对特效称号的ID进行合法性校验。
- 修改建议: 建议在 `id_ranges` 中增加 `effect_title` 字段，并定义其取值范围（如 [1, 9999]），以匹配其他外观ID的配置方式。
**当前审查总计问题:** 8 个

--- 审查时间: 2026-05-28 13:29:36 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.affection_increment
- 问题描述: 数值说明书中定义 affection_increment 为每次互动或小游戏结算时增加的好感度经验值，范围10-100，默认值为10。但策划案中互动热点系统固定增加10点，小游戏系统根据得分等级增加30-100点，两者含义不同，应拆分为两个字段或明确区分。
- 修改建议: 建议将 affection_increment 拆分为 interaction_affection_increment（固定10点）和 minigame_affection_increment（动态30-100点），或增加说明字段区分来源。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.experience_to_next_level
- 问题描述: 数值说明书中定义 experience_to_next_level 为升到下一级所需的总经验值，公式为 (affection_level + 1) * 100，范围100-1000。但策划案中好感度系统描述为“每级所需经验呈线性增长（1级需100经验，10级需1000经验）”，未明确是累计经验还是单级经验。若为单级经验，则10级需1000经验，但总经验应为5500，与公式含义冲突。
- 修改建议: 建议明确 experience_to_next_level 是单级所需经验还是累计到下一级的总经验，并调整公式或描述以保持一致。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.special_event_trigger_level
- 问题描述: 数值说明书中定义 special_event_trigger_level 为触发特殊事件的好感度等级，默认值为0。但策划案中好感度系统明确特殊事件触发等级为5、8、10，且数值配表中 special_event_trigger_level 的 base 为5，growth 为3，生成序列为5,8,11...，与策划案10级上限不符，且缺少10级事件。
- 修改建议: 建议将 special_event_trigger_level 改为离散里程碑列表 [5,8,10]，或调整 growth 使序列在10级内结束。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.story_unlock_affection_level_requirement
- 问题描述: 数值说明书中定义 story_unlock_affection_level_requirement 为解锁剧情片段所需的好感度等级，范围3-10，默认值为0。但策划案中剧情解锁系统明确5个剧情片段对应等级3、5、7、9、10，而数值配表中 story_unlock_affection_level_requirement 的 base 为3，growth 为2，生成序列为3,5,7,9,11...，与策划案10级上限不符，且缺少10级。
- 修改建议: 建议将 story_unlock_affection_level_requirement 改为离散里程碑列表 [3,5,7,9,10]，或调整 growth 使序列在10级内结束。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.minigame_unlock_affection_level
- 问题描述: 数值说明书中定义 minigame_unlock_affection_level 为解锁小游戏所需的好感度等级，范围0-10，默认值为0。但策划案中小游戏系统明确每个角色2-3个小游戏，初始解锁1个，其余需好感度等级达到3级和6级解锁，而数值配表中 minigame_unlock_affection_level 的 base 为0，growth 为3，生成序列为0,3,6,9...，与策划案初始解锁1个（等级0）和3级、6级解锁一致，但未明确只有3个等级点，且growth可能导致多余等级。
- 修改建议: 建议将 minigame_unlock_affection_level 改为离散里程碑列表 [0,3,6] 或明确只有3个等级点。
### Issue 6
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.behavior_trigger_probability
- 问题描述: 数值说明书中定义 behavior_trigger_probability 为当前AI行为的触发概率，默认值为0.3。但策划案中AI日常行为系统有7种行为，每种行为有独立概率（如看书30%、发呆20%等），而数值配表中 behavior_trigger_probability 的 base 为0.3，growth 为0.1，无法表示7种不同概率。
- 修改建议: 建议将 behavior_trigger_probability 改为对象或数组，存储每种行为的独立概率，如 {1:0.3, 2:0.2, 3:0.15, 4:0.1, 5:0.1, 6:0.05, 7:0.1}。
### Issue 7
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.voice_trigger_probability
- 问题描述: 数值说明书中定义 voice_trigger_probability 为当前AI行为触发语音的概率，默认值为0.1。但策划案中AI日常行为系统提到每个行为有预设语音列表，随机触发，触发概率可配置，未明确是全局概率还是每个行为独立概率。
- 修改建议: 建议明确 voice_trigger_probability 是全局概率还是每个行为独立，若独立则改为对象或数组。
### Issue 8
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.camera_zoom
- 问题描述: 数值说明书中定义 camera_zoom 为拍照模式下相机的缩放比例，范围0.5-5.0，默认值为1.0。但数值配表中 camera_zoom 的 base 为1.0，growth 为0.5，type 为 linear，暗示每次调整增加0.5，但策划案中未明确缩放步长，且范围0.5-5.0与线性增长不匹配。
- 修改建议: 建议将 camera_zoom 改为范围字段，或明确缩放步长和调整方式。
### Issue 9
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.selected_filter_id
- 问题描述: 数值说明书中定义 selected_filter_id 范围0-4，对应无滤镜、清新、复古、黑白、暖色，默认值为0。但数值配表中 selected_filter_id 的 base 为0，growth 为1，type 为 linear，暗示每次调整增加1，但策划案中未明确滤镜切换顺序或步长。
- 修改建议: 建议将 selected_filter_id 改为枚举类型，无需 growth 字段。
### Issue 10
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.selected_pose_id
- 问题描述: 数值说明书中定义 selected_pose_id 范围0-4，对应默认、站立、坐姿、躺姿、依靠，默认值为0。但数值配表中 selected_pose_id 的 base 为0，growth 为1，type 为 linear，暗示每次调整增加1，但策划案中未明确姿势切换顺序或步长。
- 修改建议: 建议将 selected_pose_id 改为枚举类型，无需 growth 字段。
### Issue 11
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.selected_expression_id
- 问题描述: 数值说明书中定义 selected_expression_id 范围0-4，对应默认、微笑、害羞、惊讶、眨眼，默认值为0。但数值配表中 selected_expression_id 的 base 为0，growth 为1，type 为 linear，暗示每次调整增加1，但策划案中未明确表情切换顺序或步长。
- 修改建议: 建议将 selected_expression_id 改为枚举类型，无需 growth 字段。
### Issue 12
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.screenshot_count
- 问题描述: 数值说明书中定义 screenshot_count 为拍照模式下已截图的累计数量，范围0-99999，默认值为0。但数值配表中 screenshot_count 的 base 为0，growth 为1，type 为 linear，暗示每次截图增加1，但策划案中未明确截图计数增长方式。
- 修改建议: 建议将 screenshot_count 改为简单计数器，无需 growth 字段。
### Issue 13
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.dlc_purchase_timestamp
- 问题描述: 数值说明书中定义 dlc_purchase_timestamp 为DLC购买时间戳，默认值为0。但数值配表中 dlc_purchase_timestamp 的 base 为0，growth 为1，type 为 linear，暗示每次购买增加1，但时间戳应为具体值，无需 growth。
- 修改建议: 建议将 dlc_purchase_timestamp 改为时间戳字段，无需 growth 字段。
### Issue 14
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.character_unlock_status
- 问题描述: 数值说明书中定义 character_unlock_status 为对象，键为角色ID，值为布尔，默认值为空对象。但数值配表中 character_unlock_status 的 base 为0，growth 为1，type 为 linear，与对象类型不匹配。
- 修改建议: 建议将 character_unlock_status 改为对象类型，无需 growth 字段。
### Issue 15
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.skin_unlock_status
- 问题描述: 数值说明书中定义 skin_unlock_status 为对象，键为皮肤ID，值为布尔，默认值为空对象。但数值配表中 skin_unlock_status 的 base 为0，growth 为1，type 为 linear，与对象类型不匹配。
- 修改建议: 建议将 skin_unlock_status 改为对象类型，无需 growth 字段。
### Issue 16
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.affection_reward_status
- 问题描述: 数值说明书中定义 affection_reward_status 为对象，键为等级，值为布尔，默认值为空对象。但数值配表中 affection_reward_status 的 base 为0，growth 为1，type 为 linear，与对象类型不匹配。
- 修改建议: 建议将 affection_reward_status 改为对象类型，无需 growth 字段。
### Issue 17
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.story_linkage_status
- 问题描述: 数值说明书中定义 story_linkage_status 为对象，键为剧情ID，值为布尔，默认值为空对象。但数值配表中 story_linkage_status 的 base 为0，growth 为1，type 为 linear，与对象类型不匹配。
- 修改建议: 建议将 story_linkage_status 改为对象类型，无需 growth 字段。
### Issue 18
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.souvenir_placement_position
- 问题描述: 数值说明书中定义 souvenir_placement_position 为对象，包含x、y、z三个浮点数，默认值为null。但数值配表中未包含此字段，导致缺失。
- 修改建议: 建议在数值配表中添加 souvenir_placement_position 字段，或明确其配置方式。
### Issue 19
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.souvenir_placement_rotation
- 问题描述: 数值说明书中定义 souvenir_placement_rotation 为对象，包含x、y、z三个浮点数，默认值为null。但数值配表中未包含此字段，导致缺失。
- 修改建议: 建议在数值配表中添加 souvenir_placement_rotation 字段，或明确其配置方式。
### Issue 20
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 互动热点系统
- 问题描述: 策划案中互动热点系统提到“部分热点需好感度等级解锁”，但未明确具体哪些热点需要解锁，以及解锁等级要求。数值说明书中 unlock_affection_level_requirement 默认值为0，但策划案中仅举例“躺在床上”需5级。
- 修改建议: 建议在策划案中补充所有互动热点的解锁等级要求列表，或明确配置方式。
### Issue 21
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 小游戏系统
- 问题描述: 策划案中小游戏系统提到每个角色2-3个小游戏，初始解锁1个，其余需好感度等级达到3级和6级解锁。但未明确具体小游戏名称或ID，以及每个角色的小游戏数量是否固定。
- 修改建议: 建议在策划案中补充每个角色的小游戏列表及解锁等级。
### Issue 22
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 好感度系统
- 问题描述: 策划案中好感度系统提到“好感度等级达到特定等级（如5级、8级、10级），触发特殊事件”，但未明确5级、8级、10级的具体事件内容（5级赠送纪念品，8级特殊互动动画，10级最终剧情片段），仅在数据状态变化中提及。
- 修改建议: 建议在流转逻辑中明确每个等级的特殊事件内容。
### Issue 23
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 剧情解锁系统
- 问题描述: 策划案中剧情解锁系统提到每个角色拥有5个剧情片段，分别对应好感度等级3、5、7、9、10。但未明确每个剧情片段是否需要小游戏成就，以及具体成就要求。
- 修改建议: 建议在策划案中补充每个剧情片段的解锁条件（好感度等级+小游戏成就）。
### Issue 24
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 纪念品系统
- 问题描述: 策划案中纪念品系统提到每个角色拥有10个纪念品，其中5个通过小游戏获得，5个通过好感度等级解锁。但未明确具体哪些纪念品通过小游戏获得，哪些通过好感度解锁，以及对应的好感度等级。
- 修改建议: 建议在策划案中补充纪念品列表及获取方式。
### Issue 25
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: AI日常行为系统
- 问题描述: 策划案中AI日常行为系统提到行为触发概率可配置，支持根据好感度等级调整概率（如高好感度增加“哼歌”概率）。但未明确具体调整规则或公式。
- 修改建议: 建议在策划案中补充概率调整规则或参考数值配置表。
### Issue 26
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心校验逻辑
- 问题描述: 程序蓝图中核心校验逻辑提到“好感度经验增长校验：每次互动/小游戏结算后，校验经验增加值是否与配置一致（互动固定10点，小游戏按得分等级）”，但未明确小游戏得分等级的具体校验逻辑（如S级100点+1碎片，A级80点等）。
- 修改建议: 建议在蓝图中补充小游戏得分等级奖励的校验逻辑，或引用数值配置表。
### Issue 27
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心校验逻辑
- 问题描述: 程序蓝图中核心校验逻辑提到“剧情解锁条件校验：校验好感度等级和小游戏成就是否达标”，但未明确小游戏成就的具体校验方式（如S级评价）。
- 修改建议: 建议在蓝图中补充小游戏成就的校验逻辑。
### Issue 28
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 CheckDLCStatus 接口的详细说明，如返回参数中是否包含购买平台。
- 修改建议: 建议在接口说明中补充 purchase_platform 字段。
### Issue 29
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 RecordInteraction 接口的详细说明，如是否返回冷却时间或解锁状态。
- 修改建议: 建议在接口说明中补充返回参数，如 cooldown_timer 或 hotspot_unlocked_flag。
### Issue 30
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 StartMinigame 接口的详细说明，如是否返回小游戏解锁状态或每日次数。
- 修改建议: 建议在接口说明中补充返回参数，如 minigame_unlocked_flag 和 daily_play_count。
### Issue 31
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 EndMinigame 接口的详细说明，如是否返回纪念品碎片数量或得分等级。
- 修改建议: 建议在接口说明中补充返回参数，如 score_grade 和 souvenir_fragment_count。
### Issue 32
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 CheckStoryUnlock 接口的详细说明，如是否返回小游戏成就要求。
- 修改建议: 建议在接口说明中补充返回参数，如 story_unlock_minigame_achievement_requirement。
### Issue 33
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 RecordStoryWatch 接口的详细说明，如是否返回奖励物品。
- 修改建议: 建议在接口说明中补充返回参数，如 reward_items。
### Issue 34
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 SynthesizeSouvenir 接口的详细说明，如是否返回纪念品模型数据。
- 修改建议: 建议在接口说明中补充返回参数，如 souvenir_model_data。
### Issue 35
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 PlaceSouvenir 接口的详细说明，如是否返回摆放成功状态。
- 修改建议: 建议在接口说明中补充返回参数，如 placed_flag。
### Issue 36
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 SyncRoomState 接口的详细说明，如是否返回同步时间戳。
- 修改建议: 建议在接口说明中补充返回参数，如 sync_timestamp。
### Issue 37
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 SyncAffectionReward 接口的详细说明，如是否返回主游戏奖励数据。
- 修改建议: 建议在接口说明中补充返回参数，如 main_game_reward_data。
### Issue 38
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 RequestAffectionReset 接口的详细说明，如是否返回重置后的好感度等级。
- 修改建议: 建议在接口说明中补充返回参数，如 new_affection_level。
### Issue 39
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 HeartbeatSync 接口的详细说明，如是否返回同步标志。
- 修改建议: 建议在接口说明中补充返回参数，如 sync_required_flag。
### Issue 40
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 S->C: DLCRefunded 接口的详细说明，如是否返回退款标志。
- 修改建议: 建议在接口说明中补充返回参数，如 dlc_refunded_flag。
### Issue 41
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 S->C: CharacterUnlocked 接口的详细说明，如是否返回角色解锁标志。
- 修改建议: 建议在接口说明中补充返回参数，如 character_unlocked_flag。
### Issue 42
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 核心接口列表
- 问题描述: 程序蓝图中核心接口列表缺少 S->C: SkinUnlocked 接口的详细说明，如是否返回皮肤解锁标志。
- 修改建议: 建议在接口说明中补充返回参数，如 skin_unlocked_flag。
### Issue 43
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 配置表加载流程
- 问题描述: 程序蓝图中配置表加载流程提到读取 system_numerical_data.json，但实际数值配表文件名为 system_numerical_docs.json 和 data.json，存在不一致。
- 修改建议: 建议统一文件名或明确加载哪个文件。
### Issue 44
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“小游戏得分等级奖励：score_grade = {S:100+1碎片, A:80, B:50, C:30}”，但数值配表中 score_grade 定义在 relations_and_enums.enums 中，而程序蓝图未明确引用该枚举。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.score_grade。
### Issue 45
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“剧情解锁等级要求：story_unlock_affection_level_requirement = [3,5,7,9,10]”，但数值配表中该字段为线性增长公式，生成序列为3,5,7,9,11...，与蓝图不一致。
- 修改建议: 建议统一为离散列表或调整公式。
### Issue 46
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“小游戏解锁等级：minigame_unlock_affection_level = [1,3,6]”，但数值配表中该字段 base 为0，growth 为3，生成序列为0,3,6,9...，与蓝图不一致。
- 修改建议: 建议统一为离散列表或调整公式。
### Issue 47
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“特殊事件触发等级：special_event_trigger_level = [5,8,10]”，但数值配表中该字段 base 为5，growth 为3，生成序列为5,8,11...，与蓝图不一致。
- 修改建议: 建议统一为离散列表或调整公式。
### Issue 48
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“AI行为概率表：behavior_trigger_probability = {看书:0.3, 发呆:0.2, 做家务:0.15, 哼歌:0.1, 玩手机:0.1, 伸懒腰:0.05, 走动:0.1}”，但数值配表中该字段为单一浮点数，无法表示多个概率。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.current_behavior_id 并补充概率配置。
### Issue 49
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“语音触发概率：voice_trigger_probability = 0.1”，但数值配表中该字段为单一浮点数，而策划案中每个行为可独立配置语音概率。
- 修改建议: 建议在蓝图中明确语音触发概率是全局还是每个行为独立。
### Issue 50
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“拍照模式参数范围：camera_zoom = [0.5, 5.0]”，但数值配表中该字段为线性增长，与范围不匹配。
- 修改建议: 建议在蓝图中明确 camera_zoom 是范围还是步长。
### Issue 51
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“互动热点解锁等级：unlock_affection_level_requirement = 5（如“躺在床上”）”，但数值配表中该字段为线性增长，且策划案中仅举例一个热点。
- 修改建议: 建议在蓝图中明确所有热点的解锁等级配置方式。
### Issue 52
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“房间状态枚举：room_state = [default, level5_upgrade, level8_upgrade, level10_upgrade]”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.room_state。
### Issue 53
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“行为ID枚举：current_behavior_id = {1:看书, 2:发呆, 3:做家务, 4:哼歌, 5:玩手机, 6:伸懒腰, 7:走动}”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.current_behavior_id。
### Issue 54
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“滤镜ID枚举：selected_filter_id = {0:无滤镜, 1:清新, 2:复古, 3:黑白, 4:暖色}”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.selected_filter_id。
### Issue 55
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“姿势ID枚举：selected_pose_id = {0:默认, 1:站立, 2:坐姿, 3:躺姿, 4:依靠}”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.selected_pose_id。
### Issue 56
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“表情ID枚举：selected_expression_id = {0:默认, 1:微笑, 2:害羞, 3:惊讶, 4:眨眼}”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.selected_expression_id。
### Issue 57
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“购买平台枚举：purchase_platform = [iOS, Android, PC]”，但数值配表中该枚举定义在 relations_and_enums.enums 中，而蓝图未明确引用。
- 修改建议: 建议在蓝图中明确引用 relations_and_enums.enums.purchase_platform。
### Issue 58
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“超时阈值：房间加载超时=10秒，小游戏加载超时=15秒，剧情加载超时=20秒，玩家闲置超时=5分钟”，但数值配表中未定义这些超时阈值，策划案中仅在边界与异常兜底中提及。
- 修改建议: 建议在数值配表中添加超时阈值字段，或在蓝图中明确为硬编码值。
### Issue 59
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 关键配置挂载点
- 问题描述: 程序蓝图中关键配置挂载点提到“数据同步间隔：5分钟”，但数值配表中未定义该间隔，策划案中在数据联动系统中提及。
- 修改建议: 建议在数值配表中添加数据同步间隔字段，或在蓝图中明确为硬编码值。
**当前审查总计问题:** 59 个

--- 审查时间: 2026-05-28 14:18:52 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 互动热点系统
- 问题描述: 策划案中互动热点每次触发增加好感度固定值+5点，但数值配表（continuous_formulas）中 interaction_hotspot_system 的 affection_increment 未定义，且数值说明书中 affection_increment 固定为10，与策划案+5矛盾。
- 修改建议: 请确认互动热点每次触发增加的好感度经验值应为5还是10，并确保数值配表与策划案一致。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.affection_increment
- 问题描述: 数值说明书中 affection_increment 描述为“每次互动增加的好感度经验值，固定为10”，但策划案中互动热点每次增加+5点，小游戏胜利+20、失败+5，存在冲突。
- 修改建议: 请将 affection_increment 拆分为多个字段（如 hotspot_affection_increment、minigame_win_increment、minigame_lose_increment），或明确该字段仅适用于某一类互动。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.daily_play_count
- 问题描述: 数值说明书中 daily_play_count 的默认值为0，取值范围0-3，但策划案中每个小游戏每日可玩5次，且数值配表中 max_daily_play_count 固定为3，与策划案5次矛盾。
- 修改建议: 请统一每日游玩次数为5次（策划案）或3次（数值配表），并同步修改数值说明书中的取值范围。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.experience_to_next_level
- 问题描述: 数值说明书中 experience_to_next_level 描述为“计算公式为当前等级*100”，但数值配表中 affection_system 的 experience_to_next_level 的 base=100, growth=100，公式为 100 + (level-1)*100，与描述不一致。
- 修改建议: 请统一升级所需经验公式：若为当前等级*100（1级需100，2级需200...），则配表应为 base=100, growth=100；若为固定100+等级*100，则需修改描述。
### Issue 5
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 小游戏系统
- 问题描述: 策划案中每日可玩5次，但数值配表中 max_daily_play_count 固定为3，且程序蓝图也引用3次，存在三方不一致。
- 修改建议: 请确认每日游玩次数，并同步修改数值配表和程序蓝图中的对应配置。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 好感度系统
- 问题描述: 策划案中好感度等级上限为10级，每级所需经验递增（如1级需100经验，10级需5000经验），但数值配表中 experience_to_next_level 为线性增长（base=100, growth=100），无法达到5000经验（10级时仅需1000经验）。
- 修改建议: 请明确每级所需经验的具体数值或公式，确保与数值配表一致。
### Issue 7
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: AI日常行为系统
- 问题描述: 策划案中行为列表包括：看书、发呆、做家务、哼歌、伸懒腰、玩手机、在窗边眺望，共7种行为。但数值说明书枚举中 behavior_id 包含1-8（8为睡觉），且程序蓝图未明确行为数量，存在不一致。
- 修改建议: 请统一行为列表，确认是否包含“睡觉”行为（闲置超时触发），并在所有文档中保持一致。
### Issue 8
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: relations_and_enums.enum_definitions.behavior_id
- 问题描述: 枚举中 behavior_id 包含8种行为（1-8），但策划案中仅列出7种，且缺少“走动”行为的描述（枚举中5为玩手机，6为伸懒腰，7为走动，8为睡觉），与策划案不一致。
- 修改建议: 请与策划对齐行为列表，确保枚举与策划案完全匹配。
### Issue 9
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载
- 问题描述: 程序蓝图中引用小游戏每日次数为3次（max_daily_play_count），但策划案中为5次，且数值配表中也为3次，但策划案是需求源头，需确认。
- 修改建议: 请根据最终确认的每日次数（5次或3次）更新程序蓝图中的配置引用。
### Issue 10
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载
- 问题描述: 程序蓝图中提到“好感度配置：affection_increment（固定10）”，但策划案中互动热点每次+5，小游戏胜利+20、失败+5，固定10与策划案矛盾。
- 修改建议: 请根据策划案细化好感度增量配置，区分不同来源的增量值。
### Issue 11
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 拍照模式
- 问题描述: 策划案中滤镜列表为“清新”、“暖阳”、“复古”、“黑白”共4种，但数值说明书枚举中 filter_id 为1:清新, 2:复古, 3:黑白, 4:暖色，缺少“暖阳”且顺序不同。
- 修改建议: 请统一滤镜名称和顺序，确保策划案与数值说明书一致。
### Issue 12
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: relations_and_enums.enum_definitions.filter_id
- 问题描述: 枚举中滤镜为“清新”、“复古”、“黑白”、“暖色”，但策划案中为“清新”、“暖阳”、“复古”、“黑白”，缺少“暖阳”且多出“暖色”。
- 修改建议: 请与策划对齐滤镜列表，确保枚举与策划案完全匹配。
### Issue 13
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 互动热点系统
- 问题描述: 策划案中每个热点冷却时间为30秒，但数值配表中 cooldown_timer 的 base=30, growth=0，一致。但策划案中未提及冷却时间是否随好感度变化，而数值配表为固定值，需确认是否需动态调整。
- 修改建议: 请明确冷却时间是否受好感度等级影响，若需动态调整，请补充公式。
### Issue 14
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 好感度系统
- 问题描述: 策划案中每日通过互动热点获得的好感度经验有上限200点，但数值配表和程序蓝图中均未定义该上限的配置字段。
- 修改建议: 请在数值配表中增加每日互动好感度上限字段（如 daily_interaction_affection_cap），并在程序蓝图中引用。
### Issue 15
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server)
- 问题描述: 程序蓝图中持久化数据未包含互动热点冷却时间字段（cooldown_timer），但该字段在数值说明书中定义且需要服务端校验。
- 修改建议: 请在持久化数据中增加互动热点冷却时间相关字段，或明确冷却时间仅由客户端管理。
### Issue 16
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 纪念品系统
- 问题描述: 策划案中纪念品解锁条件包括好感度6级和小游戏成就，但数值说明书中 souvenir_fragment_count 与 minigame_system 联动，策划案未提及碎片合成机制，存在逻辑缺失。
- 修改建议: 请补充纪念品碎片合成机制或移除碎片相关字段，确保策划案与数值说明书一致。
### Issue 17
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.souvenir_fragment_count
- 问题描述: 数值说明书中 souvenir_fragment_count 描述为“纪念品碎片数量”，但策划案中纪念品为直接解锁，无碎片合成机制，存在功能不匹配。
- 修改建议: 请与策划确认纪念品解锁方式，若为直接解锁则移除碎片相关字段，若为碎片合成则需在策划案中补充。
**当前审查总计问题:** 17 个

--- 审查时间: 2026-05-29 00:38:45 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 安全验证 - 密码修改/找回
- 问题描述: 策划案中密码找回流程描述为：输入绑定的手机号或邮箱，接收验证码，输入新密码。但未明确说明找回密码时是否需要先验证账号是否存在，以及验证码发送的目标（手机号/邮箱）与账号绑定状态的关系。
- 修改建议: 建议补充说明：找回密码时，系统应首先校验输入的手机号/邮箱是否已绑定账号，若未绑定则提示“该账号未绑定此手机号/邮箱”。同时明确验证码发送的目标是输入的手机号/邮箱，而非账号绑定的默认联系方式。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 账号状态管理 - 账号注销
- 问题描述: 策划案中账号注销流程提到“第二层验证：输入绑定手机号/邮箱收到的验证码”，但未说明如果账号同时绑定了手机号和邮箱，验证码发送到哪个。也未说明如果账号未绑定任何手机号或邮箱，如何完成验证。
- 修改建议: 建议补充：若账号同时绑定了手机号和邮箱，默认发送验证码到手机号，并提供切换选项。若账号未绑定任何手机号或邮箱，则无法发起注销，需先完成绑定。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 账号创建与登录 - 游客模式
- 问题描述: 策划案中游客模式描述为“允许玩家进入游戏体验前30分钟内容”，但未明确30分钟是累计游戏时间还是从首次登录开始计算的绝对时间。这会影响程序实现。
- 修改建议: 建议明确：30分钟为累计游戏时间（即玩家实际在游戏中的时间），还是从首次登录开始计算的绝对时间（即现实时间30分钟）。建议采用累计游戏时间，并说明计时器在后台运行时的处理逻辑。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - server_error_code
- 问题描述: 数值说明书中 `server_error_code` 的枚举值中，错误码7定义为“账号冻结”，但策划案中并未明确提及“账号冻结”状态的具体触发条件和处理流程，仅在边界与异常兜底中简单提到“账号处于冻结状态：无法发起注销。需先解冻。”。
- 修改建议: 建议在策划案中补充账号冻结的完整触发条件（如：多次密码错误、安全风险检测等）和解冻流程，或者在数值说明书中移除该错误码，确保一致性。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - real_name_verification_status
- 问题描述: 数值说明书中存在 `real_name_verification_status` 字段，其描述为“与real_name_status同步”，但 `real_name_status` 已存在且功能相同。这造成了字段冗余，可能导致数据不一致。
- 修改建议: 建议删除 `real_name_verification_status` 字段，统一使用 `real_name_status` 表示实名认证状态，避免数据冗余和同步问题。
### Issue 6
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - binding_status
- 问题描述: 数值说明书中 `binding_status` 字段的默认值为 `{phone: false, email: false, wechat: false, qq: false, apple_id: false}`，但策划案中未明确第三方平台是否包含“Apple ID”，仅在登录方式中提及。
- 修改建议: 建议在策划案中明确第三方平台列表是否包含Apple ID，并确保与数值说明书一致。如果包含，建议在策划案中明确列出。
### Issue 7
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 核心校验逻辑 - 验证码发送校验
- 问题描述: 程序蓝图中验证码发送频率限制描述为“频繁发送（如24小时内超过10次）临时封禁24小时”，但数值说明书和策划案中均未定义“频繁发送”的具体阈值（10次）。数值说明书中的 `verification_code_frequency_limit` 在程序蓝图中有提及，但未在数值配表中明确列出。
- 修改建议: 建议在数值配表 `discrete_milestones` 中增加 `verification_code_frequency_limit` 字段，明确24小时内允许的最大发送次数（如10次），并确保与程序蓝图一致。
### Issue 8
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - POST /api/auth/guest-to-formal
- 问题描述: 程序蓝图中游客转正API `POST /api/auth/guest-to-formal` 的请求参数包含 `formal_account_id` 和 `formal_jwt_token`，但策划案中游客转正流程描述为“系统引导玩家完成注册或登录”，并未明确说明前端需要传递正式账号ID和Token。这可能导致前端实现与后端接口不匹配。
- 修改建议: 建议明确游客转正流程：前端在玩家完成正式登录后，将游客ID和正式登录返回的JWT Token一起发送给后端，后端根据JWT Token解析出正式账号ID，无需前端传递 `formal_account_id`。
### Issue 9
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - POST /api/auth/real-name-verify
- 问题描述: 程序蓝图中实名认证API `POST /api/auth/real-name-verify` 的请求参数包含 `id_number_hash`，但策划案中描述为“系统将信息加密后发送至公安实名认证接口”，未明确前端是否需要对身份证号进行哈希处理。
- 修改建议: 建议明确：前端是否需要对身份证号进行哈希处理后再传输，还是直接传输加密后的明文。如果前端需要哈希，需统一哈希算法（如SHA-256），并确保与后端一致。
### Issue 10
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - POST /api/auth/initiate-deletion
- 问题描述: 程序蓝图中账号注销API `POST /api/auth/initiate-deletion` 的请求参数包含 `verification_code`，但策划案中账号注销流程描述为“输入绑定手机号/邮箱收到的验证码”，未说明验证码的发送时机和方式。
- 修改建议: 建议明确：前端在调用注销API前，应先调用发送验证码API，将验证码发送到玩家绑定的手机号或邮箱，然后再调用注销API并传入验证码。
**当前审查总计问题:** 10 个

--- 审查时间: 2026-05-29 00:45:00 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 账号创建与登录 - 游客模式
- 问题描述: 策划案中游客Token有效期为30分钟（1800秒），但程序蓝图（tech_blueprint.md）中数值配置挂载部分明确从continuous_formulas读取默认值1800秒，而数值配表（data.json）中continuous_formulas为空对象，未定义该关键数值。
- 修改建议: 请在数值配表（data.json）的continuous_formulas中补充游客Token有效期的配置项，例如"guest_token_ttl": 1800，并确保程序蓝图中的读取路径与此一致。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 账号创建与登录 - 注册与登录
- 问题描述: 策划案中密码规则为8-20位，必须包含大小写字母和数字，但数值配表（data.json）的discrete_milestones中未定义密码长度与复杂度规则相关的字段，程序蓝图（tech_blueprint.md）却声称从discrete_milestones读取这些规则。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充密码规则配置，例如在account_creation_login下添加"password_min_length": 8, "password_max_length": 20, "password_require_uppercase": true, "password_require_lowercase": true, "password_require_digit": true等字段。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 安全验证 - 实名认证
- 问题描述: 策划案中实名认证触发条件包含单日累计充值200元、单月累计充值1000元，但数值配表（data.json）的discrete_milestones中未定义这些充值阈值，程序蓝图（tech_blueprint.md）却声称从discrete_milestones读取。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充实名认证触发阈值，例如在security_verification下添加"daily_recharge_threshold": 200, "monthly_recharge_threshold": 1000。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.4 安全验证 - 设备管理
- 问题描述: 策划案中设备管理列表返回最近10条登录设备记录，但数值配表（data.json）和程序蓝图（tech_blueprint.md）均未定义该数量限制的配置项，导致该数值硬编码且不可配置。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充设备列表最大条数配置，例如在security_verification下添加"max_device_list_count": 10。
### Issue 5
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.5 安全验证 - 密码修改/找回
- 问题描述: 策划案中密码错误次数限制为5次，锁定15分钟，但数值配表（data.json）的discrete_milestones中未定义密码错误锁定阈值和锁定时长，程序蓝图（tech_blueprint.md）却声称从discrete_milestones和continuous_formulas读取这些值，而continuous_formulas为空。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充"password_error_lock_threshold": 5，在continuous_formulas中补充"password_error_lock_duration": 900。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 账号创建与登录 - 注册与登录
- 问题描述: 策划案中验证码发送间隔为60秒，每日上限10次，但数值配表（data.json）的discrete_milestones中未定义这些频率限制值，程序蓝图（tech_blueprint.md）却声称从discrete_milestones读取。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充验证码频率限制配置，例如在account_creation_login下添加"verification_code_interval": 60, "daily_verification_code_limit": 10。
### Issue 7
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 安全验证 - 实名认证
- 问题描述: 策划案中实名认证每日尝试上限为3次，但数值配表（data.json）的discrete_milestones中未定义该上限值，程序蓝图（tech_blueprint.md）却声称从discrete_milestones读取。
- 修改建议: 请在数值配表（data.json）的discrete_milestones中补充实名认证每日尝试上限配置，例如在security_verification下添加"daily_real_name_attempts_limit": 3。
### Issue 8
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.6 账号状态管理 - 账号注销
- 问题描述: 策划案中账号注销冷却期为7天，但数值配表（data.json）的continuous_formulas中未定义该冷却期天数，程序蓝图（tech_blueprint.md）却声称从continuous_formulas读取。
- 修改建议: 请在数值配表（data.json）的continuous_formulas中补充账号注销冷却期配置，例如"deletion_cooling_off_days": 7。
### Issue 9
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 账号创建与登录 - 注册与登录
- 问题描述: 策划案中正式账号Token有效期为30天，但数值配表（data.json）的continuous_formulas中未定义该有效期，程序蓝图（tech_blueprint.md）却声称从continuous_formulas读取。
- 修改建议: 请在数值配表（data.json）的continuous_formulas中补充正式账号Token有效期配置，例如"formal_token_ttl": 2592000。
### Issue 10
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 账号创建与登录 - 游客模式
- 问题描述: 策划案中游客Token有效期为30分钟（1800秒），但程序蓝图（tech_blueprint.md）中数值配置挂载部分明确从continuous_formulas读取默认值1800秒，而数值配表（data.json）中continuous_formulas为空对象，未定义该关键数值。
- 修改建议: 请在数值配表（data.json）的continuous_formulas中补充游客Token有效期的配置项，例如"guest_token_ttl": 1800，并确保程序蓝图中的读取路径与此一致。
**当前审查总计问题:** 10 个

--- 审查时间: 2026-05-29 01:15:57 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.1 好友容量
- 问题描述: 策划案中好友位扩容消耗描述存在歧义。第2次扩容（至30人）描述为“消耗10000信用点或50数据金”，但未明确是“信用点或数据金二选一”还是“信用点+数据金”。后续扩容描述类似。这与程序蓝图中的扩容消耗配置表（明确区分信用点消耗和数据金消耗两列）的意图不一致，可能导致实现歧义。
- 修改建议: 请明确每次扩容的消耗规则：是“信用点或数据金二选一”，还是“信用点+数据金”组合消耗？如果是二选一，请明确描述；如果是组合消耗，请明确具体数值。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.4 助战系统
- 问题描述: 策划案中助战系统解锁前置条件为“玩家等级达到10级，且至少拥有一个好友”。但数值说明书和程序蓝图中，助战系统解锁校验仅引用了玩家等级（≥10），未提及“至少拥有一个好友”这一条件。存在逻辑不一致。
- 修改建议: 请确认助战系统的解锁条件是否真的需要“至少拥有一个好友”。如果是，请在数值说明书和程序蓝图中补充该条件；如果不是，请修改策划案中的描述。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.4 助战系统 / 借用流程
- 问题描述: 策划案中描述助战角色“作为第四人加入编队（不替换己方三人）”，但在战斗规则中又提到“助战角色不占用玩家自身角色出战位”。这两处描述重复且略显冗余，且未明确说明在编队界面如何体现第四人。程序蓝图中的`Friend_ConfirmAssist`接口返回`assist_role_data`用于战斗，但未定义编队数据结构如何处理第四人。
- 修改建议: 请明确助战角色在编队数据中的定位：是作为独立的“助战位”存在，还是临时加入编队列表？请与程序蓝图对齐，明确`assist_role_data`在战斗系统中的使用方式。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / daily_gift_count
- 问题描述: 数值说明书中`daily_gift_count`的描述为“玩家当日已赠送体力的次数，取值范围0-20”，但策划案2.5节中赠送体力每次消耗自身5点体力，且每日上限20次。数值配表`continuous_formulas`中`daily_gift_count`的`growth`为1，这仅表示每次增加1，但未体现“消耗5点体力”这一关联数值。数值配表缺少对“赠送体力消耗体力值”的字段定义。
- 修改建议: 请在数值配表中增加一个字段，例如`gift_stamina_cost`，值为5，用于明确每次赠送体力消耗的体力值。或者，在`implementation_notes`中明确此消耗值。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / friend_point
- 问题描述: 数值说明书中`friend_point`的描述为“取值范围0-9999”，但策划案4.1节中计算每月总消耗约3750点，每日最大产出240点。数值配表`continuous_formulas`中`friend_point`的`growth`为240，这似乎是每日最大产出，但作为字段的growth值不合适，因为友情点并非线性增长。此外，配表中缺少对友情点获取来源的具体数值定义（如赠送体力得5点、点赞得2点、被借用得10点）。
- 修改建议: 请将`friend_point`的`growth`值移除或修改为0，因为友情点不是线性增长的字段。同时，请在数值配表中增加一个子表或明确描述，定义各交互行为对应的友情点获取数值（赠送体力：5点，点赞：2点，被借用：10点）。
### Issue 6
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / friend_capacity_expansion_count
- 问题描述: 数值说明书中`friend_capacity_expansion_count`的描述为“取值范围0-6”，但策划案2.1节中扩容次数为6次（从20人扩至50人），数值配表`discrete_milestones`中该字段的取值也是1-6。但程序蓝图中的扩容消耗配置表明确列出了0-6共7行（包含初始状态）。数值配表缺少对扩容次数为0（初始状态）的定义。
- 修改建议: 请在`discrete_milestones`的`friend_capacity_expansion_count`中增加`0: 0`的条目，以表示初始状态（未扩容）。
### Issue 7
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) / 核心接口 / Friend_GetAssistList
- 问题描述: 程序蓝图中的`Friend_GetAssistList`接口返回`assist_list`，其中包含`daily_borrowed`字段。但策划案2.4节中，助战选择界面需要显示“今日已借用”标签，这需要知道当前玩家是否已经借用过该好友。`daily_borrowed`字段名含义模糊，可能被误解为“该好友今日被借用的次数”，而非“当前玩家是否已借用该好友”。
- 修改建议: 请将`Friend_GetAssistList`返回参数中的`daily_borrowed`字段重命名为`has_borrowed_today`（布尔值），以明确表示当前玩家是否已借用过该好友。
### Issue 8
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) / 核心接口 / Friend_GetFriendProfile 与 Friend_GetFriendHomePage
- 问题描述: 程序蓝图中同时定义了`Friend_GetFriendProfile`和`Friend_GetFriendHomePage`两个接口，返回参数高度重叠（都包含签名、近期战绩、好感度角色、助战角色配置）。策划案3.2节中，好友主页展示的信息与这两个接口的返回内容基本一致。存在接口冗余，可能导致前端调用混乱。
- 修改建议: 请合并这两个接口，或明确区分它们的用途。例如，`Friend_GetFriendProfile`用于好友列表中的卡片展示（轻量级数据），`Friend_GetFriendHomePage`用于进入好友主页后的完整数据展示。如果合并，请删除冗余接口。
### Issue 9
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) / 核心校验逻辑 / 助战借用校验
- 问题描述: 程序蓝图描述“战斗开始时再次校验好友关系、借用次数、助战角色配置，防止数据同步延迟”。但策划案2.4节中，借用流程是在关卡选择界面进行的，战斗开始时再次校验是合理的。然而，程序蓝图未定义在`Friend_ConfirmAssist`接口被调用后，如果战斗开始前好友关系发生变化（如被删除），应如何处理。
- 修改建议: 请明确在`Friend_ConfirmAssist`调用后、战斗开始前，如果好友关系发生变化（如好友删除你），服务端的处理逻辑。例如：是否允许已确认的借用继续战斗，但结算时不再发放奖励？
### Issue 10
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) / 核心校验逻辑 / 邀请奖励校验
- 问题描述: 程序蓝图提到“仅限新注册玩家通过邀请链接注册”，但未定义如何验证“通过邀请链接注册”。策划案4.2节中描述“被邀请者需通过邀请链接注册”。缺少具体的校验机制描述，例如：邀请链接中是否携带邀请者ID？注册时如何记录该ID？
- 修改建议: 请补充邀请奖励校验的具体技术实现方案。例如：邀请链接中携带邀请者ID，注册时将该ID写入被邀请者的数据表中，后续通过该ID关联发放奖励。
**当前审查总计问题:** 10 个

--- 审查时间: 2026-05-29 01:23:56 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.3 轻交互：赠送体力与点赞
- 问题描述: 策划案中描述赠送体力时，发送方扣除5点体力，但未明确发送方是否获得任何奖励（如友情点）。数值说明书和程序蓝图均未定义发送方赠送体力后的奖励。这导致逻辑不闭环，且与后续友情点获取规则（通过赠送体力获得5点/次）矛盾。
- 修改建议: 请明确赠送体力后，发送方是否获得友情点奖励。如果获得，请补充说明奖励数值（如5点友情点），并确保与数值说明书中的`friend_point`获取逻辑一致。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / daily_gift_count
- 问题描述: 数值说明书中`daily_gift_count`描述为“玩家今日已赠送体力的次数”，但未定义发送方赠送体力后是否获得友情点，以及获得多少。这与策划案中“每日通过赠送体力（5点/次）获得友情点”的描述不一致。
- 修改建议: 请在`field_dictionary`中增加一个字段（如`friend_point_from_gift`）或修改`daily_gift_count`的描述，明确每次赠送体力后发送方获得的友情点数量（如5点），并确保与策划案逻辑一致。
### Issue 3
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 赠送体力校验
- 问题描述: 程序蓝图中赠送体力校验逻辑未包含发送方获得友情点的处理。策划案中明确“每日通过赠送体力（5点/次）获得友情点”，但蓝图中的校验逻辑仅涉及体力扣除和邮件发送，未提及发送方友情点的增加。
- 修改建议: 请在赠送体力校验逻辑中，增加发送方获得友情点的步骤（如5点），并更新`friend_point`字段。同时，确保`Friend_GiftStamina` API的返回参数或后续处理中包含此逻辑。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.4 助战系统
- 问题描述: 策划案中助战系统描述“借用方通关后获得5点友情点”，但未明确如果助战角色死亡，借用方友情点奖励减半（2点）后，借出方是否仍获得10点友情点。这可能导致逻辑歧义。
- 修改建议: 请明确助战角色死亡时，借出方的奖励是否受影响。建议补充说明：助战角色死亡仅影响借用方奖励，借出方仍获得10点友情点。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / daily_borrowed_count
- 问题描述: 数值说明书中`daily_borrowed_count`描述为“玩家今日助战被借用的次数”，取值范围0-10，但未定义借出方每次获得的友情点数量（10点）。这与策划案中“借出方通过邮件获得10点友情点”的描述不一致。
- 修改建议: 请在`field_dictionary`中增加一个字段（如`friend_point_from_borrowed`）或修改`daily_borrowed_count`的描述，明确每次被借用后借出方获得的友情点数量（如10点），并确保与策划案逻辑一致。
### Issue 6
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 助战借用校验
- 问题描述: 程序蓝图中助战借用校验逻辑未包含借出方获得友情点的处理。策划案中明确“借出方通过邮件获得10点友情点”，但蓝图中的校验逻辑仅涉及借用次数更新，未提及借出方友情点的增加。
- 修改建议: 请在助战借用校验逻辑中，增加借出方获得友情点的步骤（如10点），并更新`friend_point`字段。同时，确保`Friend_ConfirmAssist` API的返回参数或后续处理中包含此逻辑。
### Issue 7
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.5 友情点与商店
- 问题描述: 策划案中描述“每日通过赠送体力（5点/次）、点赞（2点/次）、助战被借用（10点/次）获得，每日上限约50-100点”，但未明确每日上限的具体计算方式。例如，是否所有交互共享一个上限，还是各自独立上限？这可能导致数值实现不明确。
- 修改建议: 请明确每日友情点获取上限的计算方式。建议说明：每日通过赠送体力、点赞、助战被借用获得的友情点总和上限为100点，或分别设置上限（如赠送体力50点、点赞20点、助战被借用100点）。
### Issue 8
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / friend_point
- 问题描述: 数值说明书中`friend_point`描述为“玩家当前持有的友情点数量”，但未定义每日获取上限。这与策划案中“每日上限约50-100点”的描述不一致，可能导致玩家无限获取友情点。
- 修改建议: 请在`field_dictionary`中增加一个字段（如`daily_friend_point_limit`），定义每日友情点获取上限（如100点），并确保与策划案逻辑一致。
### Issue 9
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 每日重置逻辑
- 问题描述: 程序蓝图中每日重置逻辑未包含`daily_friend_point_limit`或类似字段的重置。如果策划案中定义了每日友情点获取上限，则需要在每日重置时重置该上限的计数。
- 修改建议: 请在每日重置逻辑中，增加对每日友情点获取上限计数的重置（如`daily_friend_point_earned`字段重置为0），确保玩家每日可重新获取友情点。
### Issue 10
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.2 好友管理 / 推荐列表
- 问题描述: 策划案中描述推荐列表“根据玩家等级（±5级）、在线状态、助战角色强度（总战力评分）生成”，但未明确“助战角色强度”的具体计算方式（如总战力评分是否包含武器、后勤等）。这可能导致推荐算法实现不明确。
- 修改建议: 请明确“助战角色强度”的计算方式，例如：总战力评分 = 角色基础战力 + 武器战力 + 后勤小队战力。
### Issue 11
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / friend_capacity_expansion_count
- 问题描述: 数值说明书中`friend_capacity_expansion_count`描述为“取值范围0-6”，但策划案中描述“最多扩容至50人上限”，初始容量20，每次扩容+5，最多扩容6次（20+6*5=50）。但数值配表中`friend_capacity_expansion_count`的离散里程碑仅定义了0-6，未定义每次扩容对应的容量值。这可能导致扩容逻辑不完整。
- 修改建议: 请在`discrete_milestones`中增加`friend_capacity`的离散里程碑，明确每次扩容后的容量值（如0:20, 1:25, 2:30, 3:35, 4:40, 5:45, 6:50），确保与策划案逻辑一致。
### Issue 12
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 好友扩容校验
- 问题描述: 程序蓝图中好友扩容校验逻辑仅校验`friend_capacity_expansion_count < 6`，但未校验扩容后的容量是否超过50。虽然逻辑上6次扩容后容量为50，但未明确校验容量上限，可能导致数据溢出。
- 修改建议: 请在好友扩容校验逻辑中，增加对扩容后容量是否超过50的校验（如`friend_capacity + 5 <= 50`），确保数据一致性。
### Issue 13
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.4 助战系统 / 借用流程
- 问题描述: 策划案中描述“系统调用`Friend_ConfirmAssist`接口，返回`assist_role_data`”，但未明确该接口是否在每次进入战斗前调用。程序蓝图中描述“助战借用流程需在进入战斗前重新拉取好友最新助战数据”，但策划案中未明确说明。这可能导致实现不一致。
- 修改建议: 请明确`Friend_ConfirmAssist`接口的调用时机，例如：每次进入战斗前必须调用该接口，以确保助战数据是最新的。
### Issue 14
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 助战借用校验
- 问题描述: 程序蓝图中助战借用校验逻辑包含“校验好友是否仍设置了助战角色”，但未明确如果好友未设置助战角色，是否返回错误码。策划案中描述“若好友已更换，则提示‘该好友已更换助战角色，请重新选择’”，但蓝图中的校验逻辑未包含此错误码。
- 修改建议: 请在助战借用校验逻辑中，增加对好友是否设置助战角色的校验，并返回相应的错误码（如`friend_borrow_result`枚举中的2：好友已更换助战角色）。
### Issue 15
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 四、经济循环与商业化埋点 / 好友邀请奖励
- 问题描述: 策划案中描述“邀请好友注册并达到20级，邀请者获得限定头像框、100数据金”，但未明确是否每个被邀请者达到20级时，邀请者都能获得奖励，还是仅限首次。程序蓝图中描述“校验邀请者是否已领取过该被邀请者的奖励”，暗示每个被邀请者独立计算，但策划案中未明确。
- 修改建议: 请明确邀请奖励的发放规则：是每个被邀请者达到20级时，邀请者都能获得一次奖励，还是仅限首次邀请成功？建议补充说明。
### Issue 16
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / friend_invite_reward_claimed
- 问题描述: 数值说明书中`friend_invite_reward_claimed`描述为“标记玩家是否已领取过邀请奖励”，但未明确是针对单个被邀请者还是全局。程序蓝图中描述“校验邀请者是否已领取过该被邀请者的奖励”，暗示是针对单个被邀请者，但数值说明书中的布尔字段无法区分多个被邀请者。
- 修改建议: 请修改`friend_invite_reward_claimed`为数组或字典结构，存储每个被邀请者ID及其奖励领取状态，确保与程序蓝图逻辑一致。
### Issue 17
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑 / 邀请奖励校验
- 问题描述: 程序蓝图中邀请奖励校验逻辑包含“校验邀请者`friend_invite_reward_claimed`是否为false（针对该被邀请者）”，但数值说明书中的`friend_invite_reward_claimed`是布尔字段，无法针对单个被邀请者进行校验。这可能导致实现与数据模型不匹配。
- 修改建议: 请修改邀请奖励校验逻辑，使用数组或字典结构存储每个被邀请者的奖励领取状态，并针对每个被邀请者独立校验。
### Issue 18
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 三、表现层与角色展示联动 (核心强制项) / 好友列表卡片
- 问题描述: 策划案中描述“每个好友卡片展示其看板娘3D模型缩略图（半身，带动态呼吸/待机动作）”，但未明确是否所有好友卡片都加载3D模型，还是仅在线好友。这可能导致性能问题，尤其是好友数量较多时。
- 修改建议: 请明确好友卡片3D模型的加载策略，例如：仅在线好友加载3D模型，离线好友使用静态头像，或所有好友都加载但使用LOD降级。
### Issue 19
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 二、前端模块划分 (Client) / 表现层控制器 / 3D模型加载管理器
- 问题描述: 程序蓝图中3D模型加载管理器描述“实现LOD自动降级”，但未明确降级策略（如根据设备性能或好友数量）。策划案中未明确降级策略，可能导致实现不一致。
- 修改建议: 请明确LOD降级策略，例如：根据设备性能自动降级，或根据好友列表中的好友数量动态调整模型精度。
### Issue 20
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 五、旧系统与数据联动 (强依赖) / 邮件系统
- 问题描述: 策划案中描述“邮件系统支持‘一键领取’所有好友相关奖励”，但未明确“一键领取”的具体实现方式（如是否领取所有邮件奖励，还是仅好友相关）。程序蓝图中未提及“一键领取”功能。
- 修改建议: 请明确“一键领取”功能的范围：是领取所有邮件奖励，还是仅好友相关奖励？建议补充说明，并确保程序蓝图实现此功能。
### Issue 21
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中未定义`Friend_GetAllData` API的返回参数中是否包含`friend_application_count`字段。策划案中描述“主界面社交按钮出现小红点提示（有待处理申请或可领取友情点奖励时）”，但蓝图中的API未返回待处理申请数量，可能导致小红点无法正确显示。
- 修改建议: 请在`Friend_GetAllData` API的返回参数中增加`friend_application_count`字段，用于前端判断小红点显示。
### Issue 22
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中未定义`Friend_GetAllData` API的返回参数中是否包含`friend_point`字段。策划案中描述“可领取友情点奖励时”显示小红点，但蓝图中的API未返回友情点数据，可能导致小红点无法正确显示。
- 修改建议: 请在`Friend_GetAllData` API的返回参数中增加`friend_point`字段，用于前端判断是否可领取友情点奖励。
### Issue 23
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.4 助战系统 / 借用流程
- 问题描述: 策划案中描述“系统打开好友列表，仅展示已设置助战角色的好友，并按助战角色战力排序”，但未明确“助战角色战力”的计算方式。程序蓝图中也未定义排序规则。
- 修改建议: 请明确“助战角色战力”的计算方式，例如：使用`assist_role_data`中的角色等级、技能等级、武器、后勤小队配置计算总战力，并按此排序。
### Issue 24
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) / Friend_GetAssistList
- 问题描述: 程序蓝图中`Friend_GetAssistList` API的返回参数包含`assist_list`，但未明确是否包含排序后的顺序。策划案中要求按助战角色战力排序，但蓝图中的API未定义排序规则。
- 修改建议: 请在`Friend_GetAssistList` API的返回参数中明确排序规则，例如：返回的`assist_list`已按助战角色战力降序排列。
**当前审查总计问题:** 24 个

--- 审查时间: 2026-05-29 12:19:42 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary -> daily_affection_experience_cap
- 问题描述: 数值说明书中的字段名为 'daily_affection_experience_cap'，但程序蓝图持久化数据表中使用的字段名为 'daily_affection_experience'。两者命名不一致，且 'daily_affection_experience_cap' 在策划案中定义为每日上限，而程序蓝图中的 'daily_affection_experience' 更像是当日已获得经验值。这会导致数据同步和逻辑校验混乱。
- 修改建议: 请与程序蓝图对齐字段命名。建议将数值说明书中的字段名改为 'daily_affection_experience' 并明确其含义为“当日已获得的好感度经验值”，或与程序蓝图统一为 'daily_affection_experience_cap' 并明确其含义为“每日好感度经验上限”。
### Issue 2
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> economy_commerce -> daily_affection_experience_cap
- 问题描述: 数值配表中 'daily_affection_experience_cap' 的里程碑配置为所有好感度阶段（0-4）都固定为100。但策划案中并未明确每日好感度经验上限是否与好感度阶段挂钩，且此配置与数值说明书中的字段名 'daily_affection_experience_cap' 对应，但程序蓝图中的字段名为 'daily_affection_experience'。这导致逻辑不一致。
- 修改建议: 请确认每日好感度经验上限是否应该随好感度阶段变化。如果固定为100，请确保与程序蓝图中的字段名和含义一致。如果应该变化，请提供正确的里程碑配置。
### Issue 3
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> behavior_scheduling -> active_item_id
- 问题描述: 数值配表中 'active_item_id' 的里程碑配置为 '0': 0, '1': 301, '2': 302, '3': 303。但策划案中道具效果持续1个时段，且道具触发行为优先级低于好感度行为。此配置似乎将道具ID与好感度阶段绑定，而非与道具使用行为本身绑定，这与策划案逻辑不符。
- 修改建议: 请重新设计 'active_item_id' 的配置逻辑。它应该是一个动态值，由道具使用行为触发，而非由好感度阶段决定。建议将其从离散里程碑中移除，改为由后端逻辑根据道具使用结果动态设置。
### Issue 4
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> economy_commerce -> purchased_item_ids
- 问题描述: 数值配表中 'purchased_item_ids' 的里程碑配置为 '0': '[]', '1': '[301]', '2': '[301,302]', '3': '[301,302,303]'。此配置将已购买道具列表与好感度阶段绑定，但策划案中道具购买是玩家主动行为，不应受好感度阶段限制。这会导致玩家在低好感度阶段无法购买高级道具，与策划案设计相悖。
- 修改建议: 请移除 'purchased_item_ids' 与好感度阶段的绑定。已购买道具列表应是一个动态累积的列表，由玩家购买行为决定，而非由里程碑配置决定。
### Issue 5
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> system_data_linkage -> owned_character_ids
- 问题描述: 数值配表中 'owned_character_ids' 的里程碑配置为 '0': '[]', '1': '[1]', '2': '[1,2]', '3': '[1,2,3]'。此配置将已拥有角色列表与好感度阶段绑定，但策划案中角色拥有是独立于宿舍系统的，玩家通过抽卡或其他方式获得角色。此配置与策划案逻辑严重冲突。
- 修改建议: 请移除 'owned_character_ids' 与好感度阶段的绑定。已拥有角色列表应由角色系统管理，宿舍系统仅读取该列表。
### Issue 6
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> system_data_linkage -> owned_skin_ids
- 问题描述: 数值配表中 'owned_skin_ids' 的里程碑配置为 '0': '[]', '1': '[101]', '2': '[101,102]', '3': '[101,102,103]'。此配置将已拥有皮肤列表与好感度阶段绑定，但策划案中皮肤拥有是独立于宿舍系统的，玩家通过购买或活动获得。此配置与策划案逻辑严重冲突。
- 修改建议: 请移除 'owned_skin_ids' 与好感度阶段的绑定。已拥有皮肤列表应由皮肤系统管理，宿舍系统仅读取该列表。
### Issue 7
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones -> system_data_linkage -> special_behavior_skin_requirements
- 问题描述: 数值配表中 'special_behavior_skin_requirements' 的里程碑配置为 '0': '{}', '1': '{"201":101}', '2': '{"201":101,"202":102}'。此配置将特殊行为的皮肤要求与好感度阶段绑定，但策划案中特殊行为的皮肤要求是固定的（如换衣行为需要睡衣皮肤），不应随好感度阶段变化。
- 修改建议: 请移除 'special_behavior_skin_requirements' 与好感度阶段的绑定。皮肤要求应是一个静态映射表，由策划案直接定义，而非由里程碑配置决定。
### Issue 8
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> current_behavior_id
- 问题描述: 数值配表中 'current_behavior_id' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着行为ID会随时间线性增长，但策划案中行为ID是离散的，由行为池随机选择，不应随时间线性变化。此公式逻辑错误。
- 修改建议: 请移除 'current_behavior_id' 的连续公式。行为ID应由后端逻辑根据行为池权重随机选择，而非由公式计算。
### Issue 9
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> behavior_start_time
- 问题描述: 数值配表中 'behavior_start_time' 的连续公式为 'base': 0, 'growth': 3600, 'type': 'linear'。此公式意味着行为开始时间会线性增长，但策划案中行为开始时间应由行为切换逻辑动态设置，不应由公式计算。
- 修改建议: 请移除 'behavior_start_time' 的连续公式。行为开始时间应由后端逻辑在行为切换时动态记录。
### Issue 10
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> behavior_end_time
- 问题描述: 数值配表中 'behavior_end_time' 的连续公式为 'base': 7200, 'growth': 3600, 'type': 'linear'。此公式意味着行为结束时间会线性增长，但策划案中行为结束时间应由行为切换逻辑动态设置，不应由公式计算。
- 修改建议: 请移除 'behavior_end_time' 的连续公式。行为结束时间应由后端逻辑在行为切换时动态记录。
### Issue 11
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> affection_stage
- 问题描述: 数值配表中 'affection_stage' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着好感度阶段会随时间线性增长，但策划案中好感度阶段由好感度经验值决定，不应随时间线性变化。此公式逻辑错误。
- 修改建议: 请移除 'affection_stage' 的连续公式。好感度阶段应由后端逻辑根据好感度经验值和阶段阈值判断后更新。
### Issue 12
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> behavior_pool_id
- 问题描述: 数值配表中 'behavior_pool_id' 的连续公式为 'base': 1, 'growth': 1, 'type': 'linear'。此公式意味着行为池ID会随时间线性增长，但策划案中行为池ID由游戏内时段决定，不应随时间线性变化。此公式逻辑错误。
- 修改建议: 请移除 'behavior_pool_id' 的连续公式。行为池ID应由后端逻辑根据当前游戏内时段动态设置。
### Issue 13
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> behavior_scheduling -> item_effect_end_time
- 问题描述: 数值配表中 'item_effect_end_time' 的连续公式为 'base': 0, 'growth': 7200, 'type': 'linear'。此公式意味着道具效果结束时间会线性增长，但策划案中道具效果持续1个时段，结束时间应由道具使用逻辑动态计算，不应由公式计算。
- 修改建议: 请移除 'item_effect_end_time' 的连续公式。道具效果结束时间应由后端逻辑在道具使用时动态计算并设置。
### Issue 14
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> interaction_feedback -> affection_experience
- 问题描述: 数值配表中 'interaction_feedback' 下的 'affection_experience' 连续公式为 'base': 0, 'growth': 5, 'type': 'linear'。此公式意味着每次互动好感度经验增长5点，但策划案中互动增加的好感度经验应由数值策划定义，且可能因互动类型而异。此公式过于简化，且与 'economy_commerce' 下的 'affection_experience' 公式（growth: 10）冲突。
- 修改建议: 请统一并明确不同互动类型（打招呼、送礼物、触摸）增加的好感度经验值，并移除这些连续公式，改为在离散里程碑或配置表中定义。
### Issue 15
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> interaction_feedback -> touch_region
- 问题描述: 数值配表中 'touch_region' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着触摸部位ID会线性增长，但策划案中触摸部位由玩家点击决定，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'touch_region' 的连续公式。触摸部位应由客户端根据玩家点击位置确定，并传递给服务端。
### Issue 16
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> interaction_feedback -> touch_reaction_id
- 问题描述: 数值配表中 'touch_reaction_id' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着触摸反应ID会线性增长，但策划案中触摸反应由触摸部位和角色状态决定，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'touch_reaction_id' 的连续公式。触摸反应应由后端逻辑根据触摸部位和角色好感度阶段动态决定。
### Issue 17
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> interaction_feedback -> random_event_id
- 问题描述: 数值配表中 'random_event_id' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着随机事件ID会线性增长，但策划案中随机事件由概率触发，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'random_event_id' 的连续公式。随机事件应由后端逻辑根据概率和当前时段的事件池随机选择。
### Issue 18
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> affection_stage_unlock -> affection_experience
- 问题描述: 数值配表中 'affection_stage_unlock' 下的 'affection_experience' 连续公式为 'base': 0, 'growth': 10, 'type': 'linear'。此公式与 'interaction_feedback' 和 'economy_commerce' 下的 'affection_experience' 公式冲突，且含义不明。好感度经验值不应由多个公式同时定义。
- 修改建议: 请移除所有 'affection_experience' 的连续公式。好感度经验值应是一个由互动行为动态累积的数值，其增长规则应在离散里程碑或配置表中定义。
### Issue 19
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> scene_camera_display -> current_camera_id
- 问题描述: 数值配表中 'current_camera_id' 的连续公式为 'base': 1, 'growth': 1, 'type': 'linear'。此公式意味着视角ID会线性增长，但策划案中视角由玩家切换决定，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'current_camera_id' 的连续公式。视角ID应由客户端根据玩家操作确定，并记录在本地或服务端。
### Issue 20
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> economy_commerce -> dormitory_coin_balance
- 问题描述: 数值配表中 'dormitory_coin_balance' 的连续公式为 'base': 0, 'growth': 50, 'type': 'linear'。此公式意味着宿舍币余额会线性增长，但策划案中宿舍币通过签到、任务等途径获得，不应随时间线性增长。此公式逻辑错误。
- 修改建议: 请移除 'dormitory_coin_balance' 的连续公式。宿舍币余额应由后端逻辑根据玩家行为（签到、任务、购买）动态更新。
### Issue 21
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> economy_commerce -> limited_item_ticket_balance
- 问题描述: 数值配表中 'limited_item_ticket_balance' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着限定道具券余额会线性增长，但策划案中限定道具券通过抽卡副产物、礼包获得，不应随时间线性增长。此公式逻辑错误。
- 修改建议: 请移除 'limited_item_ticket_balance' 的连续公式。限定道具券余额应由后端逻辑根据玩家行为（抽卡、购买礼包）动态更新。
### Issue 22
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> system_data_linkage -> current_character_id
- 问题描述: 数值配表中 'current_character_id' 的连续公式为 'base': 1, 'growth': 1, 'type': 'linear'。此公式意味着当前角色ID会线性增长，但策划案中当前角色由玩家切换决定，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'current_character_id' 的连续公式。当前角色ID应由玩家切换操作决定，并记录在服务端。
### Issue 23
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> system_data_linkage -> current_skin_id
- 问题描述: 数值配表中 'current_skin_id' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着当前皮肤ID会线性增长，但策划案中当前皮肤由玩家切换决定，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'current_skin_id' 的连续公式。当前皮肤ID应由玩家切换操作决定，并记录在服务端。
### Issue 24
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas -> system_data_linkage -> backpack_item_ids
- 问题描述: 数值配表中 'backpack_item_ids' 的连续公式为 'base': 0, 'growth': 1, 'type': 'linear'。此公式意味着背包道具ID列表会线性增长，但策划案中背包道具通过购买、使用等行为动态变化，不应由公式计算。此公式逻辑错误。
- 修改建议: 请移除 'backpack_item_ids' 的连续公式。背包道具ID列表应由后端逻辑根据玩家行为（购买、使用、获得）动态更新。
### Issue 25
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 -> 2.1 行为种类编排
- 问题描述: 策划案中提到“道具触发行为优先级高于基础行为，但低于好感度行为”，但未明确当道具效果与好感度行为同时存在时的具体表现逻辑。例如，高好感度角色使用道具后，是执行道具行为还是好感度行为？这会导致程序实现歧义。
- 修改建议: 请明确当道具效果与好感度行为同时存在时的优先级和表现逻辑。例如，是否高好感度行为完全覆盖道具行为，还是两者可以叠加？
### Issue 26
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 -> 2.2 交互与反馈
- 问题描述: 策划案中提到“触摸互动仅在高好感阶段解锁”，但未明确触摸互动具体包含哪些操作（如点击、长按、滑动），以及不同操作对应的反馈。这会导致程序实现和数值配置不完整。
- 修改建议: 请详细定义触摸互动的具体操作方式（点击、长按、滑动等），以及每种操作在不同好感度阶段和触摸区域对应的反馈。
### Issue 27
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 三、表现层与角色展示联动（核心强制项）
- 问题描述: 策划案中提到“严禁点击敏感部位（胸部、臀部、大腿内侧）”，但未定义“敏感部位”的具体碰撞体区域和检测逻辑。这会导致程序实现时边界模糊，可能引发合规风险。
- 修改建议: 请与美术和程序团队共同定义“敏感部位”的具体碰撞体区域，并明确点击这些区域时的检测逻辑和反馈机制。
### Issue 28
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) -> 3.1 持久化数据 (DB)
- 问题描述: 程序蓝图中的持久化数据表缺少 'behavior_pool_id'、'unlocked_behavior_ids'、'random_event_pool_ids'、'special_behavior_ids'、'special_behavior_skin_requirements' 等字段，但这些字段在数值说明书和策划案中均有提及。这会导致数据不完整，影响离线行为推进和功能实现。
- 修改建议: 请在持久化数据表中补充缺失的字段，确保与数值说明书和策划案中的数据需求一致。
### Issue 29
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 核心通信接口
- 问题描述: 程序蓝图中的 'PerformInteraction' 接口返回参数缺少 'new_unlocked_random_event_ids'，但策划案中互动可能解锁新的随机事件。这会导致客户端无法获取最新的随机事件池。
- 修改建议: 请在 'PerformInteraction' 接口的返回参数中增加 'new_unlocked_random_event_ids' 字段，用于同步解锁的随机事件。
### Issue 30
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) -> 4.1 核心通信接口
- 问题描述: 程序蓝图中的 'SwitchCharacter' 接口返回参数中包含了 'new_affection_stage' 和 'new_affection_experience'，但切换角色不应改变好感度数据。这会导致数据错误。
- 修改建议: 请移除 'SwitchCharacter' 接口返回参数中的 'new_affection_stage' 和 'new_affection_experience'。切换角色时，好感度数据应保持不变。
### Issue 31
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 -> 5.1 配置表读取
- 问题描述: 程序蓝图中的配置表读取列表缺少 'interaction_option_ids' 的解锁配置，但策划案中互动选项随好感度阶段解锁。这会导致客户端无法正确显示互动选项。
- 修改建议: 请在配置表读取列表中增加 'interaction_option_ids' 的解锁配置，确保客户端能根据好感度阶段动态显示互动选项。
**当前审查总计问题:** 31 个

--- 审查时间: 2026-05-29 12:34:15 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.daily_affection_experience_cap
- 问题描述: 数值说明书中 `daily_affection_experience_cap` 的默认值为 100，但系统策划案中明确写明每日好感度经验上限为 200 点。
- 修改建议: 请将 `daily_affection_experience_cap` 的默认值修改为 200，以与策划案保持一致。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.affection_stage
- 问题描述: 数值说明书中 `affection_stage` 的取值范围描述为 '0-4'，但策划案中好感度阶段为 5 个阶段（陌生、熟悉、友好、亲密、爱慕），对应 0-4 是正确的。然而，数值配表中 `affection_stage_unlock` 的 `unlocked_behavior_ids` 等配置使用了 0-4 的 key，但策划案中好感度经验阈值是 [0, 100, 300, 600, 1000, 1500]，这意味着阶段 0 对应经验 0-100，阶段 1 对应 101-300，阶段 2 对应 301-600，阶段 3 对应 601-1000，阶段 4 对应 1001-1500。数值说明书中缺少对阶段阈值（affection_stage_thresholds）的明确定义，仅在程序蓝图中提及。
- 修改建议: 请在数值说明书的 `field_dictionary` 或 `relations_and_enums` 中增加 `affection_stage_thresholds` 字段，明确各阶段对应的经验值阈值范围，例如：`[0, 100, 300, 600, 1000, 1500]`。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.touch_region
- 问题描述: 数值说明书中 `touch_region` 的取值范围为 `['head', 'hand', 'shoulder', 'invalid']`，其中 'invalid' 代表敏感部位。但策划案中定义的敏感部位碰撞体包括胸部、臀部、大腿内侧、裆部，这些部位在点击后应触发警告反馈，而 'invalid' 这个枚举值过于笼统，无法区分具体是哪个敏感部位被点击，不利于后续的日志记录和数据分析。
- 修改建议: 请将 `touch_region` 的枚举值扩展，增加 `['chest', 'buttock', 'inner_thigh', 'crotch']` 等具体敏感部位，或将 'invalid' 替换为一个更细粒度的枚举或数组字段，以记录具体被点击的敏感部位。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.unlocked_touch_regions
- 问题描述: 数值说明书中 `unlocked_touch_regions` 的默认值为空数组，但策划案中明确提到在陌生/熟悉阶段，玩家可以触摸头部、手部、肩膀（友好/亲密/爱慕阶段逐步解锁）。数值配表中 `interaction_feedback.unlocked_touch_regions` 的配置也正确反映了这一点。然而，数值说明书的 `field_dictionary` 中缺少对 `unlocked_touch_regions` 与好感度阶段之间映射关系的明确说明。
- 修改建议: 请在数值说明书的 `relations_and_enums` 或 `field_dictionary` 中，增加对 `unlocked_touch_regions` 与 `affection_stage` 之间映射关系的描述，例如：'阶段0-1：[]，阶段2：['head']，阶段3：['head', 'hand']，阶段4：['head', 'hand', 'shoulder']'。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.interaction_option_ids
- 问题描述: 数值说明书中缺少对 `interaction_option_ids` 字段的定义，但该字段在数值配表 `interaction_feedback` 中被引用，且策划案中明确提到了不同好感度阶段下互动选项菜单的内容（打招呼、送礼物、触摸、拥抱、离开）。
- 修改建议: 请在数值说明书的 `field_dictionary` 中增加 `interaction_option_ids` 字段的定义，描述其数据类型、取值范围和默认值。
### Issue 6
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.random_event_pool_ids
- 问题描述: 数值说明书中缺少对 `random_event_pool_ids` 字段的定义，但该字段在数值配表 `interaction_feedback` 中被引用，且策划案中提到了每个时段有随机事件池。
- 修改建议: 请在数值说明书的 `field_dictionary` 中增加 `random_event_pool_ids` 字段的定义，描述其数据类型、取值范围和默认值。
### Issue 7
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.special_behavior_skin_requirements
- 问题描述: 数值说明书中定义了 `special_behavior_skin_requirements` 字段，但数值配表中 `system_data_linkage.special_behavior_skin_requirements` 的值为空对象 `{}`。策划案中提到部分特殊行为（如“换衣”）需特定皮肤触发，但数值配表中没有提供任何具体的映射关系示例，导致该配置形同虚设。
- 修改建议: 请根据策划案，在数值配表中为 `special_behavior_skin_requirements` 添加至少一个示例映射，例如：`{'101': 'skin_001'}`，表示行为ID 101 需要皮肤ID skin_001。
### Issue 8
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.behavior_pool_weights
- 问题描述: 数值说明书中定义了 `behavior_pool_weights` 字段，但数值配表中 `behavior_scheduling.behavior_pool_weights` 的所有时段对应的权重映射均为空对象 `{}`。策划案中提到行为池包含多个行为，且系统会随机选取一个播放，但权重配置为空意味着无法进行随机选取，系统将无法正常工作。
- 修改建议: 请根据策划案，为每个时段的行为池填充具体的权重映射，例如：`{'1': 10, '2': 20, '3': 15}`，表示行为ID 1的权重为10，行为ID 2的权重为20，行为ID 3的权重为15。
### Issue 9
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.unlocked_behavior_ids
- 问题描述: 数值说明书中定义了 `unlocked_behavior_ids` 字段，但数值配表中 `behavior_scheduling.unlocked_behavior_ids` 和 `affection_stage_unlock.unlocked_behavior_ids` 的配置完全一致。这导致了数据冗余，且如果后续需要修改解锁行为，需要同时修改两处，增加了维护成本和出错风险。
- 修改建议: 请考虑将 `unlocked_behavior_ids` 的配置统一到 `affection_stage_unlock` 下，并在 `behavior_scheduling` 中通过外键引用，避免数据冗余。
### Issue 10
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.current_behavior_id
- 问题描述: 数值说明书中 `current_behavior_id` 的默认值为 0，但数值配表中 `behavior_scheduling.current_behavior_id` 的 base 值也为 0。策划案中提到默认行为ID为0表示无行为，但未明确说明在无行为时角色应如何表现（例如，是静止站立还是播放一个默认的待机动画）。
- 修改建议: 请与系统策划确认，当 `current_behavior_id` 为 0 时，角色应播放何种默认行为或动画，并在数值说明书中补充说明。
### Issue 11
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的 `ReportInteraction` API 请求参数包含 `touch_region`，但策划案中触摸反馈的检测逻辑是先检测敏感部位，再检测可交互部位。如果客户端直接上报 `touch_region`，服务端将无法进行独立的二次校验，因为客户端可能伪造 `touch_region` 的值。
- 修改建议: 请修改 `ReportInteraction` API 的请求参数，将 `touch_region` 替换为原始的点击坐标 `click_position_x` 和 `click_position_y`，让服务端根据角色骨骼位置进行独立的射线检测，以确定实际触摸的部位。
### Issue 12
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 3.2 核心校验逻辑
- 问题描述: 程序蓝图中的 `ReportSensitiveTouch` API 用于上报敏感部位点击，但策划案中敏感部位点击的检测逻辑是：客户端射线检测命中敏感部位后，立即播放警告反馈，并上报坐标给服务端进行二次校验。这意味着客户端已经处理了敏感部位点击，服务端的二次校验主要用于防作弊和封禁。然而，`ReportSensitiveTouch` API 的返回参数中包含 `is_sensitive`，如果服务端二次校验发现不是敏感部位，客户端已经播放的警告反馈将无法撤回，导致体验不一致。
- 修改建议: 建议修改流程：客户端点击后，先不上报，而是等待服务端二次校验结果。如果服务端确认是敏感部位，客户端再播放警告反馈。或者，客户端先播放一个短暂的、可被打断的预备反馈（如角色身体微颤），待服务端确认后再播放完整的警告反馈。
### Issue 13
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 程序蓝图中的 `SwitchCharacter` API 返回参数包含 `unlocked_behavior_ids`、`unlocked_touch_regions`、`interaction_option_ids`，这些数据是客户端初始化角色状态所必需的。但策划案中，这些数据是由好感度阶段决定的，而好感度阶段数据已经在 `user_dormitory_character` 表中。服务端在返回 `SwitchCharacter` 响应时，应该根据当前角色的好感度阶段，从配置表中查询并返回这些数据，而不是让客户端自行计算。
- 修改建议: 请确保 `SwitchCharacter` API 的后端逻辑正确地从配置表中查询并返回与当前好感度阶段对应的 `unlocked_behavior_ids`、`unlocked_touch_regions` 和 `interaction_option_ids`。
### Issue 14
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载 - 5.1 配置表读取
- 问题描述: 程序蓝图中的 `affection_stage_thresholds` 数组为 `[0, 100, 300, 600, 1000, 1500]`，但策划案中好感度阶段阈值为：陌生 (0-100)、熟悉 (101-300)、友好 (301-600)、亲密 (601-1000)、爱慕 (1001-1500)。程序蓝图中的阈值数组有 6 个元素，对应 5 个阶段（0-4），但策划案中阶段 0 的上限是 100，阶段 1 的上限是 300，以此类推。程序蓝图中的阈值数组 `[0, 100, 300, 600, 1000, 1500]` 是正确的，但需要确保计算逻辑正确地将经验值映射到阶段。例如，经验值 100 应属于阶段 0，经验值 101 应属于阶段 1。
- 修改建议: 请在程序蓝图中明确 `affection_stage` 的计算逻辑，例如：'遍历阈值数组，找到第一个大于当前经验值的阈值，其索引减1即为当前阶段'，并确保边界值（如经验值恰好等于阈值）的处理与策划案一致。
### Issue 15
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载 - 5.2 配置表读取流程
- 问题描述: 程序蓝图中的 `sensitive_area_collider_config` 配置按角色体型（萝莉/御姐）定义球心偏移和半径，但数值说明书和数值配表中均未提供任何关于角色体型差异的配置数据。这会导致程序无法实现该功能。
- 修改建议: 请与数值策划和美术沟通，在数值配表中增加 `sensitive_area_collider_config` 配置，按角色体型（或按角色ID）定义敏感部位碰撞体的球心偏移和半径。
### Issue 16
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 四、 经济循环与商业化埋点
- 问题描述: 策划案中每日好感度经验上限为 200 点，但数值说明书中 `daily_affection_experience_cap` 的默认值为 100，两者不一致。
- 修改建议: 请确认每日好感度经验上限的正确值，并确保数值说明书和程序蓝图中的配置与之同步。
### Issue 17
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 三、 表现层与角色展示联动（核心强制项） - 擦边互动设计 - 敏感部位碰撞体定义与检测逻辑
- 问题描述: 策划案中定义了敏感部位碰撞体的半径（如胸部半径 0.15 米），但未说明这些半径值是否因角色体型（萝莉 vs 御姐）而有所不同。程序蓝图提到了按体型配置，但策划案中未明确。
- 修改建议: 请明确敏感部位碰撞体的半径是否因角色体型而异，如果是，请提供不同体型对应的半径值或配置规则。
### Issue 18
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、 核心规则与玩法机制 - 2.1 行为种类编排（混合型）
- 问题描述: 策划案中提到“系统每 2 小时（现实时间）自动切换时段”，但未说明游戏内时间与现实时间的换算关系。例如，游戏内 1 小时等于现实时间多少秒？这会影响行为切换和时段提示的实现。
- 修改建议: 请明确游戏内时间与现实时间的换算比例，例如：'游戏内 1 小时 = 现实时间 10 分钟'，或直接说明时段切换的触发机制（如：每 2 小时现实时间切换一次）。
### Issue 19
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、 核心规则与玩法机制 - 2.2 交互与反馈 - 主动触发
- 问题描述: 策划案中互动选项菜单的内容在不同好感度阶段有所不同，但未明确每个选项对应的具体动画、语音和表情反馈。例如，'打招呼'在陌生阶段和爱慕阶段的反馈是否相同？
- 修改建议: 请为每个互动选项在不同好感度阶段下的反馈（动画、语音、表情）提供更详细的描述或配置表，以便数值策划和程序进行实现。
### Issue 20
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、 核心规则与玩法机制 - 2.1 行为种类编排（混合型） - 道具触发层
- 问题描述: 策划案中提到道具触发行为会“打断当前行为”，但未说明如果当前行为是随机事件，道具触发行为是否也会打断随机事件。
- 修改建议: 请明确道具触发行为与随机事件之间的优先级关系，例如：'道具触发行为优先级高于随机事件，可以打断随机事件播放'。
### Issue 21
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 五、 旧系统与数据联动（强依赖）
- 问题描述: 策划案中提到了与角色系统、好感度系统、皮肤系统、背包/道具系统的联动，但未说明与任务系统或成就系统的联动。例如，是否可以通过完成宿舍相关任务获得奖励？
- 修改建议: 请考虑是否需要在宿舍系统中增加与任务/成就系统的联动，以增加玩家的目标感和留存率。
**当前审查总计问题:** 21 个

--- 审查时间: 2026-05-29 12:44:04 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.1.2 好感度行为层（好感度驱动）
- 问题描述: 策划案中描述好感度阶段为5阶段：陌生(0-100)、熟悉(101-300)、友好(301-600)、亲密(601-1000)、爱慕(1001-2000)，但数值说明书和数值配表中爱慕阶段的上限为1500（1001-1500），与策划案中的2000不一致。
- 修改建议: 请确认好感度阶段爱慕阶段的正确上限值，并统一策划案与数值文档中的阈值范围。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.2.3 随机事件
- 问题描述: 策划案中描述随机事件触发概率为基础15%，好感度每阶段+5%，最高35%（爱慕阶段）。但程序蓝图中写的是触发概率10%，冷却时间30分钟，与策划案数值不一致。
- 修改建议: 请确认随机事件触发概率的正确数值，并同步更新程序蓝图中的配置。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.1.1 基础行为层（时间驱动）
- 问题描述: 策划案中描述每现实30分钟=游戏内1小时，每天划分为5个时段。但程序蓝图中写的是每2小时现实时间切换一次时段，与策划案的30分钟换算不一致。
- 修改建议: 请确认时段切换的现实时间间隔，并统一策划案与程序蓝图中的描述。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 一、系统概述与设计愿景 / 1.1 系统定位
- 问题描述: 策划案中描述宿舍解锁条件为主线进度达到第2章，但程序蓝图中写的是玩家等级≥5。两个条件不一致。
- 修改建议: 请确认宿舍系统的解锁条件，并统一策划案与程序蓝图中的描述。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / affection_stage
- 问题描述: 数值说明书中好感度阶段枚举值中爱慕阶段经验范围为1001-1500，但策划案中为1001-2000，数值配表中continuous_formulas的affection_experience growth为10，未明确阶段阈值数组。
- 修改建议: 请确认爱慕阶段的正确经验上限，并确保数值配表中的阈值数组与策划案一致。
### Issue 6
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary / touch_region
- 问题描述: 数值说明书中touch_region枚举包含敏感部位（胸部、臀部、大腿内侧、裆部），但策划案中明确禁止点击这些部位，且程序蓝图中的敏感部位碰撞体检测使用了默认值，未提供按角色体型区分的配置。
- 修改建议: 请补充按角色体型区分的敏感部位碰撞体配置数据，或明确所有角色使用统一默认值。
### Issue 7
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones / interaction_feedback / unlocked_touch_regions
- 问题描述: 数值配表中unlocked_touch_regions在阶段2、3、4均为[1,2,3]（头、手、肩膀），但策划案中阶段2（友好）解锁触摸（头/手），阶段3（亲密）解锁触摸（头/手/肩膀），阶段4（爱慕）解锁触摸（头/手/肩膀），与策划案不一致。
- 修改建议: 请根据策划案的好感度阶段解锁表调整unlocked_touch_regions：阶段2应为[1,2]，阶段3和4应为[1,2,3]。
### Issue 8
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: discrete_milestones / interaction_feedback / interaction_option_ids
- 问题描述: 数值配表中interaction_option_ids在阶段0和1均为[1,2,3]，阶段2和3为[1,2,3,4]，阶段4为[1,2,3,4,5]。但策划案中阶段0和1只有打招呼、送礼物、离开（3个选项），阶段2有打招呼、送礼物、触摸（头/手）、离开（4个选项），阶段3和4有打招呼、送礼物、触摸（头/手/肩膀）、拥抱、离开（5个选项），与策划案不一致。
- 修改建议: 请根据策划案调整interaction_option_ids：阶段0和1应为[1,2,3]，阶段2应为[1,2,3,4]，阶段3和4应为[1,2,3,4,5]。
### Issue 9
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 / 5.1 配置表读取流程
- 问题描述: 程序蓝图中读取好感度经验阈值数组为[0, 100, 300, 600, 1000, 1500]，但策划案中爱慕阶段上限为2000，数值说明书中为1500，存在不一致。
- 修改建议: 请确认正确的阈值数组，并确保程序蓝图与数值文档一致。
### Issue 10
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 / 5.1 配置表读取流程
- 问题描述: 程序蓝图中读取随机事件触发概率为10%，但策划案中为基础15%+好感度加成，最高35%。
- 修改建议: 请确认随机事件触发概率的正确数值，并更新程序蓝图中的配置。
### Issue 11
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 / 5.1 配置表读取流程
- 问题描述: 程序蓝图中读取时段切换间隔为2小时现实时间，但策划案中为每现实30分钟=游戏内1小时，每天5个时段，换算后时段切换间隔应为现实2.4小时（144分钟），与2小时不一致。
- 修改建议: 请确认时段切换的现实时间间隔，并更新程序蓝图中的描述。
### Issue 12
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 一、整体架构概述
- 问题描述: 程序蓝图中主入口组件检测玩家等级≥5且拥有角色，但策划案中解锁条件为主线进度达到第2章。
- 修改建议: 请确认宿舍系统的解锁条件，并统一程序蓝图与策划案中的描述。
### Issue 13
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) / 核心校验逻辑
- 问题描述: 程序蓝图中敏感部位点击校验提到若检测到异常点击坐标，踢出宿舍并封禁账号。但策划案中仅提示“请不要这样”，没有封禁逻辑。
- 修改建议: 请确认敏感部位点击的惩罚机制，并统一程序蓝图与策划案中的描述。
### Issue 14
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 六、开发优先级与依赖链路 / 阶段三 (P2 - 表现层打磨)
- 问题描述: 程序蓝图中敏感部位连续点击3次锁定交互10秒，但策划案中为拒绝互动5分钟。
- 修改建议: 请确认敏感部位连续点击的锁定时间，并统一程序蓝图与策划案中的描述。
**当前审查总计问题:** 14 个

--- 审查时间: 2026-05-29 12:50:53 ---
### Issue 1
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 二、核心规则与玩法机制 > 2.2.2 主动触发
- 问题描述: 策划案中描述互动冷却时间为30秒，但在程序蓝图后端逻辑中提及了“敏感部位连续点击3次后锁定交互5分钟”的机制，该机制在策划案中未定义。
- 修改建议: 请在策划案中明确是否增加“敏感部位连续点击3次后锁定交互5分钟”的规则，或确认该机制为程序蓝图中的额外设计，并补充到策划案中。
### Issue 2
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones > interaction_feedback > interaction_option_ids
- 问题描述: 数值配表中，好感度阶段0和1的互动选项ID列表为[1,2,3]，但策划案中阶段0（陌生）仅解锁“打招呼”，阶段1（熟悉）解锁“打招呼、送礼物”。配表未区分阶段0和1的选项差异，且缺少“离开”选项的对应关系。
- 修改建议: 请根据策划案中的好感度阶段解锁表，调整数值配表中阶段0和1的interaction_option_ids，确保阶段0仅包含“打招呼”对应的ID，阶段1包含“打招呼”和“送礼物”对应的ID，并明确“离开”选项的ID归属。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones > interaction_feedback > random_event_pool_ids
- 问题描述: 数值配表中，所有好感度阶段的random_event_pool_ids均为空数组，但策划案中阶段1（熟悉）解锁了随机事件“打翻杯子”，阶段2（友好）解锁了“哼歌、对着镜子整理头发”等事件。配表未配置任何随机事件池。
- 修改建议: 请根据策划案中的好感度阶段解锁表，为阶段1、2、3、4配置对应的随机事件池ID列表，并确保事件池ID与随机事件配置表关联。
### Issue 4
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones > affection_stage_unlock > unlocked_behavior_ids
- 问题描述: 数值配表中，affection_stage_unlock模块的unlocked_behavior_ids在所有阶段均为空数组，但策划案中每个好感度阶段都有对应的解锁行为示例（如阶段0解锁看书、玩手机等）。配表未配置任何行为ID。
- 修改建议: 请根据策划案中的好感度阶段解锁表，为每个阶段配置对应的行为ID列表，并确保行为ID与行为配置表关联。
### Issue 5
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones > behavior_scheduling > behavior_pool_weights
- 问题描述: 数值配表中，behavior_pool_weights在所有时段均为空对象，但策划案中每个时段对应一个行为池（包含3-5个行为），且行为池中行为有权重。配表未配置任何权重映射。
- 修改建议: 请根据策划案中的时段行为池设计，为每个时段配置行为池ID对应的权重映射，例如{行为ID: 权重值}。
### Issue 6
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、 前后端通信协议 (API & 数据对接) > TriggerRandomEvent
- 问题描述: 程序蓝图中的TriggerRandomEvent API由客户端主动调用，但策划案中随机事件是“每个时段开始时，系统根据概率表判定是否触发”，即由服务端或客户端定时器驱动，而非玩家主动触发。API设计不符合策划案逻辑。
- 修改建议: 请将随机事件触发逻辑改为服务端定时触发（如时段切换时），或由客户端时段管理器在时段开始时自动请求服务端判定，而非提供玩家可调用的API。
### Issue 7
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 三、 后端逻辑划分 (Server) > 核心校验逻辑
- 问题描述: 程序蓝图后端逻辑中提到了“敏感部位连续点击3次后锁定交互5分钟”的机制，但策划案中仅定义了触摸冷却时间为10秒，未提及此防滥用规则。该机制在策划案中无依据。
- 修改建议: 请确认该机制是否为程序蓝图中的额外设计，若是，需与策划对齐并补充到策划案中；若不是，请移除该逻辑，仅保留策划案中定义的10秒触摸冷却。
### Issue 8
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 二、核心规则与玩法机制 > 2.1.3 道具触发层
- 问题描述: 策划案中描述道具效果持续时间为“当前时段剩余时间”，但未定义当道具在时段切换时是否强制结束。数值说明书中item_effect_end_time为浮点数，但未明确时段切换时是否重置。
- 修改建议: 请明确道具效果在时段切换时的处理逻辑：是强制结束还是持续到原定时长？并在策划案中补充说明。
### Issue 9
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary > interaction_option_ids
- 问题描述: 数值说明书中interaction_option_ids字段的描述提到“阶段0和1为[1,2,3]（打招呼、送礼物、离开）”，但策划案中阶段0（陌生）仅解锁“打招呼”，阶段1（熟悉）解锁“打招呼、送礼物”，与说明书描述不符。
- 修改建议: 请根据策划案修正数值说明书中interaction_option_ids的描述，确保阶段0仅包含“打招呼”对应的ID，阶段1包含“打招呼”和“送礼物”对应的ID。
### Issue 10
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary > unlocked_touch_regions
- 问题描述: 数值说明书中unlocked_touch_regions字段的描述未列出各阶段的具体值，仅说“默认值为空数组”，但策划案中明确列出了各阶段解锁的触摸区域（如阶段1解锁头，阶段2解锁头、手等）。
- 修改建议: 请根据策划案中的好感度阶段解锁表，在数值说明书中补充unlocked_touch_regions字段在各阶段的具体值列表。
### Issue 11
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary > random_event_pool_ids
- 问题描述: 数值说明书中random_event_pool_ids字段的描述未提及各阶段的具体值，仅说“默认值为空数组”，但策划案中阶段1（熟悉）解锁了随机事件“打翻杯子”，阶段2（友好）解锁了更多事件。
- 修改建议: 请根据策划案中的好感度阶段解锁表，在数值说明书中补充random_event_pool_ids字段在各阶段的具体值列表。
### Issue 12
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 五、 数值与配置表挂载 > 好感度阶段配置表 (AffectionStageConfig)
- 问题描述: 程序蓝图中好感度阶段配置表包含threshold_min和threshold_max字段，但数值配表中affection_stage_unlock模块的discrete_milestones仅定义了阶段对应的解锁列表，未定义阈值范围。配置表与配表不一致。
- 修改建议: 请确保数值配表中包含好感度阶段阈值的定义（如每个阶段的最小和最大经验值），或调整程序蓝图中的配置表结构以匹配现有配表。
**当前审查总计问题:** 12 个

--- 审查时间: 2026-05-29 15:19:44 ---
### Issue 1
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.1 好感度养成循环 - 送礼
- 问题描述: 系统案中送礼描述为“若礼物符合角色喜好标签，额外获得[GIFT_PREFERENCE_BONUS]倍经验”，但未定义“喜好标签”在数值表中的具体字段或枚举。数值表`field_dictionary`中无角色喜好标签相关字段，`discrete_milestones`中礼物ID也未关联标签。导致程序无法判断礼物是否匹配喜好。
- 修改建议: 在数值表`field_dictionary`中为礼物或角色增加喜好标签字段（如`gift_preference_tags`或`character_favorite_tags`），并在`discrete_milestones`或独立礼物表中定义每个礼物的标签，以便程序实现加成逻辑。
### Issue 2
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: continuous_formulas - affection_experience
- 问题描述: 数值配表中`affection_experience`的公式为`base + growth * (affection_level - 1)`，但系统案2.1节提到好感度等级范围为1至`[MAX_AFFECTION_LEVEL]`（10级），且每级升级所需经验由数值表定义。当前公式为线性增长，但未提供`base`和`growth`的具体数值，也未在`discrete_milestones`中给出每级阈值。程序蓝图5节引用的`EXP_THRESHOLD_LEVEL_X`数组无数据来源。
- 修改建议: 在`continuous_formulas`中补充`base`和`growth`的具体数值，或在`discrete_milestones`中为每个等级明确列出`exp_threshold`字段，确保程序能获取每级升级所需经验值。
### Issue 3
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.3 日常动作循环
- 问题描述: 系统案2.3节提到“角色当前动作状态存储在客户端本地，不同步至服务器”，但未定义断线重连后动作状态的恢复逻辑。数值表`field_dictionary`中无`current_action_state`字段，程序蓝图也未涉及客户端本地存储的持久化方案。若玩家断线，动作状态丢失，可能导致表现层不一致。
- 修改建议: 在系统案中补充断线重连后动作状态的恢复规则（如从上次状态继续或随机初始化），并在数值表`field_dictionary`中增加`current_action_state`字段（整数枚举），程序蓝图需在客户端本地存储该状态并实现恢复逻辑。
### Issue 4
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 三、后端逻辑划分 - 持久化数据
- 问题描述: 程序蓝图后端持久化字段列表包含了`skin_inventory`（整数数组），但数值表`field_dictionary`中`skin_inventory`被标注为“与owned_skins冗余，用于付费系统”。系统案5.4节图鉴系统提到“解锁的内容在图鉴系统中可回看”，但未定义`skin_inventory`与`owned_skins`的同步规则。冗余字段可能导致数据不一致。
- 修改建议: 在程序蓝图中明确`skin_inventory`与`owned_skins`的同步机制（如每次购买皮肤时同时更新两个字段），或删除冗余字段`skin_inventory`，统一使用`owned_skins`。同时，系统案需补充图鉴系统对皮肤数据的引用方式。
### Issue 5
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.6 对话
- 问题描述: 系统案2.6节提到“玩家可选择2-3个回复选项（仅表现层影响，不改变任何数值）”，但未定义回复选项的文本来源和选择后的表现层反馈细节（如角色表情变化的具体映射）。数值表`field_dictionary`中无`dialog_options`或`dialog_responses`字段，程序蓝图`TriggerDialog`接口的请求参数`dialog_option_id`无对应数据表支持。
- 修改建议: 在数值表中增加`dialog_options`表，定义每个角色的对话选项ID、文本、关联的表情和语音ID。系统案需补充回复选项与角色表情的映射规则，程序蓝图需在`TriggerDialog`接口中根据`dialog_option_id`返回对应的表现层数据。
### Issue 6
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones - affection_level 7
- 问题描述: 数值配表`discrete_milestones`中，等级7解锁了`unlocked_sensitive_areas: [6, 7]`，但系统案2.4节提到敏感区域为“耳根、腰侧”，且数值表`field_dictionary`中`unlocked_sensitive_areas`描述为“已解锁的敏感区域ID列表（耳根、腰侧）”。然而，`unlocked_touch_zones`在等级7也包含了ID 6和7，导致敏感区域与普通触摸区域ID重叠，可能引发程序逻辑冲突（如触摸区域ID 6同时属于普通和敏感区域）。
- 修改建议: 在数值表中为触摸区域ID分配独立范围（如普通区域ID 1-5，敏感区域ID 6-7），并确保`unlocked_touch_zones`在等级7时仅包含普通区域ID（1-5），敏感区域通过`unlocked_sensitive_areas`单独管理。程序蓝图需在触摸校验中区分普通和敏感区域。
### Issue 7
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 5.2 好感度数据
- 问题描述: 系统案5.2节提到“每`[AFFECTION_STAT_INTERVAL]`级（例如5级），提供微量属性加成”，但未定义具体加成数值（如暴击率`[AFFECTION_CRIT_BONUS]`、伤害`[AFFECTION_DMG_BONUS]`）。数值表`field_dictionary`和`continuous_formulas`中均无这些字段，程序蓝图5节引用的`AFFECTION_CRIT_BONUS`和`AFFECTION_DMG_BONUS`无数据来源。
- 修改建议: 在数值表`continuous_formulas`或新增`battle_bonus`节中，明确每5级提供的暴击率和伤害加成数值（如`affection_crit_bonus: 0.02`，`affection_dmg_bonus: 0.05`），并补充到`field_dictionary`中。
**当前审查总计问题:** 7 个

--- 审查时间: 2026-05-29 15:23:05 ---
### Issue 1
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 二、核心规则与玩法机制 - 2.1.3 对话
- 问题描述: 系统策划案中对话的【前置条件】为“每日首次进入宿舍”，但【流转逻辑】中又提到玩家选择回复后更新心情状态，且【边界与异常兜底】提到30秒后自动选择默认选项。这导致逻辑死胡同：如果对话仅在每日首次进入时触发一次，那么后续进入宿舍时是否还能触发对话？如果只能触发一次，则【每日对话次数上限 DAILY_DIALOG_LIMIT】与【DAILY_DIALOG_COUNT】的计数逻辑与“仅首次触发”矛盾。
- 修改建议: 请明确每日对话的触发机制：是每日首次进入宿舍时触发一次，还是每次进入宿舍都可触发一次（但有每日次数上限）？如果是前者，请删除【DAILY_DIALOG_LIMIT】和【DAILY_DIALOG_COUNT】相关描述；如果是后者，请修正【前置条件】为“玩家进入宿舍时，且当日对话次数未达上限”。
### Issue 2
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 二、核心规则与玩法机制 - 2.1.1 触摸互动
- 问题描述: 系统策划案中触摸互动的【前置条件】为“角色好感度等级至少为1”，但【流转逻辑】中又提到敏感区域（耳根、腰侧）需要【AFFECTION_LEVEL】>=【SENSITIVE_AREA_UNLOCK_LEVEL】才能解锁。然而，数值配表中敏感区域（ID 6,7）是在好感度等级7时才解锁的。这意味着在等级1-6期间，玩家触摸小腿（ID 6）和耳根（ID 7）时，系统应如何处理？系统案中仅提到“若未解锁，触发通用反馈（如角色微笑摇头）”，但未明确未解锁区域是否包含在可触摸区域列表中。
- 修改建议: 请明确在好感度等级1-6期间，小腿（ID 6）和耳根（ID 7）是否属于可触摸区域？如果是，请补充未解锁时的具体反馈逻辑；如果不是，请修正数值配表中【unlocked_touch_zones】在等级1-6时不应包含ID 6和7。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: discrete_milestones.affection_level
- 问题描述: 数值配表中【unlocked_touch_zones】在所有等级（1-10）中均为[1,2,3,4,5]，从未包含ID 6（小腿）和ID 7（耳根）。但【unlocked_sensitive_areas】在等级7-10中包含了[6,7]。根据数值说明书的【implementation_notes】第3条，程序需优先判断【unlocked_sensitive_areas】。然而，如果【unlocked_touch_zones】从未包含ID 6和7，那么玩家在等级7之前触摸小腿和耳根时，系统应如何判定？这导致了逻辑断裂：玩家在等级1-6时无法触摸小腿和耳根（因为不在【unlocked_touch_zones】中），但系统案中又提到这些是敏感区域，需要等级7才能解锁。
- 修改建议: 请修正数值配表，在等级7-10的【unlocked_touch_zones】中添加ID 6和7，以确保玩家在等级7后可以触摸这些区域，并触发敏感区域反馈。或者，如果设计意图是这些区域始终可触摸但仅在等级7后触发特殊反馈，请更新【unlocked_touch_zones】在所有等级中包含ID 6和7。
### Issue 4
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、前后端通信协议 (API & 数据对接) - EnterDormitory
- 问题描述: 程序蓝图中【EnterDormitory】API的返回参数包含【owned_characters: bitmask】，但数值说明书中的【owned_characters】字段类型为【整数数组】。根据领域裁决原则第2条，数据类型冲突以Tech Architect为准，但这里存在不一致：bitmask和整数数组是两种不同的数据结构，会导致客户端解析错误。
- 修改建议: 请统一【owned_characters】的数据类型。如果使用bitmask，请更新数值说明书中的字段类型；如果使用整数数组，请更新程序蓝图中的API返回参数。
### Issue 5
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 五、旧系统与数据联动 - 5.2 好感度数据
- 问题描述: 系统策划案中提到好感度等级每【AFFECTION_STAT_INTERVAL】级（例如5级）提供微量属性加成【AFFECTION_CRIT_BONUS】和【AFFECTION_DMG_BONUS】，并说明数值由数值策划在【numerical_design_dormitory.json】中定义。但数值配表（system_numerical_docs.json和data.json）中完全没有提供【AFFECTION_CRIT_BONUS】和【AFFECTION_DMG_BONUS】这两个字段，也没有任何与战斗属性加成相关的配置。这属于字段遗漏。
- 修改建议: 请在数值配表中添加【AFFECTION_CRIT_BONUS】和【AFFECTION_DMG_BONUS】字段，并定义每个里程碑等级（如5级、10级）对应的具体加成数值。
### Issue 6
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 四、经济循环与商业化埋点 - 4.1 免费产出
- 问题描述: 系统策划案中提到每日互动产出基础货币【BASE_CURRENCY】，并设置了每日免费产出上限【DAILY_FREE_CURRENCY_LIMIT】。但数值说明书和数值配表中均未定义【BASE_CURRENCY】和【DAILY_FREE_CURRENCY_LIMIT】这两个字段，也没有任何与基础货币产出相关的配置。这属于字段遗漏。
- 修改建议: 请在数值配表中添加【BASE_CURRENCY】和【DAILY_FREE_CURRENCY_LIMIT】字段，并定义每次互动产出的基础货币数量及每日上限。
**当前审查总计问题:** 6 个

--- 审查时间: 2026-05-29 15:25:46 ---
### Issue 1
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: [四、经济循环与商业化埋点 - 4.1 免费产出] - 失败时
- 问题描述: 系统策划案中描述了【DAILY_FREE_CURRENCY_LIMIT】作为每日基础货币获取上限，并提到触摸和送礼行为会产出【BASE_CURRENCY】。但在数值配表和程序蓝图中，完全没有定义【DAILY_FREE_CURRENCY_LIMIT】这个字段，也没有定义【BASE_CURRENCY】的产出数值（如[CURRENCY_REWARD_PER_TOUCH]、[CURRENCY_REWARD_PER_GIFT]、[CURRENCY_REWARD_PER_GREETING]）。数值配表中只定义了经验值相关的限制（DAILY_TOUCH_LIMIT、DAILY_GIFT_LIMIT），程序蓝图也只校验了触摸和送礼的次数限制，未涉及货币产出逻辑。这导致系统策划案中的经济循环逻辑在数值和程序层面完全缺失。
- 修改建议: 请系统策划与数值策划确认【DAILY_FREE_CURRENCY_LIMIT】和【BASE_CURRENCY】产出数值是否为本系统的核心设计。如果是，数值策划需在数值配表中补充这些字段和数值；如果不是，系统策划需修改文案，删除或替换为其他已定义的奖励机制（如好感度经验）。
### Issue 2
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: [四、经济循环与商业化埋点 - 4.1 免费产出] - 异常时
- 问题描述: 系统策划案中描述了断线重连后补发【BASE_CURRENCY】的逻辑，但程序蓝图的后端核心校验逻辑和API协议中，完全没有实现断线重连后的数据恢复或补发机制。程序蓝图仅在阶段三的‘边缘异常兜底’中笼统提到‘实现断线重连后的数据恢复’，但未定义具体的校验规则、补发接口或日志记录方案。这是一个逻辑死胡同，开发无法落地。
- 修改建议: 系统策划需细化断线重连补发逻辑的具体规则（如：补发依据是什么？服务器日志如何记录？补发是否有时间窗口限制？），并与主程协商后，由主程在程序蓝图中补充对应的后端校验逻辑和API接口定义。
### Issue 3
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: [四、经济循环与商业化埋点 - 4.1 免费产出] - 表现层反馈
- 问题描述: 系统策划案中描述了每日问候对话会产出【BASE_CURRENCY】并显示飘字提示，但在【数据状态变化】中，每日问候对话仅将 `player_daily_greeting_flag` 置为 `true`，并未提及增加【BASE_CURRENCY】。同时，程序蓝图中的对话校验逻辑（`[PerformDialog]`）也只更新了 `mood_state` 和 `daily_dialog_triggered`，没有涉及任何货币产出。这导致对话行为的货币产出逻辑在系统案内部自相矛盾，且与程序蓝图不一致。
- 修改建议: 系统策划需明确每日问候对话是否产出【BASE_CURRENCY】。如果是，需在【数据状态变化】中补充货币产出逻辑，并通知主程在程序蓝图的 `[PerformDialog]` 接口中增加货币产出和上限校验；如果不是，需修改【表现层反馈】中的飘字提示描述。
### Issue 4
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary.daily_touch_count
- 问题描述: 数值说明书中 `daily_touch_count` 的取值范围描述为 `0至DAILY_TOUCH_LIMIT（10）`，但数值配表 `continuous_formulas` 中 `daily_touch_count` 的 `growth` 为 `0`，且 `discrete_milestones` 中未定义 `DAILY_TOUCH_LIMIT` 这个常量。程序蓝图引用了 `[DAILY_TOUCH_LIMIT] (10)`，但数值配表中没有提供这个字段的定义或来源。这导致 `DAILY_TOUCH_LIMIT` 的值（10）没有在数值配表中明确声明，属于字段遗漏。
- 修改建议: 数值策划需在数值配表中明确声明 `DAILY_TOUCH_LIMIT` 这个常量字段及其值（10），或者将其作为 `daily_touch_count` 字段的 `max` 属性进行定义，确保程序可以从数值配表中读取到该限制值。
### Issue 5
- 责任方: numerical_planner
- 目标文件: 数值说明书
- 锚点: field_dictionary.daily_gift_count
- 问题描述: 数值说明书中 `daily_gift_count` 的取值范围描述为 `0至DAILY_GIFT_LIMIT（5）`，但数值配表 `continuous_formulas` 中 `daily_gift_count` 的 `growth` 为 `0`，且 `discrete_milestones` 中未定义 `DAILY_GIFT_LIMIT` 这个常量。程序蓝图引用了 `[DAILY_GIFT_LIMIT] (5)`，但数值配表中没有提供这个字段的定义或来源。这导致 `DAILY_GIFT_LIMIT` 的值（5）没有在数值配表中明确声明，属于字段遗漏。
- 修改建议: 数值策划需在数值配表中明确声明 `DAILY_GIFT_LIMIT` 这个常量字段及其值（5），或者将其作为 `daily_gift_count` 字段的 `max` 属性进行定义，确保程序可以从数值配表中读取到该限制值。
### Issue 6
- 责任方: numerical_planner
- 目标文件: 数值配表
- 锚点: continuous_formulas
- 问题描述: 程序蓝图在‘数值与配置表挂载’中明确要求读取 `[TOUCH_EXP_BASE]`、`[GIFT_EXP_BASE]`、`[DAILY_FREE_EXP_LIMIT]`、`[DAILY_LOGIN_AFFECTION_EXP]` 等数值常量，但数值配表 `continuous_formulas` 中完全没有定义这些字段。这导致程序无法从数值配表中获取触摸、送礼、每日登录等行为的好感度经验基础值，以及每日经验上限。
- 修改建议: 数值策划需在数值配表中补充 `TOUCH_EXP_BASE`、`GIFT_EXP_BASE`、`DAILY_FREE_EXP_LIMIT`、`DAILY_LOGIN_AFFECTION_EXP` 等字段及其具体数值，确保程序蓝图引用的所有数值常量都有定义。
### Issue 7
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 五、数值与配置表挂载
- 问题描述: 程序蓝图引用了 `[PREFERENCE_BONUS_MULTIPLIER] (1.5)` 和 `[ACTION_CYCLE_INTERVAL]`、`[LOOK_AT_CAMERA_PROBABILITY]`、`[FILTER_LIST]`、`[POSE_LIST]` 等配置，但数值配表和数值说明书中均未定义这些字段。程序蓝图作为技术文档，不应自行定义数值常量，而应引用数值配表中的字段。这属于程序蓝图与数值配表之间的字段遗漏。
- 修改建议: 主程需与数值策划协商，由数值策划在数值配表中补充 `PREFERENCE_BONUS_MULTIPLIER`、`ACTION_CYCLE_INTERVAL`、`LOOK_AT_CAMERA_PROBABILITY`、`FILTER_LIST`、`POSE_LIST` 等字段及其默认值/列表。然后主程更新程序蓝图，确保所有引用的数值常量都来源于数值配表。
### Issue 8
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 三、后端逻辑划分 - 核心校验逻辑 - 触摸互动校验
- 问题描述: 程序蓝图中的触摸互动校验逻辑仅校验了 `[DAILY_TOUCH_COUNT] < [DAILY_TOUCH_LIMIT]`，但系统策划案中明确要求触摸互动产出【BASE_CURRENCY】，且受【DAILY_FREE_CURRENCY_LIMIT】限制。程序蓝图完全忽略了货币产出和货币上限的校验逻辑，与系统策划案不一致。
- 修改建议: 主程需根据系统策划案的要求，在触摸互动校验逻辑中增加对【BASE_CURRENCY】产出和【DAILY_FREE_CURRENCY_LIMIT】上限的校验。同时，需与数值策划确认【DAILY_FREE_CURRENCY_LIMIT】字段是否已补充到数值配表中。
### Issue 9
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 三、后端逻辑划分 - 核心校验逻辑 - 送礼校验
- 问题描述: 程序蓝图中的送礼校验逻辑仅校验了次数和背包数量，但系统策划案中明确要求送礼产出【BASE_CURRENCY】，且受【DAILY_FREE_CURRENCY_LIMIT】限制。程序蓝图完全忽略了货币产出和货币上限的校验逻辑，与系统策划案不一致。
- 修改建议: 主程需根据系统策划案的要求，在送礼校验逻辑中增加对【BASE_CURRENCY】产出和【DAILY_FREE_CURRENCY_LIMIT】上限的校验。同时，需与数值策划确认【DAILY_FREE_CURRENCY_LIMIT】字段是否已补充到数值配表中。
### Issue 10
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、前后端通信协议 - [PerformTouch] 返回参数
- 问题描述: 系统策划案中触摸互动成功后，除了增加经验，还会增加【BASE_CURRENCY】。但程序蓝图 `[PerformTouch]` 接口的返回参数中，只包含了 `new_affection_experience`，没有包含货币相关的返回字段（如 `new_base_currency` 或 `new_daily_currency_count`）。这导致客户端无法获取并展示货币变化。
- 修改建议: 主程需在 `[PerformTouch]` 接口的返回参数中增加货币相关的字段，例如 `new_base_currency`（当前货币总量）和 `new_daily_currency_count`（当日已获取货币量），以便客户端更新UI。
### Issue 11
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、前后端通信协议 - [GiveGift] 返回参数
- 问题描述: 系统策划案中送礼成功后，除了增加经验，还会增加【BASE_CURRENCY】。但程序蓝图 `[GiveGift]` 接口的返回参数中，只包含了 `new_affection_experience`，没有包含货币相关的返回字段（如 `new_base_currency` 或 `new_daily_currency_count`）。这导致客户端无法获取并展示货币变化。
- 修改建议: 主程需在 `[GiveGift]` 接口的返回参数中增加货币相关的字段，例如 `new_base_currency`（当前货币总量）和 `new_daily_currency_count`（当日已获取货币量），以便客户端更新UI。
**当前审查总计问题:** 11 个

--- 审查时间: 2026-05-29 15:30:40 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.4 对话 - 前置条件
- 问题描述: 对话的前置条件与1.2设计目标中的每日问候逻辑存在冲突。2.4节前置条件要求`player_daily_greeting_flag`为false，但1.2节中每日首次进入宿舍检查的是`player_daily_login_flag`，两者字段名不一致，且1.2节中触发问候后置为`player_daily_greeting_flag`为true，但2.4节中对话完成后也置为true，逻辑重复且字段引用混乱。
- 修改建议: 统一每日问候的触发条件字段名，建议统一使用`player_daily_greeting_flag`，并明确每日首次进入宿舍时检查该字段，而非`player_daily_login_flag`。同时合并1.2和2.4中关于问候对话的重复描述，确保前置条件、流转逻辑、数据状态变化一致。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 好感度养成循环 - 流转逻辑
- 问题描述: 系统案中描述好感度升级时`[AFFECTION_EXP]`重置为0，但2.1节边界与异常兜底中又提到溢出部分保留至下一级。这两个描述存在逻辑矛盾：如果重置为0，则溢出部分无法保留。
- 修改建议: 明确升级时的经验处理规则：建议描述为`[AFFECTION_EXP]`减去当前等级阈值，剩余部分作为下一级的起始经验，而非直接重置为0。同时确保与数值配表中`EXP_THRESHOLD_CURRENT_LEVEL`的线性增长公式逻辑一致。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - daily_dialog_triggered
- 问题描述: 数值说明书中定义了`daily_dialog_triggered`字段，但系统案中使用的字段名是`player_daily_greeting_flag`，两者功能相同但命名不一致。程序蓝图中同时使用了这两个字段名（后端持久化数据表使用`daily_dialog_triggered`，API返回中使用`player_daily_greeting_flag`），导致数据模型混乱。
- 修改建议: 统一字段命名，建议统一为`player_daily_greeting_flag`，并在数值说明书中同步更新字段名，确保与系统案和程序蓝图一致。
### Issue 4
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 - 持久化数据 (DB)
- 问题描述: 程序蓝图中的角色宿舍数据表包含了`character_action_state`字段，但该字段是客户端表现层状态（日常动作循环），不应由后端持久化。系统案中明确`character_action_state`是客户端实时更新的状态，且拍照模式等纯表现层操作无后台数据变化。后端持久化该字段会导致状态同步问题。
- 修改建议: 将`character_action_state`从后端持久化数据表中移除，改为客户端本地状态管理。后端仅需在进入宿舍时返回初始状态ID，后续状态切换由客户端状态机控制器独立管理。
### Issue 5
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 - [GiveGift]
- 问题描述: 送礼API的返回参数中包含了`new_base_currency`，但系统案中送礼行为并未提及会增加基础货币。系统案中只有每日问候对话（2.4节）才会增加`[BASE_CURRENCY]`。送礼API返回基础货币字段会导致数据不一致。
- 修改建议: 从`[GiveGift]`API的返回参数中移除`new_base_currency`字段，确保送礼行为不涉及基础货币变化。如果送礼确实需要增加基础货币，则需在系统案中补充说明。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.5 日常动作循环 - 前置条件
- 问题描述: 系统案中日常动作循环的前置条件要求好感度等级至少为`[AFFECTION_LEVEL_MIN]`，但`[AFFECTION_LEVEL_MIN]`默认值为1，而玩家获得角色后好感度等级即为1，这意味着该前置条件永远为真，形同虚设。此外，如果好感度等级为0（未获得角色），玩家根本无法进入宿舍，因此该条件无实际意义。
- 修改建议: 移除该前置条件，或将其改为更合理的条件（如角色已解锁宿舍场景`character_dormitory_unlocked == true`），避免冗余逻辑。
### Issue 7
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - character_battle_stat_bonus
- 问题描述: 数值说明书中`character_battle_stat_bonus`的类型定义为【浮点数】，但程序蓝图中该字段在后端持久化数据表中也作为浮点数存储。然而，系统案5.2节中描述该字段为“微量属性加成（如暴击率、伤害）”，未明确是百分比还是绝对值。数值配表中该字段的growth为0.0，但discrete_milestones中在等级10、20、30等节点分别设置了0.01、0.02、0.03等值，这些值是否代表百分比加成（如1%、2%）未在数值说明书中明确。
- 修改建议: 在数值说明书的`character_battle_stat_bonus`字段描述中明确单位（如百分比或千分比），并确保与discrete_milestones中的数值含义一致。例如，如果0.01代表1%，则需在描述中注明。
### Issue 8
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载
- 问题描述: 程序蓝图要求挂载`touch_boundary_compliance`字段，但该字段在数值配表的`continuous_formulas`中并未定义。数值说明书中虽然定义了该字段，但类型为布尔值，而程序蓝图将其作为数值配置挂载，类型不匹配。
- 修改建议: 将`touch_boundary_compliance`从数值配置挂载列表中移除，改为在合规性配置表中定义（如布尔标志位），或由法务/合规团队直接配置，不纳入数值策划的配表范围。
**当前审查总计问题:** 8 个

--- 审查时间: 2026-05-29 17:01:20 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统策划案中，水枪射击小游戏的【流转逻辑】第6点提到“若命中数达到 [HIT_THRESHOLD_SHOOTING]，触发角色特殊奖励”，但【边界与异常兜底】第3点又提到“若玩家多次失败（连续 [FAILURE_THRESHOLD] 次未达标），可消耗 [SKIP_CURRENCY_COST] 基础货币跳过游戏直接获得奖励”。这里存在逻辑死胡同：如果玩家通过“跳过”直接获得奖励，那么“跳过”是否也消耗了“今日该角色已触发过奖励”的机会？如果消耗，则与“多次失败后跳过”的初衷矛盾（跳过是为了避免失败，但跳过本身也消耗了奖励机会）；如果不消耗，则玩家可以无限跳过刷奖励。系统案没有明确说明“跳过”后 `character_daily_game_reward_flag` 的状态变化。
- 修改建议: 请在【数据状态变化】中明确：当玩家使用“跳过”功能时，`character_daily_game_reward_flag` 是否置为 true。建议统一逻辑：无论达标、未达标还是跳过，只要玩家获得了奖励（包括跳过直接获得），该标志都应置为 true，以保持一致性。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.daily_free_refresh_count
- 问题描述: 数值说明书中定义了 `daily_free_refresh_count`（已使用次数），但系统策划案中多处使用的是 `daily_hotspring_free_refresh_count`（剩余次数）。两者语义相反，且数值配表 `continuous_formulas` 中只定义了 `daily_hotspring_free_refresh_count` 的 base 为 3，未定义 `daily_free_refresh_count` 的初始值或公式。这会导致程序蓝图中的后端校验逻辑（3.2节“免费刷新次数校验”）无法确定到底校验哪个字段。
- 修改建议: 请统一字段命名：要么全部使用 `daily_hotspring_free_refresh_count`（剩余次数），要么全部使用 `daily_free_refresh_count`（已使用次数）。建议删除 `daily_free_refresh_count` 字段，因为系统案和程序蓝图都主要使用 `daily_hotspring_free_refresh_count` 作为剩余次数。
### Issue 3
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 3.1 持久化数据 (DB)
- 问题描述: 程序蓝图的持久化数据表中，`current_game_state`、`current_game_hit_count`、`current_game_ball_count`、`camera_mode`、`ui_visibility_state` 等字段被遗漏。这些字段在数值说明书中有明确定义，且系统策划案中明确提到了它们的状态变化（如 `current_game_state` 切换为 `[GAME_STATE_SHOOTING]`）。遗漏这些字段会导致小游戏进行中的状态无法持久化，断线重连后无法恢复游戏状态（虽然系统案说“不保存进度”，但 `current_game_state` 至少应该记录“玩家是否正在游戏中”以防止重复进入）。
- 修改建议: 请在持久化数据表中补充 `current_game_state` (INT)、`current_game_hit_count` (INT)、`current_game_ball_count` (INT)、`camera_mode` (INT)、`ui_visibility_state` (INT) 字段，并确保与数值说明书中的类型和枚举值一致。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统策划案中，水枪射击小游戏的【前置条件】为“当前角色未触发过今日小游戏奖励”，但【边界与异常兜底】第1点提到“若当前角色今日已触发过小游戏奖励，入口按钮置灰”。然而，系统案2.4节【边界与异常兜底】又提到“若该角色所有奖励内容已全部解锁，小游戏奖励入口显示‘已全部解锁’，玩家仍可游玩小游戏但无奖励”。这里存在矛盾：如果所有奖励已解锁，玩家是否还能进入小游戏？前置条件说“未触发过今日小游戏奖励”，但“已全部解锁”意味着奖励已全部触发过，按前置条件应该无法进入。系统案没有明确“已全部解锁”是否覆盖“今日已触发”的判断。
- 修改建议: 请明确优先级：当角色所有奖励已全部解锁时，应覆盖“今日已触发”的判断，允许玩家进入小游戏（仅游玩无奖励）。建议修改前置条件为：“玩家点击入口按钮，且（当前角色未触发过今日小游戏奖励 或 当前角色所有奖励已全部解锁）”。
**当前审查总计问题:** 4 个

--- 审查时间: 2026-05-29 17:03:52 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统案中描述了小游戏开始、命中、结束的数据状态变化，但未明确说明当玩家在游戏过程中主动退出（如点击返回按钮）时的处理逻辑。例如：是否视为放弃？是否重置小游戏状态？是否返还已消耗的射击冷却时间？
- 修改建议: 补充主动退出小游戏的边界处理逻辑，包括数据状态如何重置、是否消耗免费次数或货币、以及UI反馈。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.4 小游戏奖励共享规则
- 问题描述: 系统案中说明两个小游戏共享每日奖励次数，但未明确当玩家在第一个小游戏中达标后，第二个小游戏入口的提示文案应统一为'今日奖励已领取'还是'已全部解锁'。同时，未说明若玩家在第一个小游戏中未达标，第二个小游戏是否仍可正常获得奖励。
- 修改建议: 明确两个小游戏奖励共享的具体规则：若玩家在任意一个小游戏中达标，则当日所有小游戏奖励入口均显示'今日奖励已领取'，且不再发放奖励。若未达标，则两个小游戏均可继续尝试。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统案中描述了小游戏结束后的数据状态变化，但未说明当玩家达标后，奖励解锁弹窗关闭后，玩家是留在结算界面还是自动返回主场景。若返回主场景，是否自动重置小游戏相关数据（如current_game_state）？
- 修改建议: 补充奖励解锁弹窗关闭后的流转逻辑：弹窗关闭后，自动返回温泉中心主场景，并重置小游戏状态（current_game_state置为0）。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 互动小游戏 - 捞水球
- 问题描述: 系统案中描述了小游戏开始、成功捞取、结束的数据状态变化，但未说明当玩家在游戏过程中断线重连后，如何恢复小游戏进度（如剩余水球数、计时器剩余时间）。当前仅说明'已捞取的水球不恢复'，但未说明是否允许玩家继续游戏。
- 修改建议: 补充断线重连后小游戏进度的恢复逻辑：若断线时游戏仍在进行中，重连后应恢复剩余水球数和剩余时间，允许玩家继续游戏。若断线时间过长导致游戏超时，则按超时处理。
### Issue 5
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统案中描述了小游戏开始、命中、结束的数据状态变化，但未说明当玩家在游戏过程中断线重连后，如何恢复小游戏进度（如剩余靶子数、计时器剩余时间）。当前仅说明'已消耗的射击次数不恢复'，但未说明是否允许玩家继续游戏。
- 修改建议: 补充断线重连后小游戏进度的恢复逻辑：若断线时游戏仍在进行中，重连后应恢复剩余靶子数和剩余时间，允许玩家继续游戏。若断线时间过长导致游戏超时，则按超时处理。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 角色刷新规则
- 问题描述: 系统案中描述了角色刷新规则，但未说明当玩家使用'今日特惠角色'刷新后，是否还能通过普通刷新（消耗货币）再次刷新出其他角色。若可以，是否影响今日特惠角色的再次出现？
- 修改建议: 补充说明：使用'今日特惠角色'刷新后，玩家仍可进行普通刷新，但今日特惠角色不会再次出现。
### Issue 7
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 角色刷新规则
- 问题描述: 系统案中描述了角色刷新规则，但未说明当玩家角色池中所有角色均已解锁全部温泉中心内容时，刷新逻辑是否发生变化（如是否仍可刷新，但无奖励可解锁）。
- 修改建议: 补充说明：若玩家所有角色均已解锁全部温泉中心内容，刷新逻辑不变，但小游戏奖励入口显示'已全部解锁'，玩家仍可游玩小游戏但无奖励。
### Issue 8
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中定义了'player_daily_hotspring_first_entry_flag'字段，但系统案中未提及该字段的用途或更新逻辑。该字段在数值配表中被用于离散里程碑，但系统案中仅使用'last_hotspring_entry_timestamp'判断每日首次进入。
- 修改建议: 确认'player_daily_hotspring_first_entry_flag'字段是否必要，若需要，则在系统案中补充其更新逻辑（如每日首次进入时置为true，次日重置为false）。
### Issue 9
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中定义了'current_game_ball_count'字段，但系统案中未提及该字段的用途。该字段在数值配表中被定义为'当前捞水球小游戏中剩余的水球数'，但系统案中仅使用'current_minigame_ball_count'记录捞取数。
- 修改建议: 统一字段命名：将'current_game_ball_count'改为'current_minigame_ball_count'，或确认该字段是否用于记录剩余水球数，并在系统案中补充其更新逻辑。
### Issue 10
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中定义了'character_hotspring_reward_unlocked'字段，但系统案中使用了'character_hotspring_reward_unlocked'作为数组（记录多条解锁记录），而数值说明书中定义为布尔值。
- 修改建议: 确认该字段的数据类型：若需记录多条解锁记录，应改为数组或列表；若仅记录是否已解锁过任何奖励，则保持布尔值，并在系统案中明确说明。
### Issue 11
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中定义了'character_daily_game_reward_flag'字段，但系统案中使用了'daily_minigame_reward_claimed'作为全局标记。字段命名不一致，可能导致开发混淆。
- 修改建议: 统一字段命名：将数值说明书中的'character_daily_game_reward_flag'改为'daily_minigame_reward_claimed'，或确认该字段是否用于记录角色维度的奖励状态。
### Issue 12
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server)
- 问题描述: 程序蓝图中将'character_hotspring_reward_unlocked'定义为布尔类型，但系统案中该字段用于记录多条解锁记录（数组），存在数据类型冲突。
- 修改建议: 根据系统案需求，将'character_hotspring_reward_unlocked'改为数组类型，用于存储已解锁的奖励ID列表。
### Issue 13
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server)
- 问题描述: 程序蓝图中将'character_daily_game_reward_flag'定义为布尔类型，但系统案中使用了'daily_minigame_reward_claimed'作为全局标记。字段命名不一致，且数据类型可能不匹配。
- 修改建议: 统一字段名为'daily_minigame_reward_claimed'，并确认其数据类型为布尔值，用于标记当日是否已获得小游戏奖励。
### Issue 14
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载
- 问题描述: 程序蓝图中列出了多个配置项，但未包含系统案中提到的'SHOT_COOLDOWN'（射击冷却时间）、'TARGET_COUNT'（靶子总数，水枪射击）、'BALL_COUNT'（水球总数，捞水球）等具体数值。这些数值在数值配表中也未明确给出。
- 修改建议: 在数值配表中补充'SHOT_COOLDOWN'、'TARGET_COUNT_SHOOTING'、'BALL_COUNT_SCOOPING'等配置项，并在程序蓝图中挂载。
### Issue 15
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的'StartMinigame'接口返回参数包含'game_timer'，但系统案中未明确小游戏计时器是前端本地计时还是服务端同步计时。若为服务端同步计时，需考虑网络延迟对游戏公平性的影响。
- 修改建议: 明确小游戏计时器的同步方式：建议采用服务端下发开始时间戳，前端本地计时，游戏结束时服务端校验实际耗时。
### Issue 16
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的'EndMinigame'接口返回参数包含'reward_id'，但系统案中未定义奖励ID的生成规则或取值范围。
- 修改建议: 定义奖励ID的生成规则（如角色ID+奖励类型+序号），并在数值配表中提供奖励ID与具体奖励内容的映射表。
**当前审查总计问题:** 16 个

--- 审查时间: 2026-05-29 17:11:37 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json & data.json
- 锚点: field_dictionary.daily_free_refresh_count
- 问题描述: 数值说明书中 `daily_free_refresh_count` 字段描述为“玩家当日剩余的免费刷新次数”，默认值为 `DAILY_FREE_REFRESH_LIMIT`。但系统策划案中 `daily_free_refresh_count` 被用于记录“已使用的免费刷新次数”。数值配表中 `daily_free_refresh_count` 的 base 值为 3，而 `daily_hotspring_free_refresh_count` 的 base 值为 0。这导致两个字段的语义与系统案中的逻辑完全相反，且数值配表与数值说明书对 `daily_free_refresh_count` 的默认值定义冲突（说明书为 DAILY_FREE_REFRESH_LIMIT，配表为 3）。
- 修改建议: 建议数值策划统一字段语义：要么将 `daily_free_refresh_count` 定义为“已使用次数”（初始为0），要么定义为“剩余次数”（初始为 DAILY_FREE_REFRESH_LIMIT）。同时，请确认 `daily_hotspring_free_refresh_count` 字段是否冗余，或明确其与 `daily_free_refresh_count` 的关系。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 角色刷新规则 - 刷新权重
- 问题描述: 系统策划案中提到了“刷新权重 = 基础权重（所有角色均等） + 当日首次进入时，若玩家拥有‘今日特惠角色’，则必定刷新该角色（每日限1次）”。但并未定义“今日特惠角色”的配置来源、判定逻辑（如何确定哪个角色是今日特惠）以及该特惠角色的刷新次数限制（每日限1次）的详细数据状态变化。同时，数值配表和程序蓝图中均未提供“今日特惠角色”相关的字段或API参数。这是一个逻辑死胡同。
- 修改建议: 建议系统策划补充“今日特惠角色”的详细设计：包括配置表结构（如每日特惠角色ID列表）、判定逻辑（进入时检查）、数据字段（如 `daily_special_character_id`、`daily_special_character_used`）以及刷新权重计算的具体公式。
### Issue 3
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 - RefreshCharacter
- 问题描述: 程序蓝图中 `RefreshCharacter` API 的返回参数包含 `daily_special_character_used: bool`，但数值说明书和数值配表中均未定义此字段。同时，系统策划案中提到的“今日特惠角色”逻辑需要此字段来记录是否已使用，但该字段在数据层缺失。这属于字段遗漏。
- 修改建议: 建议主程在数据库设计（持久化数据）中增加 `daily_special_character_used` 字段（布尔类型，默认 false），并在 `EnterHotspring` 和 `RefreshCharacter` API 中同步该字段的读写逻辑。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 & 2.3 互动小游戏 - 失败阈值跳过
- 问题描述: 系统策划案中两个小游戏都提到了“若玩家在小游戏中多次失败（连续 `[FAILURE_THRESHOLD]` 次未达标），弹出‘跳过’选项”。但未明确 `FAILURE_THRESHOLD` 的具体数值，也未说明该阈值是全局共享还是每个小游戏独立。此外，系统策划案中未定义 `minigame_failure_count` 字段在切换角色或切换小游戏时的重置逻辑（数值说明书提到“退出小游戏或切换角色时重置”，但系统案未提及切换小游戏时是否重置）。
- 修改建议: 建议系统策划明确 `FAILURE_THRESHOLD` 的数值（或引用数值表），并补充说明：当玩家从水枪射击切换到捞水球时，`player_game_failure_count` 是否重置。同时，建议在系统案中增加一条边界条件：若玩家在连续失败后选择跳过，`player_game_failure_count` 应重置为0。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json & data.json
- 锚点: continuous_formulas
- 问题描述: 数值配表中所有字段的 `growth` 和 `type` 均被设置为 `1` 和 `linear`，包括布尔类型（如 `player_daily_hotspring_first_entry_flag`）、字符串类型（如 `current_game_state`）和数组类型（如 `character_hotspring_reward_unlocked`）。这不符合数据类型定义，且 `linear` 增长模型对非数值字段无意义。例如，布尔字段的 base 为 0，growth 为 1，按线性增长会变成 1、2、3...，而非 true/false。
- 修改建议: 建议数值策划根据字段的实际数据类型（整数、布尔、字符串、数组）重新设计 `continuous_formulas` 结构。对于布尔和字符串字段，应使用 `discrete_milestones` 进行枚举映射，而非线性增长。对于数组字段，应定义其增长规则（如每次增加一个元素），而非线性数值增长。
### Issue 6
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载
- 问题描述: 程序蓝图中提到“从 `system_numerical_data.json` 中的 `field_dictionary` 和 `implementation_notes` 部分读取常量”，但 `implementation_notes` 中并未包含 `REFRESH_CURRENCY_COST`、`TARGET_COUNT`、`GAME_TIME_LIMIT`、`HIT_THRESHOLD`、`BALL_COUNT`、`BALL_GAME_TIME_LIMIT`、`BALL_THRESHOLD`、`FAILURE_THRESHOLD`、`SKIP_CURRENCY_COST`、`MIN_REWARD_SLOTS` 等具体数值。这些数值在系统策划案中以占位符形式出现（如 `[REFRESH_CURRENCY_COST]`），但在数值配表和说明书中均未定义。这导致程序无法从配置表中读取这些关键参数。
- 修改建议: 建议数值策划在 `system_numerical_docs.json` 中新增一个 `game_parameters` 或 `constants` 字段，明确列出所有占位符的具体数值（如 `REFRESH_CURRENCY_COST: 100`）。同时，建议主程在程序蓝图中明确这些常量的读取路径，例如从 `system_numerical_data.json` 的 `constants` 字段中读取。
**当前审查总计问题:** 6 个

--- 审查时间: 2026-05-29 17:14:44 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones.3
- 问题描述: 离散里程碑3中引用了字段 `daily_special_character_used`，但该字段在 `field_dictionary` 中未定义。系统策划案中多处使用了该字段，数值说明书和配表中均遗漏了其定义和默认值。
- 修改建议: 请在 `field_dictionary` 中补充 `daily_special_character_used` 字段的定义，包括数据类型（布尔）、默认值（false）和取值范围。
### Issue 2
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones.5
- 问题描述: 离散里程碑5中，主动换人（免费次数耗尽）时扣除 `player_base_currency` 的值为 -10，但系统策划案中此消耗为占位符 `[REFRESH_CURRENCY_COST]`。数值配表直接使用了具体数值，而未定义该常量，导致与系统案中的占位符约定不一致。
- 修改建议: 请在 `field_dictionary` 或新增的常量表中定义 `REFRESH_CURRENCY_COST` 常量，并将里程碑5中的 -10 替换为该常量的引用。
### Issue 3
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones.14
- 问题描述: 离散里程碑14中，使用跳过功能时扣除 `player_base_currency` 的值为 -50，但系统策划案中此消耗为占位符 `[SKIP_CURRENCY_COST]`。数值配表直接使用了具体数值，而未定义该常量，导致与系统案中的占位符约定不一致。
- 修改建议: 请在 `field_dictionary` 或新增的常量表中定义 `SKIP_CURRENCY_COST` 常量，并将里程碑14中的 -50 替换为该常量的引用。
### Issue 4
- 责任方: numerical_planner
- 目标文件: 数值说明书 (system_numerical_docs.json)
- 锚点: field_dictionary
- 问题描述: 系统策划案中定义了 `daily_minigame_reward_count` 字段，用于记录当日小游戏奖励已领取次数，并在多处逻辑中引用。但该字段在数值说明书的 `field_dictionary` 中完全缺失，导致数据模型不完整。
- 修改建议: 请在 `field_dictionary` 中补充 `daily_minigame_reward_count` 字段的定义，包括数据类型（整数）、默认值（0）和取值范围（0到DAILY_MINIGAME_REWARD_LIMIT）。
### Issue 5
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones
- 问题描述: 系统策划案中定义了 `minigame_failure_count` 字段的复杂重置逻辑（退出小游戏、切换小游戏类型、切换角色时重置为0），但数值配表中的离散里程碑仅覆盖了部分重置场景（里程碑8、9、12、13、14、15、16、17），缺少对“切换小游戏类型”时重置的明确里程碑（里程碑15描述为切换小游戏类型，但效果中重置了 `player_game_failure_count`，与系统案一致，但需确认字段名一致性）。
- 修改建议: 请确认 `player_game_failure_count` 与系统案中的 `minigame_failure_count` 是否为同一字段。如果是，请统一命名；如果不是，请补充 `minigame_failure_count` 的定义和重置逻辑。
### Issue 6
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas
- 问题描述: 数值配表中为 `current_game_state` 定义了连续公式（base='idle', growth=0, type='linear'），但该字段为字符串类型，其值应通过离散里程碑或游戏逻辑直接设置，不应出现在连续公式中。数值说明书中的 `implementation_notes` 已明确指出字符串类型字段不应出现在连续公式中，但配表未遵循此规则。
- 修改建议: 请将 `current_game_state` 从 `continuous_formulas` 中移除，其值应仅通过离散里程碑（如里程碑6、8、9、10、12、13、17）进行设置。
### Issue 7
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: continuous_formulas
- 问题描述: 数值配表中为 `character_hotspring_reward_unlocked` 定义了连续公式（base=[], growth=0, type='linear'），但该字段为数组类型，其元素应通过游戏逻辑动态增删，不应出现在连续公式中。数值说明书中的 `implementation_notes` 已明确指出数组类型字段不应出现在连续公式中，但配表未遵循此规则。
- 修改建议: 请将 `character_hotspring_reward_unlocked` 从 `continuous_formulas` 中移除，其值应仅通过游戏逻辑动态增删。
### Issue 8
- 责任方: numerical_planner
- 目标文件: 数值配表 (data.json)
- 锚点: discrete_milestones.8 & 12
- 问题描述: 离散里程碑8（水枪射击成功）和12（捞水球成功）中，效果均包含 `character_daily_game_reward_flag: 1`，但系统策划案中奖励解锁逻辑使用的是 `daily_minigame_reward_count` 字段来记录当日奖励领取次数，而非 `character_daily_game_reward_flag`。这两个字段的关系和用途不明确，可能导致逻辑冲突。
- 修改建议: 请明确 `character_daily_game_reward_flag` 和 `daily_minigame_reward_count` 的职责。建议统一使用 `daily_minigame_reward_count` 进行每日上限校验，并删除或重新定义 `character_daily_game_reward_flag`。
**当前审查总计问题:** 8 个

--- 审查时间: 2026-05-29 17:17:48 ---
### Issue 1
- 责任方: numerical_planner
- 目标文件: 数值说明书 & 数值配表
- 锚点: field_dictionary / continuous_formulas
- 问题描述: 系统策划案中多处使用占位符（如 [REFRESH_CURRENCY_COST]、[SHOOTING_TIME_LIMIT]、[FAILURE_THRESHOLD] 等），但数值说明书和数值配表中均未定义这些常量的具体数值或默认值。程序蓝图明确指出这些为待定参数，但数值策划未提供任何初始值或范围，导致开发阶段无法进行有效的数值校验和逻辑实现。
- 修改建议: 数值策划需补充所有占位符的具体数值或默认值（如 REFRESH_CURRENCY_COST = 100, SHOOTING_TIME_LIMIT = 30 等），并更新到数值说明书和数值配表中。
### Issue 2
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.2 互动小游戏 - 水枪射击靶子
- 问题描述: 系统策划案中定义了 `minigame_failure_count` 字段及其重置逻辑（退出小游戏、切换小游戏类型、切换角色时重置为0），但未定义该字段的初始值（首次进入小游戏时）以及当玩家连续失败达到阈值后选择“跳过”时，`minigame_failure_count` 是否重置。这可能导致逻辑死胡同：跳过成功后，下次进入同一小游戏时，`minigame_failure_count` 仍为累积值，可能立即触发跳过选项。
- 修改建议: 系统策划需明确：当玩家使用跳过选项成功后，`minigame_failure_count` 是否重置为0；以及首次进入小游戏时，`minigame_failure_count` 的初始值（应为0）。
### Issue 3
- 责任方: tech_architect
- 目标文件: 程序蓝图
- 锚点: 四、前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的 `GetCharacterRewardStatus` API 请求参数 `character_id` 定义为 `string` 类型，但数值说明书中 `current_hotspring_character_id` 定义为【整数】类型，且角色ID表通常为整数。数据类型不一致可能导致前后端通信时类型转换错误或校验失败。
- 修改建议: 将 `GetCharacterRewardStatus` 的 `character_id` 参数类型改为 `int`，与数值说明书中的角色ID类型保持一致。
### Issue 4
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.2 & 2.3 互动小游戏
- 问题描述: 系统策划案中两个小游戏（水枪射击和捞水球）均提到“若玩家连续 `[FAILURE_THRESHOLD]` 次未达标，弹出跳过选项”，但未定义 `minigame_failure_count` 的计数规则：是每次小游戏结束后（无论是否达标）都增加，还是仅当未达标时增加？若玩家中途退出小游戏（不消耗资源），`minigame_failure_count` 重置为0，但退出后重新进入同一小游戏，失败次数是否从0开始累积？这可能导致玩家通过反复退出重进来规避失败计数，从而绕过跳过选项的付费设计。
- 修改建议: 系统策划需明确 `minigame_failure_count` 的递增规则：仅当小游戏自然结束（计时结束）且未达标时增加；主动退出不增加。同时考虑是否限制每日退出次数以防止滥用。
### Issue 5
- 责任方: numerical_planner
- 目标文件: 数值说明书 & 数值配表
- 锚点: field_dictionary / discrete_milestones
- 问题描述: 数值配表中的离散里程碑（discrete_milestones）使用了条件 `current_game_hit_count >= TARGET_COUNT` 和 `current_game_ball_count >= BALL_COUNT`，但 `TARGET_COUNT` 和 `BALL_COUNT` 在数值说明书中仅作为取值范围上限（默认值0），未定义具体数值。同时，里程碑中直接引用 `TARGET_COUNT` 和 `BALL_COUNT` 作为成功条件，但系统策划案中成功条件是 `>= SHOOTING_SUCCESS_THRESHOLD` 和 `>= FISHING_SUCCESS_THRESHOLD`，这两个阈值可能不等于靶子总数或水球总数。数值配表中的条件与系统策划案不一致。
- 修改建议: 数值策划需明确定义 `SHOOTING_SUCCESS_THRESHOLD` 和 `FISHING_SUCCESS_THRESHOLD` 的具体数值，并更新离散里程碑中的条件，使其与系统策划案一致（例如 `current_game_hit_count >= SHOOTING_SUCCESS_THRESHOLD`）。
### Issue 6
- 责任方: system_planner
- 目标文件: 系统策划案
- 锚点: 2.4 奖励系统
- 问题描述: 系统策划案中奖励解锁逻辑提到“从奖励池中随机选取一个未解锁的奖励”，但未定义奖励池的生成规则：奖励池是每个角色固定的一组奖励ID，还是根据角色ID动态生成？若为固定奖励池，需明确每个角色的奖励槽位数（`MIN_REWARD_SLOTS`）及具体奖励ID列表。当前数值说明书中 `character_hotspring_reward_unlocked` 为整数数组，但未提供奖励ID的枚举或范围。
- 修改建议: 系统策划需补充奖励池的定义：每个角色在温泉中心的奖励列表（如表情ID、语音ID、动作ID），或提供奖励ID的生成规则（如从图鉴系统奖励ID表中筛选出温泉中心分类的奖励）。
**当前审查总计问题:** 6 个

--- 审查时间: 2026-05-30 15:06:10 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 经济循环 - 边界与异常兜底
- 问题描述: 系统案中描述了破产后玩家可选择'向系统借贷一次'，但未定义借贷后再次破产的强制结束逻辑中，是否扣除借贷利息以及如何结算。同时，借贷利息`[LOAN_INTEREST_RATE]`在数值配表中未提供具体数值或公式，导致逻辑死胡同。
- 修改建议: 请补充借贷利息的结算方式（例如：游戏结束时从最终资产中扣除`LOAN_AMOUNT * LOAN_INTEREST_RATE`），并明确强制结束游戏时是否仍扣除利息。
### Issue 2
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中缺少`[LOAN_AMOUNT]`和`[LOAN_INTEREST_RATE]`字段的定义，这两个字段在系统案2.2节中被引用，但未在数值字典中声明其数据类型、取值范围和默认值。
- 修改建议: 请在`field_dictionary`中补充`loan_amount`（整数）和`loan_interest_rate`（浮点数）字段的定义，并确保与系统案中的占位符对应。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中缺少`[BOARD_TILE_COUNT]`、`[AI_OPPONENT_COUNT]`、`[STARTING_COINS]`、`[PASS_START_BONUS]`、`[TOLL_FEE]`、`[LAND_PURCHASE_COST]`、`[BUILDING_UPGRADE_COST]`、`[EVENT_REWARD_PROBABILITY]`、`[EVENT_PENALTY_PROBABILITY]`、`[MAX_ROUNDS]`、`[FIRST_PLACE_REWARD]`、`[SECOND_PLACE_REWARD]`、`[THIRD_PLACE_REWARD]`、`[FOURTH_PLACE_REWARD]`、`[AI_DECISION_DELAY]`、`[DAILY_FIRST_PLAY_BONUS]`、`[BOARD_EVENT_AFFECTION_EXP]`、`[EVENT_COUNT_PER_CHARACTER]`、`[BUILDING_COUNT_PER_CHARACTER]`、`[INITIAL_CHARACTER_COUNT]`、`[BATCH_CHARACTER_COUNT]`、`[BALANCE_TOLERANCE]`等常量的定义。这些常量在系统案和程序蓝图中被广泛引用，但数值说明书仅提供了动态字段，未提供这些基础配置常量的数值或公式。
- 修改建议: 请在数值说明书中新增一个`constants`或`config_values`部分，明确列出所有占位符常量的具体数值或计算公式，确保数值配表完整。
### Issue 4
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 5.1 启动时加载
- 问题描述: 程序蓝图5.1节中列出了大量常量配置（如`BOARD_TILE_COUNT`、`STARTING_COINS`等），但数值配表（`system_numerical_docs.json`和`data.json`）中并未提供这些常量的具体数值。程序蓝图假设这些常量存在，但数值策划未输出，导致配置挂载时数据缺失。
- 修改建议: 请与数值策划确认这些常量的具体数值，并在`system_numerical_data.json`中补充，或由程序在代码中定义默认值并标注为待数值策划填充。
### Issue 5
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 棋盘构成 - 边界与异常兜底
- 问题描述: 系统案2.1节提到'若玩家踩中他人地块但`[BOARD_COINS]`不足以支付过路费，进入“破产”状态'，但2.2节中破产后的处理逻辑（借贷或结束游戏）与2.1节的描述存在潜在冲突：2.1节直接跳转到破产状态，未说明是否先尝试支付再破产。这可能导致玩家在踩中他人地块时，即使有部分金币也会直接破产，而不是先扣除可用金币。
- 修改建议: 请明确踩中他人地块时金币不足的具体处理流程：是直接进入破产状态，还是先扣除所有可用金币后再判断是否破产？并确保与2.2节的破产逻辑一致。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 胜负与结算 - 边界与异常兜底
- 问题描述: 系统案2.3节提到'若玩家中途退出，视为弃权，不获得任何奖励，不扣除任何资源'，但未说明中途退出后对局是否继续（AI是否继续运行），以及玩家再次进入时能否恢复对局。程序蓝图3.1节虽然提到了断线重连的`SyncGameSnapshot`接口，但系统案未定义中途退出与断线重连的关系。
- 修改建议: 请补充中途退出后的对局状态处理逻辑：是直接结束对局（AI停止），还是保留对局供玩家恢复？若保留，需明确恢复时限。
### Issue 7
- 责任方: numerical_planner
- 目标文件: data.json
- 锚点: continuous_formulas
- 问题描述: 数值配表`data.json`中`continuous_formulas`的`player_board_coins`、`player_total_earnings`、`player_total_expenses`、`character_affection_exp`等字段的`growth`均为0，`type`为`linear`。这意味着这些字段在游戏中不会自动增长，完全依赖外部事件（如购买、事件）修改。但系统案中描述了这些字段会通过游戏行为动态变化，数值配表未提供事件奖励/惩罚的具体数值或公式，导致这些字段的数值来源缺失。
- 修改建议: 请补充事件奖励/惩罚的具体数值（如`EVENT_REWARD_AMOUNT`、`EVENT_PENALTY_AMOUNT`），或提供基于概率的随机数值范围，确保`player_board_coins`等字段有明确的数值变化来源。
**当前审查总计问题:** 7 个

--- 审查时间: 2026-05-30 15:08:44 ---
### Issue 1
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 / 5.1 启动时加载 / 经济常量
- 问题描述: 程序蓝图中的 `PASS_START_BONUS` 默认值设为 80，但数值说明书的 `relations_and_enums` 中建议值为 20。根据领域裁决原则，具体数值冲突以数值策划为准，程序蓝图中的默认值 80 与数值策划的建议值 20 不一致，可能导致经济循环失衡。
- 修改建议: 将 `PASS_START_BONUS` 的默认值从 80 修改为 20，以匹配数值策划的建议值。
### Issue 2
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载 / 5.1 启动时加载 / 好感度常量
- 问题描述: 程序蓝图中的 `BOARD_EVENT_AFFECTION_EXP` 默认值设为 10，但数值说明书的 `relations_and_enums` 中建议值为 5。根据领域裁决原则，具体数值冲突以数值策划为准，程序蓝图中的默认值 10 与数值策划的建议值 5 不一致，可能导致好感度增长过快。
- 修改建议: 将 `BOARD_EVENT_AFFECTION_EXP` 的默认值从 10 修改为 5，以匹配数值策划的建议值。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.3 胜负与结算 / 边界与异常兜底
- 问题描述: 系统策划案中描述了断线重连机制，但未明确 `player_current_game_id` 字段的数据类型（Int/String）及其在数值说明书和程序蓝图中的对应关系。数值说明书中未定义此字段，程序蓝图中也未提及该字段的存储与校验逻辑，导致字段遗漏。
- 修改建议: 在系统策划案中明确 `player_current_game_id` 的数据类型（建议为字符串类型，用于唯一标识对局会话），并在数值说明书的 `field_dictionary` 中补充该字段的定义，同时在程序蓝图的后端持久化数据部分添加该字段的存储与校验逻辑。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.3 胜负与结算 / 边界与异常兜底
- 问题描述: 系统策划案中描述了断线重连机制，但未明确 `GAME_STATE_ABANDONED` 和 `GAME_STATE_IN_PROGRESS` 状态码的具体定义（如数据类型为字符串还是整数），也未在数值说明书的 `field_dictionary` 中定义这些状态码字段。程序蓝图中也未提及这些状态码的存储与校验逻辑，导致逻辑死胡同。
- 修改建议: 在系统策划案中明确 `GAME_STATE_ABANDONED` 和 `GAME_STATE_IN_PROGRESS` 的数据类型（建议为字符串枚举），并在数值说明书的 `field_dictionary` 中补充这些字段的定义，同时在程序蓝图的后端持久化数据部分添加对局状态字段的存储与校验逻辑。
### Issue 5
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 / 2.3 胜负与结算 / 边界与异常兜底
- 问题描述: 系统策划案中描述了断线重连机制，但未明确 `RECONNECTION_GRACE_PERIOD` 的具体数值（仅建议120秒），也未在数值说明书的 `relations_and_enums` 中定义该常量。程序蓝图中也未提及该常量的加载与使用逻辑，导致字段遗漏。
- 修改建议: 在数值说明书的 `relations_and_enums` 中明确 `RECONNECTION_GRACE_PERIOD` 的数值（建议120秒），并在程序蓝图的 `五、数值与配置表挂载` 部分添加该常量的定义与加载逻辑。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 15:10:52 ---
### Issue 1
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 3.1 持久化数据 (DB) - 对局状态表
- 问题描述: 程序蓝图中的`ai_opponent_coins_list`和`ai_opponent_position_list`字段类型为JSON数组，但数值说明书中`ai_opponent_coins`和`ai_opponent_position`定义为单个整数。系统策划案中AI对手数量可变（2-3个，最低1个），因此后端需要存储多个AI的状态，使用数组是合理的。但数值说明书中的字段定义与程序蓝图中的存储结构不一致，且数值配表中`ai_opponent_coins`的base值150与`ai_opponent_list`的默认空数组冲突。
- 修改建议: 数值策划需在`field_dictionary`中明确`ai_opponent_coins`和`ai_opponent_position`为数组类型，并更新`discrete_milestones`中的默认值。或者，程序蓝图应使用与数值说明书一致的单个字段名，但通过多个记录或索引来区分不同AI。建议统一采用数组结构，并在数值说明书中补充说明。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 - 2.2 经济循环 - 边界与异常兜底
- 问题描述: 系统策划案中描述了破产借贷机制（`[LOAN_AMOUNT]`和`[LOAN_INTEREST_RATE]`），但在数值说明书和数值配表中均未定义这两个常量。这属于逻辑死胡同：借贷功能在系统案中明确提及，但数值层面完全没有提供支撑数据，导致程序无法实现该逻辑。
- 修改建议: 数值策划需在`relations_and_enums`中补充`LOAN_AMOUNT`和`LOAN_INTEREST_RATE`的定义及建议值，并在数值配表中添加对应的常量配置。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 四、经济循环与商业化埋点 - 4.2 付费埋点
- 问题描述: 系统策划案中提到了付费道具（“大富翁专属骰子”、“双倍金币卡”、“角色棋盘皮肤”），但数值说明书和数值配表中完全没有定义这些道具的ID、效果、价格或关联的数值字段。这属于字段遗漏：商业化埋点依赖的道具系统在数值层面完全缺失，导致程序无法实现购买、使用和效果逻辑。
- 修改建议: 数值策划需在数值说明书中新增道具相关的字段（如`item_id`, `item_type`, `item_effect`, `item_price`等），并在数值配表中定义具体道具的配置数据。同时，系统策划需明确道具效果的具体数值（如“双倍金币卡”的倍率）。
### Issue 4
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - `RollDice`
- 问题描述: 程序蓝图中的`RollDice`接口返回了`new_player_position`和`triggered_event_id`，但未返回`player_total_earnings`和`player_total_expenses`的更新值。系统策划案中明确要求记录累计收入和支出（`player_total_earnings`, `player_total_expenses`），且数值配表中定义了这两个字段。接口遗漏了这两个关键字段的同步，可能导致前端显示的总收入/支出与后端不一致。
- 修改建议: 程序蓝图需在`RollDice`接口的返回参数中补充`player_total_earnings`和`player_total_expenses`（更新后）。同样，`PurchaseTile`、`UpgradeTile`、`PayToll`、`TriggerEvent`等涉及金币变化的接口也应同步更新这两个累计字段。
**当前审查总计问题:** 4 个

--- 审查时间: 2026-05-30 15:12:31 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 - 2.2 经济循环
- 问题描述: 系统策划案中描述了当玩家[BOARD_COINS]归零时，可向系统借贷一次（高利息），但未明确借贷的具体数值规则（如借贷金额、利息比例、还款条件），也未说明借贷后是否影响游戏结算或胜负判定。这导致数值策划无法配置相关字段，程序无法实现借贷逻辑。
- 修改建议: 请补充借贷机制的详细规则，包括：借贷金额（固定值或基于当前资产比例）、利息计算方式（如固定利率或复利）、还款触发条件（如经过起点时自动扣除）、以及借贷后对游戏结算的影响（如借贷后最终资产为负值是否算破产）。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 四、经济循环与商业化埋点 - 4.2.1 道具系统字段定义
- 问题描述: 系统策划案中定义了道具系统字段（item_effect_type、item_effect_value等），但未明确这些字段在数值配表中的具体存储结构（如JSON路径或表名），也未说明道具配置与数值配表（system_numerical_docs.json）的挂载关系。程序蓝图（tech_blueprint.md）中提及从system_numerical_data.json解析道具配置，但该JSON中并未包含道具字段。
- 修改建议: 请在数值配表（system_numerical_docs.json）中补充道具配置的完整结构，包括每个道具的ID、效果类型、效果值、价格类型、价格数值等字段，并明确其JSON路径。同时，在系统策划案中补充道具配置与数值配表的引用关系说明。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - board_tile_owner_id
- 问题描述: 数值说明书中将board_tile_owner_id定义为【字符串】类型，但程序蓝图（tech_blueprint.md）中board_game_session的board_tile_owner_id[]被定义为数组（用于存储每个格子的归属角色ID）。根据领域裁决原则，数据类型冲突以Tech Architect为准，但数值策划的字段定义与程序蓝图不一致，可能导致序列化/反序列化错误。
- 修改建议: 请将board_tile_owner_id的字段类型从【字符串】修改为【字符串数组】，并明确数组长度与棋盘总格数（BOARD_TILE_COUNT）一致，每个元素对应一个格子的归属角色ID（空字符串表示无归属）。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - ai_opponent_position
- 问题描述: 数值说明书中定义了ai_opponent_position为【整数】，但未说明当存在多个AI对手时如何存储各自的位置。程序蓝图（tech_blueprint.md）中board_game_session未包含ai_opponent_position字段，且EndTurn接口返回的ai_actions[]中包含了每个AI的ai_opponent_position。这导致多AI场景下的位置数据存储结构不明确。
- 修改建议: 请将ai_opponent_position的字段类型从【整数】修改为【整数数组】，数组长度与AI对手数量一致，每个元素对应一个AI对手的当前位置索引。同时，在数值说明书中补充该字段与ai_opponent_list的对应关系说明。
### Issue 5
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 - 持久化数据 - board_game_session
- 问题描述: 程序蓝图中的board_game_session表（Redis缓存）未包含player_total_earnings和player_total_expenses字段，但StartGame和RollDice接口的返回参数中包含了这两个字段。这导致服务端无法在会话中持久化存储累计收入和支出数据，影响结算逻辑的准确性。
- 修改建议: 请在board_game_session表中补充player_total_earnings和player_total_expenses字段，类型为整数，初始值为0。同时，在RollDice、PurchaseTile、UpgradeTile等接口的实现中，确保这些字段随玩家操作实时更新。
### Issue 6
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 - 核心校验逻辑 - 破产借贷校验
- 问题描述: 程序蓝图中的破产借贷校验仅描述了“是否允许借贷（仅一次，高利息）”，但未实现具体的借贷逻辑（如借贷金额、利息计算、还款机制）。系统策划案中提到了借贷机制，但未提供具体数值规则，导致程序无法实现该功能。
- 修改建议: 请与系统策划和数值策划协商，明确借贷的具体规则（如借贷金额固定为100金币、利息为50%、还款时自动扣除），并在RequestLoan接口中实现完整的借贷校验逻辑，包括：检查是否已借贷过、计算扣除利息后的实际到账金额、更新player_board_coins、记录借贷状态。
**当前审查总计问题:** 6 个

--- 审查时间: 2026-05-30 15:14:53 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 经济循环 - 破产借贷
- 问题描述: 系统案中仅描述了破产时可向系统借贷一次（高利息），但未明确借贷的具体金额、利息计算方式、还款机制以及借贷后的游戏状态（是否继续游戏）。程序蓝图补充了这些细节，但系统案作为最高解释权文档，缺少这些关键逻辑定义。
- 修改建议: 请在系统案2.2节中补充破产借贷的完整逻辑：借贷金额（固定值或基于起始资金的比例）、利息计算方式（固定利率或复利）、还款时机（结算时扣除或后续回合分期）、借贷后玩家是否可继续游戏（若再次破产则直接结束）。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.1 棋盘构成 - 棋盘格类型
- 问题描述: 系统案描述了五种棋盘格类型（空地、已购地、事件格、起点格、特殊格），但未定义特殊格的具体行为逻辑（如传送、抽卡、奖励翻倍等）。数值说明书和程序蓝图均未涉及特殊格的实现，导致该类型格子缺乏完整的玩法定义。
- 修改建议: 请在系统案2.1节中补充特殊格的行为规则：触发条件、效果类型（如传送至指定格子、随机获得道具、触发小游戏等）、数据变化（如位置变更、货币增减）、表现层反馈。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - board_tile_owner_id
- 问题描述: 数值说明书中将`board_tile_owner_id`定义为字符串类型，但系统案2.1节中描述该字段记录的是'角色ID'，而角色ID在角色系统中通常为整数类型（主键）。数据类型不一致可能导致后续开发中的类型转换问题。
- 修改建议: 请确认角色ID的数据类型（整数或字符串），并统一`board_tile_owner_id`的类型定义。若角色ID为整数，请将数值说明书中的类型改为'整数'；若为字符串，请在系统案中明确说明。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.4 AI对手 - 行为逻辑
- 问题描述: 系统案仅描述了AI对手的简单策略（优先购买空地、优先升级低级地块），但未定义AI对手在以下场景的具体行为：1) 当AI资金不足时的处理方式（是否借贷、是否跳过行动）；2) AI对手之间的交互规则（是否互相支付过路费）；3) AI对手的破产判定与退出机制。这些缺失可能导致AI行为不可预测。
- 修改建议: 请在系统案2.4节中补充AI对手的完整行为逻辑：资金不足时的兜底策略（如跳过购买/升级、自动借贷、或直接破产退出）、AI之间的经济交互规则（是否互相支付过路费）、AI破产判定条件（资金归零或负值）及退出后的处理（地块归属、剩余AI数量变化）。
### Issue 5
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 - 单局游戏临时数据
- 问题描述: 程序蓝图将`board_tile_owner_id`、`tile_level`等单局游戏数据存储在Redis/内存中，但未定义这些数据在玩家断线重连时的恢复机制。系统案6.3节提到了断线重连（SyncBoardProgress），但程序蓝图未实现该API的数据恢复逻辑。
- 修改建议: 请在程序蓝图三节中补充断线重连的数据恢复方案：1) 定义单局游戏数据的持久化策略（如每回合结束后落盘至临时表，或使用Redis持久化）；2) 实现SyncBoardProgress接口的数据组装逻辑，确保断线玩家能恢复完整的棋盘状态（包括格子归属、等级、AI位置等）。
### Issue 6
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 4.2.1 道具系统字段定义 - item_effect_type
- 问题描述: 系统案定义了道具效果类型枚举（FREE_PASS、DOUBLE_DICE、COIN_BOOST等），但未定义这些效果在游戏中的具体触发时机和实现逻辑。例如：FREE_PASS是免过一次过路费还是免过一次事件惩罚？DOUBLE_DICE是双倍骰子点数还是双倍移动步数？COIN_BOOST是全局倍率还是单次倍率？这些歧义可能导致开发实现与设计意图不符。
- 修改建议: 请在系统案4.2.1节中补充每个道具效果类型的详细行为定义：触发条件（主动使用/被动触发）、生效范围（单次/持续回合）、效果计算方式（加法/乘法）、与其他效果的叠加规则。
### Issue 7
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - ai_opponent_position
- 问题描述: 数值说明书中将`ai_opponent_position`定义为对象类型（键为AI角色ID字符串，值为整数位置索引），但程序蓝图三节中将其列为单局游戏临时数据，未定义该字段在API通信中的序列化格式。同时，系统案2.4节中未明确AI对手的位置数据是否需要同步给前端。
- 修改建议: 请确认AI对手位置数据的同步策略：1) 若前端需要展示AI位置，请在程序蓝图API定义中补充AI位置数据的传输字段；2) 若前端不需要，请在数值说明书中注明该字段仅服务端使用；3) 统一`ai_opponent_position`的数据结构定义（对象 vs 数组），确保前后端一致。
**当前审查总计问题:** 7 个

--- 审查时间: 2026-05-30 17:26:18 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 收藏机制（混合模式）
- 问题描述: 系统策划案中收藏机制描述为“混合模式”，但未明确说明“混合”的具体含义（自动+手动），且未定义自动收藏与手动收藏的优先级或冲突处理规则（例如：手动取消收藏后，自动收藏条件是否重新触发）。
- 修改建议: 建议在系统案中补充“混合模式”的明确定义，并说明自动收藏与手动收藏的互斥或覆盖逻辑，例如：手动取消收藏后，若邮件仍满足自动收藏条件，是否再次自动收藏。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 收藏匣
- 问题描述: 系统策划案中收藏匣支持“按角色ID、邮件类型筛选”，但数值说明书和程序蓝图中均未定义筛选接口的请求参数（filter_character_id, filter_mail_type）的具体数据类型和默认值，存在逻辑断层。
- 修改建议: 建议在系统案中明确筛选参数的数据类型（如character_id为int64，mail_type为enum string），并补充默认值（如0表示全部角色，空字符串表示全部类型）。
### Issue 3
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 3.1 持久化数据 (DB) - player_mail表
- 问题描述: 程序蓝图中的player_mail表缺少字段 `favorite_capacity`，该字段在数值说明书和系统案中均被提及为玩家维度的收藏匣容量上限，但程序蓝图仅在全局配置表 `mail_system_config` 中定义了全局容量，未提供玩家个性化容量的存储方案。
- 修改建议: 建议在player_mail表中增加 `favorite_capacity` 字段（int32），或明确说明玩家个性化容量由全局配置统一控制，并在系统案中同步更新。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.mail_content_production_phase
- 问题描述: 数值说明书中定义了 `mail_content_production_phase` 字段，但系统策划案中仅提及“首批覆盖[INITIAL_CHARACTER_COUNT]个高人气角色”，未定义该字段与角色互动邮件内容的关联逻辑（例如：该字段如何控制哪些角色的邮件可用）。
- 修改建议: 建议在数值说明书中补充该字段与角色ID的映射关系，或在系统案中明确该字段的用途（如：仅当角色的生产阶段编号 <= 当前阶段时，才生成角色互动邮件）。
**当前审查总计问题:** 4 个

--- 审查时间: 2026-05-30 17:28:08 ---
### Issue 1
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 持久化数据 (DB) - player_mail 表 - favorite_capacity 字段
- 问题描述: 程序蓝图在 player_mail 表中定义了 favorite_capacity 字段（int32，默认值50），但数值说明书（field_dictionary）中 favorite_capacity 是全局配置（int，默认值100），并非玩家维度的字段。系统策划案也将其描述为全局容量上限。这导致数据类型与存储逻辑断裂：蓝图将其作为玩家维度的可覆盖字段，而数值与系统案均视为全局固定值。
- 修改建议: 将 player_mail 表中的 favorite_capacity 字段移除，改为从全局配置表 MailSystemConfig 中读取。若需要玩家维度的个性化上限，应在数值说明书中新增一个玩家维度的字段或配置表，并明确其覆盖规则。
### Issue 2
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 数值与配置表挂载 - default_filter_mail_type 默认值
- 问题描述: 程序蓝图配置表中 default_filter_mail_type 的默认值设为 -1，但系统策划案中明确 filter_mail_type 的数据类型为 int，默认值为 [DEFAULT_FILTER_MAIL_TYPE]（表示不筛选）。数值说明书中 mail_type 枚举范围为 0~2，-1 不在枚举范围内，且系统案未定义 -1 作为合法默认值。这导致筛选接口的默认值类型与枚举定义冲突。
- 修改建议: 将 default_filter_mail_type 的默认值改为 0 或一个在系统案中明确定义的占位值（如 -1 需在系统案中补充说明），并确保与数值说明书中的 mail_type 枚举范围一致。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 收藏匣 - 筛选接口请求参数定义
- 问题描述: 系统策划案中 filter_mail_type 的数据类型定义为 int，但未明确说明默认值 [DEFAULT_FILTER_MAIL_TYPE] 的具体数值。程序蓝图将其设为 -1，但 mail_type 枚举（0=运营，1=系统，2=角色互动）中不包含 -1，导致逻辑死胡同：前端无法确定传入 -1 时后端应如何解释（是表示不筛选还是非法值）。
- 修改建议: 在系统策划案中明确 [DEFAULT_FILTER_MAIL_TYPE] 的具体数值（例如 -1 或 999），并补充说明该值不在 mail_type 枚举范围内，仅作为“不筛选”的标记。同时确保数值说明书中的枚举定义不包含该值。
### Issue 4
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - favorite_capacity
- 问题描述: 数值说明书中 favorite_capacity 的默认值为 100，但程序蓝图中的默认值写为 50，两者不一致。虽然禁止比对具体数值大小，但这里存在字段默认值的数据类型冲突：数值说明书定义为 int（默认100），蓝图定义为 int32（默认50），且蓝图将其作为玩家维度的可覆盖字段，而数值说明书未提供玩家维度的覆盖机制。这属于字段定义与使用方式的逻辑断裂。
- 修改建议: 统一 favorite_capacity 的定位：要么在数值说明书中明确其为全局配置（默认100），并移除蓝图中的玩家维度字段；要么在数值说明书中新增玩家维度的 favorite_capacity 字段，并明确其默认值与覆盖规则。
### Issue 5
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 数值与配置表挂载 - 配置键列表
- 问题描述: 程序蓝图配置表中引用了多个系统策划案中的占位符（如 [MAIL_LIST_PAGE_SIZE]、[OPERATION_MAIL_EXPIRY_DAYS]、[SYSTEM_MAIL_EXPIRY_DAYS]、[AFFECTION_MILESTONE_LEVEL_1]、[AFFECTION_MILESTONE_LEVEL_2]、[MAIL_CONTENT_PER_CHARACTER]、[INITIAL_CHARACTER_COVERAGE]），但这些占位符在系统策划案中并未定义具体数值，也未在数值说明书或数值配表中提供。这导致配置表加载时缺少数据源，属于字段遗漏。
- 修改建议: 在系统策划案中为所有占位符补充具体数值，或在数值说明书中新增对应字段，并确保程序蓝图从正确的数据源读取。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-05-30 17:30:03 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 收藏匣 - 筛选接口请求参数定义
- 问题描述: 系统策划案中定义了筛选接口参数 `filter_mail_type` 的数据类型为 `int`，默认值为 `[DEFAULT_FILTER_MAIL_TYPE]`，但未在文档中明确给出该默认值的具体数值。同时，在 2.3 节中出现了两个相同编号的标题（2.3 收藏匣 和 2.3 收藏匣 - 筛选接口请求参数定义），导致结构混乱。
- 修改建议: 请统一 2.3 节的标题编号，避免重复。并明确 `[DEFAULT_FILTER_MAIL_TYPE]` 的具体数值（例如 -1），以便与数值说明书和程序蓝图中的配置保持一致。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.5 邮件删除
- 问题描述: 系统策划案中删除邮件的前置条件要求 `is_claimed` 为 `true`（若有附件），但后续边界描述中又提到“若邮件附件未领取，删除前弹窗提示‘附件尚未领取，确认删除？’”，这意味着附件未领取时也可以删除，与前置条件矛盾。
- 修改建议: 请明确删除邮件的核心规则：是强制要求附件必须已领取才能删除，还是允许未领取时通过二次确认删除？请修正前置条件或边界描述，确保逻辑一致。
### Issue 3
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary.favorite_capacity
- 问题描述: 数值说明书中 `favorite_capacity` 的默认值为 100，但系统策划案 6.1 节中提到的示例值为 200（`[FAVORITE_CAPACITY]` 如：200封）。虽然根据最高裁决法则，具体数值冲突不视为 Issue，但此处存在一个逻辑断层：系统策划案中收藏匣容量上限的配置方式未明确是全局固定值还是玩家维度的可覆盖字段，而数值说明书明确其为玩家维度的可覆盖字段，程序蓝图也据此实现。系统策划案中未提及该字段的玩家维度可覆盖特性。
- 修改建议: 请在系统策划案 6.1 节中补充说明 `favorite_capacity` 为玩家维度的可覆盖字段，并明确运营后台可针对特定玩家调整上限的机制，以与数值说明书和程序蓝图保持一致。
### Issue 4
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的 `Mail_GetFavoriteList` 接口请求参数包含 `filter_mail_type`，但未定义该参数的数据类型。系统策划案 2.3 节中明确其为 `int` 类型，数值说明书 `implementation_notes` 中也提到默认值为 -1，但程序蓝图未显式声明其类型和默认值，存在数据类型断裂风险。
- 修改建议: 请在 `Mail_GetFavoriteList` 接口的请求参数定义中，明确 `filter_mail_type` 的数据类型为 `int`，默认值为 `-1`，并注明有效枚举值（0/1/2），与系统策划案和数值说明书保持一致。
**当前审查总计问题:** 4 个

--- 审查时间: 2026-05-30 17:31:44 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 收藏机制（混合模式）
- 问题描述: 系统案提到收藏匣上限为 `[FAVORITE_CAPACITY]`（如：200封），但数值说明书和配表中 `favorite_capacity` 的默认值为100。虽然禁止比对具体数值，但此处系统案使用了占位符 `[FAVORITE_CAPACITY]` 而非具体数值，且举例为200，与数值表默认值100存在逻辑断层，可能导致实现时混淆。
- 修改建议: 建议系统策划将 `[FAVORITE_CAPACITY]` 替换为明确的引用，如“收藏匣上限由数值表 `favorite_capacity` 字段定义”，并删除举例数值200，避免与数值表默认值100冲突。
### Issue 2
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中的 `Mail_GetMailList` 接口返回 `mail_list` (array<MailObject>)，但未定义 `MailObject` 的具体字段结构。系统案和数值表定义了多个字段（如 `mail_type`, `is_read`, `is_favorited` 等），但接口文档缺少对返回对象的字段描述，可能导致前后端联调时数据类型或字段遗漏。
- 修改建议: 建议在 `Mail_GetMailList` 接口定义中明确 `MailObject` 的字段列表（至少包含 `mail_id`, `player_id`, `send_timestamp`, `title`, `body`, `attachment_list`, `expiration_timestamp`, `mail_type`, `is_read`, `is_claimed`, `is_favorited`, `is_deleted`, `character_id`, `activity_id`, `admin_id`），并注明字段类型与约束。
### Issue 3
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.5 邮件删除
- 问题描述: 系统案描述了删除邮件时若附件未领取需弹窗提示“附件尚未领取，确认删除？”，但未定义玩家确认后附件是否自动领取或永久丢失。程序蓝图中的 `Mail_DeleteMail` 接口仅校验 `is_favorited`，未处理附件未领取时的逻辑分支，导致流程断裂。
- 修改建议: 建议系统策划明确删除未领取附件邮件时的处理规则（如：附件永久丢失或自动领取），并在程序蓝图中补充对应的后端校验逻辑（如：若附件未领取且玩家确认删除，则 `is_claimed` 置为 `true` 但道具不发放，或直接删除并标记附件丢失）。
**当前审查总计问题:** 3 个

--- 审查时间: 2026-05-30 17:33:07 ---
### Issue 1
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 收藏机制（混合模式）
- 问题描述: 系统策划案中描述收藏匣上限为 `[FAVORITE_CAPACITY]`（如：200封），但数值说明书和数值配表中 `favorite_capacity` 的默认值为100。虽然根据最高裁决法则，数值冲突不报，但此处存在逻辑断裂：系统案中未明确 `favorite_capacity` 是玩家维度字段，也未说明初始默认值，导致下游程序蓝图在挂载配置时只能依赖数值文档，而系统案中的举例（200封）与数值默认值（100）存在误导性矛盾，可能引发实现歧义。
- 修改建议: 系统策划应在系统案中明确 `favorite_capacity` 为玩家维度字段，并引用数值文档中的默认值（100），避免使用举例数值（200）造成混淆。
### Issue 2
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.5 邮件删除
- 问题描述: 系统策划案中描述删除操作时，若附件未领取则弹出确认弹窗，但未明确弹窗确认后是否执行 `Mail_DeleteMail` API 的调用。程序蓝图中的 `Mail_DeleteMail` API 返回参数仅包含 `success: bool`，未提供区分“附件未领取确认删除”与“附件已领取直接删除”的 `error_code` 或状态码，导致前端无法根据后端返回判断是否需要弹出确认弹窗。这属于逻辑死胡同：系统案描述了交互流程，但程序蓝图缺少对应的接口状态定义。
- 修改建议: 系统策划应在系统案中明确删除操作的完整交互流程，包括弹窗确认后的API调用逻辑。程序蓝图应在 `Mail_DeleteMail` API 的返回参数中增加 `error_code` 字段，用于标识“附件未领取”等场景，以便前端决策是否弹窗。
### Issue 3
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: 程序蓝图中 `Mail_GetMailList` API 的返回参数包含 `favorite_count: int` 和 `favorite_capacity: int`，但数值说明书和数值配表中 `favorite_capacity` 是玩家维度的配置字段，存储在 `player_mail_config_table` 中。程序蓝图未定义 `Mail_GetFavoriteCapacity` 或类似独立接口，而是将容量信息混入邮件列表接口。这可能导致每次拉取邮件列表时都返回容量数据，增加不必要的数据传输。更严重的是，程序蓝图未说明 `favorite_capacity` 在 `player_mail_config_table` 中的更新机制（运营后台动态覆盖），存在字段遗漏风险。
- 修改建议: 程序蓝图应明确 `favorite_capacity` 的获取方式：建议在 `Mail_GetMailList` 中保留 `favorite_capacity` 字段，但需补充说明该值从 `player_mail_config_table` 读取，并定义运营后台动态覆盖该值的接口或RPC协议。
### Issue 4
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.3 收藏匣
- 问题描述: 系统策划案中描述收藏匣支持按角色ID、邮件类型筛选，但未明确筛选功能是前端本地过滤还是后端接口支持。程序蓝图中的 `Mail_GetFavoriteList` API 虽然提供了可选的 `filter_character_id` 和 `filter_mail_type` 参数，但系统案中未定义筛选逻辑的边界条件（如：当两个筛选参数同时传入时，是AND还是OR逻辑）。这属于流程断裂：系统案描述了功能，程序蓝图实现了接口，但缺少对筛选逻辑的明确约定。
- 修改建议: 系统策划应在系统案中明确收藏匣筛选的逻辑（AND/OR），并补充筛选参数的边界条件（如：空值处理、无效ID处理）。程序蓝图需根据系统案补充筛选逻辑的注释说明。
### Issue 5
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary
- 问题描述: 数值说明书中 `favorite_capacity` 的默认值为100，但系统策划案中举例为200（虽然根据最高裁决法则不报数值冲突），然而数值配表中的 `continuous_formulas` 中 `favorite_capacity` 的 `base` 为100，与说明书一致。但数值说明书和配表均未定义 `favorite_capacity` 的运营后台动态覆盖机制对应的字段或配置表，导致程序蓝图中的 `player_mail_config_table` 缺乏数据来源定义。这属于字段遗漏：数值文档未提供运营后台可动态覆盖的配置字段。
- 修改建议: 数值策划应在数值说明书中增加 `favorite_capacity_override` 或类似字段，明确运营后台动态覆盖的配置表结构，或补充说明 `favorite_capacity` 可在运行时被运营后台修改，并定义修改后的数据持久化方式。
**当前审查总计问题:** 5 个
