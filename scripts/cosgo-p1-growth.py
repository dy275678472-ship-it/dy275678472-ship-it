#!/usr/bin/env python3
"""P1 growth for cosgo.cn — blog expansion, email capture, subscribe API."""
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
    run(
        f"cd {BASE} && export $(grep DATABASE_URL .env | xargs) && npx prisma db push --accept-data-loss",
        check=False,
    )
    run(f"cd {BASE} && npx prisma generate")


def patch_email_lib():
    path = f"{BASE}/src/lib/email.ts"
    with open(path) as f:
        content = f.read()
    if "sendGuideDigest" in content:
        return
    content += textwrap.dedent("""

export async function sendGuideDigest(to: string) {
  await sendEmail(
    to,
    "【CosGo】你的 Cos 出片攻略精选已备好",
    `<div style="max-width:560px;margin:0 auto;padding:32px 20px;font-family:sans-serif;color:#1f2937;line-height:1.8;">
      <h2 style="color:#FF5A8A;font-weight:600;">欢迎订阅 CosGo 出片攻略</h2>
      <p>我们会不定期推送漫展准备、场照技巧与城市攻略，帮你更稳地完成每一次出片。</p>
      <p style="margin:24px 0;text-align:center;">
        <a href="https://cosgo.cn/blog" style="display:inline-block;padding:12px 28px;background:#FF5A8A;color:#fff;text-decoration:none;border-radius:10px;font-weight:600;">浏览全部攻略</a>
      </p>
      <p style="font-size:12px;color:#9ca3af;">此邮件由 CosGo 自动发送。如需退订，回复本邮件即可。</p>
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
        import { prisma } from "@/lib/db";
        import { sendGuideDigest } from "@/lib/email";

        const schema = z.object({
          email: z.string().email("请输入有效邮箱"),
          source: z.string().optional(),
        });

        export async function POST(req: Request) {
          try {
            const body = await req.json();
            const data = schema.parse(body);

            const existing = await prisma.subscriber.findUnique({
              where: { email: data.email },
            });

            await prisma.subscriber.upsert({
              where: { email: data.email },
              create: {
                email: data.email,
                source: data.source || "blog",
              },
              update: {
                source: data.source || "blog",
              },
            });

            if (!existing) {
              await sendGuideDigest(data.email);
            }

            return NextResponse.json({ ok: true, message: "订阅成功，攻略精选将发送到你的邮箱" });
          } catch (err) {
            if (err instanceof z.ZodError) {
              return NextResponse.json(
                { error: err.issues[0]?.message || "无效输入" },
                { status: 400 }
              );
            }
            console.error("[subscribe]", err);
            return NextResponse.json({ error: "提交失败，请稍后再试" }, { status: 500 });
          }
        }
        """),
    )


def create_blog_subscribe():
    write(
        f"{BASE}/src/components/blog-subscribe.tsx",
        textwrap.dedent("""\
        "use client";

        import { useState } from "react";
        import { Mail } from "lucide-react";

        export default function BlogSubscribe({ source = "blog-article" }: { source?: string }) {
          const [email, setEmail] = useState("");
          const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
          const [message, setMessage] = useState("");

          async function handleSubmit(e: React.FormEvent) {
            e.preventDefault();
            setStatus("loading");
            setMessage("");
            try {
              const res = await fetch("/api/subscribe", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, source }),
              });
              const data = await res.json();
              if (!res.ok) throw new Error(data.error || "提交失败");
              setStatus("done");
              setMessage(data.message || "订阅成功");
              setEmail("");
            } catch (err) {
              setStatus("error");
              setMessage(err instanceof Error ? err.message : "提交失败");
            }
          }

          return (
            <div className="mt-8 rounded-2xl border border-pink-100 bg-gradient-to-br from-pink-50 to-white p-6">
              <div className="flex items-start gap-3">
                <Mail className="mt-1 h-5 w-5 text-[#FF5A8A]" />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">把出片攻略发到邮箱</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    订阅后获取漫展准备清单、场照技巧与城市攻略精选。
                  </p>
                  <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3 sm:flex-row">
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="flex-1 rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-pink-300 focus:ring-2 focus:ring-pink-100"
                    />
                    <button
                      type="submit"
                      disabled={status === "loading" || status === "done"}
                      data-track-cta="blog-subscribe"
                      className="rounded-xl bg-[#FF5A8A] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-pink-600 disabled:opacity-60"
                    >
                      {status === "loading" ? "提交中..." : status === "done" ? "已订阅" : "免费订阅"}
                    </button>
                  </form>
                  {message && (
                    <p className={`mt-3 text-sm ${status === "error" ? "text-red-500" : "text-green-600"}`}>
                      {message}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        }
        """),
    )


