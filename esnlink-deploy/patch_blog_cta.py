#!/usr/bin/env python3
"""Add CTA snippet to blog posts on the server (run via deploy or standalone)."""
import glob
import os

CTA = """
<!-- esnlink-cta -->
<div style="margin:2rem 0;padding:1.5rem 2rem;background:linear-gradient(135deg,#eff6ff,#e0f2fe);border-radius:16px;border:1px solid #bfdbfe;text-align:center">
  <h3 style="color:#1e3a5f;margin-bottom:0.5rem;font-size:1.2rem">需要企业通信解决方案？</h3>
  <p style="color:#64748b;margin-bottom:1rem;font-size:0.95rem">翼星科技提供 AI 外呼、短信平台、物联网一站式服务，免费试用 14 天</p>
  <a href="/booking.html" style="display:inline-block;background:linear-gradient(135deg,#f59e0b,#ea580c);color:#fff;padding:0.6rem 1.5rem;border-radius:40px;text-decoration:none;font-weight:600;margin-right:0.5rem">免费试用</a>
  <a href="/pricing.html" style="display:inline-block;border:1.5px solid #2563eb;color:#2563eb;padding:0.6rem 1.5rem;border-radius:40px;text-decoration:none;font-weight:600">查看定价</a>
</div>
"""

blog_dir = os.environ.get("BLOG_DIR", "/var/www/yixing/blog")
for path in glob.glob(f"{blog_dir}/*.html"):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "esnlink-cta" in content:
        continue
    if "</body>" not in content:
        continue
    content = content.replace("</body>", CTA + "\n</body>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Added CTA to {os.path.basename(path)}")
