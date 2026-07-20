"""
📊 V1.9 用户行为采集系统
自动采集用户浏览、停留、点击、分享等行为数据
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from api.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time

router = APIRouter()

# 行为数据存储 (生产环境应使用数据库)
USER_BEHAVIOR_DB = []


# 数据模型
class BehaviorRecord(BaseModel):
    user_id: Optional[int] = None
    content_id: str
    content_type: str = "chapter"  # chapter, story, ip
    action: str  # view, click, stay, share, return
    stay_time: Optional[int] = 0  # 停留秒数
    click_position: Optional[int] = None  # 点击位置
    from_source: Optional[str] = None  # 来源：baidu, wechat, direct


class BehaviorStats(BaseModel):
    total_views: int
    total_stays: int
    avg_stay_time: float
    hot_contents: List[dict]


# @router.post("/track")
# def track_behavior(record: BehaviorRecord):
#     """📊 记录用户行为"""
#     entry = record.dict()
#     entry["timestamp"] = datetime.now().isoformat()
#     entry["id"] = len(USER_BEHAVIOR_DB) + 1
#     USER_BEHAVIOR_DB.append(entry)
#     return {"status": "ok", "id": entry["id"]}


@router.post("/track")
def track_view(
    content_id: str,
    content_type: str = "chapter",
    user_id: Optional[int] = None,
    stay_time: int = 0,
    action: str = "view",
    from_source: Optional[str] = None
):
    """
    📊 记录用户行为 (简化版)
    """
    entry = {
        "id": len(USER_BEHAVIOR_DB) + 1,
        "user_id": user_id,
        "content_id": content_id,
        "content_type": content_type,
        "action": action,
        "stay_time": stay_time,
        "from_source": from_source,
        "timestamp": datetime.now().isoformat()
    }
    USER_BEHAVIOR_DB.append(entry)
    
    return {
        "status": "ok",
        "tracked": True,
        "content_id": content_id,
        "stay_time": stay_time
    }


@router.get("/stats")
def get_behavior_stats(limit: int = Query(10, ge=1, le=100), _user: dict = Depends(get_current_user)):
    """
    📊 获取行为统计数据
    """
    if not USER_BEHAVIOR_DB:
        return {
            "total_views": 0,
            "total_stays": 0,
            "avg_stay_time": 0,
            "hot_contents": []
        }
    
    # 统计总浏览
    total_views = len([b for b in USER_BEHAVIOR_DB if b["action"] == "view"])
    
    # 统计停留
    stays = [b for b in USER_BEHAVIOR_DB if b.get("stay_time", 0) > 0]
    total_stays = len(stays)
    avg_stay_time = sum(b["stay_time"] for b in stays) / total_stays if total_stays > 0 else 0
    
    # 热门内容 (按停留时间排序)
    sorted_behaviors = sorted(
        USER_BEHAVIOR_DB,
        key=lambda x: x.get("stay_time", 0),
        reverse=True
    )[:limit]
    
    hot_contents = []
    seen = set()
    for b in sorted_behaviors:
        cid = b["content_id"]
        if cid not in seen:
            seen.add(cid)
            hot_contents.append({
                "content_id": cid,
                "stay_time": b.get("stay_time", 0),
                "action": b["action"],
                "timestamp": b["timestamp"]
            })
    
    return BehaviorStats(
        total_views=total_views,
        total_stays=total_stays,
        avg_stay_time=round(avg_stay_time, 2),
        hot_contents=hot_contents
    )


@router.get("/patterns")
def get_hot_patterns(limit: int = Query(20, ge=1, le=100), _user: dict = Depends(get_current_user)):
    """
    🔥 获取热门模式（高停留内容）
    """
    # 过滤高停留内容
    hot = [b for b in USER_BEHAVIOR_DB if b.get("stay_time", 0) > 30]
    
    # 按内容ID聚合
    content_scores = {}
    for b in hot:
        cid = b["content_id"]
        if cid not in content_scores:
            content_scores[cid] = {"content_id": cid, "views": 0, "total_stay": 0}
        content_scores[cid]["views"] += 1
        content_scores[cid]["total_stay"] += b.get("stay_time", 0)
    
    # 计算平均停留并排序
    patterns = []
    for cid, data in content_scores.items():
        patterns.append({
            "content_id": cid,
            "views": data["views"],
            "avg_stay": round(data["total_stay"] / data["views"], 2),
            "score": data["views"] * 0.5 + data["total_stay"] * 0.5
        })
    
    patterns.sort(key=lambda x: x["score"], reverse=True)
    return patterns[:limit]


@router.get("/sources")
def get_source_stats(_user: dict = Depends(get_current_user)):
    """
    📈 来源分析
    """
    sources = {}
    for b in USER_BEHAVIOR_DB:
        src = b.get("from_source", "direct") or "direct"
        if src not in sources:
            sources[src] = {"name": src, "views": 0, "total_stay": 0}
        sources[src]["views"] += 1
        sources[src]["total_stay"] += b.get("stay_time", 0)
    
    return list(sources.values())


@router.get("/all")
def get_all_behaviors(limit: int = Query(100, ge=1, le=500), _user: dict = Depends(get_current_user)):
    """
    📋 获取所有行为记录
    """
    return USER_BEHAVIOR_DB[-limit:]


@router.post("/clear")
def clear_behaviors(_user: dict = Depends(get_current_user)):
    """
    🗑️ 清空行为数据
    """
    global USER_BEHAVIOR_DB
    USER_BEHAVIOR_DB = []
    return {"status": "ok", "message": "行为数据已清空"}


@router.post("/simulate")
def simulate_traffic(count: int = Query(50, ge=1, le=500), _user: dict = Depends(get_current_user)):
    """
    🎭 模拟流量数据（测试用）
    """
    import random
    contents = ["chapter_1", "chapter_2", "chapter_3", "story_ai", "story_xian"]
    sources = ["baidu", "wechat", "toutiao", "direct", "zhihu"]
    
    for i in range(count):
        entry = {
            "id": len(USER_BEHAVIOR_DB) + 1,
            "user_id": random.randint(1, 10),
            "content_id": random.choice(contents),
            "content_type": "chapter",
            "action": random.choice(["view", "view", "view", "stay", "click"]),
            "stay_time": random.randint(5, 120),
            "from_source": random.choice(sources),
            "timestamp": datetime.now().isoformat()
        }
        USER_BEHAVIOR_DB.append(entry)
    
    return {"status": "ok", "generated": count, "total": len(USER_BEHAVIOR_DB)}
