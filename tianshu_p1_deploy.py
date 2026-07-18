#!/usr/bin/env python3
"""TianShu MythOS P1 growth fixes."""
import re
from pathlib import Path

ROOT = Path("/data/www/mythos")


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


# 1. metadata.ts — hreflang support
meta = (ROOT / "src/lib/metadata.ts").read_text(encoding="utf-8")
if "alternateLocale" not in meta:
    meta = meta.replace(
        "  path: string;\n}): Metadata {",
        "  path: string;\n  alternateLocale?: { lang: string; path: string };\n}): Metadata {",
    )
    meta = meta.replace(
        "  const url = path === \"/\" ? SITE_URL : `${SITE_URL}${path}`;",
        "  const url = path === \"/\" ? SITE_URL : `${SITE_URL}${path}`;\n  const languages: Record<string, string> = { en: url };\n  if (alternateLocale) {\n    languages[alternateLocale.lang] = `${SITE_URL}${alternateLocale.path}`;\n  }",
    )
    meta = meta.replace(
        "    alternates: { canonical: url },",
        "    alternates: { canonical: url, languages },",
    )
    meta = meta.replace(
        "{ title, description, path }:",
        "{ title, description, path, alternateLocale }:",
    )
write("src/lib/metadata.ts", meta)

# 2. zh page hreflang
zh = (ROOT / "src/app/zh/page.tsx").read_text(encoding="utf-8")
if "alternateLocale" not in zh:
    zh = zh.replace(
        '  path: "/zh",\n});',
        '  path: "/zh",\n  alternateLocale: { lang: "en", path: "/" },\n});',
    )
write("src/app/zh/page.tsx", zh)

# 3. homepage hreflang
home = (ROOT / "src/app/page.tsx").read_text(encoding="utf-8")
if "alternateLocale" not in home:
    home = home.replace(
        '  path: "/",\n});',
        '  path: "/",\n  alternateLocale: { lang: "zh", path: "/zh" },\n});',
    )
write("src/app/page.tsx", home)

# 4. site.ts — add compare pages
site = (ROOT / "src/lib/site.ts").read_text(encoding="utf-8")
for p in ["/compare/mythos-vs-ai-dungeon", "/compare/mythos-vs-world-anvil", "/compare/mythos-vs-novelai"]:
    if p not in site:
        site = site.replace('  "/faq",\n];', f'  "/faq",\n  "{p}",\n];')
write("src/lib/site.ts", site)

# 5. throne page expansion
throne_page = '''import Link from "next/link";
import { notFound } from "next/navigation";
import PageShell from "@/components/PageShell";
import CTASection from "@/components/CTASection";
import JsonLd from "@/components/JsonLd";
import { buildPageMetadata } from "@/lib/metadata";
import { SITE_URL, THRONES, throneMeta } from "@/lib/site";
import { throneLore } from "@/lib/throne-lore";

export function generateStaticParams() {
  return THRONES.map((name) => ({ slug: throneMeta[name].slug }));
}

function getThrone(slug: string) {
  return THRONES.map((name) => ({ name, ...throneMeta[name] })).find((t) => t.slug === slug);
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getThrone(slug);
  if (!t) return { title: "Throne Not Found" };
  return buildPageMetadata({
    title: `${t.name} Throne Lore`,
    description: `${t.description} ${t.citizenPrompt}`,
    path: `/thrones/${t.slug}`,
  });
}

export default async function ThronePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getThrone(slug);
  if (!t) notFound();
  const lore = throneLore[t.slug];

  const faqs = [
    ["What does this Throne represent?", t.promise],
    ["How do citizens support it?", "Citizens join the Genesis Registry, choose an initial Throne, and back weekly votes that signal where the next canon pressure should move."],
    ["Does voting decide the whole story?", "No. Voting is one signal. The canon remains curated so the world stays coherent while still responding to its citizens."],
  ];

  const sections = lore
    ? [
        ["Origin of the Throne", lore.origin],
        ["Doctrine", lore.doctrine],
        ["Current Conflict", lore.currentConflict],
        ["Notable Heirs", lore.notableHeirs],
        ["Why back this Throne", lore.readerRole],
      ]
    : [];

  return (
    <PageShell label={`${t.name} Throne`}>
      <JsonLd data={{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: faqs.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })),
      }} />
      <JsonLd data={{
        "@context": "https://schema.org",
        "@type": "Article",
        headline: `${t.name} Throne — TianShu MythOS`,
        description: t.description,
        url: `${SITE_URL}/thrones/${t.slug}`,
        author: { "@type": "Organization", name: "TianShu MythOS" },
        isPartOf: { "@type": "CreativeWork", name: "TianShu MythOS World Bible" },
      }} />
      <section className="mx-auto max-w-[940px] px-6 py-16 md:py-24">
        <Link href="/thrones" className="font-serif text-xs uppercase tracking-[0.16em] text-[#8a8578] hover:text-[#c9a84c]">← All Thrones</Link>
        <div className="mt-8 border border-[rgba(201,168,76,0.16)] bg-[#0e0e16] p-8 md:p-12">
          <div className="font-serif text-6xl" style={{ color: t.color }}>{t.sigil}</div>
          <p className="mt-6 font-serif text-xs uppercase tracking-[0.22em] text-[#8b7535]">{t.promise}</p>
          <h1 className="mt-3 font-serif text-5xl text-[#c9a84c]">{t.name} Throne</h1>
          <p className="mt-6 text-lg leading-8 text-[#b0ab9c]">{t.description}</p>
          <p className="mt-5 border-l border-[#c9a84c] pl-5 text-base leading-7 text-[#e8d08f]">{t.citizenPrompt}</p>
        </div>
        {sections.map(([title, body]) => (
          <div key={title} className="mt-10 border border-[rgba(201,168,76,0.1)] bg-[#0b0b11] p-7">
            <h2 className="font-serif text-2xl text-[#e8d08f]">{title}</h2>
            {body.split(/\n\n+/).map((para) => (
              <p key={para.slice(0, 40)} className="mt-4 text-base leading-8 text-[#b0ab9c]">{para}</p>
            ))}
          </div>
        ))}
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {faqs.map(([q, a]) => (
            <div key={q} className="border border-[rgba(255,255,255,0.06)] bg-[#0b0b11] p-5">
              <h2 className="font-serif text-lg text-[#e8d08f]">{q}</h2>
              <p className="mt-2 text-sm leading-6 text-[#8a8578]">{a}</p>
            </div>
          ))}
        </div>
        <div className="mt-10 flex flex-wrap gap-3 text-sm">
          <Link href={`/characters?throne=${t.name}`} className="text-[#c9a84c] hover:text-[#e8d08f]">Heirs of {t.name} →</Link>
          <Link href="/events" className="text-[#c9a84c] hover:text-[#e8d08f]">World Events →</Link>
          <Link href="/join" className="text-[#c9a84c] hover:text-[#e8d08f]">Join Registry →</Link>
        </div>
      </section>
      <CTASection title={`Back the ${t.name} Throne.`} body="Join the Registry first, then return to weekly votes as the balance of power changes." />
    </PageShell>
  );
}
'''
write("src/app/thrones/[slug]/page.tsx", throne_page)

