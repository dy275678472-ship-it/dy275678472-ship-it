#!/usr/bin/env python3
"""P3 growth implementation for zhenxi.hk.cn on Seoul server."""
import subprocess
import textwrap

LOG = []
BASE = "/opt/zhenxi"


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:4000])
    if check and r.returncode != 0:
        raise RuntimeError(f"Failed ({r.returncode}): {cmd}\n{out}")
    return r


def write(path, content):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


def patch_prisma():
    schema_path = f"{BASE}/prisma/schema.prisma"
    with open(schema_path) as f:
        schema = f.read()
    if "model Subscriber" not in schema:
        schema += textwrap.dedent("""

model Subscriber {
  id        String   @id @default(cuid())
  email     String   @unique
  source    String?
  createdAt DateTime @default(now())

  @@index([email])
}
""")
        write(schema_path, schema)
    run(f"cd {BASE} && export $(grep DATABASE_URL .env | xargs) && npx prisma db push --accept-data-loss", check=False)


def create_blog_cta():
    write(
        f"{BASE}/src/components/blog-cta.tsx",
        textwrap.dedent("""\
        import Link from "next/link";
        import { Heart, ArrowRight, ClipboardCheck } from "lucide-react";

        export default function BlogCta() {
          return (
            <div className="mt-12 text-center">
              <div className="rounded-2xl bg-gradient-to-br from-cream via-primary/5 to-mist-light p-8">
                <Heart className="mx-auto mb-3 h-7 w-7 text-primary" fill="#C9A96E" />
                <p className="mb-2 text-lg font-light text-foreground">喜欢这篇文章？</p>
                <p className="mb-6 text-sm text-warm-gray">3 分钟测评，获取专属疗愈建议</p>
                <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
                  <Link
                    href="/assessment"
                    data-track-cta="blog-assessment"
                    className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary-dark"
                  >
                    <ClipboardCheck className="h-4 w-4" />
                    开始身心评估
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    href="/services"
                    data-track-cta="blog-services"
                    className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-white px-6 py-2.5 text-sm font-medium text-primary transition-all hover:bg-primary/5"
                  >
                    浏览疗愈指南
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          );
        }
        """),
    )


def patch_email_lib():
    path = f"{BASE}/src/lib/email.ts"
    with open(path) as f:
        content = f.read()
    if "sendAssessmentReport" in content:
        return
    content += textwrap.dedent("""

export async function sendAssessmentReport(
  to: string,
  assessmentType: string,
  resultLabel: string
) {
  const titles: Record<string, string> = {
    sleep: "睡眠质量评估",
    stress: "压力水平评估",
    body: "身体紧张度评估",
    emotion: "情绪状态评估",
  };
  const title = titles[assessmentType] || "身心评估";
  await sendEmail(
    to,
    `【真汐】你的${title}结果：${resultLabel}`,
    `<div style="max-width:550px;margin:0 auto;padding:40px 20px;background:#FAF8F5;font-family:sans-serif;color:#2C2A27;line-height:1.8;">
      <h2 style="color:#C9A96E;font-weight:300;">你的疗愈报告已生成</h2>
      <p>感谢完成 <b>${escapeHtml(title)}</b>。你的当前状态：<b>${escapeHtml(resultLabel)}</b></p>
      <p>我们为你准备了对应的疗愈指南，建议在今晚睡前阅读一篇：</p>
      <p style="text-align:center;margin:24px 0;">
        <a href="https://zhenxi.hk.cn/services" style="display:inline-block;padding:12px 30px;background:#C9A96E;color:#fff;text-decoration:none;border-radius:20px;">浏览疗愈指南</a>
      </p>
      <p style="font-size:12px;color:#9A958A;">此邮件由真汐自动发送。愿你今夜好眠。</p>
    </div>`
  );
}
""")
    write(path, content)


def create_subscribe_api():
    write(
        f"{BASE}/src/app/api/subscribe/route.ts",
        textwrap.dedent("""\
        import { NextResponse } from "next/server";
        import { z } from "zod";
        import { db } from "@/lib/db";
        import { sendAssessmentReport } from "@/lib/email";

        const schema = z.object({
          email: z.string().email("请输入有效邮箱"),
          source: z.string().optional(),
          assessmentType: z.string().optional(),
          resultLabel: z.string().optional(),
        });

        export async function POST(req: Request) {
          try {
            const body = await req.json();
            const data = schema.parse(body);

            await db.subscriber.upsert({
              where: { email: data.email },
              create: {
                email: data.email,
                source: data.source || "assessment",
              },
              update: {
                source: data.source || "assessment",
              },
            });

            if (data.assessmentType && data.resultLabel) {
              await sendAssessmentReport(
                data.email,
                data.assessmentType,
                data.resultLabel
              );
            }

            return NextResponse.json({ ok: true, message: "报告已发送到你的邮箱" });
          } catch (err) {
            if (err instanceof z.ZodError) {
              return NextResponse.json({ error: err.errors[0]?.message || "无效输入" }, { status: 400 });
            }
            console.error("[subscribe]", err);
            return NextResponse.json({ error: "提交失败，请稍后再试" }, { status: 500 });
          }
        }
        """),
    )


