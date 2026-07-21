-- LyRead V2 migration 003: admin role + content review queue
-- 若 role 列已存在，可忽略 ALTER 报错

ALTER TABLE users ADD COLUMN role VARCHAR(16) DEFAULT 'user' AFTER vip_level;

CREATE TABLE IF NOT EXISTS content_reviews (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  target_type VARCHAR(20) NOT NULL,
  target_id   BIGINT NOT NULL,
  user_id     VARCHAR(12) NULL,
  title       VARCHAR(255) NULL,
  result      VARCHAR(20) DEFAULT 'pending',
  reason      VARCHAR(255) NULL,
  reviewer    VARCHAR(64) NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  KEY idx_result (result, id),
  KEY idx_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
