# LyRead V2 施工包（Construction Package）

本目录是 LyRead 从 V1.9「功能演示原型」升级到 V2「可收费运营版」的完整规格。
来源：ChatGPT 产品定位分析对话的结论 + 对线上 V1.9 代码/数据库的实际核查。

## 背景（当前线上真实状态）

服务器 `101.34.63.137`，Docker 部署。域名 `lyread.cn` → nginx(443) → 后端 `127.0.0.1:8004`（FastAPI）→ MySQL 容器 `lyread-mysql`。

本轮已修复的 P0（详见仓库 `lyread/backend` 与 `lyread/DEPLOY.md`）：

- 注册 500（`users.id varchar(12)` 与 24 位 ID 冲突）→ 改 12 位数字 ID，注册直接返回 JWT。
- `stories` 增加 `user_id`、`word_count`；新增作品 CRUD（save/list/get/create/update/delete），全部按登录用户隔离。
- `generate-title` 兼容 `{genre, prompt}`，对匿名开放（nginx 限流）。
- 统计/创作者路由补齐（`/api/stats/*`、`/api/creator/*`）。
- 进化调度器由空 `pass` 改为 APScheduler 真实周期任务。
- MySQL/Redis 端口收敛到 `127.0.0.1`；停用旧 8003 后端。

因此本施工包聚焦 V1.9 → V2 仍缺失的核心：**点数账户 + 按量计费 + 支付闭环 + 章节独立表 + 小说记忆（小说大脑）+ 真实审核/案例**。

## 文档清单

| 文件 | 内容 |
|---|---|
| `01-PRODUCT-POSITIONING.md` | 产品定位与商业模式 |
| `02-PRD-V2.md` | 功能需求（可开发、可验收） |
| `03-MVP-SCOPE.md` | MVP 范围表（保留/重构/新增/下线） |
| `04-DATABASE-DESIGN.md` | 数据库设计说明 |
| `05-schema.sql` | 建表与迁移 SQL |
| `06-API-SPEC.md` | API 接口规范（含扣费/幂等/鉴权） |
| `07-AI-STORY-ENGINE.md` | 短故事/长篇生成与记忆引擎 |
| `08-PROMPT-SPEC.md` | Prompt 版本化规范 |
| `09-UI-FLOW.md` | 页面清单与用户流程 |
| `10-ACCEPTANCE-TESTS.md` | 端到端验收标准 |
| `11-SECURITY-CHECKLIST.md` | 安全清单 |
| `12-DEPLOYMENT-SPEC.md` | 部署规范 |

## 交给 Codex 的总任务

> 根据本 `lyread/v2-spec` 目录中的产品、数据库、API、AI 引擎、安全、部署与验收规范，将现有 LyRead V1.9（`lyread/backend`）升级为 V2 可收费运营版本。

硬性要求：

1. 不得使用模拟数据、占位组件、TODO 或空接口。
2. 保留可复用的 Vue 3 页面与 FastAPI 代码，但允许重构。
3. 数据库必须通过迁移脚本创建（见 `05-schema.sql`），不允许只写文档。
4. 所有作品/章节接口必须校验当前用户所有权。
5. 所有 AI 生成任务必须走「额度预冻结 → 成功结算 → 失败返还」。
6. 支付回调必须验签、核对金额、保证幂等。
7. 所有密码/密钥仅通过环境变量注入；源码、日志、示例数据中不得出现真实密钥。
8. 提供完整 Docker Compose（MySQL、Redis、Worker、Nginx、后端、前端）。
9. 必须执行 `10-ACCEPTANCE-TESTS.md` 全部验收。
10. 每完成一个阶段更新 `IMPLEMENTATION-STATUS.md`。

## 分工

- **Codex**：全量工程（数据库迁移、后端业务、前端、Worker、Docker、测试）。分阶段执行，每阶段可运行可验收。
- **Cursor**：实时小范围修改（改页面、文案、组件、CSS、单个报错、调 Prompt、查某张表）。

## 阶段顺序

1. 安全清理与体检 → 2. 数据库与迁移 → 3. 认证与权限 → 4. 点数与计费 → 5. 生成任务系统 → 6. 小说大脑 → 7. 前端用户流程 → 8. 支付 → 9. 后台与审核 → 10. 测试部署。