MISSING_POSTS = """  {
    slug: "meditation-for-anxiety-relief",
    title: "冥想：抚平焦虑的温柔力量",
    excerpt: "焦虑像不请自来的访客，而冥想是一扇门——教你温柔地邀请它坐下，喝茶，然后目送它离开。",
    category: "正念冥想",
    date: "2026-07-15",
    readTime: "6 分钟",
    author: "林溪",
  },
  {
    slug: "seasonal-mood-regulation-for-women",
    title: "四季情绪调适指南",
    excerpt: "季节更替影响女性情绪，从冬季忧郁到夏季躁动，通过自然节律与身心小技巧，找到内在平衡。",
    category: "身心疗愈",
    date: "2026-07-09",
    readTime: "5 分钟",
    author: "林溪月",
  },
  {
    slug: "body-scan-meditation-practice",
    title: "身体扫描冥想：与内在对话",
    excerpt: "身体扫描冥想是一种温和的自我觉察练习，帮助女性释放压力，连接内在智慧，提升睡眠质量。",
    category: "正念冥想",
    date: "2026-07-09",
    readTime: "6 分钟",
    author: "静水流深",
  },
  {
    slug: "workplace-women-stress-management",
    title: "职场女性压力管理术",
    excerpt: "职场女性常陷于多重角色压力，本文从识别信号到日常练习，提供一套温和而有效的压力管理方法。",
    category: "身心疗愈",
    date: "2026-07-09",
    readTime: "5 分钟",
    author: "林溪",
  },
  {
    slug: "aromatherapy-and-emotions",
    title: "芳香疗愈情绪密码",
    excerpt: "精油如何透过嗅觉直达大脑，唤醒深层情绪记忆？探索芳香疗法的科学原理与日常应用。",
    category: "身心疗愈",
    date: "2026-07-08",
    readTime: "6 分钟",
    author: "清悦",
  },
  {
    slug: "menopause-natural-remedies-guide",
    title: "更年期自然调理指南",
    excerpt: "更年期不是终点，而是新的起点。通过饮食、运动和情绪调整，平稳度过这个转变期。",
    category: "女性健康",
    date: "2026-07-08",
    readTime: "5 分钟",
    author: "林静溪",
  },
  {
    slug: "mindful-eating-guide",
    title: "正念饮食入门指南",
    excerpt: "放下手机，感受食物的温度与味道。正念饮食教你用五感吃饭，告别情绪性进食。",
    category: "正念冥想",
    date: "2026-07-08",
    readTime: "5 分钟",
    author: "若溪",
  },
  {
    slug: "postpartum-body-mind-recovery",
    title: "产后身心恢复指南",
    excerpt: "产后恢复不仅是身体的重塑，更是心灵的回归。从情绪波动到身体变化，一步步找回自己。",
    category: "女性健康",
    date: "2026-06-27",
    readTime: "5 分钟",
    author: "芷兰",
  },
"""


def patch_blog_listing():
    path = f"{BASE}/src/app/blog/page.tsx"
    with open(path) as f:
        content = f.read()
    if "meditation-for-anxiety-relief" in content:
        LOG.append("Blog listing already has 22 posts")
        return
    content = content.replace(
        'const categories = ["全部", "身体疗愈", "心灵疗愈", "正念冥想", "睡眠科学", "疗愈故事"];',
        'const categories = ["全部", "身体疗愈", "心灵疗愈", "正念冥想", "睡眠科学", "身心疗愈", "女性健康", "疗愈故事"];',
    )
    content = content.replace(
        "const posts = [",
        "const posts = [\n" + MISSING_POSTS,
        1,
    )
    content = content.replace(
        '"疗愈故事": "💫",\n};',
        '"疗愈故事": "💫",\n  "身心疗愈": "🌿",\n  "女性健康": "🌺",\n};',
    )
    write(path, content)


