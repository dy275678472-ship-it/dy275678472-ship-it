-- 为 stories 表补充多用户与字数字段（幂等：列已存在时忽略错误）
-- 用法：docker exec -i lyread-mysql mysql -uroot -p<pass> lyread < 001_stories_user_id.sql

ALTER TABLE stories
    ADD COLUMN user_id VARCHAR(12) NULL AFTER id;

ALTER TABLE stories
    ADD COLUMN word_count INT DEFAULT 0 AFTER chapters;

ALTER TABLE stories
    ADD INDEX idx_user (user_id);
