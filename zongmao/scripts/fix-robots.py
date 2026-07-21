#!/usr/bin/env python3
from pathlib import Path
import re
p = Path("/opt/zongmao/app.py")
text = p.read_text(encoding="utf-8")
fixed = '''    return Response(content="User-agent: *\\nAllow: /\\nDisallow: /admin/\\nDisallow: /api/\\nDisallow: /cards/\\nSitemap: https://zongmao.cn/sitemap.xml\\nSitemap: https://zongmao.cn/feed.xml\\nSitemap: https://zongmao.cn/rss.xml", media_type="text/plain")'''
text = re.sub(
    r"async def robots\(\):\n    return Response\(content=.*?\), media_type=\"text/plain\"\)",
    "async def robots():\n" + fixed,
    text,
    count=1,
    flags=re.S,
)
p.write_text(text, encoding="utf-8")
import py_compile
py_compile.compile(str(p), doraise=True)
print("robots fixed OK")
