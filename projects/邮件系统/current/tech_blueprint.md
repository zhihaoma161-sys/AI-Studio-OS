# 邮件系统 - 程序开发蓝图

## 一、 整体架构概述
邮件系统是一个**弱实时性、强数据一致性**的模块。核心性能瓶颈在于**大量玩家同时登录时拉取未读邮件列表的数据库查询压力**，以及**附件领取时的道具发放与背包容量校验**。系统需与运营后台、活动系统、角色好感度系统、战斗结算系统通过**内部RPC**对接。邮件数据采用**软删除**策略，收藏邮件永久保留。

## 二、 前端模块划分 (Client)

### UI 组件层
- **MailMainPanel**：邮件主界面，包含收件箱列表与“收藏匣”入口按钮。
- **MailListItem**：单封邮件列表项，展示发件人头像、标题、时间、附件状态（未领取/已领取）、收藏状态图标、过期倒计时标签。
- **MailDetailPanel**：邮件详情全屏展示页，包含正文、附件领取按钮、收藏/取消收藏按钮、删除按钮。
- **FavoriteCollectionPanel**：收藏匣子页面，采用“回忆录”式卡片UI，支持按角色ID、邮件类型筛选。
- **FavoriteCard**：收藏匣内的单张卡片，正面显示标题与发件人，背面显示正文摘要，支持翻转动画与长按语音触发。
- **EmptyStateWidget**：空状态提示组件，用于收藏匣为空或筛选结果为空时显示。
- **RedDotComponent**：邮件系统红点提示组件，监听未读邮件数量变化。

### 表现层控制器
- **MailAnimationController**：管理收藏按钮“叮”音效播放、卡片翻转动画、附件领取特效与飘字提示。
- **CharacterMailDisplayController**：负责角色互动邮件的特殊表现，包括角色Q版头像加载、立绘资源引用解析、毛玻璃背景视差滚动效果。
- **VoicePlayerController**：管理收藏匣长按卡片时的角色语音播放，需处理设备不支持时的文字降级。
- **ResourceFallbackController**：处理角色立绘资源加载失败时的占位图降级、默认渐变背景切换。

## 三、 后端逻辑划分 (Server)

### 持久化数据 (DB)
- **mail_table**：核心邮件数据表，字段严格对应数值文档 `field_dictionary`，包含 `mail_id` (主键)、`player_id`、`send_timestamp`、`title`、`body`、`attachment_list`、`expiration_timestamp`、`mail_type`、`is_read`、`is_claimed`、`is_favorited`、`is_deleted`、`character_id`、`activity_id`、`admin_id`。
- **player_mail_config_table**：玩家维度的邮件配置表，存储 `player_id` 与 `favorite_capacity`（可被运营后台动态覆盖）。

### 核心校验逻辑
- **附件领取校验**：服务端必须校验 `is_claimed` 状态防止重复领取；校验背包容量，支持部分成功（已成功道具正常发放，失败道具保留 `is_claimed = false` 可重试）。
- **收藏操作校验**：服务端必须校验当前玩家收藏数是否已达 `favorite_capacity` 上限，防止客户端绕过限制。
- **邮件过期自动清理**：定时任务扫描 `expiration_timestamp` 小于当前时间且 `is_favorited = false` 的邮件，自动将 `is_deleted` 置为 `true`。
- **邮件生成权限校验**：仅允许运营后台、活动系统、好感度系统、战斗结算系统通过内部RPC调用邮件生成接口，防止伪造。
- **敏感词拦截**：运营邮件发送前，服务端需进行敏感词过滤，拦截后返回错误码提示运营修改。

## 四、 前后端通信协议 (API & 数据对接)

- **Mail_GetMailList**: C->S / 请求参数: `player_id` / 返回参数: `{ mail_list: array<MailObject>, favorite_count: int, favorite_capacity: int }`。其中 `MailObject` 包含以下字段：
  - `mail_id` (int)
  - `send_timestamp` (int)
  - `title` (string)
  - `body` (string)
  - `attachment_list` (array<int>)
  - `expiration_timestamp` (int)
  - `mail_type` (int, 枚举: 0=运营, 1=系统, 2=角色互动)
  - `is_read` (bool)
  - `is_claimed` (bool)
  - `is_favorited` (bool)
  - `is_deleted` (bool)
  - `character_id` (int)
  - `activity_id` (int)
  - `admin_id` (int)
