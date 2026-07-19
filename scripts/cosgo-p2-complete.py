#!/usr/bin/env python3
"""Complete remaining cosgo P0/P1/P2 items on Seoul server."""
import json
import os
import subprocess
import textwrap
import time
import urllib.request

LOG = []
BASE = "/opt/cosgo"


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:4000])
    if check and r.returncode != 0:
        raise RuntimeError(f"Failed: {cmd}\n{out}")
    return r


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


def db_url():
    with open(f"{BASE}/.env") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'").replace("?schema=public", "")
    raise RuntimeError("DATABASE_URL not found")


def psql(sql):
    url = db_url()
    one_line = " ".join(sql.split())
    run(f"psql {json.dumps(url)} -t -A -c {json.dumps(one_line)}")


def cron_secret():
    with open(f"{BASE}/.env") as f:
        for line in f:
            if line.startswith("CRON_SECRET="):
                return line.split("=", 1)[1].strip()
    return ""


def published_count():
    url = db_url()
    r = subprocess.run(
        f"psql {json.dumps(url)} -t -A -c \"SELECT count(*) FROM \\\"ContentArticle\\\" WHERE status='PUBLISHED';\"",
        shell=True,
        capture_output=True,
        text=True,
    )
    return int((r.stdout or "0").strip() or 0)


def generate_and_publish_one():
    secret = cron_secret()
    if not secret:
        return False
    url = f"http://127.0.0.1:3004/api/cron/content-generate?secret={secret}"
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            body = json.loads(resp.read().decode())
            slug = body.get("slug")
            if slug:
                psql(
                    f"UPDATE \"ContentArticle\" SET status = 'PUBLISHED', \"publishedAt\" = NOW() WHERE slug = '{slug}' AND length(content) >= 900"
                )
            LOG.append(f"generate: {body}")
            return bool(slug)
    except Exception as exc:
        LOG.append(f"generate failed: {exc}")
        return False


def patch_help_faq_schema():
    path = f"{BASE}/src/app/help/page.tsx"
    with open(path) as f:
        content = f.read()
    if "FAQPage" in content:
        return
    content = content.replace(
        "export default function HelpPage() {",
        """export default function HelpPage() {
  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((faq) => ({
      "@type": "Question",
      name: faq.q,
      acceptedAnswer: { "@type": "Answer", text: faq.a },
    })),
  };""",
    )
    content = content.replace(
        '    <div className="min-h-screen bg-gray-50">',
        '    <div className="min-h-screen bg-gray-50"><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />',
    )
    write(path, content)


