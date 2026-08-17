"""
🧬 V1.9 内容进化系统 (核心)
自动识别爆款结构并生成变异内容
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
import re

router = APIRouter()


# 进化变异模板
TITLE_MUTATIONS = [
    "（系统觉醒版）",
    "（逆袭加强版）",
    "（爽点强化版）",
    "（隐藏剧情曝光）",
    "（完整版）",
    "（全集）",
    "（终极版）",
    "（高能版）",
    "（绝密档案）",
    "（独家首发）"
]

CONTENT_MUTATIONS = [
    "【系统提示】：内容已觉醒",
    "【独家揭秘】",
    "【深度解析】",
    "【粉丝福利】",
    "【完整版】",
    "【加强剧情】"
]

INTRO_TEMPLATES = [
    "开局直接起飞，",
    " 谁也没想到，",
    " 惊天逆转来了！",
    " 所有人都低估了",
    " 这一次，",
    " 真正的王者的",
    " 从零开始的逆袭，"
]

ENDING_TEMPLATES = [
    " 震惊所有人！",
    " 故事才刚刚开始...",
    " 命运齿轮开始转动！",
    " 所有人都傻眼了！",
    " 这只是开始！",
    " 真正的挑战才到来！",
    " 未完待续..."
]


class EvolutionRequest(BaseModel):
    base_content: str
    content_type: str = "title"  # title, content, story
    mutate_count: int = 3


class EvolvedContent(BaseModel):
    original: str
    evolved: str
    mutation_type: str


@router.post("/mutate")
def mutate_content(req: EvolutionRequest):
    """
    🧬 内容变异 - 基于模板随机组合
    """
    evolved_list = []
    
    if req.content_type == "title":
        mutations = random.sample(TITLE_MUTATIONS, min(req.mutate_count, len(TITLE_MUTATIONS)))
        for m in mutations:
            evolved_list.append({
                "original": req.base_content,
                "evolved": req.base_content + m,
                "mutation_type": "title_extension"
            })
    
    elif req.content_type == "content":
        mutations = random.sample(CONTENT_MUTATIONS, min(req.mutate_count, len(CONTENT_MUTATIONS)))
        for m in mutations:
            evolved_list.append({
                "original": req.base_content[:50] + "...",
                "evolved": m + req.base_content,
                "mutation_type": "content_prepend"
            })
    
    else:  # story
        # 生成多种变异版本
        for _ in range(req.mutate_count):
            intro = random.choice(INTRO_TEMPLATES)
            ending = random.choice(ENDING_TEMPLATES)
            evolved = intro + req.base_content + ending
            evolved_list.append({
                "original": req.base_content,
                "evolved": evolved,
                "mutation_type": "story_enhance"
            })
    
    return {
        "status": "ok",
        "count": len(evolved_list),
        "evolutions": evolved_list
    }


@router.post("/evolve_list")
def evolve_hot_content(hot_titles: List[str]):
    """
    🔥 批量进化热门内容
    """
    evolved = []
    for title in hot_titles:
        mutation = random.choice(TITLE_MUTATIONS)
        evolved.append({
            "original": title,
            "evolved": title + mutation,
            "mutation_type": "hot_boost"
        })
    
    return {
        "status": "ok",
        "evolved_count": len(evolved),
        "results": evolved
    }


@router.get("/templates")
def get_mutation_templates():
    """
    📋 获取可用变异模板
    """
    return {
        "title_mutations": TITLE_MUTATIONS,
        "content_mutations": CONTENT_MUTATIONS,
        "intro_templates": INTRO_TEMPLATES,
        "ending_templates": ENDING_TEMPLATES
    }


# ==================== Request Models ====================

class EnhanceRequest(BaseModel):
    """内容增强请求"""
    title: str
    content: str = ""
    style: str = "default"  # default, intense, mystery

class SmartEvolveRequest(BaseModel):
    """智能进化请求"""
    base_title: str
    target_score: int = 80
    context: str = ""

class GenerateVariantsRequest(BaseModel):
    """生成变体请求"""
    base_title: str
    count: int = 5


# ==================== API Endpoints ====================

@router.post("/enhance")
def enhance_content(req: EnhanceRequest):
    """
    💪 内容增强 - 根据风格自动调整
    """
    title = req.title
    content = req.content
    style = req.style
    
    enhancements = {
        "default": {
            "title": title,
            "intro": "故事开始于",
            "ending": "未完待续..."
        },
        "intense": {
            "title": "【高能】" + title + "（极限挑战）",
            "intro": "危机降临！",
            "ending": "真正的战斗才开始！"
        },
        "mystery": {
            "title": title + "（隐藏真相）",
            "intro": "谁也没有想到，",
            "ending": "秘密永远被封印..."
        }
    }
    
    style_enhance = enhancements.get(style, enhancements["default"])
    
    # 生成增强版内容
    enhanced = {
        "title": style_enhance["title"],
        "content_intro": style_enhance["intro"] + (content[:100] if content else ""),
        "content_ending": style_enhance["ending"],
        "full_title": style_enhance["title"]
    }
    
    return {
        "status": "ok",
        "original": {"title": title, "content": content[:100] if content else ""},
        "enhanced": enhanced,
        "style": style
    }


@router.post("/generate_variants")
def generate_variants(req: GenerateVariantsRequest):
    """
    🎨 生成标题变体 - A/B测试用
    """
    base_title = req.base_title
    count = req.count
    
    # 组合不同元素生成多种变体
    prefixes = ["", "【爆】", "【爽】", "🔥", "🚀", "✨"]
    suffixes = ["", "（必看）", "（收藏）", "（推荐）", "完整版", "全集"]
    
    variants = []
    for i in range(count):
        prefix = random.choice(prefixes) if i % 2 == 0 else ""
        suffix = random.choice(suffixes) if i % 3 == 0 else ""
        
        # 随机组合
        variant = prefix + base_title + suffix
        if variant not in [v["title"] for v in variants]:
            variants.append({
                "title": variant,
                "variant_id": i + 1,
                "type": f"variant_{i+1}"
            })
    
    return {
        "base_title": base_title,
        "variant_count": len(variants),
        "variants": variants
    }


@router.post("/smart_evolve")
def smart_evolve(req: SmartEvolveRequest):
    """
    🧠 智能进化 - 根据目标受众自动调整
    """
    base_title = req.base_title
    target_score = req.target_score
    context = req.context
    
    # 分析目标受众并选择合适的变异
    if "逆袭" in base_title or "废柴" in base_title:
        # 逆袭类
        templates = [
            f"逆天改命：{base_title}",
            f"{base_title}（从废物到强者）",
            f"{base_title}：绝境重生",
            f"重活一世：{base_title}"
        ]
    elif "修仙" in base_title or "仙侠" in base_title:
        # 修仙类
        templates = [
            f"仙途崛起：{base_title}",
            f"{base_title}（修仙成神）",
            f"飞升之路：{base_title}"
        ]
    elif "都市" in base_title or "重生" in base_title:
        # 都市类
        templates = [
            f"都市王者：{base_title}",
            f"{base_title}（首富之路）",
            f"重生传奇：{base_title}"
        ]
    else:
        # 默认
        templates = [base_title + random.choice(TITLE_MUTATIONS) for _ in range(4)]
    
    return {
        "base_title": base_title,
        "target_score": target_score,
        "context": context,
        "evolved_titles": templates,
        "strategy": "auto_detected"
    }