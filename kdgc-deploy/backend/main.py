import os
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from models import Base, Case, Lead, News, Product

app = FastAPI(title="KDGC API", version="2.0.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://kdgc.cc,http://kdgc.cc,http://150.158.42.39").split(",")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "kdgc-admin-change-me")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_rate: dict[str, list[float]] = defaultdict(list)


def check_rate(ip: str, limit: int = 5, window: int = 3600):
    now = time.time()
    _rate[ip] = [t for t in _rate[ip] if now - t < window]
    if len(_rate[ip]) >= limit:
        raise HTTPException(429, "提交过于频繁，请稍后再试")
    _rate[ip].append(now)


class LeadIn(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    email: Optional[EmailStr] = None
    product_interest: Optional[str] = None
    requirement: Optional[str] = None
    website: Optional[str] = None  # honeypot


class AIChatIn(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "version": "2.0.0"}


@app.post("/api/leads")
async def create_lead(data: LeadIn, request: Request, db: AsyncSession = Depends(get_db)):
    if data.website:
        return {"success": True, "message": "我们将在24小时内联系您"}
    if not re.match(r"^1[3-9]\d{9}$", data.phone) and "@" not in data.phone:
        if not data.email:
            raise HTTPException(400, "请填写有效手机号或邮箱")
    check_rate(request.client.host if request.client else "unknown")
    lead = Lead(
        company=data.company.strip(),
        contact_name=data.contact_name.strip(),
        phone=data.phone.strip(),
        email=str(data.email) if data.email else None,
        product_interest=data.product_interest,
        requirement=data.requirement,
        source="website",
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    if FEISHU_WEBHOOK:
        text = (
            f"🔔 新询盘 — 中科国瓷官网\n"
            f"公司：{lead.company}\n联系人：{lead.contact_name}\n"
            f"手机：{lead.phone}\n邮箱：{lead.email or '-'}\n"
            f"产品：{lead.product_interest or '-'}\n需求：{lead.requirement or '-'}"
        )
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": text}})
        except Exception:
            pass
    return {"success": True, "message": "提交成功，我们将在24小时内联系您", "id": lead.id}


@app.get("/api/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Product).where(Product.is_published == True).order_by(Product.sort_order))
    items = r.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "tagline": p.tagline,
            "summary": p.summary,
            "image_url": p.image_url,
            "is_featured": p.is_featured,
        }
        for p in items
    ]


@app.get("/api/products/{slug}")
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Product).where(Product.slug == slug, Product.is_published == True))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404)
    return {
        "name": p.name,
        "slug": p.slug,
        "category": p.category,
        "tagline": p.tagline,
        "summary": p.summary,
        "content": p.content,
        "specs": p.specs,
        "applications": p.applications,
        "image_url": p.image_url,
        "seo_title": p.seo_title,
        "seo_description": p.seo_description,
    }


@app.get("/api/news")
async def list_news(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(News).where(News.is_published == True).order_by(News.published_at.desc()))
    return [
        {
            "title": n.title,
            "slug": n.slug,
            "summary": n.summary,
            "cover_image": n.cover_image,
            "published_at": n.published_at.isoformat() if n.published_at else None,
        }
        for n in r.scalars().all()
    ]


@app.get("/api/news/{slug}")
async def get_news(slug: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(News).where(News.slug == slug, News.is_published == True))
    n = r.scalar_one_or_none()
    if not n:
        raise HTTPException(404)
    return {
        "title": n.title,
        "slug": n.slug,
        "summary": n.summary,
        "content": n.content,
        "cover_image": n.cover_image,
        "published_at": n.published_at.isoformat() if n.published_at else None,
    }


@app.get("/api/cases")
async def list_cases(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Case).where(Case.is_published == True).order_by(Case.sort_order))
    return [
        {
            "title": c.title,
            "slug": c.slug,
            "industry": c.industry,
            "challenge": c.challenge,
            "solution": c.solution,
            "result": c.result,
            "cover_image": c.cover_image,
        }
        for c in r.scalars().all()
    ]


@app.get("/api/leads")
async def list_leads(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.headers.get("X-Admin-Token")
    if token != ADMIN_TOKEN:
        raise HTTPException(401)
    r = await db.execute(select(Lead).order_by(Lead.created_at.desc()).limit(100))
    return [
        {
            "id": l.id,
            "company": l.company,
            "contact_name": l.contact_name,
            "phone": l.phone,
            "email": l.email,
            "product_interest": l.product_interest,
            "requirement": l.requirement,
            "status": l.status,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in r.scalars().all()
    ]


@app.post("/api/ai/chat")
async def ai_chat(data: AIChatIn):
    """P3 skeleton — returns curated FAQ until RAG is connected."""
    faq = {
        "氮化铝": "氮化铝陶瓷基板导热率可达 150–200 W/m·K，适用于 IGBT 功率模块封装。",
        "dbc": "DBC（直接覆铜）工艺将铜层直接键合在陶瓷基板上，适用于大功率电力电子。",
        "样品": "可通过官网联系页提交样品申请，我们的技术团队将在24小时内回复。",
        "氧化铝": "氧化铝陶瓷纯度 92%–99.7%，耐温 1600°C，适用于高绝缘高温场景。",
    }
    answer = "感谢您的咨询。我们的技术团队可提供陶瓷基板选型建议。"
    for k, v in faq.items():
        if k.lower() in data.question.lower():
            answer = v
            break
    return {"answer": answer, "source": "faq", "note": "AI RAG 知识库接入中"}


# Legacy route compatibility
@app.get("/health")
async def health_legacy():
    return {"status": "ok"}


@app.post("/crm/lead")
async def crm_lead_legacy(data: LeadIn, request: Request, db: AsyncSession = Depends(get_db)):
    return await create_lead(data, request, db)
