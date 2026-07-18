#!/usr/bin/env python3
"""Seed KDGC database with products, news, and cases."""
import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy import text
from database import SessionLocal, engine
from models import Base, Case, News, Product

PRODUCTS = [
    {
        "name": "氮化铝陶瓷基板",
        "slug": "aln-substrate",
        "category": "aln",
        "tagline": "导热 200W/m·K，IGBT 封装首选",
        "summary": "高导热氮化铝陶瓷基板，适用于功率半导体模块、新能源汽车电控系统。",
        "content": "氮化铝（AlN）陶瓷具有优异的热导率和电绝缘性能，是 IGBT、MOSFET 等功率器件封装的核心材料。",
        "specs": {"导热率": "150–200 W/m·K", "热膨胀系数": "4.5×10⁻⁶/°C", "介电强度": "≥14 kV/mm", "抗弯强度": "≥300 MPa"},
        "applications": ["IGBT功率模块", "新能源汽车电控", "激光器散热"],
        "image_url": "/assets/images/aln-substrate.webp",
        "sort_order": 1,
        "is_featured": True,
        "seo_title": "氮化铝陶瓷基板 — 高导热IGBT封装材料 | 中科国瓷",
        "seo_description": "中科国瓷氮化铝陶瓷基板，导热率200W/m·K，适用于IGBT功率模块与新能源汽车电控系统。",
    },
    {
        "name": "DBC/AMB 陶瓷基板",
        "slug": "dbc-amb",
        "category": "dbc-amb",
        "tagline": "直接覆铜 + 活性钎焊双工艺",
        "summary": "DBC 直接覆铜与 AMB 活性钎焊陶瓷基板，电力电子封装核心材料。",
        "content": "DBC（Direct Bonded Copper）和 AMB（Active Metal Brazing）是两种主流的陶瓷金属化工艺。",
        "specs": {"DBC导热率": "24–28 W/m·K", "AMB导热率": "90–170 W/m·K", "工作温度": "≤350°C", "铜层厚度": "0.1–0.5mm"},
        "applications": ["电力电子模块", "逆变器", "轨道交通"],
        "image_url": "/assets/images/dbc-amb.webp",
        "sort_order": 2,
        "is_featured": True,
        "seo_title": "DBC/AMB陶瓷基板 — 电力电子封装 | 中科国瓷",
        "seo_description": "DBC直接覆铜与AMB活性钎焊陶瓷基板，适用于电力电子、逆变器、轨道交通。",
    },
    {
        "name": "氧化铝陶瓷",
        "slug": "alumina",
        "category": "alumina",
        "tagline": "纯度 92%–99.7%，耐温 1600°C",
        "summary": "高纯度氧化铝陶瓷，优异绝缘性与耐腐蚀性，适用于高温电子封装。",
        "content": "氧化铝（Al₂O₃）是最常用的工程陶瓷材料，具有高绝缘性、耐腐蚀性和良好的机械强度。",
        "specs": {"纯度": "92%–99.7%", "导热率": "20–30 W/m·K", "最高温度": "1600°C", "介电强度": "≥15 kV/mm"},
        "applications": ["电子封装", "高温绝缘", "耐磨部件"],
        "image_url": "/assets/images/alumina.webp",
        "sort_order": 3,
        "is_featured": False,
        "seo_title": "氧化铝陶瓷 — 高纯度电子陶瓷材料 | 中科国瓷",
        "seo_description": "中科国瓷氧化铝陶瓷，纯度92%-99.7%，耐温1600°C，适用于电子封装与高温绝缘。",
    },
]

NEWS = [
    {"title": "参加2025中国先进陶瓷材料产业峰会", "slug": "ceramic-summit-2025", "summary": "展示最新高导热氮化铝基板产品。", "published_at": datetime(2025, 6, 15, tzinfo=timezone.utc)},
    {"title": "通过 ISO 9001 质量管理体系认证", "slug": "iso9001-certification", "summary": "质量管理体系覆盖陶瓷材料全生产流程。", "published_at": datetime(2025, 3, 20, tzinfo=timezone.utc)},
    {"title": "新一代氧化铝陶瓷基板量产", "slug": "alumina-mass-production", "summary": "高纯度氧化铝基板通过多家客户验证，进入规模化量产。", "published_at": datetime(2025, 1, 8, tzinfo=timezone.utc)},
    {"title": "氮化铝基板通过第三方导热率检测", "slug": "aln-thermal-test", "summary": "导热率实测达 195 W/m·K，检测报告编号 [待公司提供]。", "published_at": datetime(2025, 8, 1, tzinfo=timezone.utc)},
    {"title": "与某头部新能源车企达成战略合作", "slug": "ev-partnership", "summary": "为电控系统提供高导热陶瓷基板解决方案（客户名称脱敏）。", "published_at": datetime(2025, 10, 12, tzinfo=timezone.utc)},
]

CASES = [
    {
        "title": "某半导体封装企业 IGBT 模块散热方案",
        "slug": "semiconductor-packaging",
        "industry": "semiconductor",
        "challenge": "IGBT 模块工作温度高，传统基板散热不足导致器件寿命缩短。",
        "solution": "采用氮化铝陶瓷基板（导热率 195 W/m·K），优化铜层厚度与键合工艺。",
        "result": "模块热阻降低 35%，通过 1000 小时高温老化测试。",
    },
    {
        "title": "某新能源汽车电控 Tier1 供应商",
        "slug": "ev-power-module",
        "industry": "ev",
        "challenge": "电控系统功率密度提升，需要更高导热率的基板材料。",
        "solution": "提供 DBC 陶瓷基板定制方案，匹配客户封装工艺。",
        "result": "通过车规级可靠性测试，进入小批量供货阶段。",
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        existing = await db.execute(text("SELECT count(*) FROM products_v2"))
        if existing.scalar() > 0:
            print("Already seeded, skipping.")
            return
        for p in PRODUCTS:
            db.add(Product(**p))
        for n in NEWS:
            db.add(News(**n, is_published=True, content=n["summary"]))
        for c in CASES:
            db.add(Case(**c, is_published=True))
        await db.commit()
        print("Seeded:", len(PRODUCTS), "products,", len(NEWS), "news,", len(CASES), "cases")


if __name__ == "__main__":
    asyncio.run(seed())
