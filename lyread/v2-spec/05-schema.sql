-- LyRead V2 schema (MySQL 8.0, utf8mb4)
-- 可重复执行。用户 id 兼容现网 varchar(12)。点数以整数记账。
-- 交给 Codex 时应改造为带版本表的迁移；此处给出目标结构。

SET NAMES utf8mb4;

-- ============ 账号 ============
CREATE TABLE IF NOT EXISTS users (
  id            VARCHAR(12) NOT NULL,
  username      VARCHAR(64) NOT NULL,
  password_hash VARCHAR(100) NOT NULL,           -- bcrypt/argon2
  email         VARCHAR(100) NULL,
  vip_level     INT DEFAULT 0,
  role          VARCHAR(16) DEFAULT 'user',       -- user/admin
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 点数账户与流水 ============
CREATE TABLE IF NOT EXISTS credit_accounts (
  user_id        VARCHAR(12) NOT NULL,
  free_balance   INT NOT NULL DEFAULT 0,          -- 每日免费额度（不累计）
  paid_balance   INT NOT NULL DEFAULT 0,          -- 充值/赠送额度
  reserved       INT NOT NULL DEFAULT 0,          -- 已冻结
  updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_credacc_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS credit_transactions (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id         VARCHAR(12) NOT NULL,
  type            VARCHAR(24) NOT NULL,            -- recharge/daily_grant/signup_bonus/reserve/settle/refund/admin_adjust/order_refund
  amount          INT NOT NULL,                    -- 正=增，负=减
  free_delta      INT NOT NULL DEFAULT 0,
  paid_delta      INT NOT NULL DEFAULT 0,
  balance_after   INT NOT NULL,                    -- free+paid 之和快照
  ref_type        VARCHAR(24) NULL,                -- job/order/admin
  ref_id          VARCHAR(64) NULL,
  idempotency_key VARCHAR(80) NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_user (user_id, id),
  UNIQUE KEY uq_idem (idempotency_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_free_grants (
  user_id     VARCHAR(12) NOT NULL,
  grant_date  DATE NOT NULL,
  points      INT NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, grant_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 作品 / 分卷 / 章节 ============
CREATE TABLE IF NOT EXISTS story_projects (
  id           BIGINT NOT NULL,
  user_id      VARCHAR(12) NOT NULL,
  type         VARCHAR(16) NOT NULL DEFAULT 'novel', -- novel/short
  title        VARCHAR(255) NOT NULL,
  genre        VARCHAR(50) NULL,
  style        VARCHAR(50) NULL,
  target_words INT NULL,
  intro        TEXT NULL,
  status       VARCHAR(20) DEFAULT 'draft',          -- draft/published/archived
  is_public    TINYINT(1) DEFAULT 0,
  word_count   INT DEFAULT 0,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_user (user_id),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS volumes (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id   BIGINT NOT NULL,
  idx        INT NOT NULL,
  title      VARCHAR(255) NULL,
  KEY idx_story (story_id, idx)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chapters (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id     BIGINT NOT NULL,
  user_id      VARCHAR(12) NOT NULL,
  volume_id    BIGINT NULL,
  idx          INT NOT NULL,                     -- 章序
  title        VARCHAR(255) NULL,
  content      MEDIUMTEXT NULL,
  word_count   INT DEFAULT 0,
  status       VARCHAR(20) DEFAULT 'draft',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_story (story_id, idx),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chapter_versions (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  chapter_id  BIGINT NOT NULL,
  content     MEDIUMTEXT NULL,
  word_count  INT DEFAULT 0,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_chapter (chapter_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 小说大脑（记忆） ============
CREATE TABLE IF NOT EXISTS characters (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id    BIGINT NOT NULL,
  name        VARCHAR(100) NOT NULL,
  profile     TEXT NULL,                          -- 设定/关系/外貌/目标
  KEY idx_story (story_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_states (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  character_id  BIGINT NOT NULL,
  after_chapter INT NOT NULL,
  state         TEXT NULL,                        -- 该章后的状态/位置/关系变化
  KEY idx_char (character_id, after_chapter)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS world_settings (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id  BIGINT NOT NULL,
  category  VARCHAR(50) NULL,                     -- 势力/地点/规则/物品
  name      VARCHAR(150) NULL,
  detail    TEXT NULL,
  KEY idx_story (story_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS plot_arcs (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id  BIGINT NOT NULL,
  kind      VARCHAR(20) NULL,                     -- main/sub
  title     VARCHAR(255) NULL,
  detail    TEXT NULL,
  KEY idx_story (story_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS foreshadowings (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id           BIGINT NOT NULL,
  content            TEXT NULL,
  planted_chapter    INT NULL,
  expected_recover   INT NULL,
  recovered_chapter  INT NULL,
  status             VARCHAR(20) DEFAULT 'open',  -- open/recovered/dropped
  KEY idx_story (story_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chapter_summaries (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id    BIGINT NOT NULL,
  chapter_idx INT NOT NULL,
  summary     TEXT NULL,
  KEY idx_story (story_id, chapter_idx)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS story_memory_snapshots (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id     BIGINT NOT NULL,
  after_chapter INT NOT NULL,
  snapshot     MEDIUMTEXT NULL,                   -- 压缩后的整书记忆
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_story (story_id, after_chapter)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 生成任务 ============
CREATE TABLE IF NOT EXISTS generation_jobs (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id          VARCHAR(12) NOT NULL,
  story_id         BIGINT NULL,
  chapter_id       BIGINT NULL,
  job_type         VARCHAR(32) NOT NULL,           -- title/outline/chapters/chapter/continue/consistency
  provider         VARCHAR(32) NULL,
  model            VARCHAR(64) NULL,
  prompt_version   VARCHAR(32) NULL,
  input_tokens     INT NULL,
  output_tokens    INT NULL,
  reserved_credits INT NOT NULL DEFAULT 0,
  actual_credits   INT NULL,
  status           VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/running/succeeded/failed/refunded
  error_code       VARCHAR(64) NULL,
  retry_count      INT DEFAULT 0,
  started_at       DATETIME NULL,
  finished_at      DATETIME NULL,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_user (user_id, id),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 订单 / 支付 ============
CREATE TABLE IF NOT EXISTS orders (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  out_trade_no      VARCHAR(64) NOT NULL,          -- 商户订单号
  user_id           VARCHAR(12) NOT NULL,
  points            INT NOT NULL,                  -- 购买点数
  amount_fen        INT NOT NULL,                  -- 原始金额（分）
  paid_amount_fen   INT NULL,                      -- 实付
  channel           VARCHAR(16) DEFAULT 'alipay',
  status            VARCHAR(20) DEFAULT 'created', -- created/paid/closed/refunded
  trade_no          VARCHAR(64) NULL,              -- 支付平台交易号
  callback_digest   VARCHAR(255) NULL,
  idempotency_key   VARCHAR(80) NULL,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  paid_at           DATETIME NULL,
  closed_at         DATETIME NULL,
  refund_status     VARCHAR(20) NULL,
  refund_amount_fen INT NULL,
  UNIQUE KEY uq_out_trade (out_trade_no),
  UNIQUE KEY uq_idem (idempotency_key),
  KEY idx_user (user_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 平台案例 / 审核 / 指标 ============
CREATE TABLE IF NOT EXISTS system_generation_plans (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  plan_date   DATE NOT NULL,
  topic       VARCHAR(255) NULL,
  genre       VARCHAR(50) NULL,
  status      VARCHAR(20) DEFAULT 'planned',       -- planned/generating/review/published/stopped
  story_id    BIGINT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_date (plan_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS content_reviews (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  target_type VARCHAR(20) NOT NULL,                -- story/chapter
  target_id   BIGINT NOT NULL,
  result      VARCHAR(20) DEFAULT 'pending',       -- pending/approved/rejected
  reason      VARCHAR(255) NULL,
  reviewer    VARCHAR(64) NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS story_metrics (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id       BIGINT NOT NULL,
  date           DATE NOT NULL,
  views          INT DEFAULT 0,
  first_read     INT DEFAULT 0,
  finish_first   INT DEFAULT 0,
  next_chapter   INT DEFAULT 0,
  conversions    INT DEFAULT 0,
  UNIQUE KEY uq_story_date (story_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
