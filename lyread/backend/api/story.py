"""
网文创作核心 API
🧠 70% AI + 30% 人工 创作流程
"""

import os
import json
import hashlib
import time
import requests
import mysql.connector
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI
from api.auth import get_current_user, get_optional_user
from settings import database_config
from services.content_moderation import check_many, moderation_detail

# 说明：路由不再强制全局登录。
# - 创作类"试用"接口（生成书名等）对匿名开放，配合 nginx 限流保护额度。
# - 保存 / 发布 / 列表 / 续写等涉及数据与额度的接口按接口级要求登录。
router = APIRouter()


def _guard_content(*texts: str, label: str = "内容") -> None:
    """生成/发布前敏感词检测。"""
    result = check_many(*texts)
    if not result["ok"]:
        raise HTTPException(status_code=422, detail=f"{label}{moderation_detail(result['hits'])}")


def _db():
    """获取 MySQL 连接（失败抛 503）。"""
    try:
        return mysql.connector.connect(**database_config())
    except Exception as exc:
        print(f"[Story] DB 连接失败: {exc}")
        raise HTTPException(status_code=503, detail="数据库暂时不可用")

# ==================== LLM Provider 配置 ====================

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# PollinationsAI 配置 (免费无Key)
POLLINATIONS_URL = "https://text.pollinations.ai/openai-compatible/v1/chat/completions"

def get_openai_client():
    """获取 DeepSeek 客户端"""
    if not DEEPSEEK_API_KEY:
        return None
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def call_pollinations(prompt: str, max_tokens: int = 500) -> str:
    """调用 PollinationsAI 免费 API"""
    try:
        response = requests.post(
            POLLINATIONS_URL,
            json={
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            },
            timeout=(5, 60)
        )
        response.raise_for_status()
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return f"[PollinationsAI Error: {str(e)}]"

def chat_with_llm(prompt: str, max_tokens: int = 500, model: str = "deepseek-chat") -> str:
    """
    通用 LLM 调用函数
    优先使用 DeepSeek，如果失败则使用 PollinationsAI
    """
    # 尝试 DeepSeek
    client = get_openai_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=model or DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DeepSeek Error: {str(e)}, 尝试 PollinationsAI...]")
    
    # 回退到 PollinationsAI
    print(f"[使用 PollinationsAI 作为备选]")
    return call_pollinations(prompt, max_tokens)

# ==================== 数据模型 ====================

class GenerateTitleRequest(BaseModel):
    """生成书名请求（兼容首页试用的 {genre, prompt} 与创作台的 {keywords}）。"""
    keywords: Optional[List[str]] = None  # 核心脑洞词
    genre: Optional[str] = None  # 题材
    prompt: Optional[str] = None  # 首页试用的自由描述

class GenerateOutlineRequest(BaseModel):
    """生成大纲请求"""
    title: str
    intro: str
    genre: str
    hot_points: List[str]  # 爽点

class GenerateChaptersRequest(BaseModel):
    """生成章纲请求"""
    outline: dict
    chapter_count: int = 20

class AIContinueRequest(BaseModel):
    """AI续写请求"""
    context: str = ""
    content: str = ""
    style: Optional[str] = "网文"
    story_id: Optional[int] = None
    chapter_title: Optional[str] = "当前章节"

class PublishRequest(BaseModel):
    """发布请求"""
    title: str
    intro: str
    genre: str
    chapters: List[dict]
    user_id: Optional[int] = 1

# ==================== API 接口 ====================

