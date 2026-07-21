import os
import re
import time
import uuid
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
from auth import require_perm, resolve_admin
from models import (
    AuditLog,
    Base,
    Case,
    ChatMessage,
    ChatSession,
    Knowledge,
    Lead,
    News,
    PageEvent,
    Product,
    Ticket,
)

app = FastAPI(title="KDGC API", version="2.2.0")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "https://kdgc.cc,http://kdgc.cc,http://150.158.42.39,http://127.0.0.1"
).split(",")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
# Tokens / roles: see auth.py (ADMIN_TOKEN, EDITOR_TOKEN, OPS_TOKEN, ADMIN_USERS)

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
    """Backward-compatible full-access check (maps to admin role via resolve)."""
    return resolve_admin(request)


class LeadIn(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    email: Optional[EmailStr] = None
    product_interest: Optional[str] = None
    requirement: Optional[str] = None
    website: Optional[str] = None


class LeadStatusIn(BaseModel):
    status: Optional[str] = Field(default=None, min_length=2, max_length=30)
    assignee: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=2000)


class TicketIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    category: str = Field(default="support", max_length=40)
    priority: str = Field(default="normal", max_length=20)
    requester_name: Optional[str] = None
    requester_contact: Optional[str] = None
    body: Optional[str] = None
    assignee: Optional[str] = None
    chat_session_id: Optional[int] = None
    lead_id: Optional[int] = None