def patch_activity_detail():
    write(
        f"{BASE}/src/app/activities/[id]/page.tsx",
        textwrap.dedent('''\
        import { notFound } from "next/navigation";
        import type { Metadata } from "next";
        import Link from "next/link";
        import { prisma } from "@/lib/db";
        import { TicketLink } from "@/components/TicketLink";
        import CoverImage from "@/app/city/cover-image";
        import { Calendar, MapPin, Users, ArrowLeft, BookOpen } from "lucide-react";
        import { SITE_URL } from "@/lib/seo";
        import { CITY_SLUG_TO_NAME } from "@/config/cities";
        import { HotelSearchWidget } from "@/components/layout/hotel-search-widget";
        import BlogSubscribe from "@/components/blog-subscribe";

        export const dynamic = "force-dynamic";

        async function getActivity(id: string) {
          return prisma.activity.findUnique({ where: { id } });
        }

        export async function generateMetadata({
          params,
        }: {
          params: Promise<{ id: string }>;
        }): Promise<Metadata> {
          const { id } = await params;
          const activity = await getActivity(id);
          if (!activity) return { title: "活动未找到" };
          const title = `${activity.name || "Cos团拍活动"} — ${activity.city} | CosGo`;
          const description =
            activity.description?.slice(0, 160) ||
            `${activity.city} Cosplay 团拍与漫展活动，查看详情与购票信息。`;
          return {
            title,
            description,
            alternates: { canonical: `${SITE_URL}/activities/${id}` },
            openGraph: { title, description, type: "website", locale: "zh_CN" },
          };
        }

        export default async function ActivityDetailPage({
          params,
        }: {
          params: Promise<{ id: string }>;
        }) {
          const { id } = await params;
          const activity = await getActivity(id);
          if (!activity) notFound();

          const cityLabel = CITY_SLUG_TO_NAME[activity.city] || activity.city;
          const [relatedGuides] = await Promise.all([
            prisma.contentArticle.findMany({
              where: { status: "PUBLISHED" },
              orderBy: { publishedAt: "desc" },
              take: 3,
              select: { slug: true, title: true, excerpt: true, category: true },
            }),
          ]);

          const eventSchema = {
            "@context": "https://schema.org",
            "@type": "Event",
            name: activity.name || "Cos团拍活动",
            startDate: activity.date?.toISOString(),
            location: {
              "@type": "Place",
              name: cityLabel,
              address: activity.location || cityLabel,
            },
            description: activity.description,
            url: `${SITE_URL}/activities/${id}`,
          };

          const breadcrumbSchema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "首页", item: SITE_URL },
              { "@type": "ListItem", position: 2, name: "漫展活动", item: `${SITE_URL}/activities` },
              { "@type": "ListItem", position: 3, name: activity.name || "活动详情", item: `${SITE_URL}/activities/${id}` },
            ],
          };

          return (
            <>
              <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(eventSchema) }} />
              <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
              <div className="min-h-screen bg-gray-50">
                <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-pink-900 py-12">
                  <div className="max-w-3xl mx-auto px-4">
                    <Link href="/activities" className="inline-flex items-center gap-1 text-sm text-pink-200 hover:text-white">
                      <ArrowLeft className="w-4 h-4" /> 返回活动列表
                    </Link>
                    <h1 className="mt-4 text-3xl sm:text-4xl font-bold text-white">{activity.name || "Cos团拍活动"}</h1>
                    <p className="mt-2 text-gray-300">{cityLabel}</p>
                  </div>
                </div>

                <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
                  <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
                    <div className="aspect-[16/9] bg-gray-100 relative">
                      {activity.coverImage ? (
                        <CoverImage src={activity.coverImage} alt={activity.name} />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-pink-100 to-purple-100">
                          <Calendar className="w-16 h-16 text-pink-300" />
                        </div>
                      )}
                    </div>
                    <div className="p-6 space-y-4">
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="w-4 h-4 text-[#FF5A8A]" />
                        <span>{cityLabel}{activity.location ? ` · ${activity.location}` : ""}</span>
                      </div>
                      {activity.date && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Calendar className="w-4 h-4 text-[#FF5A8A]" />
                          <span>{new Date(activity.date).toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" })}</span>
                        </div>
                      )}
                      {activity.maxPeople > 0 && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Users className="w-4 h-4 text-[#FF5A8A]" />
                          <span>{activity.currentPeople}/{activity.maxPeople} 人</span>
                        </div>
                      )}
                      {activity.description && (
                        <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">{activity.description}</p>
                      )}
                      <div className="pt-4 flex flex-wrap gap-3">
                        <TicketLink activityId={activity.id} activityName={activity.name} sourceUrl={activity.sourceUrl} variant="primary" />
                        <Link href={`/city/${activity.city}`} className="inline-flex items-center gap-1 text-sm font-medium text-[#FF5A8A] hover:text-pink-600">
                          查看{cityLabel}攻略 →
                        </Link>
                        <Link href="/blog" className="inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700">
                          <BookOpen className="w-4 h-4" /> 出片攻略
                        </Link>
                      </div>
                    </div>
                  </div>

                  <HotelSearchWidget cityName={cityLabel} country="CN" />

                  {relatedGuides.length > 0 && (
                    <section className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
                      <h2 className="text-lg font-semibold text-gray-900">出发前推荐阅读</h2>
                      <div className="mt-4 grid gap-3">
                        {relatedGuides.map((guide) => (
                          <Link key={guide.slug} href={`/blog/${guide.slug}`} className="rounded-xl border border-gray-100 p-4 hover:border-pink-200 hover:bg-pink-50/30">
                            <p className="text-xs text-pink-600">{guide.category}</p>
                            <h3 className="mt-1 font-medium text-gray-900">{guide.title}</h3>
                            <p className="mt-1 text-sm text-gray-500 line-clamp-2">{guide.excerpt}</p>
                          </Link>
                        ))}
                      </div>
                    </section>
                  )}

                  <BlogSubscribe source="activity-detail" />
                </div>
              </div>
            </>
          );
        }
        '''),
    )


