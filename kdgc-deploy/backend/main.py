import os
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from models import Base, Case, Knowledge, Lead, News, Product

app = FastAPI(title="KDGC API", version="2.1.0")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "https://kdgc.cc,http://kdgc.cc,http://150.158.42.39,http://127.0.0.1"
).split(",")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "kdgc-admin-change-me")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()] + ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

_rate: dict[str, list[float]] = defaultdict(list)


def check_rate(ip: str, limit: int = 5, window: int = 3600):
    now = time.time()
    _rate[ip] = [t for t in _rate[ip] if now - t < window]
    if len(_rate[ip]) >= limit:
        raise HTTPException(429, "提交过于频繁，请稍后再试")
    _rate[ip].append(now)


def require_admin(request: Request):
    token = request.headers.get("X-Admin-Token") or ""
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "未授权：请提供正确的 Admin Token")


class LeadIn(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    email: Optional[EmailStr] = None
    product_interest: Optional[str] = None
    requirement: Optional[str] = None
    website: Optional[str] = None


class LeadStatusIn(BaseModel):
    status: str = Field(min_length=2, max_length=30)


class AIChatIn(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


class NewsIn(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool = True


class CaseIn(BaseModel):
    title: str
    slug: str
    industry: Optional[str] = None
    customer_alias: Optional[str] = None
    challenge: Optional[str] = None
    solution: Optional[str] = None
    result: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool = True
    sort_order: int = 0


class KnowledgeIn(BaseModel):
    title: str
    slug: str
    category: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool = True
    sort_order: int = 0


class ProductIn(BaseModel):
    name: str
    slug: str
    category: Optional[str] = None
    tagline: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: bool = False
    is_published: bool = True
    sort_order: int = 0


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # lightweight migrations for existing DBs
        for stmt in (
            "ALTER TABLE cases ADD COLUMN IF NOT EXISTS customer_alias VARCHAR(120)",
        ):
            try:
                await conn.execute(__import__("sqlalchemy").text(stmt))
            except Exception:
                pass


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "version": "2.1.0"}


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
            "id": n.id,
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
            "id": c.id,
            "title": c.title,
            "slug": c.slug,
            "industry": c.industry,
            "customer_alias": c.customer_alias,
            "challenge": c.challenge,
            "solution": c.solution,
            "result": c.result,
            "cover_image": c.cover_image,
        }
        for c in r.scalars().all()
    ]


@app.get("/api/knowledge")
async def list_knowledge(db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(Knowledge).where(Knowledge.is_published == True).order_by(Knowledge.sort_order, Knowledge.id)
    )
    return [
        {
            "id": k.id,
            "title": k.title,
            "slug": k.slug,
            "category": k.category,
            "summary": k.summary,
            "cover_image": k.cover_image,
        }
        for k in r.scalars().all()
    ]


@app.get("/api/knowledge/{slug}")
async def get_knowledge(slug: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Knowledge).where(Knowledge.slug == slug, Knowledge.is_published == True))
    k = r.scalar_one_or_none()
    if not k:
        raise HTTPException(404)
    return {
        "title": k.title,
        "slug": k.slug,
        "category": k.category,
        "summary": k.summary,
        "content": k.content,
        "cover_image": k.cover_image,
    }


# ---------- Admin ----------
@app.post("/api/admin/login")
async def admin_login(request: Request):
    require_admin(request)
    return {"ok": True, "role": "admin"}


@app.get("/api/admin/stats")
async def admin_stats(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)

    async def count(model):
        r = await db.execute(select(func.count()).select_from(model))
        return int(r.scalar() or 0)

    new_leads = await db.execute(select(func.count()).select_from(Lead).where(Lead.status == "new"))
    return {
        "products": await count(Product),
        "news": await count(News),
        "cases": await count(Case),
        "knowledge": await count(Knowledge),
        "leads": await count(Lead),
        "leads_new": int(new_leads.scalar() or 0),
    }


@app.get("/api/admin/leads")
@app.get("/api/leads")
async def list_leads(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Lead).order_by(Lead.created_at.desc()).limit(200))
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
            "source": l.source,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in r.scalars().all()
    ]


