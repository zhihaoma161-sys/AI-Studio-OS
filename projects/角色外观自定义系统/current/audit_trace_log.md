
--- 审查时间: 2026-06-02 15:45:26 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 接口 `Dye_ApplyDye` 的请求参数中包含了 `dye_preset_slot_id` (可选)，用于保存方案至槽位。但系统策划案中，应用染色与保存方案是两个独立的操作（2.2节：点击应用按钮执行染色；2.4节：点击保存当前方案按钮保存至槽位）。蓝图将两个独立步骤合并到一个API中，导致逻辑耦合。如果玩家只想应用染色但不保存（例如临时预览），此API无法支持。同时，`Dye_SavePreset` 接口的存在也与此逻辑冲突。
- 修改建议: 将 `Dye_ApplyDye` 接口的 `dye_preset_slot_id` 参数移除，使其仅执行染色操作（消耗材料、更新当前穿戴数据）。保存方案应完全由 `Dye_SavePreset` 接口负责，该接口应接收当前界面的 `dye_region_hsv_data` 作为参数，而不是依赖 `Dye_ApplyDye` 的结果。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 3.1 持久化数据 (DB)
- 问题描述: 系统策划案（5.2节）明确要求 `character_data` 表新增 `outfit_dye_data` 字段，用于存储当前穿戴时装的染色方案。但蓝图在3.1节中描述 `dye_preset_data` 表时，将其标记为“可选”，并称“若需云端同步，可独立建表”。这存在致命歧义：如果 `dye_preset_data` 表不建，则所有已保存的染色方案（`dye_preset_slot_data`）将仅存储在客户端，无法实现云端同步，与系统策划案（6.3节）中“方案存储支持云端同步”的要求直接冲突。
- 修改建议: 将 `dye_preset_data` 表从“可选”改为“必须”建表，并明确其结构（关联 `character_id` 和 `outfit_id`），用于持久化存储所有已保存的染色方案数据，确保云端同步功能可实现。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 系统策划案（2.5节）描述了高级染色模式（金属/渐变/珠光），这些模式需要额外的材质参数（如金属质感强度、渐变方向、珠光密度）。但 `Dye_ApplyDye` 接口的请求参数 `dye_region_hsv_data` 是一个仅包含HSV值的JSON对象，没有字段用于传递这些高级模式的额外参数。这会导致高级染色模式的参数无法被后端记录和同步。
- 修改建议: 在 `Dye_ApplyDye` 接口的请求参数中，增加一个可选字段 `advanced_params` (JSON对象)，用于存储高级染色模式的额外参数（如 `metal_intensity`, `gradient_direction`, `pearl_density`）。同时，`dye_region_hsv_data` 的结构也应扩展，允许每个分区携带自己的高级参数。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 系统策划案（2.2节）描述了“应用”染色操作后，会播放“焕新展示”动画。但蓝图中的 `Dye_ApplyDye` 接口返回参数中，没有提供任何信息来触发或控制这个动画。虽然动画是纯前端表现，但后端返回的 `success` 状态不足以让前端判断是否应该播放动画（例如，如果后端校验失败，前端不应播放）。
- 修改建议: 在 `Dye_ApplyDye` 接口的返回参数中，增加一个字段 `show_reveal_animation` (布尔)，由后端根据操作结果决定是否建议前端播放动画。这可以避免前端在操作失败时错误地播放动画。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、核心规则与玩法机制 - 2.2 深度自由染色流程
- 问题描述: 系统策划案（2.2节）描述了“应用”染色操作，但未明确说明“应用”操作成功后，当前调色进度（`current_dye_preset_data`）是否会自动保存为一个新的预设方案，还是仅更新当前穿戴的染色数据。这导致了与2.4节（预设方案管理）的边界模糊，并直接导致了上述API设计中的逻辑耦合问题。
- 修改建议: 明确“应用”操作的行为：它仅消耗材料并更新角色当前穿戴的染色数据（`outfit_dye_data`），不会自动保存到预设方案槽位。保存到预设方案槽位是一个独立的、需要玩家主动点击“保存当前方案”按钮的操作。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 15:48:32 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 系统策划案 2.2 节明确要求：'应用'操作成功后，系统将当前调色进度自动保存为一个新的预设方案。但程序蓝图中的 `Dye_ApplyDye` 接口返回参数中，没有返回自动生成的预设方案的索引或数据，导致前端无法获知新方案已生成并更新UI列表。这是一个流程断裂，会导致前端在应用染色后无法正确显示新增的预设方案。
- 修改建议: 在 `Dye_ApplyDye` 的返回参数中，增加一个字段（如 `new_preset_slot_index` 或 `new_preset_data`），用于通知前端自动生成的预设方案信息。
### Issue 2 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 3.1 持久化数据 (DB)
- 问题描述: 系统策划案 5.2 节要求 `character_data` 表新增 `outfit_dye_data` 字段。程序蓝图虽然提到了这个字段，但未定义其具体的数据结构（JSON Schema）。同时，数值配表 `character_data` 中的 `outfit_dye_data` 是一个空对象 `{}`，也未定义结构。这会导致后端开发时对存储格式理解不一致，可能引发数据解析错误。
- 修改建议: 在程序蓝图或数值配表中，明确定义 `outfit_dye_data` 的 JSON 结构，例如：`{"outfit_id": "...", "regions": {"region_1": {"h": ..., "s": ..., "v": ...}, ...}, "dye_mode": "basic"}`。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 3.2 核心校验逻辑
- 问题描述: 系统策划案 2.2 节描述了调色过程中退出界面的兜底逻辑：'系统提示是否保存当前调色进度？'。但程序蓝图中的后端校验逻辑和 API 接口均未定义任何用于'暂存'或'放弃'调色进度的接口或状态管理机制。这会导致该交互逻辑无法实现，玩家退出后调色进度必然丢失。
- 修改建议: 增加一个临时存储调色进度的机制。可以是在前端本地缓存，或者新增一个后端接口（如 `Dye_DiscardDraft`）来明确放弃未保存的进度。
### Issue 4 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - 4.1 核心接口
- 问题描述: 系统策划案 2.4 节提到预设方案列表包含'系统默认配色方案'，且不可删除。但 `Dye_GetOutfitList` 接口返回的 `dye_preset_slot_data` 并未区分方案类型（系统默认 vs 玩家自定义）。前端无法据此判断哪些方案可删除，哪些不可删除。
- 修改建议: 在 `dye_preset_slot_data` 的每个方案元素中，增加一个字段（如 `is_system_default` 布尔值），用于标识该方案是否为系统默认方案。
### Issue 5 [严重级别: 中]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、数值与配置表挂载
- 问题描述: 程序蓝图中的配置表挂载字段列表，缺少了 `max_preset_slots` 字段。该字段在系统策划案和数值配表中均有定义，且是预设方案管理的核心上限。缺少此字段会导致服务端无法正确校验预设方案槽位上限。
- 修改建议: 在程序蓝图第五节的配置表挂载列表中，增加 `max_preset_slots` 字段，类型为整数，默认值为 5。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 15:51:14 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: API 接口 `C2S_ApplyDye` 的请求参数中包含了 `dye_mode (enum)`，但系统策划案和数值说明书中均未定义该字段的枚举值或具体逻辑。系统案仅提及了“基础”和“高级”染色材料，但未说明如何通过 API 传递染色模式（如金属、渐变、珠光）。这会导致后端无法正确解析请求，属于逻辑死胡同。
- 修改建议: 需要在系统策划案或数值说明书中明确 `dye_mode` 的枚举值（如 basic, advanced_metal, advanced_gradient, advanced_pearl），并定义不同模式对应的消耗规则（如高级模式消耗高级材料）。或者，如果染色模式由前端根据材料类型自动决定，则应在 API 文档中移除 `dye_mode` 参数，并补充说明逻辑。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、 后端逻辑划分 (Server) - 持久化数据 (DB)
- 问题描述: 程序蓝图声明需要新增 `outfit_preset_list` 表来存储每个角色每个时装的预设方案列表，但系统策划案和数值配表中均未定义该表的结构、字段或关联关系。这会导致后端开发时缺少数据模型定义，属于严重的字段遗漏。
- 修改建议: 需要在数值说明书或系统策划案中补充 `outfit_preset_list` 表的详细定义，包括主键（如 `character_id + outfit_id + preset_slot_id`）、字段（如 `preset_name`, `dye_data` JSON, `is_system_default` 布尔等）以及与其他表的关联关系。
### Issue 3 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、2.2 深度自由染色流程 - 步骤7
- 问题描述: 系统策划案规定“应用”操作成功后，系统会自动将当前调色进度保存为一个新的预设方案。但程序蓝图中的 `C2S_ApplyDye` API 返回参数中包含了 `new_preset_slot_id`，暗示了自动保存的逻辑。然而，数值配表中的 `max_preset_slots` 字段定义了每个时装的最大方案槽位数。当槽位已满时，自动保存逻辑会与“预设方案已满”的边界处理产生冲突：系统案要求自动保存，但槽位已满时无法保存。这是一个逻辑死胡同。
- 修改建议: 需要明确当预设方案槽位已满时，“应用”操作的行为。建议修改系统案：当槽位已满时，应用染色操作仍然成功（更新 `outfit_dye_data`），但不再自动保存为新预设，而是覆盖当前应用的方案或提示玩家手动删除一个旧方案后再保存。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接) - C2S_ApplyDye
- 问题描述: `C2S_ApplyDye` API 的请求参数中包含了 `dye_data (JSON)`，但未定义该 JSON 对象的具体结构。系统策划案和数值说明书中虽然提到了 `dye_region_hsv_data` 和 `current_dye_preset_data`，但未明确 API 请求中 `dye_data` 应包含哪些字段（例如，是仅包含已修改分区的 HSV 数据，还是包含所有分区的完整数据）。这会导致前后端数据解析不一致。
- 修改建议: 需要在 API 文档中明确定义 `dye_data` 的 JSON Schema，例如：`{"regions": [{"region_id": "collar", "h": 180, "s": 50, "v": 80}, ...], "dye_mode": "basic"}`。同时，数值说明书中的 `dye_region_hsv_data` 字段定义应与此对齐。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 二、2.2 深度自由染色流程 - 边界与异常兜底
- 问题描述: 系统策划案描述了玩家在调色过程中退出染色界面时的提示逻辑（“是否保存当前调色进度？”），但未定义玩家点击“保存为预设”后的具体行为。例如，是直接保存并退出，还是保存后停留在当前界面？此外，该提示与“应用”操作的自动保存逻辑存在潜在冲突：如果玩家在调色后直接退出，系统会询问是否保存；但如果玩家点击“应用”，系统会自动保存。这可能导致玩家困惑。
- 修改建议: 需要明确“保存为预设”按钮的具体流转逻辑（保存后是否关闭界面？），并考虑是否将“应用”和“保存为预设”合并为一个操作，或者明确区分两者的行为（例如，“应用”仅更新当前穿戴染色，不自动保存；“保存为预设”则仅保存方案，不应用）。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 15:53:42 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - C2S_ApplyDye
- 问题描述: API `C2S_ApplyDye` 的请求参数中包含了 `dye_mode: string`，但系统策划案和数值配表中均未定义该字段的枚举值或具体含义。系统案仅提及了基础染色，数值配表虽然定义了 `dye_mode` 枚举（basic, advanced_metal, advanced_gradient, advanced_pearl），但并未说明该参数如何传入 `C2S_ApplyDye` 接口。这导致程序蓝图引入了一个未在系统设计和数值表中明确对接的字段，属于逻辑断链。
- 修改建议: 建议 Tech Architect 与 System Planner 确认 `dye_mode` 参数是否应作为 `C2S_ApplyDye` 的请求参数。如果确认需要，则需在系统策划案中明确染色模式的选择流程，并在数值配表中补充该字段与 `dye_cost_per_region_advanced` 的关联逻辑。如果不需要，则从 API 定义中移除该参数。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 三、后端逻辑划分 (Server) - 核心校验逻辑 - 染色材料消耗校验
- 问题描述: 后端校验逻辑描述为：校验材料数量是否 >= `dye_cost_per_region` * 当前时装已解锁分区数。但系统策划案 2.2 节明确说明消耗逻辑是 `[DYE_COST_PER_REGION] * [已染色分区数]`，即仅对玩家实际修改了颜色的分区收费，而非所有已解锁分区。程序蓝图中的校验逻辑与系统策划案存在严重冲突，会导致玩家被多收费或系统逻辑错误。
- 修改建议: 建议 Tech Architect 修改后端校验逻辑，使其与系统策划案一致：仅对客户端提交的 `dye_data` 中包含的分区（即实际修改的分区）进行材料消耗计算，而非对所有已解锁分区收费。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、前后端通信协议 (API & 数据对接) - C2S_ApplyDye
- 问题描述: API `C2S_ApplyDye` 的返回参数中包含了 `new_material_count: int`，但系统策划案和数值配表中均未定义该字段。系统案仅提到消耗材料，未提及需要返回剩余材料数量。这属于未定义字段，可能导致前端显示逻辑与后端实际数据不一致。
- 修改建议: 建议 Tech Architect 与 System Planner 确认是否需要返回剩余材料数量。如果不需要，则从 API 返回参数中移除该字段。如果需要，则需在系统策划案中明确该字段的用途和显示逻辑。
### Issue 4 [严重级别: 高]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 深度自由染色流程 - 边界与异常兜底
- 问题描述: 系统策划案描述了当玩家在调色过程中退出时，弹出确认弹窗提供三个选项。但未定义当玩家点击“应用”后，系统自动保存草稿并消耗材料，此时若玩家直接退出，是否还需要弹出弹窗。系统案仅提到“无需再次询问”，但未明确此时退出是否应直接关闭界面，还是仍需要某种确认。这属于逻辑死胡同，可能导致前端实现时出现歧义。
- 修改建议: 建议 System Planner 明确补充：在点击“应用”成功后，系统已自动保存当前方案并消耗材料，此时玩家点击返回或关闭按钮，应直接关闭染色界面，无需弹出任何确认弹窗。
### Issue 5 [严重级别: 中]
- 责任方: numerical_planner
- 目标文件: system_numerical_docs.json
- 锚点: field_dictionary - decompose_dye_material_reward
- 问题描述: 数值说明书中定义了 `decompose_dye_material_reward`（分解一件重复时装获得的基础染色材料数量），但数值配表 `data.json` 中同时存在 `decompose_dye_material_ratio` 和 `decompose_dye_material_reward` 两个字段。系统策划案 4.3 节仅提到“分解重复时装少量回收”，未明确回收逻辑是固定值还是基于比例。这两个字段的存在可能导致逻辑冲突（是使用固定值还是比例计算？），属于字段定义冗余且未明确优先级。
- 修改建议: 建议 Numerical Planner 明确分解回收逻辑：是使用固定值 `decompose_dye_material_reward`，还是基于 `decompose_dye_material_ratio` 计算。如果使用固定值，则移除 `decompose_dye_material_ratio` 字段；如果使用比例，则移除 `decompose_dye_material_reward` 字段，并补充计算公式。
**当前审查总计问题:** 5 个