@router.post("/generate-title")
async def generate_title(req: GenerateTitleRequest, user: Optional[dict] = Depends(get_optional_user)):
    """步骤1：AI生成爆款书名。匿名可试用一次（nginx 限流）；登录用户扣 1 点。"""
    elements = req.prompt or (",".join(req.keywords) if req.keywords else "")
    elements = elements.strip()
    if not elements:
        raise HTTPException(status_code=422, detail="请填写题材关键词或故事想法")
    _guard_content(elements, label="输入")
    genre = req.genre or "都市"

    prompt = f"""你是一个资深网文编辑，精通各平台爆款书的命名套路。
用户提供的核心元素：{elements}
题材：{genre}

请生成5个极具吸睛力的书名，每个书名都要：
1. 前20字内出现核心爽点关键词
2. 带有强烈的"点击欲望"
3. 格式：书名 | 一句话黄金钩子简介

只输出5行，不要其他内容。"""

    # 登录用户走计费；匿名用户免费试用（不计费）
    uid = str(user["sub"]) if user and user.get("sub") else None
    job = None
    if uid:
        from api.credits import reserve, settle, refund, estimate_points
        job = reserve(uid, estimate_points("title"), "title")
    try:
        result = chat_with_llm(prompt, max_tokens=500)
        mod = check_many(result)
        if not mod["ok"]:
            if uid and job:
                refund(uid, job["job_id"])
            raise HTTPException(status_code=422, detail=moderation_detail(mod["hits"]))
        titles = []
        for line in result.strip().split("\n"):
            if "|" in line:
                parts = line.split("|")
                titles.append({
                    "title": parts[0].strip(),
                    "hook": parts[1].strip() if len(parts) > 1 else ""
                })
        if uid and job:
            settle(uid, job["job_id"], estimate_points("title"))
        first = titles[0] if titles else {"title": "", "hook": ""}
        return {
            "success": True,
            "titles": titles[:5],
            "title": first["title"],
            "description": first["hook"],
        }
    except Exception as e:
        if uid and job:
            refund(uid, job["job_id"])
        return {"success": False, "error": str(e)}


@router.post("/generate-outline")
async def generate_outline(req: GenerateOutlineRequest, user: dict = Depends(get_current_user)):
    """步骤2：AI生成大纲（起承转合树）。扣 3 点，失败返还。"""
    from api.credits import reserve, settle, refund, estimate_points
    uid = str(user["sub"])
    _guard_content(req.title, req.intro, *req.hot_points, label="输入")
    job = reserve(uid, estimate_points("outline"), "outline")
    client = get_openai_client()

    hot_points = ",".join(req.hot_points)
    
    prompt = f"""你是一个网文大纲大师，精通"起承转合"结构。

书名：{req.title}
简介：{req.intro}
题材：{req.genre}
爽点：{hot_points}

请生成完整的四维大纲结构（起、承、转、合），每个节点包含：
- 章节范围（如1-5章）
- 核心剧情
- 爽点设计

输出JSON格式：
{{
  "起": {{"章节": "1-5", "剧情": "...", "爽点": "..."}},
  "承": {{"章节": "6-15", "剧情": "...", "爽点": "..."}},
  "转": {{"章节": "16-25", "剧情": "...", "爽点": "..."}},
  "合": {{"章节": "26-30", "剧情": "...", "爽点": "..."}}
}}

只输出JSON。"""

    try:
        # 使用统一的 LLM 调用（DeepSeek优先，失败则用PollinationsAI）
        result = chat_with_llm(prompt, max_tokens=1000)
        
        # 解析 JSON
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            outline = json.loads(json_match.group())
        else:
            outline = {}

        settle(uid, job["job_id"], estimate_points("outline"))
        return {"success": True, "outline": outline}
    except Exception as e:
        refund(uid, job["job_id"])
        return {"success": False, "error": str(e)}


@router.get("/godfingers")
async def get_godfingers():
    """步骤3：获取金手指类型"""
    godfingers = [
        {"id": "money", "name": "神豪系统", "icon": "💰", "desc": "花钱就能变强"},
        {"id": "skill", "name": "技能系统", "icon": "⚡", "desc": "完成任务解锁技能"},
        {"id": "level", "name": "升级系统", "icon": "📈", "desc": "打怪升级变强"},
        {"id": "inherit", "name": "血脉传承", "icon": "🩸", "desc": "继承远古血脉"},
        {"id": "learn", "name": "全能学习", "icon": "📚", "desc": "任何技能秒学会"},
        {"id": "weapon", "name": "神器认主", "icon": "⚔️", "desc": "神兵自动认主"},
        {"id": "medical", "name": "神医系统", "icon": "🏥", "desc": "治病就能升级"},
        {"id": "game", "name": "游戏系统", "icon": "🎮", "desc": "游戏能力现实化"},
        {"id": "stock", "name": "炒股系统", "icon": "📈", "desc": "股市预测成首富"},
        {"id": "beauty", "name": "魅力系统", "icon": "💄", "desc": "魅力值兑换一切"}
    ]
    return {"success": True, "godfingers": godfingers}