@app.patch("/api/admin/leads/{lead_id}")
async def update_lead(lead_id: int, data: LeadStatusIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = r.scalar_one_or_none()
    if not lead:
        raise HTTPException(404)
    lead.status = data.status.strip()
    await db.commit()
    return {"ok": True, "id": lead.id, "status": lead.status}


@app.get("/api/admin/news")
async def admin_list_news(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(News).order_by(News.id.desc()))
    return [
        {
            "id": n.id,
            "title": n.title,
            "slug": n.slug,
            "summary": n.summary,
            "content": n.content,
            "cover_image": n.cover_image,
            "is_published": n.is_published,
            "published_at": n.published_at.isoformat() if n.published_at else None,
        }
        for n in r.scalars().all()
    ]


@app.post("/api/admin/news")
async def admin_create_news(data: NewsIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    n = News(
        title=data.title,
        slug=data.slug,
        summary=data.summary,
        content=data.content,
        cover_image=data.cover_image,
        is_published=data.is_published,
        published_at=datetime.now(timezone.utc) if data.is_published else None,
    )
    db.add(n)
    await db.commit()
    await db.refresh(n)
    return {"ok": True, "id": n.id}


@app.put("/api/admin/news/{item_id}")
async def admin_update_news(item_id: int, data: NewsIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(News).where(News.id == item_id))
    n = r.scalar_one_or_none()
    if not n:
        raise HTTPException(404)
    n.title, n.slug, n.summary, n.content = data.title, data.slug, data.summary, data.content
    n.cover_image, n.is_published = data.cover_image, data.is_published
    await db.commit()
    return {"ok": True}


@app.delete("/api/admin/news/{item_id}")
async def admin_delete_news(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(News).where(News.id == item_id))
    n = r.scalar_one_or_none()
    if not n:
        raise HTTPException(404)
    await db.delete(n)
    await db.commit()
    return {"ok": True}


@app.get("/api/admin/cases")
async def admin_list_cases(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Case).order_by(Case.sort_order, Case.id))
    return [
        {
            "id": c.id,
            "title": c.title,
            "slug": c.slug,
            "industry": c.industry,
            "customer_alias": c.customer_alias,
            "challenge": c.challenge,
            "solution": c.solution,
            "result": c.result,
            "cover_image": c.cover_image,
            "is_published": c.is_published,
            "sort_order": c.sort_order,
        }
        for c in r.scalars().all()
    ]


@app.post("/api/admin/cases")
async def admin_create_case(data: CaseIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    c = Case(**data.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"ok": True, "id": c.id}


@app.put("/api/admin/cases/{item_id}")
async def admin_update_case(item_id: int, data: CaseIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Case).where(Case.id == item_id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(404)
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    await db.commit()
    return {"ok": True}


@app.delete("/api/admin/cases/{item_id}")
async def admin_delete_case(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Case).where(Case.id == item_id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(404)
    await db.delete(c)
    await db.commit()
    return {"ok": True}


@app.get("/api/admin/knowledge")
async def admin_list_knowledge(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Knowledge).order_by(Knowledge.sort_order, Knowledge.id))
    return [
        {
            "id": k.id,
            "title": k.title,
            "slug": k.slug,
            "category": k.category,
            "summary": k.summary,
            "content": k.content,
            "cover_image": k.cover_image,
            "is_published": k.is_published,
            "sort_order": k.sort_order,
        }
        for k in r.scalars().all()
    ]


@app.post("/api/admin/knowledge")
async def admin_create_knowledge(data: KnowledgeIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    k = Knowledge(**data.model_dump(), published_at=datetime.now(timezone.utc) if data.is_published else None)
    db.add(k)
    await db.commit()
    await db.refresh(k)
    return {"ok": True, "id": k.id}


@app.put("/api/admin/knowledge/{item_id}")
async def admin_update_knowledge(item_id: int, data: KnowledgeIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Knowledge).where(Knowledge.id == item_id))
    k = r.scalar_one_or_none()
    if not k:
        raise HTTPException(404)
    for key, val in data.model_dump().items():
        setattr(k, key, val)
    await db.commit()
    return {"ok": True}


@app.delete("/api/admin/knowledge/{item_id}")
async def admin_delete_knowledge(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Knowledge).where(Knowledge.id == item_id))
    k = r.scalar_one_or_none()
    if not k:
        raise HTTPException(404)
    await db.delete(k)
    await db.commit()
    return {"ok": True}


@app.get("/api/admin/products")
async def admin_list_products(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Product).order_by(Product.sort_order))
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "tagline": p.tagline,
            "summary": p.summary,
            "content": p.content,
            "image_url": p.image_url,
            "is_featured": p.is_featured,
            "is_published": p.is_published,
            "sort_order": p.sort_order,
        }
        for p in r.scalars().all()
    ]


@app.put("/api/admin/products/{item_id}")
async def admin_update_product(item_id: int, data: ProductIn, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    r = await db.execute(select(Product).where(Product.id == item_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404)
    for key, val in data.model_dump().items():
        setattr(p, key, val)
    await db.commit()
    return {"ok": True}


@app.post("/api/ai/chat")
async def ai_chat(data: AIChatIn):
    faq = {
        "探头": "KD0100-02S-T1 为线束探头型，氧分压 0.5–101 kPa，配套控制器 KD0100-03，探头重量≦35g（不含线束）。",
        "插针": "KD0100-02S-TO 为插针型，氧分压 0.5–101 kPa，探头重量≦5g，适合紧凑设备集成。",
        "面罩": "面罩用低温型变频氧传感器已试制成功，面向航空生命保障供氧监测，氧分压方向 0.5~101 kPa。",
        "加热": "KD0100 系列加热电压可选约 4.5V / 9V，须按 KD0100-03 说明书操作，错误加热可能导致永久损坏。",
        "量程": "公开量程为氧分压 0.5–101 kPa，可覆盖空气、纯氧及氮氧混合气等评估场景。",
        "样品": "请通过官网「联系我们」提交咨询表单，技术团队将尽快回复。",
        "质保": "公司秉承诚信为本，产品承诺质保 5 年（以合同与说明书约定为准）。",
    }
    answer = (
        "我是中科国瓷材料助手。可咨询探头/插针/面罩氧传感器选型、量程、加热电压与接线注意事项。"
        "复杂工况请提交联系表单，由工程师跟进。"
    )
    q = data.question.lower()
    for k, v in faq.items():
        if k.lower() in data.question or k in data.question:
            answer = v
            break
        if k.lower() in q:
            answer = v
            break
    return {"answer": answer, "source": "faq"}


@app.get("/health")
async def health_legacy():
    return {"status": "ok"}


@app.post("/crm/lead")
async def crm_lead_legacy(data: LeadIn, request: Request, db: AsyncSession = Depends(get_db)):
    return await create_lead(data, request, db)
