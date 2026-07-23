"""
🧠 V1.9 爆款识别模型 (核心大脑)
AI驱动的内容评分系统 - 自动识别什么是"爆款"
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import math

router = APIRouter()


# 模型权重配置
MODEL_WEIGHTS = {
    "stay_time": 0.35,      # 停留时间权重
    "click_rate": 0.25,     # 点击率权重  
    "share_rate": 0.20,     # 分享率权重
    "return_rate": 0.15,    # 回访率权重
    "completion": 0.05      # 完成率权重
}


# 爆款阈值配置
HOT_THRESHOLDS = {
    "S": 85,   # S级爆款
    "A": 70,   # A级热门
    "B": 50,   # B级普通
    "C": 0     # C级冷门
}


class ContentScoreRequest(BaseModel):
    content_id: str
    stay_time: int = 0          # 平均停留时间(秒)
    click_count: int = 0        # 点击次数
    share_count: int = 0        # 分享次数
    return_count: int = 0       # 回访次数
    view_count: int = 0         # 浏览次数
    completion_rate: float = 0  # 完成率 (0-1)


class ScoreResponse(BaseModel):
    content_id: str
    total_score: float
    level: str  # S/A/B/C
    factors: dict
    is_hot: bool


def calculate_entropy_score(data: dict) -> float:
    """
    🌊 基于信息熵的内容多样性评分
    衡量内容的"信息密度"
    """
    if not data.get("content_text"):
        return 50.0
    
    text = data["content_text"]
    # 简单熵值计算：不同词汇越多，信息量越大
    words = set(text)
    unique_ratio = len(words) / max(len(text), 1)
    
    return min(100, unique_ratio * 200)


def calculate_momentum_score(data: dict) -> float:
    """
    🚀 内容增长动量评分
    最近的流量趋势
    """
    recent_views = data.get("recent_views", 0)
    older_views = data.get("older_views", 1)
    
    if older_views == 0:
        return 50.0
    
    growth_rate = (recent_views - older_views) / older_views
    
    # 动量评分：增长越快分数越高
    momentum = 50 + (growth_rate * 50)
    return max(0, min(100, momentum))


@router.post("/score")
def score_content(req: ContentScoreRequest):
    """
    🧠 对内容进行爆款评分
    """
    # 基础评分计算
    score = 0
    
    # 1. 停留时间评分 (0-100)
    stay_score = min(100, req.stay_time * 1.5)  # 60秒=90分
    score += stay_score * MODEL_WEIGHTS["stay_time"]
    
    # 2. 点击率评分
    if req.view_count > 0:
        click_rate = req.click_count / req.view_count
        click_score = min(100, click_rate * 200)
    else:
        click_score = 0
    score += click_score * MODEL_WEIGHTS["click_rate"]
    
    # 3. 分享率评分
    if req.view_count > 0:
        share_rate = req.share_count / req.view_count
        share_score = min(100, share_rate * 500)  # 分享少但珍贵
    else:
        share_score = 0
    score += share_score * MODEL_WEIGHTS["share_rate"]
    
    # 4. 回访率评分
    if req.click_count > 0:
        return_rate = req.return_count / req.click_count
        return_score = min(100, return_rate * 200)
    else:
        return_score = 0
    score += return_score * MODEL_WEIGHTS["return_rate"]
    
    # 5. 完成率评分
    completion_score = req.completion_rate * 100
    score += completion_score * MODEL_WEIGHTS["completion"]
    
    total_score = round(score, 2)
    
    # 确定级别
    if total_score >= HOT_THRESHOLDS["S"]:
        level = "S"
    elif total_score >= HOT_THRESHOLDS["A"]:
        level = "A"
    elif total_score >= HOT_THRESHOLDS["B"]:
        level = "B"
    else:
        level = "C"
    
    return ScoreResponse(
        content_id=req.content_id,
        total_score=total_score,
        level=level,
        is_hot=total_score >= HOT_THRESHOLDS["B"],
        factors={
            "stay_score": round(stay_score * MODEL_WEIGHTS["stay_time"], 2),
            "click_score": round(click_score * MODEL_WEIGHTS["click_rate"], 2),
            "share_score": round(share_score * MODEL_WEIGHTS["share_rate"], 2),
            "return_score": round(return_score * MODEL_WEIGHTS["return_rate"], 2),
            "completion_score": round(completion_score * MODEL_WEIGHTS["completion"], 2)
        }
    )


@router.get("/is_hot/{content_id}")
def check_is_hot(
    content_id: str,
    stay_time: int = 30,
    click_count: int = 10,
    share_count: int = 2,
    view_count: int = 100
):
    """
    🔥 快速检查内容是否为爆款
    """
    req = ContentScoreRequest(
        content_id=content_id,
        stay_time=stay_time,
        click_count=click_count,
        share_count=share_count,
        view_count=view_count
    )
    result = score_content(req)
    return {
        "content_id": content_id,
        "is_hot": result.is_hot,
        "score": result.total_score,
        "level": result.level
    }


@router.post("/batch_score")
def batch_score(contents: list[ContentScoreRequest]):
    """
    📊 批量评分
    """
    results = []
    for req in contents:
        result = score_content(req)
        results.append({
            "content_id": result.content_id,
            "score": result.total_score,
            "level": result.level,
            "is_hot": result.is_hot
        })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "total": len(results),
        "hot_count": len([r for r in results if r["is_hot"]]),
        "results": results
    }


@router.get("/leaderboard")
def get_leaderboard(limit: int = 10):
    """
    🏆 爆款排行榜
    """
    # 模拟数据 - 更丰富的热门作品
    mock_data = [
        {"content_id": "1", "score": 98, "level": "S", "title": "开局十个亿，我在都市横着走", "type": "都市神豪", "views": "256万", "tags": ["系统", "爽文", "打脸"]},
        {"content_id": "2", "score": 95, "level": "S", "title": "战神回归，发现女儿住狗窝", "type": "战神归来", "views": "183万", "tags": ["虐心", "逆袭", "女儿"]},
        {"content_id": "3", "score": 92, "level": "S", "title": "重生2003，当首富很简单", "type": "重生创业", "views": "152万", "tags": ["重生", "赚钱", "创业"]},
        {"content_id": "4", "score": 88, "level": "S", "title": "我在仙界拍短视频", "type": "脑洞搞笑", "views": "128万", "tags": ["穿越", "搞笑", "仙侠"]},
        {"content_id": "5", "score": 85, "level": "A", "title": "全职艺术家：从up主开始", "type": "娱乐明星", "views": "105万", "tags": ["系统", "文娱", "反转"]},
        {"content_id": "6", "score": 82, "level": "A", "title": "都市绝品神医", "type": "都市医生", "views": "92万", "tags": ["医生", "逆袭", "高手"]},
        {"content_id": "7", "score": 78, "level": "A", "title": "修仙五百年，我举世无敌", "type": "玄幻修仙", "views": "88万", "tags": ["修仙", "无敌", "升级"]},
        {"content_id": "8", "score": 75, "level": "A", "title": "逃婚99次：特工萌妻难搞定", "type": "甜宠婚恋", "views": "76万", "tags": ["甜宠", "特工", "闪婚"]},
        {"content_id": "9", "score": 72, "level": "B", "title": "末日游戏：只有我能生存", "type": "末世求生", "views": "65万", "tags": ["末世", "游戏", "生存"]},
        {"content_id": "10", "score": 68, "level": "B", "title": "离婚后，前夫求我再婚一次", "type": "豪门虐恋", "views": "58万", "tags": ["虐恋", "复仇", "霸总"]},
    ]
    return mock_data[:limit]


@router.get("/config")
def get_model_config():
    """
    ⚙️ 获取模型配置
    """
    return {
        "weights": MODEL_WEIGHTS,
        "thresholds": HOT_THRESHOLDS,
        "version": "1.9.0",
        "model_type": "weighted_scoring"
    }


@router.post("/config")
def update_model_config(weights: dict = None, thresholds: dict = None):
    """
    ⚙️ 更新模型配置
    """
    global MODEL_WEIGHTS, HOT_THRESHOLDS
    
    if weights:
        MODEL_WEIGHTS.update(weights)
    if thresholds:
        HOT_THRESHOLDS.update(thresholds)
    
    return {"status": "ok", "weights": MODEL_WEIGHTS, "thresholds": HOT_THRESHOLDS}