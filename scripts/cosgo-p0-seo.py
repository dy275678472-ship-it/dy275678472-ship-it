#!/usr/bin/env python3
"""P0 SEO fixes for cosgo.cn on Seoul server."""
import subprocess
import textwrap

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
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


def patch_start_sh():
    path = f"{BASE}/start.sh"
    with open(path) as f:
        content = f.read()
    if "ln -sf /opt/cosgo/public public" not in content:
        content = content.replace(
            "if [ ! -e .next/static ]; then\n  ln -sf /opt/cosgo/.next/static .next/static\nfi\n",
            "if [ ! -e .next/static ]; then\n  ln -sf /opt/cosgo/.next/static .next/static\nfi\n"
            "if [ ! -e public ]; then\n  ln -sf /opt/cosgo/public public\nfi\n",
        )
        write(path, content)
    run("chmod +x /opt/cosgo/start.sh")


def create_seo_lib():
    write(
        f"{BASE}/src/lib/seo.ts",
        """export const SITE_URL = "https://cosgo.cn";

export function pageCanonical(path: string) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return { alternates: { canonical: `${SITE_URL}${normalized}` } };
}
""",
    )


def create_activity_detail_page():
    write(
        f"{BASE}/src/app/activities/[id]/page.tsx",
        textwrap.dedent('''\
        import { notFound } from "next/navigation";
        import type { Metadata } from "next";
        import Link from "next/link";
        import { prisma } from "@/lib/db";
        import { TicketLink } from "@/components/TicketLink";
        import CoverImage from "@/app/city/cover-image";
        import { Calendar, MapPin, Users, ArrowLeft } from "lucide-react";
        import { SITE_URL } from "@/lib/seo";

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

          const eventSchema = {
            "@context": "https://schema.org",
            "@type": "Event",
            name: activity.name || "Cos团拍活动",
            startDate: activity.date?.toISOString(),
            location: {
              "@type": "Place",
              name: activity.city,
              address: activity.location || activity.city,
            },
            description: activity.description,
            url: `${SITE_URL}/activities/${id}`,
          };

          return (
            <>
              <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(eventSchema) }}
              />
              <div className="min-h-screen bg-gray-50">
                <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-pink-900 py-12">
                  <div className="max-w-3xl mx-auto px-4">
                    <Link
                      href="/activities"
                      className="inline-flex items-center gap-1 text-sm text-pink-200 hover:text-white"
                    >
                      <ArrowLeft className="w-4 h-4" /> 返回活动列表
                    </Link>
                    <h1 className="mt-4 text-3xl sm:text-4xl font-bold text-white">
                      {activity.name || "Cos团拍活动"}
                    </h1>
                    <p className="mt-2 text-gray-300">{activity.city}</p>
                  </div>
                </div>

                <div className="max-w-3xl mx-auto px-4 py-8">
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
                        <span>
                          {activity.city}
                          {activity.location ? ` · ${activity.location}` : ""}
                        </span>
                      </div>
                      {activity.date && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Calendar className="w-4 h-4 text-[#FF5A8A]" />
                          <span>
                            {new Date(activity.date).toLocaleDateString("zh-CN", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })}
                          </span>
                        </div>
                      )}
                      {activity.maxPeople > 0 && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Users className="w-4 h-4 text-[#FF5A8A]" />
                          <span>
                            {activity.currentPeople}/{activity.maxPeople} 人
                          </span>
                        </div>
                      )}
                      {activity.description && (
                        <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                          {activity.description}
                        </p>
                      )}
                      <div className="pt-4 flex flex-wrap gap-3">
                        <TicketLink
                          activityId={activity.id}
                          activityName={activity.name}
                          sourceUrl={activity.sourceUrl}
                          variant="primary"
                        />
                        <Link
                          href={`/city/${activity.citySlug || activity.city}`}
                          className="inline-flex items-center gap-1 text-sm font-medium text-[#FF5A8A] hover:text-pink-600"
                        >
                          查看{activity.city}攻略 →
                        </Link>
                        <Link
                          href="/blog"
                          className="inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                        >
                          出片攻略 →
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          );
        }
        '''),
    )