def patch_blog_slug():
    path = f"{BASE}/src/app/blog/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()

    if 'import BlogCta from "@/components/blog-cta"' not in content:
        content = content.replace(
            'import type { Metadata } from "next";',
            'import type { Metadata } from "next";\nimport BlogCta from "@/components/blog-cta";',
        )

    if "application/ld+json" not in content:
        content = content.replace(
            "  return (\n    <div className=\"min-h-screen pt-20\">",
            """  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.excerpt,
    author: { "@type": "Person", name: post.author },
    datePublished: post.date,
    image: "https://zhenxi.hk.cn/og-image.png",
    publisher: {
      "@type": "Organization",
      name: "真汐",
      logo: { "@type": "ImageObject", url: "https://zhenxi.hk.cn/og-image.png" },
    },
    mainEntityOfPage: `https://zhenxi.hk.cn/blog/${slug}`,
  };

  return (
    <div className="min-h-screen pt-20">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />""",
            1,
        )

    old_cta = """          {/* CTA */}
          <div className="mt-12 text-center">
            <div className="rounded-2xl bg-gradient-to-br from-cream via-primary/5 to-mist-light p-8">
              <Heart className="mx-auto mb-3 h-7 w-7 text-primary" fill="#C9A96E" />
              <p className="mb-4 text-lg font-light text-foreground">
                喜欢这篇文章？探索更多疗愈内容
              </p>
              <div className="flex items-center justify-center gap-4">
                <Link
                  href="/services"
                  className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary-dark"
                >
                  浏览指南
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/blog"
                  className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-white px-6 py-2.5 text-sm font-medium text-primary transition-all hover:bg-primary/5"
                >
                  更多文章
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>"""
    if old_cta in content:
        content = content.replace(old_cta, "          <BlogCta />")

    if "openGraph:" not in content.split("generateMetadata")[1].split("export default")[0]:
        content = content.replace(
            """    ...(post ? { alternates: { canonical: `${SITE_URL}/blog/${slug}` } } : {}),
  };""",
            """    ...(post
      ? {
          alternates: { canonical: `${SITE_URL}/blog/${slug}` },
          openGraph: {
            title: post.title,
            description: post.excerpt,
            type: "article",
            url: `${SITE_URL}/blog/${slug}`,
            images: [{ url: `${SITE_URL}/og-image.png` }],
          },
        }
      : {}),
  };""",
        )

    write(path, content)


def patch_assessment_quiz():
    path = f"{BASE}/src/app/assessment/[type]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "EmailCapture" in content or "subscribe" in content:
        LOG.append("Assessment email capture already present")
        return

    content = content.replace(
        '"use client";\n\nimport { useState } from "react";',
        '"use client";\n\nimport { useState, useEffect } from "react";',
    )

    email_capture = textwrap.dedent("""

function EmailCapture({
  assessmentType,
  resultLabel,
}: {
  assessmentType: string;
  resultLabel: string;
}) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined" && (window as unknown as { trackEvent?: (e: string, d?: object) => void }).trackEvent) {
      (window as unknown as { trackEvent: (e: string, d?: object) => void }).trackEvent("assessment_complete", {
        type: assessmentType,
        result: resultLabel,
      });
    }
  }, [assessmentType, resultLabel]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("sending");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          source: "assessment",
          assessmentType,
          resultLabel,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus("sent");
        setMessage(data.message || "报告已发送");
      } else {
        setStatus("error");
        setMessage(data.error || "发送失败");
      }
    } catch {
      setStatus("error");
      setMessage("网络错误，请稍后再试");
    }
  };

  if (status === "sent") {
    return (
      <div className="mt-6 rounded-xl border border-primary/20 bg-primary/5 p-4 text-center text-sm text-primary">
        {message}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 rounded-xl border border-primary/10 bg-cream/30 p-6">
      <h3 className="mb-2 text-sm font-semibold text-foreground">将报告发送到邮箱</h3>
      <p className="mb-4 text-xs text-warm-gray">留下邮箱，我们会把本次评估结果和推荐阅读发给你（无需注册）</p>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          className="flex-1 rounded-lg border border-primary/20 bg-white px-4 py-2.5 text-sm outline-none focus:border-primary"
        />
        <button
          type="submit"
          disabled={status === "sending"}
          data-track-cta="assessment-email"
          className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
        >
          {status === "sending" ? "发送中…" : "发送报告"}
        </button>
      </div>
      {status === "error" && <p className="mt-2 text-xs text-red-500">{message}</p>}
    </form>
  );
}
""")

    content = content.replace(
        "export default function AssessmentQuiz",
        email_capture + "\nexport default function AssessmentQuiz",
    )

    content = content.replace(
        """            </div>
          </div>
          <div className="flex gap-4">
            <Link href="/assessment" className="inline-flex items-center gap-2 rounded-full border border-primary/40 px-6 py-2.5 text-sm text-primary hover:bg-primary/5"><ArrowLeft className="h-4 w-4" />返回评估列表</Link>""",
        """            </div>
            <EmailCapture assessmentType={params.type} resultLabel={result.label} />
          </div>
          <div className="flex gap-4">
            <Link href="/assessment" className="inline-flex items-center gap-2 rounded-full border border-primary/40 px-6 py-2.5 text-sm text-primary hover:bg-primary/5"><ArrowLeft className="h-4 w-4" />返回评估列表</Link>""",
    )

    write(path, content)


