#!/usr/bin/env python3
"""P0 SEO fixes for zhenxi.hk.cn on Seoul server."""
import os
import re
import subprocess

LOG = []


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:3000])
    if check and r.returncode != 0:
        raise RuntimeError(f"Command failed ({r.returncode}): {cmd}\n{out}")
    return r


def write(path, content):
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


def patch_start_sh():
    path = "/opt/zhenxi/start.sh"
    with open(path) as f:
        content = f.read()
    if "ln -sf /opt/zhenxi/public public" not in content:
        insert = """if [ ! -e public ]; then
  ln -sf /opt/zhenxi/public public
fi
"""
        content = content.replace(
            "if [ ! -e .next/static ]; then\n  ln -sf /opt/zhenxi/.next/static .next/static\nfi\n",
            "if [ ! -e .next/static ]; then\n  ln -sf /opt/zhenxi/.next/static .next/static\nfi\n"
            + insert,
        )
        write(path, content)
    run("chmod +x /opt/zhenxi/start.sh")


def create_seo_lib():
    write(
        "/opt/zhenxi/src/lib/seo.ts",
        """export const SITE_URL = "https://zhenxi.hk.cn";

/** Per-page canonical URL helper for Next.js metadata */
export function pageCanonical(path: string) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return { alternates: { canonical: `${SITE_URL}${normalized}` } };
}
""",
    )


def patch_layout():
    path = "/opt/zhenxi/src/app/layout.tsx"
    with open(path) as f:
        content = f.read()

    # Remove global canonical and broken /en hreflang
    content = content.replace(
        """  alternates: {
    canonical: "https://zhenxi.hk.cn",
    languages: {
      "zh-CN": "https://zhenxi.hk.cn",
      "x-default": "https://zhenxi.hk.cn",
      en: "https://zhenxi.hk.cn/en",
    },
  },""",
        """  alternates: {
    languages: {
      "zh-CN": "https://zhenxi.hk.cn",
      "x-default": "https://zhenxi.hk.cn",
    },
  },""",
    )

    content = content.replace(
        """                  potentialAction: {
                    "@type": "SearchAction",
                    target: {
                      "@type": "EntryPoint",
                      urlTemplate:
                        "https://zhenxi.hk.cn/search?q={search_term_string}",
                    },
                    "query-input": "required name=search_term_string",
                  },""",
        "",
    )

    content = content.replace(
        'logo: "https://zhenxi.hk.cn/logo.png",',
        'logo: "https://zhenxi.hk.cn/og-image.png",',
    )

    write(path, content)


def add_canonical_to_static_page(path, canonical_path):
    with open(path) as f:
        content = f.read()
    if "alternates:" in content and "canonical" in content:
        return
    if 'from "@/lib/seo"' not in content:
        content = content.replace(
            'import type { Metadata } from "next";',
            'import type { Metadata } from "next";\nimport { pageCanonical } from "@/lib/seo";',
        )
    # Insert pageCanonical into metadata block
    if "export const metadata: Metadata = {" in content:
        content = content.replace(
            "export const metadata: Metadata = {",
            "export const metadata: Metadata = {\n  ...pageCanonical(\"" + canonical_path + "\"),",
            1,
        )
        write(path, content)


def patch_homepage():
    path = "/opt/zhenxi/src/app/page.tsx"
    with open(path) as f:
        content = f.read()
    if "pageCanonical" in content:
        return
    content = content.replace(
        'import Link from "next/link";',
        'import type { Metadata } from "next";\nimport Link from "next/link";\nimport { pageCanonical } from "@/lib/seo";',
    )
    content = content.replace(
        "export const revalidate = 3600;",
        "export const metadata: Metadata = pageCanonical(\"/\");\n\nexport const revalidate = 3600;",
    )
    write(path, content)


def patch_contact_layout():
    path = "/opt/zhenxi/src/app/contact/layout.tsx"
    if os.path.exists(path):
        return
    write(
        path,
        """import type { Metadata } from "next";
import { pageCanonical } from "@/lib/seo";

export const metadata: Metadata = {
  title: "深夜信箱 — 写给真汐的一封信 | 真汐",
  description:
    "在深夜写下你的心事。真汐是一座安静的邮箱——你投递，我们封存。写下来本身，就是一种疗愈。",
  ...pageCanonical("/contact"),
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
""",
    )


def patch_blog_slug_metadata():
    path = "/opt/zhenxi/src/app/blog/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "alternates:" in content:
        return
    if 'from "@/lib/seo"' not in content:
        content = content.replace(
            'import type { Metadata } from "next";',
            'import type { Metadata } from "next";\nimport { SITE_URL } from "@/lib/seo";',
        )
    content = content.replace(
        """  return {
    title: post
      ? `${post.title} — 真汐疗愈指南`
      : "文章未找到 — 真汐",
    description: post?.excerpt || "探索女性身心疗愈的深度内容，归于真实，回归自己。",
  };""",
        """  return {
    title: post
      ? `${post.title} — 真汐疗愈指南`
      : "文章未找到 — 真汐",
    description: post?.excerpt || "探索女性身心疗愈的深度内容，归于真实，回归自己。",
    ...(post ? { alternates: { canonical: `${SITE_URL}/blog/${slug}` } } : {}),
  };""",
    )
    write(path, content)