class TicketStatusIn(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    body: Optional[str] = None


class PageEventIn(BaseModel):
    event_type: str = Field(default="pageview", max_length=40)
    path: str = Field(min_length=1, max_length=300)
    referrer: Optional[str] = Field(default=None, max_length=500)


class AIChatIn(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


class ChatSessionIn(BaseModel):
    visitor_name: Optional[str] = Field(default=None, max_length=100)
    visitor_contact: Optional[str] = Field(default=None, max_length=120)
    page_url: Optional[str] = Field(default=None, max_length=500)


class ChatMessageIn(BaseModel):
    token: str = Field(min_length=20, max_length=100)
    body: str = Field(min_length=1, max_length=1000)


class AdminChatMessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class ChatStatusIn(BaseModel):
    status: str = Field(pattern="^(open|closed)$")


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
            "ALTER TABLE leads_v2 ADD COLUMN IF NOT EXISTS assignee VARCHAR(80)",
            "ALTER TABLE leads_v2 ADD COLUMN IF NOT EXISTS notes TEXT",
            "ALTER TABLE leads_v2 ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ",
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
    return {"status": "ok", "db": db_status, "version": "2.2.0"}


@app.post("/api/leads")
async def create_lead(data: LeadIn, request: Request, db: AsyncSession = Depends(get_db)):
    if data.website:
        return {"success": True, "message": "我们将在24小时内联系您"}
    # spam heuristics
    blob = " ".join(
        [
            data.company or "",
            data.contact_name or "",
            data.requirement or "",
            data.product_interest or "",
        ]
    ).lower()
    spam_words = ("viagra", "casino", "crypto pump", "seo backlink", "http://", "https://")
    if any(w in blob for w in spam_words) or len(re.findall(r"https?://", blob)) >= 2:
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


def chat_message_dict(message: ChatMessage):
    return {
        "id": message.id,
        "sender": message.sender,
        "body": message.body,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


async def get_public_chat(public_id: str, token: str, db: AsyncSession):
    result = await db.execute(select(ChatSession).where(ChatSession.public_id == public_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "会话不存在")
    if session.visitor_token != token:
        raise HTTPException(403, "会话凭证无效")
    return session


@app.post("/api/chat/sessions")
async def create_chat_session(
    data: ChatSessionIn, request: Request, db: AsyncSession = Depends(get_db)
):
    check_rate(f"chat-session:{request.client.host if request.client else 'unknown'}", limit=10, window=3600)
    session = ChatSession(
        public_id=str(uuid.uuid4()),
        visitor_token=uuid.uuid4().hex,
        visitor_name=(data.visitor_name or "").strip() or None,
        visitor_contact=(data.visitor_contact or "").strip() or None,
        page_url=(data.page_url or "").strip() or None,
        status="open",
        last_message_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"public_id": session.public_id, "token": session.visitor_token, "status": session.status}


@app.get("/api/chat/sessions/{public_id}/messages")
async def public_chat_messages(
    public_id: str,
    token: str,
    after: int = 0,
    db: AsyncSession = Depends(get_db),
):
    session = await get_public_chat(public_id, token, db)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id, ChatMessage.id > max(after, 0))
        .order_by(ChatMessage.id)
        .limit(200)
    )
    return [chat_message_dict(message) for message in result.scalars().all()]


@app.post("/api/chat/sessions/{public_id}/messages")
async def public_send_chat_message(
    public_id: str,
    data: ChatMessageIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    check_rate(f"chat-message:{request.client.host if request.client else 'unknown'}", limit=30, window=60)
    session = await get_public_chat(public_id, data.token, db)
    if session.status != "open":
        raise HTTPException(409, "该会话已关闭，请刷新页面开始新会话")
    message = ChatMessage(session_id=session.id, sender="visitor", body=data.body.strip())
    session.last_message_at = datetime.now(timezone.utc)
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # AI / FAQ bot first-response for high-frequency questions
    bot_reply = None
    q = message.body
    for k, v in {
        "探头": "KD0100-02S-T1 探头型，氧分压 0.5–101 kPa，配套 KD0100-03。需要规格书可在产品页下载。",
        "插针": "KD0100-02S-TO 插针型，探头重量≦5g，适合紧凑 OEM。",
        "面罩": "面罩用低温型已试制成功，面向航空生命保障供氧监测。",
        "样品": "请留下公司与工况，或前往 /contact/ 提交表单，工程师将跟进样品。",
        "质保": "产品承诺质保 5 年（以合同与说明书为准）。",
        "价格": "价格与交期视批量与定制接口而定，请留下联系方式由销售回复。",
    }.items():
        if k in q:
            bot_reply = v + " 如需人工，请稍候，客服会接入。"
            break
    bot_msg = None
    if bot_reply:
        bot_msg = ChatMessage(session_id=session.id, sender="agent", body=bot_reply)
        session.last_message_at = datetime.now(timezone.utc)
        db.add(bot_msg)
        await db.commit()
        await db.refresh(bot_msg)

    if FEISHU_WEBHOOK:
        text = (
            f"💬 官网在线客服新消息\n"
            f"访客：{session.visitor_name or '匿名'}\n"
            f"联系方式：{session.visitor_contact or '-'}\n"
            f"页面：{session.page_url or '-'}\n"
            f"消息：{message.body}"
        )
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": text}})
        except Exception:
            pass
    out = chat_message_dict(message)
    if bot_msg:
        out["bot_reply"] = chat_message_dict(bot_msg)
    return out


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
async def write_audit(
    db: AsyncSession,
    request: Request,
    action: str,
    target: str | None = None,
    detail: str | None = None,
):
    try:
        user = resolve_admin(request)
    except HTTPException:
        return
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action=action,
            target=target,
            detail=(detail or "")[:2000] or None,
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()


@app.post("/api/admin/login")
async def admin_login(request: Request, db: AsyncSession = Depends(get_db)):
    user = resolve_admin(request)
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="login",
            target="admin",
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    from auth import ROLE_PERMS

    return {
        "ok": True,
        "role": user.role,
        "name": user.name,
        "perms": sorted(ROLE_PERMS[user.role]),
    }


@app.get("/api/admin/stats")
async def admin_stats(request: Request, db: AsyncSession = Depends(get_db)):
    require_perm(request, "stats")

    async def count(model):
        r = await db.execute(select(func.count()).select_from(model))
        return int(r.scalar() or 0)

    new_leads = await db.execute(select(func.count()).select_from(Lead).where(Lead.status == "new"))
    open_chats = await db.execute(
        select(func.count()).select_from(ChatSession).where(ChatSession.status == "open")
    )
    open_tickets = await db.execute(
        select(func.count()).select_from(Ticket).where(Ticket.status.in_(["open", "progress"]))
    )

    # last 7 days lead counts
    from datetime import timedelta

    day_rows = []
    now = datetime.now(timezone.utc)
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        r = await db.execute(
            select(func.count()).select_from(Lead).where(Lead.created_at >= start, Lead.created_at < end)
        )
        pv = await db.execute(
            select(func.count())
            .select_from(PageEvent)
            .where(
                PageEvent.event_type == "pageview",
                PageEvent.created_at >= start,
                PageEvent.created_at < end,
            )
        )
        day_rows.append(
            {
                "date": day.isoformat(),
                "leads": int(r.scalar() or 0),
                "pageviews": int(pv.scalar() or 0),
            }
        )

    top_pages = await db.execute(
        select(PageEvent.path, func.count().label("c"))
        .where(PageEvent.event_type == "pageview")
        .group_by(PageEvent.path)
        .order_by(func.count().desc())
        .limit(8)
    )

    return {
        "products": await count(Product),
        "news": await count(News),
        "cases": await count(Case),
        "knowledge": await count(Knowledge),
        "leads": await count(Lead),
        "leads_new": int(new_leads.scalar() or 0),
        "chats_open": int(open_chats.scalar() or 0),
        "tickets_open": int(open_tickets.scalar() or 0),
        "pageviews": await count(PageEvent),
        "series_7d": day_rows,
        "top_pages": [{"path": p, "views": int(c)} for p, c in top_pages.all()],
    }


@app.get("/api/admin/leads")
@app.get("/api/leads")
async def list_leads(request: Request, db: AsyncSession = Depends(get_db)):
    require_perm(request, "leads_read")
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
            "assignee": getattr(l, "assignee", None),
            "notes": getattr(l, "notes", None),
            "source": l.source,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in r.scalars().all()
    ]


@app.patch("/api/admin/leads/{lead_id}")
async def update_lead(lead_id: int, data: LeadStatusIn, request: Request, db: AsyncSession = Depends(get_db)):
    user = require_perm(request, "leads_write")
    r = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = r.scalar_one_or_none()
    if not lead:
        raise HTTPException(404)
    if data.status is not None:
        lead.status = data.status.strip()
    if data.assignee is not None:
        lead.assignee = data.assignee.strip() or None
    if data.notes is not None:
        lead.notes = data.notes.strip() or None
    await db.commit()
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="lead_update",
            target=f"lead:{lead.id}",
            detail=f"status={lead.status}; assignee={lead.assignee}",
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    return {
        "ok": True,
        "id": lead.id,
        "status": lead.status,
        "assignee": lead.assignee,
        "notes": lead.notes,
    }


@app.get("/api/admin/chat/sessions")
async def admin_chat_sessions(request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    last_message = (
        select(ChatMessage.body)
        .where(ChatMessage.session_id == ChatSession.id)
        .order_by(ChatMessage.id.desc())
        .limit(1)
        .scalar_subquery()
    )
    result = await db.execute(
        select(ChatSession, last_message.label("last_message"))
        .order_by(ChatSession.last_message_at.desc(), ChatSession.id.desc())
        .limit(200)
    )
    return [
        {
            "id": session.id,
            "public_id": session.public_id,
            "visitor_name": session.visitor_name,
            "visitor_contact": session.visitor_contact,
            "page_url": session.page_url,
            "status": session.status,
            "last_message": latest,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
        }
        for session, latest in result.all()
    ]


@app.get("/api/admin/chat/sessions/{session_id}/messages")
async def admin_chat_messages(
    session_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    require_admin(request)
    session_result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    if not session_result.scalar_one_or_none():
        raise HTTPException(404)
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id)
    )
    return [chat_message_dict(message) for message in result.scalars().all()]


@app.post("/api/admin/chat/sessions/{session_id}/messages")
async def admin_send_chat_message(
    session_id: int,
    data: AdminChatMessageIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    require_admin(request)
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404)
    if session.status != "open":
        raise HTTPException(409, "会话已关闭")
    message = ChatMessage(session_id=session.id, sender="admin", body=data.body.strip())
    session.last_message_at = datetime.now(timezone.utc)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return chat_message_dict(message)


@app.patch("/api/admin/chat/sessions/{session_id}")
async def admin_update_chat_session(
    session_id: int,
    data: ChatStatusIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    require_admin(request)
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404)
    session.status = data.status
    session.last_message_at = datetime.now(timezone.utc)
    await db.commit()
    return {"ok": True, "id": session.id, "status": session.status}


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
async def ai_chat(data: AIChatIn, db: AsyncSession = Depends(get_db)):
    faq = {
        "探头": "KD0100-02S-T1 为线束探头型，氧分压 0.5–101 kPa，配套控制器 KD0100-03，探头重量≦35g（不含线束）。",
        "插针": "KD0100-02S-TO 为插针型，氧分压 0.5–101 kPa，探头重量≦5g，适合紧凑设备集成。",
        "面罩": "面罩用低温型变频氧传感器已试制成功，面向航空生命保障供氧监测，氧分压方向 0.5~101 kPa。",
        "加热": "KD0100 系列加热电压可选约 4.5V / 9V，须按 KD0100-03 说明书操作，错误加热可能导致永久损坏。",
        "量程": "公开量程为氧分压 0.5–101 kPa，可覆盖空气、纯氧及氮氧混合气等评估场景。",
        "样品": "请通过官网「联系我们」提交咨询表单，技术团队将尽快回复。",
        "质保": "公司秉承诚信为本，产品承诺质保 5 年（以合同与说明书约定为准）。",
        "工单": "复杂问题可由客服转为工单，进入技术支持/售后流程跟进。",
        "规格书": "产品详情页可下载公开规格书 PDF；也可通过联系表单索取。",
    }
    answer = (
        "我是中科国瓷材料助手。可咨询探头/插针/面罩氧传感器选型、量程、加热电压与接线注意事项。"
        "复杂工况请提交联系表单或转人工客服；需要时可生成工单交给销售/技术跟进。"
    )
    source = "faq"
    q = data.question.lower()
    for k, v in faq.items():
        if k.lower() in data.question or k in data.question or k.lower() in q:
            answer = v
            break
    else:
        # knowledge base keyword match
        r = await db.execute(
            select(Knowledge).where(Knowledge.is_published.is_(True)).order_by(Knowledge.sort_order).limit(40)
        )
        best = None
        for krow in r.scalars().all():
            title = (krow.title or "").lower()
            summary = (krow.summary or "").lower()
            if any(tok in title or tok in summary for tok in re.findall(r"[\u4e00-\u9fff]{2,}|[a-z0-9-]{3,}", q)[:8]):
                best = krow
                break
        if best:
            answer = (
                f"【知识库参考】{best.title}：{(best.summary or '')[:180]} "
                f"详情：/knowledge/{best.slug}.html"
            )
            source = "knowledge"
    return {"answer": answer, "source": source}


@app.post("/api/admin/publish")
async def admin_publish(request: Request, db: AsyncSession = Depends(get_db)):
    """Regenerate static HTML from generate_pages.py into the live dist tree."""
    user = require_perm(request, "publish")
    import subprocess
    from pathlib import Path

    candidates = [
        Path("/opt/kdgc-growth/generate_pages.py"),
        Path(__file__).resolve().parents[1] / "generate_pages.py",
    ]
    script = next((p for p in candidates if p.exists()), None)
    if not script:
        raise HTTPException(500, "generate_pages.py not found")
    r = subprocess.run(
        ["python3", str(script)],
        cwd=str(script.parent),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode != 0:
        raise HTTPException(500, detail=(r.stderr or r.stdout or "publish failed")[-2000:])
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="publish",
            target="frontend",
            detail="generate_pages.py ok",
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    return {"ok": True, "message": "前台静态页已重新生成", "log": (r.stdout or "")[-1500:]}


@app.get("/api/admin/leads/export")
async def export_leads(request: Request, db: AsyncSession = Depends(get_db)):
    require_perm(request, "leads_export")
    from fastapi.responses import PlainTextResponse
    import csv
    import io

    r = await db.execute(select(Lead).order_by(Lead.created_at.desc()).limit(2000))
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "id",
            "created_at",
            "company",
            "contact_name",
            "phone",
            "email",
            "product_interest",
            "requirement",
            "status",
            "assignee",
            "notes",
            "source",
        ]
    )
    for l in r.scalars().all():
        w.writerow(
            [
                l.id,
                l.created_at.isoformat() if l.created_at else "",
                l.company,
                l.contact_name,
                l.phone,
                l.email or "",
                l.product_interest or "",
                (l.requirement or "").replace("\n", " "),
                l.status,
                getattr(l, "assignee", None) or "",
                (getattr(l, "notes", None) or "").replace("\n", " "),
                l.source,
            ]
        )
    return PlainTextResponse(
        buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=kdgc-leads.csv"},
    )


@app.get("/api/admin/logs")
async def list_audit_logs(request: Request, db: AsyncSession = Depends(get_db)):
    require_perm(request, "logs")
    r = await db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(200))
    return [
        {
            "id": x.id,
            "actor": x.actor,
            "role": x.role,
            "action": x.action,
            "target": x.target,
            "detail": x.detail,
            "ip": x.ip,
            "created_at": x.created_at.isoformat() if x.created_at else None,
        }
        for x in r.scalars().all()
    ]