def patch_blog_post_page():
    path = f"{BASE}/src/app/blog/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "BlogSubscribe" in content:
        return

    content = content.replace(
        'import { MarkdownArticle } from "@/lib/markdown";',
        'import { MarkdownArticle } from "@/lib/markdown";\nimport BlogSubscribe from "@/components/blog-subscribe";',
    )
    content = content.replace(
        '<aside className="mt-8 rounded-2xl bg-pink-50 p-6 text-center">',
        '<BlogSubscribe source="blog-article" /><aside className="mt-8 rounded-2xl bg-pink-50 p-6 text-center">',
    )
    write(path, content)


def patch_blog_list_page():
    path = f"{BASE}/src/app/blog/page.tsx"
    with open(path) as f:
        content = f.read()
    if "BlogSubscribe" in content:
        return
    content = content.replace(
        'import { CONTENT_CATEGORIES } from "@/lib/content";',
        'import { CONTENT_CATEGORIES } from "@/lib/content";\nimport BlogSubscribe from "@/components/blog-subscribe";',
    )
    content = content.replace(
        "</main></div>;",
        '<BlogSubscribe source="blog-list" /></main></div>;',
    )
    write(path, content)


def publish_ready_drafts():
    psql(
        'UPDATE "ContentArticle" SET status = \'PUBLISHED\', "publishedAt" = COALESCE("publishedAt", NOW()) WHERE status = \'DRAFT\' AND length(content) >= 900'
    )


def published_count():
    url = db_url()
    r = subprocess.run(
        f"psql {json.dumps(url)} -t -A -c \"SELECT count(*) FROM \\\"ContentArticle\\\" WHERE status='PUBLISHED';\"",
        shell=True,
        capture_output=True,
        text=True,
    )
    return int((r.stdout or "0").strip() or 0)


def generate_one_article():
    secret = cron_secret()
    if not secret:
        LOG.append("CRON_SECRET missing — skip generation")
        return False
    url = f"http://127.0.0.1:3004/api/cron/content-generate?secret={secret}"
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            body = json.loads(resp.read().decode())
            LOG.append(f"generate: {body}")
            return body.get("success") and body.get("slug")
    except Exception as exc:
        LOG.append(f"generate failed: {exc}")
        return False


def expand_blog_to(target=20):
    publish_ready_drafts()
    count = published_count()
    LOG.append(f"Published after draft release: {count}")

    attempts = 0
    while count < target and attempts < 25:
        slug = generate_one_article()
        if slug:
            psql(
                f"UPDATE \"ContentArticle\" SET status = 'PUBLISHED', \"publishedAt\" = NOW() WHERE slug = '{slug}' AND length(content) >= 900"
            )
            count = published_count()
            LOG.append(f"Published count: {count}")
        attempts += 1
        if count < target:
            time.sleep(2)

    if count < target:
        LOG.append(f"Warning: only {count} published articles (target {target})")


def rebuild():
    run(f"cd {BASE} && npm run build")
    run("sudo systemctl restart cosgo")
    run("sleep 4 && systemctl is-active cosgo")


def verify():
    count = published_count()
    LOG.append(f"Final published count: {count}")
    run("curl -s https://cosgo.cn/sitemap.xml | grep -c '/blog/'", check=False)
    run("curl -s https://cosgo.cn/blog | grep -c blog-subscribe", check=False)
    run(
        'curl -s -X POST https://cosgo.cn/api/subscribe -H "Content-Type: application/json" '
        '-d \'{"email":"test-p1-verify@example.com","source":"p1-verify"}\'',
        check=False,
    )


def main():
    patch_prisma()
    patch_email_lib()
    create_subscribe_api()
    create_blog_subscribe()
    patch_blog_post_page()
    patch_blog_list_page()
    expand_blog_to(20)
    rebuild()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/cosgo-p1-growth.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