--- 审查时间: 2026-06-02 15:55:45 ---
### Issue 1 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 五、 数值与配置表挂载
- 问题描述: 程序蓝图中声明的默认值与数值配表（data.json）中的默认值存在大量不一致，且蓝图中的默认值并非从数值表读取，而是硬编码了错误的值。例如：max_preset_slots 蓝图写5，数值表为3；dye_cost_per_region_advanced 蓝图写2，数值表为0；daily_dye_material_reward 蓝图写3，数值表为1；dye_material_pack_price 蓝图写300，数值表为60；preset_slot_extension_count 蓝图写5，数值表为2；decompose_dye_material_reward 蓝图写10，数值表为5；reveal_animation_duration 蓝图写3.0，数值表为2.5；preset_data_size 蓝图写1.0，数值表为1024。这会导致程序运行时读取的配置与数值策划的定价和设计完全脱节，属于严重的数据断裂。
- 修改建议: 请 tech_architect 修改 tech_blueprint.md 中“五、数值与配置表挂载”部分，将所有默认值改为与 data.json 中 dye_system 模块的 discrete_milestones 字段完全一致，并明确说明这些值是从 ConfigManager 读取，而非硬编码。
### Issue 2 [严重级别: 致命]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: API C2S_ApplyDye 的请求参数中缺少 dye_mode 字段对应的枚举定义，且系统策划案中提及的“高级染色材料”和“特殊染色模式（金属质感、渐变效果）”在 API 接口和数值表中均未定义对应的枚举值或字段。这导致高级染色功能无法通过接口实现，属于逻辑死胡同。
- 修改建议: 请 tech_architect 在 API 文档中补充 dye_mode 的枚举定义（如：BASIC, METALLIC, GRADIENT），并在 C2S_ApplyDye 的返回参数或相关接口中增加对高级材料消耗的校验逻辑。同时，请 numerical_planner 在数值表中补充 dye_mode 相关的枚举或字段。
### Issue 3 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: API C2S_ApplyDye 的请求参数中缺少 dye_mode 字段对应的枚举定义，且系统策划案中提及的“高级染色材料”和“特殊染色模式（金属质感、渐变效果）”在 API 接口和数值表中均未定义对应的枚举值或字段。这导致高级染色功能无法通过接口实现，属于逻辑死胡同。
- 修改建议: 请 tech_architect 在 API 文档中补充 dye_mode 的枚举定义（如：BASIC, METALLIC, GRADIENT），并在 C2S_ApplyDye 的返回参数或相关接口中增加对高级材料消耗的校验逻辑。同时，请 numerical_planner 在数值表中补充 dye_mode 相关的枚举或字段。
### Issue 4 [严重级别: 高]
- 责任方: tech_architect
- 目标文件: tech_blueprint.md
- 锚点: 四、 前后端通信协议 (API & 数据对接)
- 问题描述: API C2S_GetOutfitList 的返回参数中包含了 default_open_region_count 和 max_preset_slots，但这两个字段是系统级配置，而非每个时装的实例属性。这会导致数据冗余和潜在的不一致。正确的做法是客户端从 ConfigManager 读取这些全局配置。
- 修改建议: 请 tech_architect 修改 C2S_GetOutfitList 的返回参数，移除 default_open_region_count 和 max_preset_slots，改为客户端在启动时从 ConfigManager 加载全局配置。
### Issue 5 [严重级别: 中]
- 责任方: system_planner
- 目标文件: system_design_detail.md
- 锚点: 2.2 深度自由染色流程
- 问题描述: 系统策划案中描述了“若玩家在调色过程中退出（未点击‘应用’），弹出确认弹窗”，但未明确该弹窗的三个选项（保存草稿并退出、放弃修改并退出、取消）中，“保存草稿”的草稿数据存储在哪里？是本地缓存还是服务器？如果是本地，如何保证跨设备同步？如果是服务器，需要新增一个保存草稿的 API。目前程序蓝图中没有对应的接口。
- 修改建议: 请 system_planner 明确“保存草稿”的数据存储方案（本地/服务器），如果涉及服务器存储，请 tech_architect 补充对应的 API（如 C2S_SaveDyeDraft）。
**当前审查总计问题:** 5 个
