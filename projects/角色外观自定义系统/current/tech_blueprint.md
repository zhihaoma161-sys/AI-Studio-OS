# 角色外观自定义系统 - 程序开发蓝图

## 一、 整体架构概述
本系统为**纯表现层**模块，所有操作仅改变角色外观视觉表现，不涉及任何战斗属性修改。系统核心为**客户端实时渲染**，需要处理高频率的HSV调色实时预览（GPU实例化渲染），因此**前端性能是核心瓶颈**。后端主要负责染色方案数据的持久化存储、染色材料消耗校验与扣减、以及染色方案云端同步。系统**非强联网**，但染色方案数据需支持跨场景（大厅、战斗、拍照）同步，因此需要后端接口提供数据存取能力。

## 二、 前端模块划分 (Client)

### - UI 组件层
1. **主入口界面**：角色详情页/大厅换装入口按钮。
2. **时装列表界面**：展示当前角色已拥有的时装卡片（含默认基础时装），支持点击切换。
3. **染色主界面**：左半屏模型展示 + 右半屏调色面板布局。
   - **模型展示组件**：支持近肩特写视角，可手动旋转/缩放。
   - **分区选择组件**：模型上可点击的染色分区高亮（边缘发光）。
   - **调色面板组件**：色相环（圆形拖拽）、饱和度滑块（横向）、明度滑块（横向）。
   - **染色模式选择组件**：基础/金属/渐变/珠光模式切换。
4. **预设方案管理界面**：
   - 预设列表（卡片式展示，显示方案名称和缩略色块）。
   - 预设命名弹窗（限制 `preset_name_max_length` 字符）。
   - 预设操作菜单（切换/重命名/删除/覆盖）。
5. **材料不足提示界面**：快捷购买弹窗。
6. **焕新展示动画组件**：镜头环绕、角色展示姿势、粒子特效。
7. **分区解锁状态指示器**：锁图标/解锁状态显示。

### - 表现层控制器
1. **实时预览控制器**：监听HSV滑块变化，驱动模型材质参数实时更新（使用GPU实例化渲染）。
2. **分区高亮控制器**：点击分区时触发边缘发光效果。
3. **模型过渡动画控制器**：预设方案切换时，根据 `preset_switch_animation_duration` 执行线性插值过渡。
4. **焕新展示动画控制器**：染色应用成功后播放，时长由 `reveal_animation_duration` 控制。
5. **低端设备降级控制器**：检测设备性能（如iPhone 8/骁龙845），自动将高级染色模式降级为基础染色效果。
6. **物理与材质联动控制器**：确保染色改变影响材质表现（高饱和度反光更强，深色区域布料纹理更明显），角色物理（头发、裙摆）在展示动画中保持活跃。

## 三、 后端逻辑划分 (Server)

### - 持久化数据 (DB)
1. **`character_data` 表**：新增字段 `outfit_dye_data` (JSON) - 存储角色当前穿戴时装的染色方案数据，包含所有分区的HSV值及特殊模式参数。
2. **`item_definition` 表**：新增字段 `is_dyeable` (bool)、`dye_region_count` (int)、`use_effect_id` (string) - 用于定义时装是否可染色、染色分区数、染色材料使用效果。
3. **`inventory` 表**：存储染色材料道具（基础染色剂、高级染色剂、分区解锁券）的数量，堆叠上限由 `dye_material_stack_limit` 控制。

### - 核心校验逻辑
1. **染色材料消耗校验**：每次应用染色时，服务端必须校验背包中对应材料数量是否 >= `dye_cost_per_region` * 当前染色分区数（或 `dye_cost_per_region_advanced` * 当前染色分区数）。
2. **染色方案保存校验**：校验预设方案数量是否超过 `max_preset_slots`，校验方案名称长度是否超过 `preset_name_max_length`。
3. **分区解锁校验**：校验 `outfit_unlocked_region_count` 是否超过 `dye_region_count`，校验玩家是否拥有足够的分区解锁券。
4. **时装染色权限校验**：校验目标时装的 `is_dyeable` 字段是否为 `true`。
5. **材料消耗防刷校验**：所有材料消耗操作必须在服务端完成，防止客户端篡改。

## 四、 前后端通信协议 (API & 数据对接)