@app.post("/api/admin/backup")
async def admin_backup(request: Request, db: AsyncSession = Depends(get_db)):
    user = require_perm(request, "backup")
    import json
    from pathlib import Path

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = Path("/opt/kdgc-growth/backups")
    if not out_dir.exists():
        out_dir = Path(__file__).resolve().parents[1] / "backups"
    out_dir.mkdir(parents=True, exist_ok=True)

    async def dump(model, mapper):
        r = await db.execute(select(model).limit(5000))
        return [mapper(x) for x in r.scalars().all()]

    payload = {
        "created_at": stamp,
        "leads": await dump(
            Lead,
            lambda l: {
                "id": l.id,
                "company": l.company,
                "contact_name": l.contact_name,
                "phone": l.phone,
                "email": l.email,
                "product_interest": l.product_interest,
                "requirement": l.requirement,
                "status": l.status,
                "assignee": getattr(l, "assignee", None),
                "notes": getattr(l, "notes", None),
                "source": l.source,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            },
        ),
        "tickets": await dump(
            Ticket,
            lambda t: {
                "id": t.id,
                "public_id": t.public_id,
                "title": t.title,
                "category": t.category,
                "status": t.status,
                "priority": t.priority,
                "assignee": t.assignee,
                "body": t.body,
                "chat_session_id": t.chat_session_id,
                "lead_id": t.lead_id,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            },
        ),
        "chat_sessions": await dump(
            ChatSession,
            lambda s: {
                "id": s.id,
                "public_id": s.public_id,
                "visitor_name": s.visitor_name,
                "visitor_contact": s.visitor_contact,
                "status": s.status,
                "page_url": s.page_url,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            },
        ),
    }
    path = out_dir / f"kdgc-backup-{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="backup",
            target=str(path.name),
            detail=f"leads={len(payload['leads'])} tickets={len(payload['tickets'])}",
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    return {"ok": True, "file": str(path), "counts": {k: len(v) for k, v in payload.items() if isinstance(v, list)}}