# 6. compare pages
COMPARE = {
    "mythos-vs-ai-dungeon": {
        "title": "TianShu MythOS vs AI Dungeon",
        "desc": "Compare TianShu MythOS and AI Dungeon: living canon archive vs open-ended AI roleplay.",
        "competitor": "AI Dungeon",
        "points": [
            ["Core model", "MythOS is a curated living archive with weekly canon; AI Dungeon is open-ended prompt roleplay."],
            ["World coherence", "MythOS maintains editorial canon; AI Dungeon prioritizes player freedom over consistency."],
            ["Community role", "MythOS citizens vote on Throne pressure; AI Dungeon has multiplayer but no shared canon votes."],
            ["Best for", "MythOS suits readers who want evolving lore; AI Dungeon suits improvisational storytellers."],
        ],
    },
    "mythos-vs-world-anvil": {
        "title": "TianShu MythOS vs World Anvil",
        "desc": "Compare TianShu MythOS and World Anvil: AI-native living world vs creator-built wiki platform.",
        "competitor": "World Anvil",
        "points": [
            ["Content creation", "World Anvil is author-driven wiki building; MythOS generates and updates canon at scale."],
            ["Reader participation", "MythOS has Registry voting and Chronicle; World Anvil is primarily creator-to-reader publishing."],
            ["AI role", "MythOS is AI-native; World Anvil is a traditional worldbuilding toolkit."],
            ["Best for", "World Anvil for DMs documenting homebrew; MythOS for shared evolving universe fandom."],
        ],
    },
    "mythos-vs-novelai": {
        "title": "TianShu MythOS vs NovelAI",
        "desc": "Compare TianShu MythOS and NovelAI: community canon universe vs personal AI writing assistant.",
        "competitor": "NovelAI",
        "points": [
            ["Product focus", "NovelAI is a private writing assistant; MythOS is a public fantasy civilization."],
            ["Canon", "MythOS publishes weekly world events; NovelAI outputs stay in your private projects."],
            ["Social layer", "MythOS has Thrones, voting, and Registry identity; NovelAI is primarily solo creation."],
            ["Best for", "NovelAI for personal fiction drafting; MythOS for communal dark fantasy worldbuilding."],
        ],
    },
}

