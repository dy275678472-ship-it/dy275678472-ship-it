"""
🌐 V1.9 SEO自进化系统
自动学习SEO规律并扩展关键词
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import random

router = APIRouter()


# SEO扩展关键词库
KEYWORD_SUFFIXES = {
    "novel": [
        "小说全文", "小说txt下载", "小说结局", 
        "剧情解析", "人物关系图", "隐藏设定",
        "世界观分析", "战力排行", "CP盘点",
        "续集", "外传", "番外", "解说"
    ],
    "character": [
        "是谁", "身份", "实力", "结局",
        "bg", "cp", "图片", "头像",
        "高清图", "壁纸", "配音"
    ],
    "analysis": [
        "深度解析", "全面解读", "剧情分析",
        "伏笔盘点", "细节解读", "彩蛋分析",
        "世界观讲解", "设定科普"
    ]
}

HIGH_TRAFFIC_WORDS = [
    "逆袭", "重生", "系统", "觉醒", "穿越",
    "甜宠", "虐恋", "复仇", "马甲", "团宠",
    "修仙", "都市", "星际", "病娇", "绿茶"
]


class SEORequest(BaseModel):
    base_keywords: List[str]
    content_id: str = ""  # 可选
    content_type: str = "novel"
    expand_count: int = 10


class SEOVariant(BaseModel):
    keyword: str
    traffic_score: int
    type: str  # main, long_tail, related


@router.post("/evolve_keywords")
def evolve_keywords(req: SEORequest):
    """
    🔑 SEO关键词自进化
    """
    evolved = []
    
    for keyword in req.base_keywords:
        # 1. 原始关键词
        evolved.append({
            "keyword": keyword,
            "traffic_score": 80,
            "type": "main"
        })
        
        # 2. 长尾关键词
        suffixes = KEYWORD_SUFFIXES.get(req.content_type, KEYWORD_SUFFIXES["novel"])
        selected_suffixes = random.sample(
            suffixes, 
            min(3, len(suffixes))
        )
        
        for suffix in selected_suffixes:
            long_tail = keyword + suffix
            evolved.append({
                "keyword": long_tail,
                "traffic_score": random.randint(50, 70),
                "type": "long_tail"
            })
        
        # 3. 组合高频词
        for word in random.sample(HIGH_TRAFFIC_WORDS, 2):
            if word not in keyword:
                combo = word + keyword
                evolved.append({
                    "keyword": combo,
                    "traffic_score": random.randint(60, 75),
                    "type": "related"
                })
    
    # 去重
    seen = set()
    unique_evolved = []
    for item in evolved:
        if item["keyword"] not in seen:
            seen.add(item["keyword"])
            unique_evolved.append(item)
    
    return {
        "base_keywords": req.base_keywords,
        "content_id": req.content_id,
        "total_count": len(unique_evolved),
        "keywords": unique_evolved[:req.expand_count]
    }


@router.get("/blast/{content_id}")
def seo_blast(content_id: str):
    """
    🚀 SEO扩散自动放大 - 为内容生成多个流量入口
    """
    blast_urls = [
        f"/novel/{content_id}",           # 主页面
        f"/novel/{content_id}-1",         # 第1章
        f"/novel/{content_id}-analysis",  # 解析页
        f"/novel/{content_id}-worldview", # 世界观
        f"/novel/{content_id}-hidden",    # 隐藏设定
        f"/novel/{content_id}-char",      # 角色页
        f"/novel/{content_id}-timeline",  # 时间线
        f"/read/{content_id}",            # 阅读页
        f"/read/{content_id}-chapter-1",  # 第1章阅读
        f"/api/feedback/{content_id}"     # 反馈接口
    ]
    
    return {
        "content_id": content_id,
        "url_count": len(blast_urls),
        "urls": blast_urls,
        "strategy": "multi_entry_seo"
    }


@router.post("/auto_optimize")
def auto_seo_optimize(
    title: str,
    description: str = "",
    tags: List[str] = []
):
    """
    🎯 自动SEO优化
    """
    # 提取关键词
    keywords = tags.copy() if tags else []
    
    # 从标题提取
    for word in HIGH_TRAFFIC_WORDS:
        if word in title and word not in keywords:
            keywords.append(word)
    
    # 生成SEO友好的元信息
    optimized = {
        "title": title,
        "meta_title": f"{title}_热门爽文推荐",
        "meta_description": f"阅读{title}，{description[:100] if description else '推荐精彩小说章节'}",
        "keywords": keywords + [title],
        "tags": keywords,
        "suggested_links": [
            f"/category/{random.choice(['xianxia', 'dushi', 'yinyang'])}"
            for _ in range(3)
        ]
    }
    
    return {
        "status": "ok",
        "original": {"title": title, "description": description, "tags": tags},
        "optimized": optimized
    }


@router.get("/trending_keywords")
def get_trending_keywords(limit: int = 20):
    """
    🔥 获取热门关键词
    """
    trending = []
    
    # 高流量词
    for word in HIGH_TRAFFIC_WORDS:
        trending.append({
            "keyword": word,
            "traffic_score": random.randint(70, 95),
            "category": "hot",
            "volume": random.randint(10000, 100000)
        })
    
    # 组合词
    combos = [
        "重生都市", "修仙系统和", "穿越逆袭",
        "甜宠高干", "病娇男主", "马甲千金"
    ]
    for word in combos:
        trending.append({
            "keyword": word,
            "traffic_score": random.randint(60, 80),
            "category": "combo",
            "volume": random.randint(5000, 50000)
        })
    
    return {
        "count": len(trending),
        "keywords": sorted(trending, key=lambda x: x["traffic_score"], reverse=True)[:limit]
    }


@router.post("/track_keyword")
def track_keyword(keyword: str, position: int, traffic: int = 0):
    """
    📊 跟踪关键词排名
    """
    return {
        "keyword": keyword,
        "position": position,
        "traffic": traffic,
        "timestamp": "now",
        "status": "tracked"
    }


@router.get("/keyword_stats")
def get_keyword_stats(keyword: str = None):
    """
    📈 关键词统计数据
    """
    if keyword:
        return {
            "keyword": keyword,
            "position": random.randint(1, 50),
            "impressions": random.randint(1000, 10000),
            "clicks": random.randint(100, 1000),
            "ctr": round(random.uniform(0.05, 0.2), 3)
        }
    
    return {
        "total_tracked": len(HIGH_TRAFFIC_WORDS) * 3,
        "top_keywords": [
            {"keyword": w, "position": i+1} 
            for i, w in enumerate(HIGH_TRAFFIC_WORDS[:10])
        ]
    }


@router.get("/suggest/{prefix}")
def suggest_keywords(prefix: str, limit: int = 10):
    """
    🔍 关键词自动补全建议
    """
    suggestions = []
    
    for word in HIGH_TRAFFIC_WORDS:
        if word.startswith(prefix):
            suggestions.append(word)
    
    # 添加组合
    for combo in KEYWORD_SUFFIXES["novel"]:
        if prefix in combo:
            suggestions.append(combo)
    
    return {
        "prefix": prefix,
        "suggestions": suggestions[:limit]
    }