-- LyRead migration 005: 案例正文预览（审核发布同步）
-- 若列已存在，部署脚本可忽略 duplicate column 错误

ALTER TABLE contents ADD COLUMN story_id BIGINT NULL;
ALTER TABLE contents ADD COLUMN preview_body MEDIUMTEXT NULL;
CREATE INDEX idx_contents_story ON contents (story_id);