@router.get("/level-systems")
async def get_level_systems():
    """步骤4：获取修炼等级体系"""
    level_systems = [
        {
            "id": "xianxia",
            "name": "修仙体系",
            "levels": ["炼气", "筑基", "金丹", "元婴", "化神", "渡劫", "大乘", "仙人", "真仙", "金仙"]
        },
        {
            "id": "urban",
            "name": "都市体系",
            "levels": ["普通人", "进阶", "精英", "上层", "顶级", "传奇", "传说", "神话"]
        },
        {
            "id": "military",
            "name": "战神体系",
            "levels": ["列兵", "上等兵", "士官", "尉官", "校官", "将官", "元帅", "战神"]
        },
        {
            "id": "cultivation",
            "name": "修炼体系",
            "levels": ["入门", "初窥", "小成", "大成", "巅峰", "圆满", "超凡", "入圣", "至圣"]
        }
    ]
    return {"success": True, "systems": level_systems}


@router.post("/generate-chapters")
async def generate_chapters(req: GenerateChaptersRequest, user: dict = Depends(get_current_user)):
    """步骤5：批量生成章纲（带爽点芯片）。扣 5 点，失败返还。"""
    from api.credits import reserve, settle, refund, estimate_points
    uid = str(user["sub"])
    outline_str = json.dumps(req.outline, ensure_ascii=False)
    _guard_content(outline_str, label="大纲")
    job = reserve(uid, estimate_points("chapters"), "chapters")
    client = get_openai_client()
    
    prompt = f"""你是一个网文章纲大师。

宏观大纲：{json.dumps(req.outline, ensure_ascii=False)}
需要生成{req.chapter_count}章的章纲。

每章章纲包含：
- 章节标题
- 本章核心爽点标签（如：打脸、装逼、逆袭、获得宝贝、感情升温等）
- 本章剧情要点（50字内）

输出JSON数组格式：
[
  {{"chapter": 1, "title": "第1章 标题", "hot_point": "打脸", "summary": "剧情要点"}},
  ...
]

只输出JSON数组。"""

    try:
        if client:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content
            
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                chapters = json.loads(json_match.group())
            else:
                chapters = []
        else:
            # 模拟返回
            chapters = []
            for i in range(1, req.chapter_count + 1):
                hot_points = ["打脸", "装逼", "逆袭", "宝贝", "升级", "打怪", "救人", "表白"]
                chapters.append({
                    "chapter": i,
                    "title": f"第{i}章 章节名",
                    "hot_point": hot_points[(i-1) % len(hot_points)],
                    "summary": f"第{i}章的剧情摘要..."
                })

        settle(uid, job["job_id"], estimate_points("chapters"))
        return {"success": True, "chapters": chapters}
    except Exception as e:
        refund(uid, job["job_id"])
        return {"success": False, "error": str(e)}