@app.get("/api/admin/tickets")
async def list_tickets(request: Request, db: AsyncSession = Depends(get_db)):
    require_perm(request, "tickets")
    r = await db.execute(select(Ticket).order_by(Ticket.id.desc()).limit(200))
    return [
        {
            "id": t.id,
            "public_id": t.public_id,
            "title": t.title,
            "category": t.category,
            "status": t.status,
            "priority": t.priority,
            "requester_name": t.requester_name,
            "requester_contact": t.requester_contact,
            "body": t.body,
            "assignee": t.assignee,
            "chat_session_id": t.chat_session_id,
            "lead_id": t.lead_id,
            "created_by": t.created_by,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in r.scalars().all()
    ]


@app.post("/api/admin/tickets")
async def create_ticket(data: TicketIn, request: Request, db: AsyncSession = Depends(get_db)):
    user = require_perm(request, "tickets")
    ticket = Ticket(
        public_id=str(uuid.uuid4()),
        title=data.title.strip(),
        category=(data.category or "support").strip(),
        priority=(data.priority or "normal").strip(),
        requester_name=data.requester_name,
        requester_contact=data.requester_contact,
        body=data.body,
        assignee=data.assignee,
        chat_session_id=data.chat_session_id,
        lead_id=data.lead_id,
        created_by=user.name,
        status="open",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="ticket_create",
            target=f"ticket:{ticket.id}",
            detail=ticket.title,
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    return {"ok": True, "id": ticket.id, "public_id": ticket.public_id}


@app.post("/api/admin/chat/sessions/{session_id}/ticket")
async def ticket_from_chat(session_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = require_perm(request, "tickets")
    r = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = r.scalar_one_or_none()
    if not session:
        raise HTTPException(404)
    msgs = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id.desc()).limit(12)
    )
    transcript = "\n".join(f"[{m.sender}] {m.body}" for m in reversed(list(msgs.scalars().all())))
    ticket = Ticket(
        public_id=str(uuid.uuid4()),
        title=f"客服会话转工单 #{session.id}",
        category="support",
        priority="normal",
        requester_name=session.visitor_name,
        requester_contact=session.visitor_contact,
        body=transcript or "（无消息）",
        chat_session_id=session.id,
        created_by=user.name,
        status="open",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return {"ok": True, "id": ticket.id, "public_id": ticket.public_id}


@app.patch("/api/admin/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: int, data: TicketStatusIn, request: Request, db: AsyncSession = Depends(get_db)
):
    user = require_perm(request, "tickets")
    r = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = r.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404)
    if data.status is not None:
        ticket.status = data.status.strip()
    if data.assignee is not None:
        ticket.assignee = data.assignee.strip() or None
    if data.priority is not None:
        ticket.priority = data.priority.strip()
    if data.body is not None:
        ticket.body = data.body
    await db.commit()
    db.add(
        AuditLog(
            actor=user.name,
            role=user.role,
            action="ticket_update",
            target=f"ticket:{ticket.id}",
            detail=f"status={ticket.status}",
            ip=request.client.host if request.client else None,
        )
    )
    await db.commit()
    return {"ok": True, "id": ticket.id, "status": ticket.status}


@app.post("/api/events")
async def track_event(data: PageEventIn, request: Request, db: AsyncSession = Depends(get_db)):
    check_rate(f"evt:{request.client.host if request.client else 'unknown'}", limit=120, window=3600)
    evt = PageEvent(
        event_type=(data.event_type or "pageview")[:40],
        path=data.path[:300],
        referrer=(data.referrer or "")[:500] or None,
        ua=(request.headers.get("user-agent") or "")[:300] or None,
    )
    db.add(evt)
    await db.commit()
    return {"ok": True}


@app.get("/health")
async def health_legacy():
    return {"status": "ok"}


@app.post("/crm/lead")
async def crm_lead_legacy(data: LeadIn, request: Request, db: AsyncSession = Depends(get_db)):
    return await create_lead(data, request, db)
