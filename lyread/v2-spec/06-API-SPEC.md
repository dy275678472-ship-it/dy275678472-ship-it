# 06 · API 接口规范

统一前缀 `/api`。除标注「公开」外均需 `Authorization: Bearer <JWT>`。
每个扣费接口必须走「预冻结 → 结算/返还」并支持幂等（`Idempotency-Key` 头或 body 字段）。

## 通用返回

成功：`{"success": true, ...}`；失败：HTTP 4xx/5xx + `{"detail": "中文提示"}`。
扣费类成功额外返回：`{"job_id", "reserved", "actual", "balance": {"free","paid"}}`。

## 认证 `/api/auth`

| 方法 | 路径 | 登录 | 说明 |
|---|---|---|---|
| POST | `/register` | 否 | 注册；成功返回 JWT + 赠 30 点 |
| POST | `/login` | 否 | 登录返回 JWT + user |
| GET | `/me` | 是 | 当前用户 |
| POST | `/forgot` `/reset` | 否 | 找回密码（V2.1） |

## 额度 `/api/credits`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/balance` | `{free, paid, reserved}` |
| POST | `/daily-claim` | 领取每日免费额度（幂等按日） |
| GET | `/transactions` | 流水分页 |
| POST | `/estimate` | 传 job_type/参数，返回预计消耗点数 |

## 作品 `/api/story`

| 方法 | 路径 | 登录 | 扣费 | 说明 |
|---|---|---|---|---|
| POST | `/generate-title` | 公开(限流) | 登录用户 1 点/匿名免费一次 | 兼容 `{genre,prompt}`/`{keywords}` |
| POST | `/generate-outline` | 是 | 3 点 | 起承转合 |
| POST | `/generate-chapters` | 是 | 5 点/10 章 | 章纲 |
| POST | `/generate-chapter` | 是 | 10 点/2000字 | 单章正文；成功后触发记忆更新 |
| POST | `/continue` | 是 | 8–10 点 | 续写 |
| POST | `/consistency-check` | 是 | 2 点 | 一致性检测 |
| GET | `/list` | 是 | - | 本人作品（已实现） |
| POST | `/save` `/create` | 是 | - | 保存/新建（已实现，按用户隔离） |
| GET/PUT/DELETE | `/{id}` | 是 | - | 本人作品（已实现） |
| POST | `/publish` | 是 | - | 发布（需过审核） |
| GET | `/{id}/export?format=txt|md` | 是 | - | 导出 |

**扣费流程（所有生成接口统一）：**
1. 计算预计点数 → 校验余额（free 优先，再 paid）→ 写 `credit_transactions(type=reserve)` 并增加 `reserved`。
2. 创建 `generation_jobs(status=running)`。
3. 调模型；成功 → `settle`（按实际字数结算，多退少不补或分档），失败 → `refund`（全额返还，job=failed）。
4. 返回 job 结果与最新余额。

## 章节/记忆 `/api/story/{id}`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/chapters` | 章节列表 |
| GET | `/chapters/{idx}` | 单章 |
| GET | `/memory` | 人物/设定/伏笔/摘要（小说大脑视图） |

## 订单/支付 `/api/orders`

| 方法 | 路径 | 登录 | 说明 |
|---|---|---|---|
| POST | `/create` | 是 | 建订单，返回支付宝下单参数 |
| GET | `/{out_trade_no}` | 是 | 查询订单状态 |
| POST | `/alipay/notify` | 公开(支付宝) | **异步回调：必须验签 + 核对金额/商户号/交易号 + 幂等入账** |

回调硬规则：验签失败/金额不符/重复 `trade_no` → 直接拒绝，不入账，不重复加点数。

## 案例阅读（公开）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/ep/{id}` | 案例阅读页（SEO 友好，已存在） |
| GET | `/api/cases` | 已发布案例列表 |

## 后台 `/api/admin`（仅 admin）

用户/作品/任务/订单/额度调整/审核队列/案例发布计划。所有额度调整写 `credit_transactions(type=admin_adjust)`。

## 错误码约定

`401` 未登录/失效；`403` 越权；`402`/`{detail:"点数不足"}` 余额不足；`409` 重复；`422` 参数错误；`429` 并发/限流超限；`503` 依赖不可用。