@router.post("/ai-continue")
async def ai_continue(req: AIContinueRequest, user: dict = Depends(get_current_user)):
    """步骤6：AI续写（小说大脑完整上下文 + 自动更新记忆）。扣 10 点。"""
    from api.credits import reserve, settle, refund, estimate_points
    from services.chapter_store import merge_chapters_for_story, chapters_to_json
    from services.story_memory import (
        build_memory_context, load_brain, extract_brain_update_prompt,
        apply_brain_update, parse_brain_json,
    )
    from services.copyright import inject_watermark

    uid = str(user["sub"])
    if not get_openai_client():
        return {"success": False, "error": "AI服务未配置"}

    _guard_content(req.context, req.content, label="输入")
    job = reserve(uid, estimate_points("continue"), "continue", story_id=req.story_id)
    memory_ctx = req.context or req.content
    chapter_idx = 1

    if req.story_id:
        db = _db()
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM stories WHERE id=%s LIMIT 1", (req.story_id,))
            story_row = cursor.fetchone()
            if story_row and str(story_row.get("user_id")) != uid:
                refund(uid, job["job_id"])
                raise HTTPException(status_code=403, detail="无权续写该作品")
            if story_row:
                chapters = merge_chapters_for_story(cursor, req.story_id, story_row.get("chapters"))
                brain = load_brain(cursor, req.story_id)
                memory_ctx = build_memory_context(
                    story_row.get("title") or "", story_row.get("intro") or "",
                    story_row.get("outline") or "", story_row.get("characters") or "",
                    chapters, brain,
                )
                if req.content:
                    memory_ctx += f"\n\n当前编辑：\n{req.content[-4000:]}"
                cursor.execute("SELECT COALESCE(MAX(idx),0)+1 FROM chapters WHERE story_id=%s", (req.story_id,))
                r = cursor.fetchone()
                chapter_idx = int(list(r.values())[0] if isinstance(r, dict) else r[0])
        finally:
            if db.is_connected():
                db.close()

    prompt = f"""你是网文作家，擅长爽文。

【全书记忆】
{memory_ctx}

风格：{req.style}
续写 800–1200 字正文，人物设定一致，情节有爽点。直接输出正文。"""

    try:
        new_content = chat_with_llm(prompt, max_tokens=2000)
        mod = check_many(new_content)
        if not mod["ok"]:
            refund(uid, job["job_id"])
            raise HTTPException(status_code=422, detail=moderation_detail(mod["hits"]))
        watermarked = inject_watermark(new_content, user_id=uid)

        if req.story_id and new_content:
            try:
                db2 = _db()
                cur = db2.cursor(dictionary=True)
                brain = load_brain(cur, req.story_id)
                names = [c["name"] for c in brain.get("characters", [])]
                upd_prompt = extract_brain_update_prompt(chapter_idx, new_content, names)
                brain_raw = chat_with_llm(upd_prompt, max_tokens=800)
                brain_data = parse_brain_json(brain_raw)
                apply_brain_update(cur, req.story_id, chapter_idx, brain_data)
                cur.execute(
                    "INSERT INTO chapters (story_id, user_id, idx, title, content, word_count) "
                    "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content=VALUES(content), word_count=VALUES(word_count)",
                    (req.story_id, uid, chapter_idx, req.chapter_title or f"第{chapter_idx}章", new_content, len(new_content)),
                )
                chs = merge_chapters_for_story(cur, req.story_id, None)
                chs.append({"chapter": chapter_idx, "title": req.chapter_title or f"第{chapter_idx}章", "content": new_content})
                cur2 = db2.cursor()
                cur2.execute(
                    "UPDATE stories SET chapters=%s, word_count=%s, updated_at=NOW() WHERE id=%s",
                    (chapters_to_json(chs), sum(len(c.get("content", "")) for c in chs), req.story_id),
                )
                db2.commit()
                db2.close()
            except Exception as mem_exc:
                print(f"[ai-continue] 大脑更新失败: {mem_exc}")

        settle(uid, job["job_id"], estimate_points("continue"))
        return {"success": True, "content": new_content, "watermarked": watermarked, "length": len(new_content), "chapter_idx": chapter_idx}
    except HTTPException:
        raise
    except Exception as e:
        refund(uid, job["job_id"])
        return {"success": False, "error": str(e)}