def patch_city_metadata():
    path = "/opt/zhenxi/src/app/city/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "alternates:" in content:
        return
    content = content.replace(
        '    robots: { index: true, follow: true },\n  };',
        '    robots: { index: true, follow: true },\n    alternates: { canonical: `https://zhenxi.hk.cn/city/${slug}` },\n  };',
    )
    write(path, content)


def patch_assessment_type_metadata():
    path = "/opt/zhenxi/src/app/assessment/[type]/layout.tsx"
    with open(path) as f:
        content = f.read()
    if "alternates:" in content:
        return
    content = content.replace(
        """  return {
    title: TITLES[type] || "身心评估 | 真汐",
  };""",
        """  return {
    title: TITLES[type] || "身心评估 | 真汐",
    alternates: { canonical: `https://zhenxi.hk.cn/assessment/${type}` },
  };""",
    )
    write(path, content)


def patch_journal_slug_metadata():
    path = "/opt/zhenxi/src/app/journal/[slug]/page.tsx"
    with open(path) as f:
        content = f.read()
    if "alternates:" in content and "canonical" in content:
        return
    content = content.replace(
        """    openGraph: {
      title: journal.title,
      description: journal.excerpt,
      type: "article",
    },
  };""",
        """    openGraph: {
      title: journal.title,
      description: journal.excerpt,
      type: "article",
    },
    alternates: { canonical: `https://zhenxi.hk.cn/journal/${slug}` },
  };""",
    )
    write(path, content)


def patch_nginx():
    nginx = "/etc/nginx/sites-enabled/traffic-override.conf"
    with open(nginx) as f:
        content = f.read()
    block = """
    location = /sitemap.xml {
        root /opt/zhenxi/public;
        try_files /sitemap.xml =404;
        add_header Cache-Control "public, max-age=3600";
        default_type application/xml;
    }
    location = /og-image.png {
        root /opt/zhenxi/public;
        try_files /og-image.png =404;
        add_header Cache-Control "public, max-age=86400";
    }
"""
    if "location = /sitemap.xml" not in content:
        content = content.replace(
            "    location = /llms-full.txt {\n"
            "        root /opt/zhenxi/public;\n"
            "        try_files $uri =404;\n"
            "        add_header Cache-Control \"public, max-age=3600\";\n"
            "    }\n",
            "    location = /llms-full.txt {\n"
            "        root /opt/zhenxi/public;\n"
            "        try_files $uri =404;\n"
            "        add_header Cache-Control \"public, max-age=3600\";\n"
            "    }\n"
            + block,
        )
        write("/tmp/traffic-override.conf", content)
        run("sudo cp /tmp/traffic-override.conf " + nginx)
        run("sudo nginx -t")
        run("sudo systemctl reload nginx")


def rebuild_and_verify():
    run("cd /opt/zhenxi && npm run build")
    run("sudo systemctl restart zhenxi")
    run("sleep 3")
    run("systemctl is-active zhenxi")

    checks = [
        ("sitemap", "curl -s -o /dev/null -w '%{http_code}' https://zhenxi.hk.cn/sitemap.xml"),
        ("og-image", "curl -s -o /dev/null -w '%{http_code}' https://zhenxi.hk.cn/og-image.png"),
        ("blog-canonical", "curl -s https://zhenxi.hk.cn/blog | grep -o 'canonical\" href=\"[^\"]*\"' | head -1"),
        ("home-canonical", "curl -s https://zhenxi.hk.cn/ | grep -o 'canonical\" href=\"[^\"]*\"' | head -1"),
        ("no-en-hreflang", "curl -s https://zhenxi.hk.cn/ | grep -c 'zhenxi.hk.cn/en' || true"),
    ]
    for name, cmd in checks:
        r = run(cmd, check=False)
        LOG.append(f"VERIFY {name}: {r.stdout.strip()}")


def main():
    patch_start_sh()
    create_seo_lib()
    patch_layout()
    patch_homepage()
    patch_contact_layout()

    static_pages = [
        ("/opt/zhenxi/src/app/about/page.tsx", "/about"),
        ("/opt/zhenxi/src/app/blog/page.tsx", "/blog"),
        ("/opt/zhenxi/src/app/services/page.tsx", "/services"),
        ("/opt/zhenxi/src/app/assessment/page.tsx", "/assessment"),
        ("/opt/zhenxi/src/app/healers/page.tsx", "/healers"),
        ("/opt/zhenxi/src/app/partners/page.tsx", "/partners"),
    ]
    for path, canonical in static_pages:
        add_canonical_to_static_page(path, canonical)

    patch_blog_slug_metadata()
    patch_city_metadata()
    patch_assessment_type_metadata()
    patch_journal_slug_metadata()
    patch_nginx()
    rebuild_and_verify()

    report = "\n".join(LOG)
    with open("/tmp/zhenxi-p0-seo.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