FAQ_ASSESSMENT = """
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: "身心评估需要多长时间？",
                acceptedAnswer: { "@type": "Answer", text: "每项评估约 1.5–3 分钟，共 4 项可选评估。" },
              },
              {
                "@type": "Question",
                name: "评估结果准确吗？",
                acceptedAnswer: { "@type": "Answer", text: "评估基于简化版专业量表，仅供自我了解参考，不能替代医疗诊断。" },
              },
              {
                "@type": "Question",
                name: "评估后会有推荐内容吗？",
                acceptedAnswer: { "@type": "Answer", text: "完成评估后会获得个性化推荐阅读，也可选择将报告发送到邮箱。" },
              },
            ],
          }),
        }}
      />
"""


def patch_assessment_faq():
    path = f"{BASE}/src/app/assessment/page.tsx"
    with open(path) as f:
        content = f.read()
    if "FAQPage" in content:
        return
    content = content.replace(
        '    <div className="min-h-screen pt-20">',
        '    <div className="min-h-screen pt-20">' + FAQ_ASSESSMENT,
        1,
    )
    write(path, content)


def patch_services_faq():
    path = f"{BASE}/src/app/services/page.tsx"
    with open(path) as f:
        content = f.read()
    if "FAQPage" in content:
        return
    faq = """
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: "真汐的疗愈指南是付费服务吗？",
                acceptedAnswer: { "@type": "Answer", text: "疗愈指南是免费阅读内容，归于真实，回归自己。" },
              },
              {
                "@type": "Question",
                name: "有哪些疗愈主题？",
                acceptedAnswer: { "@type": "Answer", text: "涵盖肩颈舒缓、睡眠恢复、压力释放、身体恢复、正念陪伴五大主题。" },
              },
            ],
          }),
        }}
      />
"""
    content = content.replace(
        '    <div className="min-h-screen pt-20">',
        '    <div className="min-h-screen pt-20">' + faq,
        1,
    )
    write(path, content)


def patch_tracker():
    path = f"{BASE}/public/tracker.js"
    with open(path) as f:
        content = f.read()
    if "data-track-cta" in content:
        return
    extra = textwrap.dedent("""

  // CTA clicks
  document.addEventListener('click', function(e) {
    var el = e.target.closest('[data-track-cta]');
    if (el) send('cta_click', { cta: el.dataset.trackCta || el.textContent.trim().slice(0, 50) });
  });

  // Public API for custom events (assessment_complete, etc.)
  window.trackEvent = function(event, data) {
    send(event, data || {});
  };
""")
    content = content.rstrip()
    if content.endswith("})();"):
        content = content[:-5] + extra + "\n})();"
    write(path, content)


def rebuild():
    run(f"cd {BASE} && export $(grep DATABASE_URL .env | xargs) && npx prisma generate")
    run(f"cd {BASE} && npm run build")
    run("sudo systemctl restart zhenxi")
    run("sleep 3")
    run("systemctl is-active zhenxi")


def verify():
    run("curl -s https://zhenxi.hk.cn/blog | grep -c 'href=\"/blog/'", check=False)
    run("curl -s https://zhenxi.hk.cn/assessment | grep -c FAQPage", check=False)
    run("curl -s https://zhenxi.hk.cn/blog/shoulder-neck | grep -c '\"@type\":\"Article\"'", check=False)
    run("curl -s https://zhenxi.hk.cn/blog/shoulder-neck | grep -c blog-assessment", check=False)


def main():
    patch_prisma()
    create_blog_cta()
    patch_email_lib()
    create_subscribe_api()
    patch_blog_listing()
    patch_blog_slug()
    patch_assessment_quiz()
    patch_assessment_faq()
    patch_services_faq()
    patch_tracker()
    rebuild()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/zhenxi-p3-growth.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