1. **`C2S_GetOutfitList`**: C->S / 请求参数: `character_id` / 返回参数: `outfit_list: [ { outfit_id, outfit_name, is_dyeable, dye_region_count, default_open_region_count, max_preset_slots, unlocked_region_count } ]`
2. **`C2S_GetDyePresetList`**: C->S / 请求参数: `character_id, outfit_id` / 返回参数: `preset_list: [ { preset_id, preset_name, dye_data (JSON) } ]`
3. **`C2S_ApplyDye`**: C->S / 请求参数: `character_id, outfit_id, dye_data (JSON), dye_mode (enum)` / 返回参数: `success: bool, error_code: int`
4. **`C2S_SaveDyePreset`**: C->S / 请求参数: `character_id, outfit_id, preset_name, dye_data (JSON)` / 返回参数: `preset_id, success: bool, error_code: int`
5. **`C2S_SwitchDyePreset`**: C->S / 请求参数: `character_id, outfit_id, preset_id` / 返回参数: `success: bool, error_code: int`
6. **`C2S_DeleteDyePreset`**: C->S / 请求参数: `character_id, outfit_id, preset_id` / 返回参数: `success: bool, error_code: int`
7. **`C2S_UnlockDyeRegion`**: C->S / 请求参数: `character_id, outfit_id` / 返回参数: `new_unlocked_count, success: bool, error_code: int`
8. **`C2S_GetCharacterDyeData`**: C->S / 请求参数: `character_id` / 返回参数: `outfit_dye_data (JSON)` - 用于战斗/拍照场景加载。
9. **`S2C_DyeMaterialUpdate`**: S->C / 推送 / 参数: `material_type, new_count` - 材料数量变化时推送。

## 五、 数值与配置表挂载
程序启动时，从 `system_numerical_data.json` 中读取 `dye_system` 模块下的所有离散字段，并加载到全局配置管理器 `ConfigManager` 中。具体字段如下：
- `is_dyeable` (默认 false)
- `dye_region_count` (默认 0)
- `max_preset_slots` (默认 5)
- `dye_cost_per_region` (默认 1)
- `dye_cost_per_region_advanced` (默认 2)
- `default_open_region_count` (默认 2)
- `regions_per_voucher` (默认 1)
- `preset_switch_animation_duration` (默认 0.5)
- `preset_name_max_length` (默认 20)
- `daily_dye_material_reward` (默认 3)
- `affection_level_interval` (默认 10)
- `affection_dye_material_reward` (默认 5)
- `event_currency_to_dye_material_ratio` (默认 10)
- `dye_material_pack_size` (默认 50)
- `dye_material_pack_price` (默认 300)
- `preset_slot_extension_count` (默认 5)
- `decompose_dye_material_ratio` (默认 0.1)
- `decompose_dye_material_reward` (默认 10)
- `dye_material_stack_limit` (默认 999)
- `reveal_animation_duration` (默认 3.0)
- `preset_data_size` (默认 1.0)

同时，从 `item_definition` 模块读取 `use_effect_id` 为 `EFFECT_DYE_MATERIAL` 的道具定义，用于染色材料的使用逻辑。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

- **阶段一 (P0 - 底层数据与协议)**：
  1. 数据库建表：`character_data` 表新增 `outfit_dye_data` 字段，`item_definition` 表新增 `is_dyeable`、`dye_region_count`、`use_effect_id` 字段。
  2. 定义并实现所有后端 API（C2S_GetOutfitList, C2S_ApplyDye, C2S_SaveDyePreset 等）。
  3. 实现后端核心校验逻辑（材料消耗校验、方案数量校验、分区解锁校验）。
  4. 加载数值配置表到 `ConfigManager`。

- **阶段二 (P1 - 前端核心表现)**：
  1. 搭建染色主界面 UI 框架（左半屏模型 + 右半屏调色面板）。
  2. 实现模型实时预览控制器（HSV 滑块驱动材质参数）。
  3. 接入后端 API，实现核心玩法流程（选择时装 -> 调色 -> 应用染色 -> 消耗材料）。
  4. 实现预设方案管理（保存、切换、删除）。
  5. 实现分区解锁功能（使用分区解锁券）。

- **阶段三 (P2 - 表现层打磨与边缘兜底)**：
  1. 实现焕新展示动画（镜头环绕、粒子特效）。
  2. 实现预设方案切换时的模型过渡动画（线性插值）。
  3. 实现低端设备自动降级逻辑。
  4. 实现材料不足时的快捷购买弹窗。
  5. 实现退出染色界面时的保存确认弹窗。
  6. 实现断线重连后的数据同步逻辑。
  7. 实现染色方案数据的云端增量同步策略。