def patch_layout():
    path = f"{BASE}/src/app/layout.tsx"
    with open(path) as f:
        content = f.read()
    content = content.replace(
        """  alternates: {
    canonical: "/",
  },
""",
        "",
    )
    write(path, content)


def add_canonical_to_page(path, canonical_path, import_seo=True):
    with open(path) as f:
        content = f.read()
    if "pageCanonical" in content or f'canonical: "https://cosgo.cn{canonical_path}"' in content:
        return
    if import_seo and 'from "@/lib/seo"' not in content:
        if "import type { Metadata }" in content:
            content = content.replace(
                'import type { Metadata } from "next";',
                'import type { Metadata } from "next";\nimport { pageCanonical } from "@/lib/seo";',
            )
        elif "import { Metadata }" in content:
            content = content.replace(
                'import { Metadata } from "next";',
                'import { Metadata } from "next";\nimport { pageCanonical } from "@/lib/seo";',
            )
    if "export const metadata: Metadata = {" in content:
        content = content.replace(
            "export const metadata: Metadata = {",
            f'export const metadata: Metadata = {{\n  ...pageCanonical("{canonical_path}"),',
            1,
        )
        write(path, content)


def patch_homepage():
    path = f"{BASE}/src/app/page.tsx"
    with open(path) as f:
        content = f.read()

    if "getArticleCount" not in content:
        content = content.replace(
            "async function getLatestGuides() {",
            "async function getArticleCount() {\n"
            '  return prisma.contentArticle.count({ where: { status: "PUBLISHED" } });\n'
            "}\n\nasync function getLatestGuides() {",
        )
        content = content.replace(
            "const [cities, activities, latestGuides] = await Promise.all([",
            "const [cities, activities, latestGuides, articleCount] = await Promise.all([",
        )
        content = content.replace(
            "    getLatestGuides(),\n  ]);",
            "    getLatestGuides(),\n    getArticleCount(),\n  ]);",
        )
        content = content.replace(
            'import Link from "next/link";',
            'import type { Metadata } from "next";\nimport Link from "next/link";\n'
            'import { pageCanonical } from "@/lib/seo";\nimport { GLOBAL_CITY_MAP } from "@/config/cities";',
        )
        if "export const metadata" not in content:
            content = content.replace(
                "export const revalidate = 3600;",
                'export const metadata: Metadata = pageCanonical("/");\n\nexport const revalidate = 3600;',
            )

    city_count = "Object.keys(GLOBAL_CITY_MAP).length"
    content = content.replace(
        """            <div className="flex gap-8 mt-12">
              <div>
                <div className="text-2xl font-bold text-white">持续更新</div>
                <div className="text-sm text-gray-400">拍摄攻略</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{67}</div>
                <div className="text-sm text-gray-400">覆盖城市</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{totalActivities}</div>
                <div className="text-sm text-gray-400">漫展活动</div>
              </div>
            </div>""",
        f"""            <div className="flex gap-8 mt-12">
              <div>
                <div className="text-2xl font-bold text-white">{{articleCount}}+</div>
                <div className="text-sm text-gray-400">拍摄攻略</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{{{city_count}}}</div>
                <div className="text-sm text-gray-400">覆盖城市</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{{totalActivities}}</div>
                <div className="text-sm text-gray-400">漫展活动</div>
              </div>
            </div>""",
    )

    if 'href={`/activities/${a.id}`}' not in content:
        content = content.replace(
            '<h3 className="font-semibold text-gray-900 text-sm line-clamp-2">{a.name}</h3>',
            '<Link href={`/activities/${a.id}`} className="font-semibold text-gray-900 text-sm line-clamp-2 hover:text-[#FF5A8A]">{a.name}</Link>',
        )
        content = content.replace(
            """                      <TicketLink activityId={a.id} activityName={a.name} sourceUrl={a.sourceUrl} variant="outline" />
                    </div>""",
            """                      <div className="mt-3 flex items-center gap-3">
                        <TicketLink activityId={a.id} activityName={a.name} sourceUrl={a.sourceUrl} variant="outline" />
                        <Link href={`/activities/${a.id}`} className="text-xs font-medium text-[#FF5A8A] hover:text-pink-600">详情 →</Link>
                      </div>
                    </div>""",
        )

    write(path, content)


