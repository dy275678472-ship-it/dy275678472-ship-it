"""JSON-LD 结构化数据构建（SEO + GEO）。"""

import json

SITE_BASE = "https://lyread.cn"


def _org() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{SITE_BASE}/#organization",
        "name": "LyRead AI",
        "alternateName": "LyRead 智能小说创作",
        "url": SITE_BASE,
        "logo": {
            "@type": "ImageObject",
            "url": f"{SITE_BASE}/images/logo-icon-v2.svg",
        },
        "description": "LyRead AI 是面向中文作者与工作室的智能小说创作 SaaS 平台，支持长篇连载、短故事、人物伏笔记忆与按量点数计费。",
    }


def website_graph() -> str:
    data = {
        "@context": "https://schema.org",
        "@graph": [
            _org(),
            {
                "@type": "WebSite",
                "@id": f"{SITE_BASE}/#website",
                "url": SITE_BASE,
                "name": "LyRead AI",
                "description": "让 AI 陪你写完一部长篇小说。支持大纲、章纲、正文续写与小说大脑记忆。",
                "publisher": {"@id": f"{SITE_BASE}/#organization"},
                "inLanguage": "zh-CN",
            },
            {
                "@type": "SoftwareApplication",
                "@id": f"{SITE_BASE}/#app",
                "name": "LyRead AI",
                "applicationCategory": "WritingApplication",
                "operatingSystem": "Web",
                "url": SITE_BASE,
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "CNY",
                    "description": "注册送 30 点，每日免费 5 点；充值 10 元 = 100 点",
                },
                "featureList": [
                    "AI 生成书名与大纲",
                    "长篇章节续写",
                    "人物与伏笔记忆（小说大脑）",
                    "短故事一键生成",
                    "按章点数计费，失败返还",
                ],
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def faq_graph(faqs: list[tuple[str, str]]) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def breadcrumb(items: list[tuple[str, str]]) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": url,
            }
            for i, (name, url) in enumerate(items)
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def combine_json_ld(*parts: str) -> str:
    """合并多个 JSON-LD 对象为 @graph。"""
    graphs = []
    for part in parts:
        if not part:
            continue
        obj = json.loads(part)
        if "@graph" in obj:
            graphs.extend(obj["@graph"])
        else:
            graphs.append(obj)
    return json.dumps({"@context": "https://schema.org", "@graph": graphs}, ensure_ascii=False)
