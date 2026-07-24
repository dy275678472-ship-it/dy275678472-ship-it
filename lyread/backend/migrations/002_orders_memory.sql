-- LyRead V2 migration 002: orders + chapter_summaries (小说大脑基础)

CREATE TABLE IF NOT EXISTS orders (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  out_trade_no      VARCHAR(64) NOT NULL,
  user_id           VARCHAR(12) NOT NULL,
  points            INT NOT NULL,
  amount_fen        INT NOT NULL,
  paid_amount_fen   INT NULL,
  channel           VARCHAR(16) DEFAULT 'alipay',
  status            VARCHAR(20) DEFAULT 'created',
  trade_no          VARCHAR(64) NULL,
  idempotency_key   VARCHAR(80) NULL,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  paid_at           DATETIME NULL,
  UNIQUE KEY uq_out_trade (out_trade_no),
  UNIQUE KEY uq_idem (idempotency_key),
  KEY idx_user (user_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chapter_summaries (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id    BIGINT NOT NULL,
  chapter_idx INT NOT NULL,
  summary     TEXT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_story_ch (story_id, chapter_idx),
  KEY idx_story (story_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