@router.post("/consistency-check")
async def consistency_check(req: AIContinueRequest, user: dict = Depends(get_current_user)):
    """一致性检测：人物/设定冲突。扣 2 点。"""
    from api.credits import reserve, settle, refund, estimate_points
    uid = str(user["sub"])
    job = reserve(uid, estimate_points("consistency"), "consistency", story_id=req.story_id)
    content = req.content or req.context
    if not content:
        refund(uid, job["job_id"])
        raise HTTPException(status_code=422, detail="请提供待检测内容")
    prompt = f"""你是网文编辑，检查下面内容是否存在人物姓名混乱、设定冲突、时间线矛盾。
只输出 JSON：{{"ok": true/false, "issues": ["问题1", ...], "suggestion": "修改建议"}}

内容：
{content[:5000]}"""
    try:
        result = chat_with_llm(prompt, max_tokens=600)
        import re
        m = re.search(r"\{.*\}", result, re.DOTALL)
        report = json.loads(m.group()) if m else {"ok": True, "issues": [], "suggestion": ""}
        settle(uid, job["job_id"], estimate_points("consistency"))
        return {"success": True, "report": report}
    except Exception as e:
        refund(uid, job["job_id"])
        return {"success": False, "error": str(e)}


@router.post("/publish")
async def publish_story(req: PublishRequest, user: dict = Depends(get_current_user)):
    """提交发布审核（不再直接公开，需管理员通过）。"""
    uid = str(user.get("sub", "0"))
    chapter_text = "".join(ch.get("content", "") for ch in req.chapters)
    _guard_content(req.title, req.intro, chapter_text, label="作品")
    word_count = sum(len(ch.get("content", "")) for ch in req.chapters)
    db = _db()
    try:
        cursor = db.cursor()
        story_id = int(time.time() * 1000)
        cursor.execute(
            "INSERT INTO stories (id, user_id, title, genre, intro, chapters, status, word_count, created_at, updated_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,'pending_review',%s,NOW(),NOW())",
            (story_id, uid, req.title, req.genre, req.intro,
             json.dumps(req.chapters, ensure_ascii=False), word_count),
        )
        cursor.execute(
            "INSERT INTO content_reviews (target_type, target_id, user_id, title, result) "
            "VALUES ('story', %s, %s, %s, 'pending')",
            (story_id, uid, req.title),
        )
        db.commit()
        return {
            "success": True,
            "story_id": story_id,
            "word_count": word_count,
            "status": "pending_review",
            "message": "已提交审核，通过后将在案例区展示",
        }
    except Exception as e:
        db.rollback()
        print(f"[Publish] 失败: {e}")
        raise HTTPException(status_code=500, detail="提交审核失败")
    finally:
        if db.is_connected():
            db.close()


@router.post("/{story_id}/submit-review")
async def submit_review(story_id: int, user: dict = Depends(get_current_user)):
    """将已有草稿提交审核。"""
    uid = str(user["sub"])
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT user_id, title, status, intro, chapters FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if str(row["user_id"]) != uid:
            raise HTTPException(status_code=403, detail="无权操作")
        chs = row.get("chapters")
        if isinstance(chs, str):
            try:
                chs = json.loads(chs)
            except Exception:
                chs = []
        chapter_text = "".join(
            (c.get("content", "") if isinstance(c, dict) else "") for c in (chs or [])
        )
        _guard_content(row.get("title"), row.get("intro"), chapter_text, label="作品")
        cursor.execute(
            "SELECT id FROM content_reviews WHERE target_type='story' AND target_id=%s AND result='pending' LIMIT 1",
            (story_id,),
        )
        if cursor.fetchone():
            return {"success": True, "message": "已在审核队列中"}
        cursor2 = db.cursor()
        cursor2.execute(
            "INSERT INTO content_reviews (target_type, target_id, user_id, title, result) VALUES ('story',%s,%s,%s,'pending')",
            (story_id, uid, row["title"]),
        )
        cursor2.execute("UPDATE stories SET status='pending_review' WHERE id=%s", (story_id,))
        db.commit()
        return {"success": True, "message": "已提交审核"}
    finally:
        if db.is_connected():
            db.close()


