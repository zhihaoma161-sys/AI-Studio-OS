# 全品类美术图鉴 - 程序开发蓝图

## 一、 整体架构概述

本系统为**单机弱联网**模块，核心逻辑（解锁状态、进度计算、奖励发放）均在服务端完成，以保证数据安全与防作弊。前端主要负责美术资产的高精度展示与交互。核心性能瓶颈在于高精度3D模型的加载与渲染，以及CG/音乐资源的流式加载。系统通过事件驱动机制，被动接收来自其他系统（角色获取、武器获取、战斗、剧情、活动）的解锁推送，并异步处理里程碑奖励的发放。

## 二、 前端模块划分 (Client)

### - UI 组件层
1.  **图鉴主界面 (AlbumMainPanel)**:
    -   顶部标题栏：显示“全品类美术图鉴”及总进度百分比。
    -   品类卡片网格：6个一级分类入口卡片，每个卡片展示品类图标、名称、单品类进度百分比、已解锁/总数。
    -   底部总进度里程碑奖励列表：显示所有总进度里程碑条目及其领取状态。
2.  **品类子页面 (CategorySubPanel)**:
    -   角色子页面 (CharacterSubPanel): 立绘/3D模型双视图切换、模型旋转/缩放、剧情回放入口。
    -   武器子页面 (WeaponSubPanel): 3D模型旋转查看、高光材质背景。
    -   敌人子页面 (EnemySubPanel): 原画/设定图展示、模型旋转。
    -   场景子页面 (SceneSubPanel): 原画/概念图展示、全景漫游交互。
    -   CG子页面 (CGSubPanel): 全屏CG展示、缩放、剧情文本/配音回放。
    -   音乐子页面 (MusicSubPanel): 专辑封面UI、播放/暂停/循环控制、动态频谱/背景图。
3.  **条目详情弹窗 (EntryDetailPopup)**:
    -   展示条目名称、稀有度、解锁时间、获取途径提示。
    -   根据条目类型加载对应的预览组件（模型、立绘、CG、音乐播放器）。
4.  **排序/筛选控件 (SortFilterWidget)**:
    -   排序下拉菜单：解锁时间、稀有度、阵营、版本。
    -   筛选条件面板：稀有度、阵营、版本、解锁状态、二级分类。
5.  **奖励领取提示 (RewardClaimToast)**:
    -   里程碑奖励领取成功/失败的轻提示。

### - 表现层控制器
1.  **模型预览控制器 (ModelPreviewController)**:
    -   负责加载和卸载角色/武器/敌人的3D模型。
    -   实现镜头控制（旋转、缩放、平移）。
    -   触发待机动画与物理效果（头发、裙摆）。
    -   **资源缓存策略**:
        -   已解锁条目：根据设备性能（通过API获取设备等级标识）决定缓存策略。高端设备缓存高精度模型（LOD0），中端设备缓存中精度模型（LOD1），低端设备默认仅缓存立绘（Sprite）并禁用3D模型预览。
        -   未解锁条目：仅缓存灰色剪影/锁图标与文本信息（`entry_name`, `acquisition_hint`, `is_obsolete`）。对于 `acquisition_hint` 字段，前端需根据 `is_obsolete` 字段的值进行展示逻辑处理：若 `is_obsolete` 为 `true`，则直接显示“该内容已绝版”；若 `is_obsolete` 为 `false`，则显示 `acquisition_hint` 字段的原始文本。该逻辑完全依赖服务端下发的数据，前端不做任何动态计算。
2.  **CG播放器控制器 (CGPlayerController)**:
    -   管理CG图片的加载、全屏展示与缩放。
    -   同步播放关联的剧情文本与配音音频。
3.  **音乐播放器控制器 (MusicPlayerController)**:
    -   管理音频资源的加载、播放、暂停、循环。
    -   驱动动态频谱可视化或切换背景静态图。
4.  **全景漫游控制器 (PanoramaController)**:
    -   为已解锁场景提供360度全景漫游交互。
5.  **特效播放器 (EffectPlayer)**:
    -   在解锁新条目或领取里程碑奖励时播放通用庆祝特效（如粒子、光效）。

## 三、 后端逻辑划分 (Server)

### - 持久化数据 (DB)
-   **玩家图鉴数据表 (player_album_data)**:
    -   `player_id` (主键)
    -   `category_progress` (JSON): 存储每个品类的进度数据，结构为 `Map<category_id, CategoryProgress>`，其中 `CategoryProgress` 包含 `category_unlocked_count`, `category_total_count`, `category_progress`。
    -   `total_progress` (JSON): 存储总进度数据，结构为 `TotalProgress`，包含 `all_categories_unlocked_count`, `all_categories_total_count`, `total_progress`。
    -   `entry_unlock_records` (JSON): 存储所有已解锁条目的记录，结构为 `Map<entry_id, EntryUnlockRecord>`，其中 `EntryUnlockRecord` 包含 `unlock_time`, `unlock_status`。
    -   `milestone_reward_claims` (JSON): 存储所有里程碑奖励的领取状态，结构为 `Map<milestone_id, MilestoneRewardClaim>`，其中 `MilestoneRewardClaim` 包含 `claim_status`。