for slug, data in COMPARE.items():
    points_js = "\n".join(
        f'    ["{p[0]}", "{p[1]}"],' for p in data["points"]
    )
    content = f'''import Link from "next/link";
import PageShell from "@/components/PageShell";
import CTASection from "@/components/CTASection";
import {{ buildPageMetadata }} from "@/lib/metadata";

export const metadata = buildPageMetadata({{
  title: "{data['title']}",
  description: "{data['desc']}",
  path: "/compare/{slug}",
}});

const rows = [
{points_js}
];

export default function ComparePage() {{
  return (
    <PageShell label="Compare">
      <section className="mx-auto max-w-[900px] px-6 py-16 md:py-24">
        <p className="font-serif text-xs uppercase tracking-[0.26em] text-[#8b7535]">Comparison</p>
        <h1 className="mt-4 font-serif text-5xl text-[#c9a84c]">{data['title']}</h1>
        <p className="mt-5 text-lg leading-8 text-[#b0ab9c]">{data['desc']}</p>
        <div className="mt-10 overflow-hidden border border-[rgba(201,168,76,0.12)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#0e0e16] text-xs uppercase tracking-[0.14em] text-[#8b7535]">
              <tr><th className="px-5 py-4">Dimension</th><th className="px-5 py-4">TianShu MythOS vs {data['competitor']}</th></tr>
            </thead>
            <tbody>
              {{rows.map(([k, v]) => (
                <tr key={{k}} className="border-t border-[rgba(255,255,255,0.05)]">
                  <td className="px-5 py-4 font-serif text-[#e8d08f]">{{k}}</td>
                  <td className="px-5 py-4 text-[#b0ab9c]">{{v}}</td>
                </tr>
              ))}}
            </tbody>
          </table>
        </div>
        <p className="mt-8 text-sm text-[#8a8578]">
          <Link href="/how-it-works" className="text-[#c9a84c] hover:text-[#e8d08f]">How MythOS works</Link>
          {" · "}
          <Link href="/join" className="text-[#c9a84c] hover:text-[#e8d08f]">Join the Registry</Link>
        </p>
      </section>
      <CTASection title="Enter the Genesis Registry." body="See whether the living archive earns your return before paid tiers open." />
    </PageShell>
  );
}}
'''
    write(f"src/app/compare/{slug}/page.tsx", content)

# 7. footer compare links
footer = (ROOT / "src/components/SiteFooter.tsx").read_text(encoding="utf-8")
if "MythOS vs AI Dungeon" not in footer:
    footer = footer.replace(
        '      ["Press Kit", "/press"],',
        '      ["Press Kit", "/press"],\n      ["MythOS vs AI Dungeon", "/compare/mythos-vs-ai-dungeon"],',
    )
write("src/components/SiteFooter.tsx", footer)

# 8. character page — paragraph bio + buildPageMetadata in generateMetadata
char_page = (ROOT / "src/app/characters/[slug]/page.tsx").read_text(encoding="utf-8")
if "buildPageMetadata" not in char_page:
    char_page = char_page.replace(
        'import pool from "@/lib/db";',
        'import pool from "@/lib/db";\nimport { buildPageMetadata } from "@/lib/metadata";\nimport { SITE_URL } from "@/lib/site";',
    )
    char_page = re.sub(
        r"export async function generateMetadata\([\s\S]*?return \{[\s\S]*?\};\n\}",
        '''export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const c = await getCharacter(slug);
  if (!c) return { title: "Character Not Found — MythOS" };
  return buildPageMetadata({
    title: `${c.name} — Character File`,
    description: (c.description || "").replace(/<!--[\\s\\S]*?-->/g, "").slice(0, 155),
    path: `/characters/${slug}`,
  });
}''',
        char_page,
        count=1,
    )
    char_page = char_page.replace(
        '"@type": "Person",',
        '"@type": "Person",\n              "@id": `${SITE_URL}/characters/${c.slug}#person`,',
    )
    char_page = char_page.replace(
        '"affiliation": c.faction,',
        '"jobTitle": `Heir of the ${c.throne} Throne`,\n              "affiliation": { "@type": "Organization", "name": c.faction || "TianShu MythOS" },',
    )
    char_page = char_page.replace(
        '{c.description || "No recorded history."}',
        '{(c.description || "No recorded history.").replace(/<!--[\\s\\S]*?-->/g, "").split(/\\n\\n+/).map((para, i) => (\n                <p key={i} className={i > 0 ? "mt-4" : ""}>{para.trim()}</p>\n              ))}',
    )
write("src/app/characters/[slug]/page.tsx", char_page)

# 9. event page metadata
evt = (ROOT / "src/app/events/[slug]/page.tsx").read_text(encoding="utf-8")
if "buildPageMetadata" not in evt:
    evt = evt.replace(
        'import pool from "@/lib/db";',
        'import pool from "@/lib/db";\nimport { buildPageMetadata } from "@/lib/metadata";\nimport { SITE_URL } from "@/lib/site";',
    )
    evt = re.sub(
        r"export async function generateMetadata\([\s\S]*?return \{[\s\S]*?\};\n\}",
        '''export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const e = await getEvent(slug);
  if (!e) return { title: "Event Not Found — MythOS" };
  return buildPageMetadata({
    title: `${e.title} — Chronicle Event`,
    description: (e.description || "").slice(0, 155),
    path: `/events/${slug}`,
  });
}''',
        evt,
        count=1,
    )
    if '"@type": "Event"' not in evt:
        evt = evt.replace(
            '"@type": "CreativeWork"',
            '"@type": "Event"',
        )
write("src/app/events/[slug]/page.tsx", evt)

print("P1 code patches done.")