def patch_activities_list():
    path = f"{BASE}/src/app/activities/page.tsx"
    with open(path) as f:
        content = f.read()

    if 'from "@/lib/seo"' not in content:
        content = content.replace(
            'import type { Metadata } from "next";',
            'import type { Metadata } from "next";\nimport { pageCanonical } from "@/lib/seo";',
        )
    if '...pageCanonical("/activities")' not in content:
        content = content.replace(
            "export const metadata: Metadata = {",
            'export const metadata: Metadata = {\n  ...pageCanonical("/activities"),',
            1,
        )

    if 'href={`/activities/${a.id}`}' not in content:
        content = content.replace(
            '<h3 className="font-semibold text-gray-900 mb-3 line-clamp-2">{a.name || "Cos团拍活动"}</h3>',
            '<Link href={`/activities/${a.id}`} className="font-semibold text-gray-900 mb-3 line-clamp-2 hover:text-[#FF5A8A] block">{a.name || "Cos团拍活动"}</Link>',
        )
        content = content.replace(
            """                                        <div className="mt-4">
                      <TicketLink activityId={a.id} activityName={a.name} sourceUrl={a.sourceUrl} variant="primary" />
                    </div>""",
            """                                        <div className="mt-4 flex items-center gap-3">
                      <TicketLink activityId={a.id} activityName={a.name} sourceUrl={a.sourceUrl} variant="primary" />
                      <Link href={`/activities/${a.id}`} className="text-sm font-medium text-[#FF5A8A] hover:text-pink-600">查看详情 →</Link>
                    </div>""",
        )

    write(path, content)


def patch_blog_article_schema():
    path = f"{BASE}/src/app/blog/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "Article" in content and "application/ld+json" in content:
        return
    # Add Article schema in return - the file is minified on one line, append before return
    if 'type="application/ld+json"' not in content:
        content = content.replace(
            "if (!post) notFound();",
            """if (!post) notFound();
  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.excerpt,
    datePublished: (post.publishedAt || post.createdAt).toISOString(),
    image: "https://cosgo.cn/og-image.png",
    publisher: { "@type": "Organization", name: "CosGo", logo: { "@type": "ImageObject", url: "https://cosgo.cn/og-image.png" } },
    mainEntityOfPage: `https://cosgo.cn/blog/${post.slug}`,
  };""",
        )
        content = content.replace(
            'return <div className="min-h-screen bg-gray-50">',
            'return <div className="min-h-screen bg-gray-50"><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }} />',
        )
        write(path, content)


def rebuild():
    run(f"cd {BASE} && npm run build")
    run("sudo systemctl restart cosgo")
    run("sleep 3 && systemctl is-active cosgo")


def verify():
    run("curl -sI https://cosgo.cn/activities/global-con-2026-6n79yu | head -3", check=False)
    run("curl -s https://cosgo.cn/pricing | grep -o 'canonical\" href=\"[^\"]*\"' | head -1", check=False)
    run("curl -s https://cosgo.cn/activities | grep -o 'canonical\" href=\"[^\"]*\"' | head -1", check=False)
    run("curl -s https://cosgo.cn/ | grep -o 'canonical\" href=\"[^\"]*\"' | head -1", check=False)
    run("curl -s https://cosgo.cn/sitemap.xml | grep -c '<loc>'", check=False)


def main():
    patch_start_sh()
    create_seo_lib()
    create_activity_detail_page()
    patch_layout()
    patch_homepage()
    patch_activities_list()
    for p, c in [
        (f"{BASE}/src/app/pricing/page.tsx", "/pricing"),
        (f"{BASE}/src/app/photographers/page.tsx", "/photographers"),
        (f"{BASE}/src/app/about/page.tsx", "/about"),
        (f"{BASE}/src/app/contact/page.tsx", "/contact"),
        (f"{BASE}/src/app/help/page.tsx", "/help"),
    ]:
        add_canonical_to_page(p, c)
    patch_blog_article_schema()
    rebuild()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/cosgo-p0-seo.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