### - 核心校验逻辑
1.  **解锁事件幂等性校验**：服务端在收到解锁事件（如 `on_character_acquired`）时，必须检查 `entry_unlock_records` 中对应 `entry_id` 的 `unlock_status`。若已为 `true`，则直接忽略该事件，不做任何处理，确保幂等性。
2.  **进度计算校验**：每次解锁事件处理后，服务端必须重新计算 `category_progress` 和 `total_progress`。计算必须严格遵循 `floor((unlocked_count / total_count) * 100)` 公式，确保前后端数据一致。
3.  **里程碑奖励触发与防重复领取校验**：
    -   进度更新后，服务端需遍历所有里程碑阈值（`category_milestone_1` 至 `5`，`total_milestone_1` 至 `5`），判断当前进度是否首次达到或超过某个阈值。
    -   若首次达到，则生成奖励记录，通过异步邮件系统发放，并将对应 `milestone_reward_claims` 中的 `claim_status` 标记为 `true`。
    -   客户端请求领取奖励时，服务端必须校验 `claim_status` 是否为 `false`，防止重复领取。
4.  **奖励发放边界处理**：奖励发放采用异步邮件系统，需处理以下边界情况：
    -   **邮箱满**：邮件系统应支持暂存，待玩家清理邮箱后重新投递。
    -   **玩家离线**：邮件系统应支持离线存储，玩家上线时自动接收。

## 四、 前后端通信协议 (API & 数据对接)

-   **[GetAlbumMainData]**: C->S / 请求参数: 无 / 返回参数: `category_progress` (JSON), `total_progress` (JSON), `milestone_reward_claims` (JSON)。
-   **[GetCategoryDetail]**: C->S / 请求参数: `category_id` (string) / 返回参数: 该品类下所有 `entry_display` 列表 (JSON Array)。
-   **[GetEntryDetail]**: C->S / 请求参数: `entry_id` (string) / 返回参数: 该条目的 `entry_display` 和 `entry_unlock` 数据 (JSON)。
-   **[UnlockEntry]**: S->C / 推送参数: `entry_id` (string), `unlock_time` (int) / 说明: 当其他系统触发解锁事件时，服务端向客户端推送此消息。
-   **[ClaimMilestoneReward]**: C->S / 请求参数: `milestone_id` (string) / 返回参数: 操作结果 (success/fail)。
-   **[UpdateAcquisitionHint]**: S->C / 推送参数: `entry_id` (string), `new_hint` (string), `is_obsolete` (bool) / 说明: 当活动结束，系统策划手动更新 `acquisition_hint` 和 `is_obsolete` 字段后，服务端向在线玩家推送更新。

## 五、 数值与配置表挂载

程序启动时，从 `system_numerical_data.json` 中读取以下配置并加载到内存中的配置表：
1.  **品类定义表 (CategoryDefinitionTable)**: 读取 `category_definition` 数组，建立 `category_id` 到 `CategoryDefinition` 对象的映射。用于前端展示品类名称、图标等。
2.  **条目展示表 (EntryDisplayTable)**: 读取 `entry_display` 数组，建立 `entry_id` 到 `EntryDisplay` 对象的映射。用于前端展示条目名称、稀有度、获取途径提示、绝版状态。
3.  **里程碑阈值配置**: 从 `category_progress` 和 `total_progress` 数组中读取各品类的 `category_milestone_1` 至 `5` 和 `total_milestone_1` 至 `5` 的阈值百分比。这些值作为服务端计算奖励触发点的依据。
4.  **系统联动配置表 (SystemLinkageTable)**: 读取 `system_linkage` 数组，建立 `source_system` + `trigger_event` 到 `linked_entry_id` 的映射。用于服务端在收到其他系统事件时，快速查找需要解锁的图鉴条目。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

-   **阶段一 (P0 - 底层数据与协议)**:
    -   数据库建表：`player_album_data`。
    -   定义并实现核心API：`GetAlbumMainData`, `GetCategoryDetail`, `GetEntryDetail`, `ClaimMilestoneReward`。
    -   实现服务端核心逻辑：
        -   解锁事件监听与幂等性处理。
        -   进度计算（`floor` 向下取整）。
        -   里程碑奖励触发与防重复领取校验。
        -   异步邮件系统对接。
    -   加载并解析 `system_numerical_data.json` 配置表。

-   **阶段二 (P1 - 前端核心表现)**:
    -   搭建UI框架：图鉴主界面、品类子页面、条目详情弹窗、排序/筛选控件。
    -   接入后端API，实现数据驱动UI更新。
    -   实现核心交互：
        -   品类卡片点击跳转。
        -   条目列表的排序与筛选。
        -   已解锁条目的基础展示（立绘、模型预览、CG展示、音乐播放）。
        -   未解锁条目的剪影/锁图标与获取途径提示展示（依赖 `acquisition_hint` 和 `is_obsolete` 字段）。
    -   实现里程碑奖励列表展示与领取功能。

-   **阶段三 (P2 - 表现层打磨与边缘处理)**:
    -   接入模型LOD分级策略与低端设备立绘模式。
    -   实现模型预览的物理效果（头发、裙摆）与镜头控制。
    -   实现CG播放器的剧情文本与配音回放。
    -   实现音乐播放器的动态频谱可视化。
    -   实现场景全景漫游。
    -   实现解锁新条目/领取奖励的特效播放。
    -   处理边缘异常：
        -   断线重连后数据同步。
        -   邮箱满时奖励暂存逻辑的前端提示。
        -   活动结束后，`acquisition_hint` 与 `is_obsolete` 字段更新的实时推送处理。