@router.post("/publish-legacy")
async def publish_story_legacy(req: PublishRequest, user: dict = Depends(get_current_user)):
    """旧版直接发布（保留兼容，内部使用）。"""
    from services.copyright import generate_copyright_fingerprint
    import hashlib
    import mysql.connector

    uid = str(user.get("sub", "0"))

    # 1. 生成版权指纹
    full_content = req.title + req.intro + "".join([ch.get("content", "") for ch in req.chapters])
    fingerprint = generate_copyright_fingerprint(full_content)
    
    # 2. 生成零宽水印
    from services.copyright import inject_watermark
    watermarked_chapters = []
    for ch in req.chapters:
        watermarked = inject_watermark(ch.get("content", ""), user_id=uid)
        watermarked_chapters.append({
            **ch,
            "content_watermarked": watermarked
        })
    
    # 3. 计算总字数
    word_count = sum(len(ch.get("content", "")) for ch in req.chapters)
    
    # 4. 保存到 MySQL contents 表
    db_id = None
    db = None
    try:
        db = mysql.connector.connect(**database_config())
        cursor = db.cursor()
        content_id = f"story_{int(time.time())}"
        cursor.execute(
            "INSERT INTO contents (content_id, title, category, word_count, heat, score, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (content_id, req.title, req.genre, word_count, 0, 0.0, "active")
        )
        db.commit()
        db_id = cursor.lastrowid
        cursor.close()
        
        # 5. 通知搜索引擎
        try:
            import requests
            sitemap_url = "https://lyread.cn/sitemap.xml"
            requests.get(f"https://www.google.com/ping?sitemap={sitemap_url}", timeout=5)
            requests.get(f"https://www.bing.com/ping?sitemap={sitemap_url}", timeout=5)
            print(f"[Publish] 🔔 pinged search engines for new content {db_id}")
        except Exception as ping_err:
            print(f"[Publish] ping engines failed: {ping_err}")
    except Exception as e:
        print(f"[Publish] DB save failed: {e}")
    finally:
        if db:
            db.close()
    
    return {
        "success": True,
        "story_id": db_id or int(time.time()),
        "fingerprint": fingerprint,
        "chapters_count": len(req.chapters),
        "word_count": word_count,
        "seo_url": f"https://lyread.cn/ep/{db_id}" if db_id else None,
        "status": "published",
        "copyright": {
            "hash": fingerprint,
            "timestamp": time.time(),
            "watermarked": True
        }
    }


@router.get("/suggest-genres")
async def suggest_genres():
    """获取热门题材推荐"""
    genres = [
        {"id": "urban", "name": "都市神豪", "hot": 95, "tags": ["系统", "爽文", "打脸"]},
        {"id": "system", "name": "系统流", "hot": 92, "tags": ["任务", "升级", "神器"]},
        {"id": "reborn", "name": "重生流", "hot": 90, "tags": ["逆袭", "创业", "赚钱"]},
        {"id": "warrior", "name": "战神归来", "hot": 88, "tags": ["复仇", "都市", "兵王"]},
        {"id": "fantasy", "name": "玄幻修仙", "hot": 85, "tags": ["修炼", "升级", "丹药"]},
        {"id": "brainhole", "name": "脑洞文", "hot": 82, "tags": ["创意", "反套路", "搞笑"]},
        {"id": "games", "name": "游戏文", "hot": 80, "tags": ["电竞", "虚拟", "异界"]},
        {"id": "entertainment", "name": "文娱", "hot": 78, "tags": ["明星", "娱乐", "文艺"]}
    ]
    return {"success": True, "genres": genres}


# ==================== 作品 CRUD（草稿保存 / 列表 / 详情） ====================

class SaveStoryRequest(BaseModel):
    """保存/更新作品草稿。outline / characters / chapters 为前端 JSON 字符串。"""
    id: Optional[int] = None
    title: str = ""
    genre: Optional[str] = ""
    intro: Optional[str] = ""
    outline: Optional[str] = ""
    characters: Optional[str] = ""
    chapters: Optional[str] = ""
    status: Optional[str] = "draft"


