#!/usr/bin/env python3
"""Pivot TianShu MythOS to English-only, conversion-first. Run on server."""
from pathlib import Path

ROOT = Path("/data/www/mythos")


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


# 1. metadata.ts — English only, no hreflang
write(
    "src/lib/metadata.ts",
    """import type { Metadata } from "next";
import { SITE_NAME, SITE_URL } from "./site";

export function buildPageMetadata({
  title,
  description,
  path,
}: {
  title: string;
  description: string;
  path: string;
}): Metadata {
  const url = path === "/" ? SITE_URL : `${SITE_URL}${path}`;
  const ogTitle =
    title.includes("TianShu") || title.includes("MythOS") ? title : `${title} | ${SITE_NAME}`;
  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: {
      title: ogTitle,
      description,
      url,
      siteName: SITE_NAME,
      type: "website",
      locale: "en_US",
      images: [{ url: "/og-image.png", width: 1200, height: 630, alt: SITE_NAME }],
    },
    twitter: {
      card: "summary_large_image",
      title: ogTitle,
      description,
      images: ["/og-image.png"],
    },
  };
}
""",
)

# 2. site.ts — remove /zh
site = (ROOT / "src/lib/site.ts").read_text(encoding="utf-8")
site = site.replace('  "/zh",\n', "")
write("src/lib/site.ts", site)

# 3. homepage — remove alternateLocale
home = (ROOT / "src/app/page.tsx").read_text(encoding="utf-8")
home = home.replace(
    '  path: "/",\n  alternateLocale: { lang: "zh", path: "/zh" },\n',
    '  path: "/",\n',
)
write("src/app/page.tsx", home)

# 4. footer — remove Chinese link
footer = (ROOT / "src/components/SiteFooter.tsx").read_text(encoding="utf-8")
footer = footer.replace('      ["Creators", "/creators"],\n      ["中文", "/zh"],\n', '      ["Creators", "/creators"],\n')
write("src/components/SiteFooter.tsx", footer)

# 5. FAQ — remove Chinese question
faq = (ROOT / "src/app/faq/page.tsx").read_text(encoding="utf-8")
faq = faq.replace(
    """  [
    "Is there a Chinese version?",
    "A Chinese homepage is available at /zh. More Chinese content is planned.",
  ],
""",
    "",
)
write("src/app/faq/page.tsx", faq)

# 6. next.config — redirect /zh to /
nc = (ROOT / "next.config.ts").read_text(encoding="utf-8")
if 'source: "/zh"' not in nc:
    nc = nc.replace(
        '    return [\n      {\n        source: "/seo/:slug",',
        '    return [\n      {\n        source: "/zh",\n        destination: "/",\n        permanent: true,\n      },\n      {\n        source: "/zh/:path*",\n        destination: "/",\n        permanent: true,\n      },\n      {\n        source: "/seo/:slug",',
    )
write("next.config.ts", nc)

# 7. llms.txt
llms_path = ROOT / "public/llms.txt"
if llms_path.exists():
    llms = llms_path.read_text(encoding="utf-8")
    for line in list(llms.splitlines()):
        if "/zh" in line:
            llms = llms.replace(line + "\n", "")
    write("public/llms.txt", llms)

# 8. Deprecate bulk char expansion
chars_tool = ROOT / "tools/tianshu_expand_chars.py"
if chars_tool.exists():
    text = chars_tool.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        text = (
            '"""DEPRECATED — Bulk character expansion removed from roadmap (English-only, conversion-first).\n'
            "Do not run. P1 expanded 50 thinnest pages only; no further bulk runs planned.\\n\"\"\"\n"
            "import sys\nsys.exit('tianshu_expand_chars.py is deprecated. See ROADMAP.md')\n\n"
        ) + text
        write("tools/tianshu_expand_chars.py", text)

print("English-only pivot applied.")