- **Mail_ReadMail**: C->S / 请求参数: `mail_id` / 返回参数: `{ success: bool }`。服务端将 `is_read` 置为 `true`。
- **Mail_ClaimAttachment**: C->S / 请求参数: `mail_id` / 返回参数: `{ success: bool, failed_items: array<int>, error_code: int }`。`error_code` 用于区分“背包已满”、“附件已领取”、“邮件已过期”等场景。
- **Mail_ToggleFavorite**: C->S / 请求参数: `mail_id`, `new_favorite_status: bool` / 返回参数: `{ success: bool, current_favorite_count: int, error_code: int }`。`error_code` 用于标识“收藏匣已满”等异常。
- **Mail_DeleteMail**: C->S / 请求参数: `mail_id` / 返回参数: `{ success: bool }`。服务端将 `is_deleted` 置为 `true`（仅非收藏邮件可删除）。
- **Mail_GetFavoriteList**: C->S / 请求参数: `player_id`, `filter_character_id` (可选), `filter_mail_type` (可选) / 返回参数: `{ favorite_list: array<MailObject> }`。
- **Mail_NewMailPush**: S->C / 推送参数: `{ mail_object: MailObject }`。当玩家在线时，新邮件到达实时推送。
- **Mail_RedDotUpdate**: S->C / 推送参数: `{ unread_count: int }`。未读邮件数量变化时推送红点更新。

## 五、 数值与配置表挂载
程序启动时，读取 `system_numerical_data.json` 中的 `field_dictionary` 字段，挂载以下配置：
- **favorite_capacity**：从 `field_dictionary` 中读取 `favorite_capacity` 的默认值（100），作为玩家初始收藏匣容量上限。该值可在运行时被运营后台动态覆盖。
- **mail_content_production_phase**：从 `field_dictionary` 中读取 `mail_content_production_phase` 的默认值（0），用于控制前端是否展示角色互动邮件的特殊UI（如角色头像、情感化标题）。当阶段为0时，角色互动邮件降级为普通邮件表现。
- **过期时间默认值**：根据 `mail_type` 在代码中硬编码默认过期时长（运营邮件30天，系统邮件7天，角色互动邮件永不过期），无需从配置表读取，但需预留接口供运营后台覆盖。

## 六、 开发优先级与依赖链路 (执行排期) ★ 核心

### 阶段一 (P0 - 底层数据与协议)
- **建表**：创建 `mail_table` 与 `player_mail_config_table` 数据库表，字段严格对齐数值文档。
- **定义 API**：完成 `Mail_GetMailList`、`Mail_ReadMail`、`Mail_ClaimAttachment`、`Mail_ToggleFavorite`、`Mail_DeleteMail`、`Mail_GetFavoriteList` 的协议定义与序列化。
- **后端核心校验逻辑**：实现附件领取校验（含部分成功逻辑）、收藏上限校验、过期自动清理定时任务。
- **内部RPC对接**：实现与运营后台、活动系统、好感度系统、战斗结算系统的邮件生成接口。

### 阶段二 (P1 - 前端核心表现)
- **UI 框架搭建**：完成 `MailMainPanel`、`MailListItem`、`MailDetailPanel`、`FavoriteCollectionPanel`、`FavoriteCard` 的界面搭建与基础交互。
- **接入后端 API**：前端所有核心接口联调，确保邮件列表拉取、阅读、领取、收藏、删除流程跑通。
- **核心玩法跑通**：实现红点推送逻辑、新邮件实时推送接收、收藏匣筛选功能。

### 阶段三 (P2 - 表现层打磨)
- **特效接入**：附件领取特效与飘字、收藏按钮“叮”音效、卡片翻转动画、毛玻璃背景视差滚动。
- **角色互动邮件特殊表现**：角色头像加载、立绘资源引用解析、情感化标题拼接、语音播放控制器。
- **边缘异常兜底**：背包已满提示、收藏匣已满提示、网络中断回滚、资源加载失败降级、设备不支持语音降级、空状态UI展示。
- **运营后台动态配置**：实现 `favorite_capacity` 的动态覆盖接口、邮件过期时间的运营配置覆盖。