def _count_words(chapters_raw: Optional[str]) -> int:
    """从 chapters JSON 字符串估算总字数。"""
    if not chapters_raw:
        return 0
    try:
        data = json.loads(chapters_raw)
        if isinstance(data, list):
            return sum(len(str(ch.get("content", ""))) for ch in data if isinstance(ch, dict))
    except Exception:
        pass
    return len(chapters_raw)


def _story_to_dict(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "genre": row.get("genre"),
        "intro": row.get("intro"),
        "outline": row.get("outline"),
        "characters": row.get("characters"),
        "chapters": row.get("chapters"),
        "status": row.get("status"),
        "word_count": row.get("word_count", 0),
        "created_at": str(row.get("created_at")) if row.get("created_at") else None,
        "updated_at": str(row.get("updated_at")) if row.get("updated_at") else None,
    }


@router.post("/save")
async def save_story(req: SaveStoryRequest, user: dict = Depends(get_current_user)):
    """保存或更新作品草稿；同步写入 chapters 表。"""
    from services.chapter_store import parse_chapters_json, sync_chapters_table, chapters_to_json

    uid = str(user.get("sub", "0"))
    ch_list = parse_chapters_json(req.chapters)
    word_count = sum(len(str(ch.get("content", ""))) for ch in ch_list if isinstance(ch, dict))
    db = _db()
    try:
        cursor = db.cursor()
        if req.id:
            cursor.execute("SELECT user_id FROM stories WHERE id = %s LIMIT 1", (req.id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="作品不存在")
            if row[0] and str(row[0]) != uid:
                raise HTTPException(status_code=403, detail="无权修改该作品")
            story_id = req.id
            cursor.execute(
                "UPDATE stories SET title=%s, genre=%s, intro=%s, outline=%s, characters=%s, "
                "chapters=%s, status=%s, word_count=%s, user_id=%s, updated_at=NOW() WHERE id=%s",
                (req.title, req.genre, req.intro, req.outline, req.characters,
                 req.chapters, req.status or "draft", word_count, uid, story_id),
            )
        else:
            story_id = int(time.time() * 1000)
            cursor.execute(
                "INSERT INTO stories (id, user_id, title, genre, intro, outline, characters, chapters, "
                "status, word_count, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())",
                (story_id, uid, req.title, req.genre, req.intro, req.outline, req.characters,
                 req.chapters, req.status or "draft", word_count),
            )
        if ch_list:
            wc = sync_chapters_table(cursor, story_id, uid, ch_list)
            cursor.execute("UPDATE stories SET word_count=%s, chapters=%s WHERE id=%s",
                           (wc, chapters_to_json(parse_chapters_json(req.chapters) or ch_list), story_id))
        db.commit()
        return {"success": True, "story_id": story_id}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        print(f"[Story.save] 失败: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="保存失败")
    finally:
        if db.is_connected():
            db.close()


@router.post("/create")
async def create_story(req: SaveStoryRequest, user: dict = Depends(get_current_user)):
    """新建作品（等价于不带 id 的保存）。"""
    req.id = None
    return await save_story(req, user)


@router.get("/list")
async def list_stories(status: Optional[str] = None, user: dict = Depends(get_current_user)):
    """获取当前用户的作品列表。"""
    uid = str(user.get("sub", "0"))
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        if status and status != "all":
            cursor.execute(
                "SELECT * FROM stories WHERE user_id=%s AND status=%s ORDER BY updated_at DESC",
                (uid, status),
            )
        else:
            cursor.execute(
                "SELECT * FROM stories WHERE user_id=%s ORDER BY updated_at DESC", (uid,)
            )
        rows = cursor.fetchall()
        return {"success": True, "stories": [_story_to_dict(r) for r in rows], "total": len(rows)}
    except Exception as exc:
        print(f"[Story.list] 失败: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="获取作品列表失败")
    finally:
        if db.is_connected():
            db.close()


@router.get("/{story_id}/chapters")
async def list_chapters(story_id: int, user: dict = Depends(get_current_user)):
    """章节列表（优先 chapters 表）。"""
    from services.chapter_store import merge_chapters_for_story, chapters_to_json
    uid = str(user["sub"])
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT user_id, chapters FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if str(row["user_id"]) != uid:
            raise HTTPException(status_code=403, detail="无权查看")
        chapters = merge_chapters_for_story(cursor, story_id, row.get("chapters"))
        return {"success": True, "chapters": chapters, "total": len(chapters)}
    finally:
        if db.is_connected():
            db.close()


@router.get("/{story_id}/export")
async def export_story(story_id: int, format: str = "txt", user: dict = Depends(get_current_user)):
    """导出作品为 TXT 或 Markdown。"""
    uid = str(user.get("sub", "0"))
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if row.get("user_id") and str(row["user_id"]) != uid:
            raise HTTPException(status_code=403, detail="无权导出该作品")
        from services.chapter_store import merge_chapters_for_story
        chapters = merge_chapters_for_story(cursor, story_id, row.get("chapters"))
        title = row.get("title") or "未命名"
        lines = [f"# {title}" if format == "md" else title, ""]
        if row.get("intro"):
            lines += [row["intro"], ""]
        for i, ch in enumerate(chapters, 1):
            if not isinstance(ch, dict):
                continue
            ct = ch.get("title") or f"第{i}章"
            body = ch.get("content") or ch.get("summary") or ""
            if format == "md":
                lines += [f"## {ct}", "", body, ""]
            else:
                lines += [ct, body, ""]
        text = "\n".join(lines)
        media = "text/markdown" if format == "md" else "text/plain"
        ext = "md" if format == "md" else "txt"
        return PlainTextResponse(
            content=text,
            media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{title}.{ext}"'},
        )
    finally:
        if db.is_connected():
            db.close()


@router.get("/{story_id}/memory")
async def story_memory(story_id: int, user: dict = Depends(get_current_user)):
    """小说大脑完整视图。"""
    from services.story_memory import load_brain
    uid = str(user.get("sub", "0"))
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT user_id, title, characters, outline FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if row.get("user_id") and str(row["user_id"]) != uid:
            raise HTTPException(status_code=403, detail="无权查看")
        brain = load_brain(cursor, story_id)
        return {"success": True, "title": row.get("title"), "outline": row.get("outline"), **brain}
    finally:
        if db.is_connected():
            db.close()


@router.get("/{story_id}")
async def get_story(story_id: int, user: dict = Depends(get_current_user)):
    """获取作品详情（章节优先从 chapters 表加载）。"""
    from services.chapter_store import merge_chapters_for_story, chapters_to_json
    uid = str(user.get("sub", "0"))
    db = _db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if row.get("user_id") and str(row["user_id"]) != uid:
            raise HTTPException(status_code=403, detail="无权查看该作品")
        chapters = merge_chapters_for_story(cursor, story_id, row.get("chapters"))
        if chapters:
            row["chapters"] = chapters_to_json(chapters)
        return {"success": True, "story": _story_to_dict(row)}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"[Story.get] 失败: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="获取作品失败")
    finally:
        if db.is_connected():
            db.close()


@router.put("/{story_id}")
async def update_story(story_id: int, req: SaveStoryRequest, user: dict = Depends(get_current_user)):
    """更新作品（仅本人）。"""
    req.id = story_id
    return await save_story(req, user)


@router.delete("/{story_id}")
async def delete_story(story_id: int, user: dict = Depends(get_current_user)):
    """删除作品（仅本人）。"""
    uid = str(user.get("sub", "0"))
    db = _db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM stories WHERE id=%s LIMIT 1", (story_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="作品不存在")
        if row[0] and str(row[0]) != uid:
            raise HTTPException(status_code=403, detail="无权删除该作品")
        cursor.execute("DELETE FROM stories WHERE id=%s", (story_id,))
        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        print(f"[Story.delete] 失败: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="删除失败")
    finally:
        if db.is_connected():
            db.close()
