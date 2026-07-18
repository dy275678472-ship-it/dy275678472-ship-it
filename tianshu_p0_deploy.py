#!/usr/bin/env python3
"""TianShu MythOS P0 growth fixes - run on server."""
import re
from pathlib import Path

ROOT = Path("/data/www/mythos")
BACKUP = ROOT / ".backup-p0"


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not (BACKUP / rel).exists():
        (BACKUP / rel).parent.mkdir(parents=True, exist_ok=True)
        (BACKUP / rel).write_bytes(p.read_bytes())
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


def patch_metadata_file(rel: str, title: str, desc: str, path: str) -> None:
    p = ROOT / rel
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    if "buildPageMetadata" in text:
        return
    text = text.replace('import { SITE_URL } from "@/lib/site";', 'import { buildPageMetadata } from "@/lib/metadata";')
    text = text.replace('import type { Metadata } from "next";\n', "")
    text = re.sub(
        r"export const metadata: Metadata = \{[\s\S]*?\};\n",
        (
            "export const metadata = buildPageMetadata({\n"
            f'  title: "{title}",\n'
            f'  description: "{desc}",\n'
            f'  path: "{path}",\n'
            "});\n"
        ),
        text,
        count=1,
    )
    write(rel, text)


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

site = (ROOT / "src/lib/site.ts").read_text(encoding="utf-8")
if "SOCIAL_PROFILES" not in site:
    site = site.replace(
        "export const SITE_DESCRIPTION =",
        (
            "export const SOCIAL_PROFILES = [\n"
            '  "https://x.com/TianShuMythOS",\n'
            '  "https://www.reddit.com/user/TianShuMythOS/",\n'
            '  "https://github.com/TianShuMythOS",\n'
            "] as const;\n\n"
            "export const SITE_DESCRIPTION ="
        ),
    )
site = site.replace('  "/zh",\n];', '  "/zh",\n  "/pricing",\n  "/faq",\n];')
write("src/lib/site.ts", site)

layout = (ROOT / "src/app/layout.tsx").read_text(encoding="utf-8")
layout = layout.replace(
    'import { SITE_DESCRIPTION, SITE_NAME, SITE_URL } from "@/lib/site";',
    'import { SITE_DESCRIPTION, SITE_NAME, SITE_URL, SOCIAL_PROFILES } from "@/lib/site";',
)
layout = layout.replace("sameAs: [],", "sameAs: [...SOCIAL_PROFILES],")
write("src/app/layout.tsx", layout)

PAGE_META = {
    "src/app/about/page.tsx": (
        "About TianShu MythOS",
        "TianShu MythOS is an AI-native living fantasy universe that combines narrative generation, editorial curation, and reader-backed canon pressure.",
        "/about",
    ),
    "src/app/founding-citizen/page.tsx": (
        "Founding Citizen Membership",
        "Founding Citizen is the proposed early membership layer for TianShu MythOS, with private votes, early canon drops, and character naming rounds.",
        "/founding-citizen",
    ),
    "src/app/how-it-works/page.tsx": (
        "How TianShu MythOS Works",
        "Learn how the Genesis Registry, Twelve Thrones, weekly votes, and canon Chronicle turn TianShu MythOS into a living fantasy universe.",
        "/how-it-works",
    ),
    "src/app/join/page.tsx": (
        "Join the Genesis Registry",
        "Claim your TianShu MythOS Genesis Registry number, choose a Throne, and receive weekly canon events from the living fantasy universe.",
        "/join",
    ),
}

for rel, meta in PAGE_META.items():
    patch_metadata_file(rel, *meta)

for rel in [
    "src/app/ai-living-world/page.tsx",
    "src/app/bible/page.tsx",
    "src/app/characters/page.tsx",
    "src/app/chronicle/page.tsx",
    "src/app/community-guidelines/page.tsx",
    "src/app/creators/page.tsx",
    "src/app/events/page.tsx",
    "src/app/press/page.tsx",
    "src/app/privacy/page.tsx",
    "src/app/roadmap/page.tsx",
    "src/app/search/page.tsx",
    "src/app/terms/page.tsx",
    "src/app/thrones/page.tsx",
    "src/app/zh/page.tsx",
]:
    p = ROOT / rel
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    m = re.search(
        r'title: "([^"]+)"[\s\S]*?description: "([^"]+)"[\s\S]*?canonical: `\$\{SITE_URL\}(/[^`]+)`',
        text,
    )
    if m:
        patch_metadata_file(rel, m.group(1), m.group(2), m.group(3))

