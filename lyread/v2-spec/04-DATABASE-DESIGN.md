# 04 · 数据库设计

MySQL 8.0，`utf8mb4`。所有金额/点数用整数点数记账，禁止用浮点余额作为唯一账本。

## V1.9 现存表（现网）

- `users(id varchar(12), username, password_hash, email, vip_level, balance, created_at)`
- `stories(id bigint, user_id varchar(12), title, genre, intro, outline, characters, chapters TEXT, word_count, status, created_at, updated_at)` — 本轮已补 `user_id`/`word_count`
- `contents`、`recommendations`、`user_behaviors`、`user_predictions`、`user_tokens`、`evolution_history`（本轮新增）

## V2 主要问题与修复

1. **章节不应放在 `stories.chapters JSON`**：改独立 `chapters` 表（单章保存、版本、字数、成本、断点续写）。
2. **缺连续创作结构**：新增人物/状态/世界设定/剧情线/伏笔/摘要/记忆快照表。
3. **缺生成任务表**：`generation_jobs` 支撑「生成中/失败重试/失败返还/成本核算」。
4. **余额不安全**：新增 `credit_accounts` + `credit_transactions` 不可变流水，`balance` 只作缓存。
5. **订单缺字段**：商户单号、平台交易号、原始/实付金额、渠道、状态、回调摘要、幂等键、各时间戳、退款状态。

## 表清单（V2 新增/重构）

| 表 | 作用 |
|---|---|
| `story_projects` | 小说项目主表（替代/规范 stories） |
| `volumes` | 分卷 |
| `chapters` | 章节正文 |
| `chapter_versions` | 章节历史版本 |
| `characters` | 人物档案 |
| `character_states` | 人物在各章后的状态 |
| `world_settings` | 背景/规则/势力/地点 |
| `plot_arcs` | 主线/支线剧情 |
| `foreshadowings` | 伏笔：埋设/预计回收/实际回收 |
| `chapter_summaries` | 每章压缩摘要 |
| `story_memory_snapshots` | 阶段性记忆快照 |
| `generation_jobs` | AI 生成任务 |
| `credit_accounts` | 点数账户（免费/充值分账） |
| `credit_transactions` | 不可变点数流水 |
| `orders` | 充值订单 |
| `daily_free_grants` | 每日免费额度发放记录 |
| `system_generation_plans` | 平台自动生成计划 |
| `content_reviews` | 内容审核 |
| `publication_schedules` | 案例发布计划 |
| `story_metrics` | 案例真实表现指标 |

## 关键约束

- `story_projects.user_id`、`chapters.user_id` 均 `NOT NULL` + 外键 + 索引，所有查询按 user 过滤。
- `credit_transactions` 只增不改；每条含 `type`（recharge/daily_grant/reserve/settle/refund/admin_adjust/refund_order）、`amount`（正负）、`balance_after`、`ref_type`、`ref_id`、`idempotency_key`。
- `orders.idempotency_key`、`generation_jobs` 的 reserve/settle 必须幂等。
- 迁移必须可重复执行（`CREATE TABLE IF NOT EXISTS` / 迁移版本表）。