def patch_zhenxi_crosspromo():
    path = f"{BASE}/src/app/blog/page.tsx"
    with open(path) as f:
        content = f.read()
    if "zhenxi.hk.cn" in content:
        return
    banner = (
        '<section className="border-y border-pink-100 bg-pink-50/50 py-3">'
        '<div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm">'
        '<p className="text-gray-600"><span className="font-medium text-gray-900">姐妹站推荐</span> · 真汐身心疗愈与睡眠改善指南</p>'
        '<a href="https://zhenxi.hk.cn/assessment" target="_blank" rel="noopener" data-track-cta="crosspromo-zhenxi" className="font-medium text-[#FF5A8A] hover:text-pink-600">免费身心评估 →</a>'
        "</div></section>"
    )
    content = content.replace(
        '<div className="min-h-screen bg-gray-50">',
        '<div className="min-h-screen bg-gray-50">' + banner,
        1,
    )
    write(path, content)


def patch_blog_subscribe_tracker():
    path = f"{BASE}/src/components/blog-subscribe.tsx"
    with open(path) as f:
        content = f.read()
    if "subscribe_complete" in content:
        return
    content = content.replace(
        "setStatus(\"done\");",
        """setStatus("done");
              if (typeof window !== "undefined" && (window as unknown as { umami?: { track: (e: string, d?: object) => void } }).umami) {
                (window as unknown as { umami: { track: (e: string, d?: object) => void } }).umami.track("subscribe_complete", { source });
              }""",
    )
    write(path, content)


def patch_cron_auto_publish():
    path = f"{BASE}/scripts/cron-content.sh"
    with open(path) as f:
        content = f.read()
    if "PUBLISHED" in content:
        return
    append = textwrap.dedent("""
    # Auto-publish if content passes quality check
    DB_URL=$(grep '^DATABASE_URL=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | sed 's/?schema=public//')
  SLUG=$(tail -2 "$LOG_FILE" | grep -oP '"slug":"\\K[^"]+' | tail -1)
  if [ -n "$SLUG" ] && [ -n "$DB_URL" ]; then
    psql "$DB_URL" -c "UPDATE \\"ContentArticle\\" SET status='PUBLISHED', \\"publishedAt\\"=NOW() WHERE slug='$SLUG' AND status='DRAFT' AND length(content) >= 900;" >> "$LOG_FILE" 2>&1 || true
  fi
""")
    write(path, content.rstrip() + append)
    run(f"chmod +x {path}")


def compress_og_image():
    path = f"{BASE}/public/og-image.png"
    run(
        f"convert {path} -strip -quality 82 -resize 1200x630 {path}.tmp && mv {path}.tmp {path}",
        check=False,
    )
    run(f"wc -c {path}", check=False)


def expand_blog_to(target=25):
    psql(
        "UPDATE \"ContentArticle\" SET status = 'PUBLISHED', \"publishedAt\" = COALESCE(\"publishedAt\", NOW()) WHERE status = 'DRAFT' AND length(content) >= 900"
    )
    count = published_count()
    attempts = 0
    while count < target and attempts < 10:
        if generate_and_publish_one():
            count = published_count()
            LOG.append(f"Published count: {count}")
        attempts += 1
        time.sleep(2)


def run_indexnow():
    run("sudo bash /opt/indexnow-submit.sh", check=False)
    run("tail -3 /var/log/indexnow.log", check=False)


def rebuild():
    run(f"cd {BASE} && npm run build")
    run("sudo systemctl restart cosgo")
    run("sleep 4 && systemctl is-active cosgo")


def verify():
    run("curl -s https://cosgo.cn/help | grep -c FAQPage", check=False)
    run("curl -s https://cosgo.cn/activities/global-con-2026-6n79yu | grep -c HotelSearchWidget", check=False)
    run("curl -s https://cosgo.cn/blog | grep -c crosspromo-zhenxi", check=False)
    run("curl -s https://cosgo.cn/sitemap.xml | grep -c '/blog/'", check=False)
    run("wc -c /opt/cosgo/public/og-image.png", check=False)


def main():
    patch_help_faq_schema()
    patch_activity_detail()
    patch_zhenxi_crosspromo()
    patch_blog_subscribe_tracker()
    patch_cron_auto_publish()
    compress_og_image()
    expand_blog_to(25)
    rebuild()
    run_indexnow()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/cosgo-p2-complete.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
