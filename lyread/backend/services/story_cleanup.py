"""作品删除级联、过期任务退款。"""


def cascade_delete_story(cursor, story_id: int) -> None:
    """删除作品关联的章节与小说大脑数据。"""
    cursor.execute(
        "DELETE cs FROM character_states cs "
        "INNER JOIN characters c ON c.id = cs.character_id WHERE c.story_id=%s",
        (story_id,),
    )
    cursor.execute("DELETE FROM chapters WHERE story_id=%s", (story_id,))
    cursor.execute("DELETE FROM chapter_summaries WHERE story_id=%s", (story_id,))
    cursor.execute("DELETE FROM characters WHERE story_id=%s", (story_id,))
    cursor.execute("DELETE FROM foreshadowings WHERE story_id=%s", (story_id,))
    cursor.execute("DELETE FROM world_settings WHERE story_id=%s", (story_id,))
    cursor.execute("DELETE FROM stories WHERE id=%s", (story_id,))


def sweep_stale_jobs(cursor, max_age_minutes: int = 30) -> int:
    """将超时 running 任务标记失败并退款。返回处理数量。"""
    from api.credits import refund

    cursor.execute(
        "SELECT id, user_id, reserved_credits, free_reserved, paid_reserved FROM generation_jobs "
        "WHERE status='running' AND created_at < DATE_SUB(NOW(), INTERVAL %s MINUTE)",
        (max_age_minutes,),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        job_id = row["id"] if isinstance(row, dict) else row[0]
        uid = str(row["user_id"] if isinstance(row, dict) else row[1])
        try:
            refund(uid, job_id)
        except Exception:
            pass
        cursor.execute(
            "UPDATE generation_jobs SET status='failed', error_message='任务超时自动退款' WHERE id=%s",
            (job_id,),
        )
        count += 1
    return count
