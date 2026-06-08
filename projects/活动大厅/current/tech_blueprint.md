# 活动大厅 - 程序开发蓝图

## 一、 整体架构概述
本模块为游戏内所有限时/周期性活动的统一入口框架，采用**弱联网**架构（核心状态由服务器时间驱动，但客户端可基于本地时间做临时兜底）。核心性能瓶颈在于：1) 活动配置表（JSON）的解析与页签列表的动态生成；2) 多张背景插画的预加载与切换性能。系统不承载具体活动玩法逻辑，仅负责页签展示、状态判定与跳转调度。

## 二、 前端模块划分 (Client)

### UI 组件层
- **ActivityHallMainPanel**：活动大厅主界面，包含顶部页签栏（横向滑动容器）与下方内容占位区域。
- **ActivityTabItem**：单个页签组件，显示活动图标、名称、红点状态。
- **MoreTabDropdown**：当页签数量超过 `max_tab_count` 时，折叠至“更多”下拉菜单。
- **EmptyStatePlaceholder**：无可用活动时的占位提示（“暂无活动”）。
- **TimeSyncLoadingOverlay**：时间同步失败时的加载遮罩（“时间同步中...”）。
- **DailySigninPanel**：日签到活动子界面，包含签到按钮、奖励列表、连续签到里程碑展示。
- **CharacterPortraitWidget**：日签到界面中的角色半身立绘组件，支持呼吸动画与表情切换。

### 表现层控制器
- **ActivityBackgroundController**：管理活动大厅背景插画的预加载与切换，支持平滑过渡动画（如淡入淡出）。
- **SigninCharacterController**：控制日签到角色立绘的播放（签到语音、表情变化、飘字特效）。
- **ReddotObserver**：监听 `reddot_update` 事件，刷新主界面入口按钮与页签的红点状态。
- **TimeSyncManager**：负责服务器时间同步请求、本地时间兜底逻辑、重试机制。

## 三、 后端逻辑划分 (Server)

### 持久化数据 (DB)
- **player_signin_data** 表：
  - `player_id` (主键)
  - `current_month` (整数，1-12，默认当前服务器月份)
  - `signed_days_bitmask` (整数，位掩码，默认0)
  - `claimed_reward_tiers` (整数，位掩码，默认0)
  - `consecutive_signin_days` (整数，默认0)
  - `last_signin_date` (整数，Unix时间戳，默认0) — 用于连续签到判定。跨月处理逻辑：当玩家在1月31日签到后，`last_signin_date` 记录为1月31日。2月1日玩家再次签到，服务器判定 `last_signin_date` 的月份（1月）与当前月份（2月）不同，且 `last_signin_date` 为上一月最后一天，则连续签到**不中断**，`consecutive_signin_days` 继承上一月最后一天的连续天数并继续累加。若 `last_signin_date` 与当前日期间隔超过1天（非跨月情况），则连续签到中断重置为1。

### 核心校验逻辑
- **活动状态判定**：服务端根据当前服务器时间戳与活动配置表中的 `start_time`、`end_time` 计算 `current_status`，客户端不可自行判定。
- **签到请求校验**：
  - 校验 `current_month` 是否与服务器当前月份一致，若不一致则自动重置数据。
  - 校验 `signed_days_bitmask` 对应位是否为0（防止重复签到）。
  - 校验 `consecutive_signin_days` 的连续性（基于 `last_signin_date` 与当前日期的差值）。
- **补签请求校验**：
  - 校验漏签天数是否超过 `max_missed_days_for_retroactive`。
  - 校验补签价格（根据 `retroactive_cost_base` 与递增曲线计算）。
  - 校验玩家付费货币是否充足。
- **加速请求校验**：校验 `accelerate_fixed_cost` 是否足够，且未来 `accelerate_days` 天内未签到。
- **奖励发放校验**：调用 `check_bag_space` 接口，若空间不足则调用 `send_mail` 补发。

## 四、 前后端通信协议 (API & 数据对接)

- **`GetActivityHallData`**: C->S / 无参数 / 返回 `activity_config` 数组（完整配置表）及当前服务器时间戳。
- **`GetSigninData`**: C->S / 无参数 / 返回 `player_signin_data` 对象（`current_month`, `signed_days_bitmask`, `claimed_reward_tiers`, `consecutive_signin_days`）。
- **`DoSignin`**: C->S / 无参数 / 返回结果（成功/错误码）。错误码：`err_already_signed` (1001), `err_month_full` (1002)。
- **`DoRetroactiveSignin`**: C->S / 参数 `target_day` (整数，补签目标日期) / 返回结果（成功/错误码）。错误码：`err_already_retroactive` (1003)。
- **`DoAccelerateSignin`**: C->S / 无参数 / 返回结果（成功/失败）。
- **`PushActivityStatusChange`**: S->C / 推送 `activity_id` 与 `new_status`（枚举值：`inactive`/`active`/`ended`）。
- **`PushReddotUpdate`**: S->C / 推送 `activity_id` 与 `is_active` (布尔值)。
- **`SyncServerTime`**: C->S / 无参数 / 返回当前服务器时间戳（秒级Unix时间）。

## 五、 数值与配置表挂载
程序启动时，从 `system_numerical_data.json` 中读取以下字段并缓存：
- **全局参数**：`max_tab_count`, `reddot_timeout_duration`, `max_retry_count`。
- **日签到参数**：`signin_unlock_level`, `month_max_days`, `consecutive_7_days`, `consecutive_14_days`, `consecutive_21_days`, `consecutive_full_month`, `max_missed_days_for_retroactive`, `retroactive_cost_base`, `retroactive_cost_max`, `accelerate_days`, `accelerate_fixed_cost`, `gold_coin_amount`, `monthly_gacha_ticket_fragments_min`, `monthly_gacha_ticket_fragments_max`。
- **活动配置表**：`activity_config` 数组（由运营后台维护，客户端只读）。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

### 阶段一 (P0 - 底层数据与协议)
- 建表：`player_signin_data` 表结构设计（含 `last_signin_date` 字段及跨月处理逻辑）。
- 定义 API：`GetActivityHallData`, `GetSigninData`, `DoSignin`, `SyncServerTime`。
- 后端核心校验逻辑：活动状态机判定、签到/补签/加速校验、连续签到跨月处理。
- 时间同步机制：服务端时间戳下发、客户端重试与本地兜底逻辑。

### 阶段二 (P1 - 前端核心表现)
- UI 框架搭建：`ActivityHallMainPanel`, `ActivityTabItem`, `EmptyStatePlaceholder`, `TimeSyncLoadingOverlay`。
- 接入后端 API：活动页签列表动态生成、状态刷新、红点监听。
- 核心玩法跑通：日签到界面（`DailySigninPanel`）与签到流程联调。

### 阶段三 (P2 - 表现层打磨)
- 特效接入：背景插画预加载与切换动画、签到飘字特效、角色立绘呼吸动画与表情切换。
- 边缘异常兜底：网络断线重连后的状态同步、活动配置表为空时的占位处理、页签数量超出 `max_tab_count` 时的折叠逻辑。
- 红点系统逐级上报机制完善。