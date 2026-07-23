#!/usr/bin/env python3
"""Seed KDGC database with products, news, knowledge, and industry cases."""
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from content_site import CASES as INDUSTRY_CASES  # noqa: E402
from content_site import KNOWLEDGE  # noqa: E402
from database import SessionLocal, engine  # noqa: E402
from models import Base, Case, Knowledge, News, Product  # noqa: E402

PRODUCTS = [
    {
        "name": "KD0100-02S-T1 氧气传感器-探头",
        "slug": "kd0100-02s-t1",
        "category": "oxygen-sensor",
        "tagline": "氧压范围 0.5–101 kPa · 线束探头型",
        "summary": "氧压范围 0.5kPa–101kPa，与外部接口板配合工作，可测试空气、纯氧及氮氧混合气等气体的氧分压。",
        "content": "规格：传感器型号 KD0100-02S，配套控制器 KD0100-03，加热电压 ~4.5V/9V（可选），允许气体温度（-50~200）℃，气流速率（0~10）m/s，探头重量≦35g。",
        "specs": {
            "传感器型号": "KD0100-02S",
            "配套控制器": "KD0100-03",
            "加热电压": "~4.5V/9V",
            "允许气体温度": "(-50~200)℃",
            "气流速率": "(0~10)m/s",
            "探头重量": "≦35g",
        },
        "applications": ["工业气体检测", "氮氧混合气", "燃烧气氛控制"],
        "image_url": "/assets/images/products/kd0100-02s-t1.webp",
        "sort_order": 1,
        "is_featured": True,
        "seo_title": "KD0100-02S-T1 氧气传感器-探头 | 中科国瓷",
        "seo_description": "KD0100-02S-T1 氧气传感器探头，氧压范围0.5-101kPa，配套KD0100-03控制器。",
    },
    {
        "name": "KD0100-02S-TO 氧气传感器-插针",
        "slug": "kd0100-02s-to",
        "category": "oxygen-sensor",
        "tagline": "氧压范围 0.5–101 kPa · 插针型 · ≦5g",
        "summary": "插针电气连接，探头重量≦5g，配套控制器 KD0100-03。",
        "content": "规格：传感器型号 KD0100-02S，配套控制器 KD0100-03，加热电压 ~4.5V/9V，探头重量≦5g，尺寸公差≦0.5mm。",
        "specs": {
            "传感器型号": "KD0100-02S",
            "配套控制器": "KD0100-03",
            "加热电压": "~4.5V/9V",
            "探头重量": "≦5g",
        },
        "applications": ["紧凑型设备集成", "工业气体检测"],
        "image_url": "/assets/images/products/kd0100-02s-to.webp",
        "sort_order": 2,
        "is_featured": True,
        "seo_title": "KD0100-02S-TO 氧气传感器-插针 | 中科国瓷",
        "seo_description": "KD0100-02S-TO 插针型氧气传感器，轻量化≦5g。",
    },
    {
        "name": "面罩用氧传感器",
        "slug": "mask-o2-sensor",
        "category": "oxygen-sensor",
        "tagline": "战机飞行员面罩用低温型变频式氧传感器",
        "summary": "公司开发的战机飞行员面罩用低温型变频式氧传感器已试制成功，产品各项性能指标优异。",
        "content": "面向航空面罩应用的低温型变频式氧传感器，氧分压测量范围 0.5 ~ 101 kPa。",
        "specs": {"氧分压测量范围": "0.5~101kPa"},
        "applications": ["航空面罩", "供氧监测"],
        "image_url": "/assets/images/products/mask-o2-sensor.webp",
        "sort_order": 3,
        "is_featured": True,
        "seo_title": "面罩用氧传感器 | 中科国瓷",
        "seo_description": "战机飞行员面罩用低温型变频式氧传感器。",
    },
]

NEWS = [
    {
        "title": "2022年1月国瓷团建户外活动！新年新气象！虎年虎虎生威！",
        "slug": "team-building-2022",
        "summary": "新年伊始，国瓷公司进行周末全员户外团建。",
        "cover_image": "/assets/images/news/team-building-2022.webp",
        "published_at": datetime(2022, 1, 16, tzinfo=timezone.utc),
    },
    {
        "title": "国内车用氮氧传感器市场超百亿元",
        "slug": "nox-sensor-market",
        "summary": "国Ⅵ排放标准下国内氮氧传感器市场空间超百亿元。",
        "cover_image": "/assets/images/news/nox-sensor-market.webp",
        "published_at": datetime(2021, 6, 1, tzinfo=timezone.utc),
    },
    {
        "title": "一文读懂氧传感器",
        "slug": "understand-o2-sensor",
        "summary": "氧传感器原理、结构、分类与未来发展方向科普。",
        "cover_image": "/assets/images/news/understand-o2-sensor.webp",
        "published_at": datetime(2021, 5, 1, tzinfo=timezone.utc),
    },
]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        for table in ("products_v2", "news", "cases", "knowledge"):
            try:
                await session.execute(text(f"DELETE FROM {table}"))
            except Exception as e:
                print(f"skip delete {table}: {e}")
                await session.rollback()

        for p in PRODUCTS:
            session.add(Product(**p))
        for n in NEWS:
            session.add(News(**n, content=n["summary"], is_published=True))

        for i, k in enumerate(KNOWLEDGE):
            session.add(
                Knowledge(
                    title=k["title"],
                    slug=k["slug"],
                    category=k["category"],
                    summary=k["summary"],
                    content=k["body"],
                    cover_image=f"/assets/images/{k['cover']}".replace(".jpg", ".webp").replace(".png", ".webp"),
                    is_published=True,
                    sort_order=i + 1,
                    published_at=datetime.now(timezone.utc),
                )
            )

        for i, c in enumerate(INDUSTRY_CASES):
            session.add(
                Case(
                    title=c["title"],
                    slug=c["slug"],
                    industry=c["industry"],
                    customer_alias=c["customer"],
                    challenge=c["challenge"],
                    solution=c["solution"],
                    result="；".join(c["results"]),
                    cover_image=f"/assets/images/{c['cover']}".replace(".jpg", ".webp").replace(".png", ".webp"),
                    is_published=True,
                    sort_order=i + 1,
                )
            )

        await session.commit()
        print(
            f"Seeded {len(PRODUCTS)} products, {len(NEWS)} news, "
            f"{len(KNOWLEDGE)} knowledge, {len(INDUSTRY_CASES)} cases"
        )


if __name__ == "__main__":
    asyncio.run(main())