home = (ROOT / "src/app/page.tsx").read_text(encoding="utf-8")
home = home.replace('import type { Metadata } from "next";\n', "")
home = home.replace(
    'import { SITE_DESCRIPTION, SITE_URL, THRONES, throneMeta } from "@/lib/site";',
    'import { SITE_DESCRIPTION, SITE_URL, THRONES, throneMeta } from "@/lib/site";\nimport { buildPageMetadata } from "@/lib/metadata";',
)
home = re.sub(
    r"export const metadata: Metadata = \{[\s\S]*?\};\n",
    (
        "export const metadata = buildPageMetadata({\n"
        '  title: "TianShu MythOS — AI Living Fantasy Universe",\n'
        "  description: SITE_DESCRIPTION,\n"
        '  path: "/",\n'
        "});\n"
    ),
    home,
    count=1,
)

if "registryCount" not in home:
    home = home.replace(
        "async function getHomeData() {",
        (
            "async function getRegistryCount() {\n"
            '  try {\n'
            '    const { rows } = await pool.query("SELECT COUNT(*)::int AS count FROM subscribers");\n'
            "    return rows[0]?.count ?? 0;\n"
            "  } catch {\n"
            "    return 0;\n"
            "  }\n"
            "}\n\n"
            "async function getHomeData() {"
        ),
    )
    home = home.replace(
        "export default async function HomePage() {\n  const { witnesses, cataclysms } = await getHomeData();",
        "export default async function HomePage() {\n  const [{ witnesses, cataclysms }, registryCount] = await Promise.all([getHomeData(), getRegistryCount()]);",
    )
    home = home.replace(
        '{[["12", "Thrones"], ["176+", "Heirs"], ["Weekly", "Canon"]].map(([num, label]) => (',
        '{[[String(registryCount || 0), "Citizens"], ["12", "Thrones"], ["Weekly", "Canon"]].map(([num, label]) => (',
    )
    home = home.replace(
        '<div className="relative border border-[rgba(201,168,76,0.16)] bg-[#0e0e16] p-6 shadow-[0_0_120px_rgba(201,168,76,0.06)]">',
        '<div id="vote" className="relative border border-[rgba(201,168,76,0.16)] bg-[#0e0e16] p-6 shadow-[0_0_120px_rgba(201,168,76,0.06)]">',
    )
write("src/app/page.tsx", home)

reg = (ROOT / "src/components/RegistryForm.tsx").read_text(encoding="utf-8")
if "Cast your first vote" not in reg:
    reg = reg.replace(
        '        <a href="/thrones" className="mt-5 inline-block border border-[#c9a84c] px-5 py-2 font-serif text-xs uppercase tracking-[0.14em] text-[#c9a84c] hover:bg-[#c9a84c] hover:text-[#08080c]">\n          View the Thrones\n        </a>',
        (
            '        <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:justify-center">\n'
            '          <a href="/#vote" className="inline-block bg-[#c9a84c] px-5 py-2 font-serif text-xs uppercase tracking-[0.14em] text-[#08080c] hover:bg-[#e8d08f]">\n'
            "            Cast your first vote\n"
            "          </a>\n"
            '          <a href="/thrones" className="inline-block border border-[#c9a84c] px-5 py-2 font-serif text-xs uppercase tracking-[0.14em] text-[#c9a84c] hover:bg-[#c9a84c] hover:text-[#08080c]">\n'
            "            View the Thrones\n"
            "          </a>\n"
            "        </div>"
        ),
    )
write("src/components/RegistryForm.tsx", reg)

footer = (ROOT / "src/components/SiteFooter.tsx").read_text(encoding="utf-8")
footer = footer.replace(
    '      ["Founding Citizen", "/founding-citizen"],\n      ["Chronicle", "/chronicle"],',
    '      ["Pricing", "/pricing"],\n      ["Founding Citizen", "/founding-citizen"],\n      ["FAQ", "/faq"],\n      ["Chronicle", "/chronicle"],',
)
write("src/components/SiteFooter.tsx", footer)

llms = (ROOT / "public/llms.txt").read_text(encoding="utf-8")
for link in [
    "- [Pricing](https://tianshu.online/pricing): Membership tiers",
    "- [FAQ](https://tianshu.online/faq): Common questions",
]:
    if link not in llms:
        llms = llms.replace("- [Bible]", link + "\n- [Bible]")
write("public/llms.txt", llms)

print("P0 core patches done.")
