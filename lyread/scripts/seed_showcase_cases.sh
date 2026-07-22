#!/usr/bin/env bash
# 写入精选展示案例（通过 case_quality 过滤，供 /trending 与 /case/* 阅读区使用）
# 幂等：按 content_id 去重；每次运行会刷新 preview_body 节选正文
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER="${MYSQL_CONTAINER:-lyread-mysql}"
DB="${MYSQL_DATABASE:-lyread}"
ROOT_PW=$(docker exec "$CONTAINER" printenv MYSQL_ROOT_PASSWORD)

docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB" <<'EOSQL'
INSERT INTO contents (content_id, title, category, word_count, heat, score, status) VALUES
  ('showcase_urban_01', '开局十个亿，我在都市横着走', '都市神豪', 128000, 9200, 8.6, 'active'),
  ('showcase_urban_03', '穷小子被退婚，亮出黑卡全场跪', '都市神豪', 118000, 5100, 8.3, 'active'),
  ('showcase_urban_04', '被赶出家门那天，我继承了百亿集团', '都市神豪', 122000, 5050, 8.3, 'active'),
  ('showcase_urban_05', '相亲遇到女总裁，她是我下属', '都市神豪', 98000, 4216, 8.2, 'active'),
  ('showcase_urban_06', '外卖员竟是隐藏富豪', '都市神豪', 110000, 4980, 8.2, 'active'),
  ('showcase_urban_07', '同学聚会，班长向我敬酒', '都市神豪', 102000, 4102, 8.2, 'active'),
  ('showcase_urban_08', '保安队长竟是集团继承人', '都市神豪', 112000, 4272, 8.2, 'active'),
  ('showcase_urban_09', '穷亲戚上门，我随手开了张支票', '都市神豪', 98000, 3988, 8.2, 'active'),
  ('showcase_warrior_01', '战神回归，发现女儿住狗窝', '战神归来', 156000, 8800, 8.4, 'active'),
  ('showcase_warrior_03', '上门女婿被赶出门，亮出战神令', '战神归来', 142000, 5200, 8.3, 'active'),
  ('showcase_warrior_04', '女儿被欺负，我一个电话调动十万精兵', '战神归来', 148000, 5150, 8.3, 'active'),
  ('showcase_warrior_05', '退役兵王当保安，业主竟是前女友', '战神归来', 125000, 4046, 8.2, 'active'),
  ('showcase_warrior_06', '女儿婚礼当天，有人敢闹事', '战神归来', 138000, 4900, 8.2, 'active'),
  ('showcase_warrior_07', '儿子被绑架，我调了一个师的兵力', '战神归来', 140000, 4850, 8.2, 'active'),
  ('showcase_warrior_08', '隐姓埋名十年，仇家找上门', '战神归来', 135000, 4387, 8.2, 'active'),
  ('showcase_reborn_01', '重生2003，当首富很简单', '重生', 98000, 7600, 8.2, 'active'),
  ('showcase_xianxia_01', '仙帝归来，都市横推一切', '仙侠玄幻', 210000, 7100, 8.5, 'active'),
  ('showcase_romance_01', '她走后，我让全世界追悔莫及', '言情甜宠', 86000, 6500, 8.1, 'active'),
  ('showcase_scifi_01', '星际裂痕：最后的人类舰队', '科幻脑洞', 142000, 5900, 8.0, 'active'),
  ('showcase_suspense_01', '第七个证人消失了', '悬疑推理', 112000, 5400, 7.9, 'active'),
  ('showcase_history_01', '大明第一权臣', '历史架空', 178000, 4800, 8.3, 'active'),
  ('showcase_system_01', '每写一个字，全网打赏十万', '系统流', 95000, 8700, 8.7, 'active'),
  ('showcase_system_03', '反派自救系统已上线', '系统流', 108000, 4216, 8.3, 'active'),
  ('showcase_system_04', '直播写小说，观众打赏变系统积分', '系统流', 98000, 4800, 8.3, 'active'),
  ('showcase_system_05', '我绑定了神豪消费系统', '系统流', 102000, 4750, 8.3, 'active'),
  ('showcase_system_06', '写作系统要求日更一万字', '系统流', 99000, 4700, 8.2, 'active'),
  ('showcase_system_07', '反派光环系统让我必须作死', '系统流', 105000, 4650, 8.2, 'active'),
  ('showcase_apocalypse_01', '极寒第七日，我囤了一整座超市', '末世求生', 118000, 6200, 8.2, 'active'),
  ('showcase_campus_01', '转学生竟是隐藏学神，摸底考炸了', '校园青春', 72000, 5800, 8.0, 'active'),
  ('showcase_game_01', '被战队开除那天，我登回国服第一', '游戏竞技', 105000, 8100, 8.4, 'active')
ON DUPLICATE KEY UPDATE
  title=VALUES(title),
  category=VALUES(category),
  word_count=VALUES(word_count),
  heat=VALUES(heat),
  score=VALUES(score),
  status='active';

SELECT COUNT(*) AS active_showcase FROM contents WHERE status='active';
EOSQL

python3 "$SCRIPT_DIR/seed_showcase_preview_sql.py" | docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB"

echo "[seed_showcase] showcase cases + reading excerpts ready"
