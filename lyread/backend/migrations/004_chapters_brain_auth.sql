-- LyRead V2 migration 004: chapters table + novel brain + password reset

CREATE TABLE IF NOT EXISTS chapters (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id     BIGINT NOT NULL,
  user_id      VARCHAR(12) NOT NULL,
  idx          INT NOT NULL,
  title        VARCHAR(255) NULL,
  content      MEDIUMTEXT NULL,
  word_count   INT DEFAULT 0,
  status       VARCHAR(20) DEFAULT 'draft',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_story_idx (story_id, idx),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS characters (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id    BIGINT NOT NULL,
  name        VARCHAR(100) NOT NULL,
  profile     TEXT NULL,
  KEY idx_story (story_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_states (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  character_id  BIGINT NOT NULL,
  after_chapter INT NOT NULL,
  state         TEXT NULL,
  KEY idx_char (character_id, after_chapter)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS world_settings (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  story_id  BIGINT NOT NULL,
  category  VARCHAR(50) NULL,
  name      VARCHAR(150) NULL,
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
  status             VARCHAR(20) DEFAULT 'open',
  KEY idx_story (story_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id    VARCHAR(12) NOT NULL,
  token      VARCHAR(64) NOT NULL,
  expires_at DATETIME NOT NULL,
  used_at    DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_token (token),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
