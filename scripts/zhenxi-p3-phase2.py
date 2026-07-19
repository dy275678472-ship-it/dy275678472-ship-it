#!/usr/bin/env python3
"""P3 phase 2: IndexNow, after2am hardening, analytics, monetization, backups."""
import subprocess
import textwrap

LOG = []
BASE = "/opt/zhenxi"
ZHENXI_INDEXNOW_KEY = "2fe69684fa3d13c08fc930bf444f295a"


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


def fix_indexnow_key():
    write(f"{BASE}/public/{ZHENXI_INDEXNOW_KEY}.txt", ZHENXI_INDEXNOW_KEY + "\n")
    nginx = "/etc/nginx/sites-enabled/traffic-override.conf"
    with open(nginx) as f:
        content = f.read()
    block = f"""
    location = /{ZHENXI_INDEXNOW_KEY}.txt {{
        root /opt/zhenxi/public;
        try_files /{ZHENXI_INDEXNOW_KEY}.txt =404;
        add_header Cache-Control "public, max-age=86400";
    }}
"""
    zhenxi_start = content.find("# 6. zhenxi.hk.cn")
    zhenxi_end = content.find("# 7. g.zhenxi.hk.cn")
    zhenxi = content[zhenxi_start:zhenxi_end]
    if ZHENXI_INDEXNOW_KEY not in zhenxi:
        zhenxi = zhenxi.replace(
            "    location = /sitemap.xml {",
            block + "\n    location = /sitemap.xml {",
            1,
        )
        content = content[:zhenxi_start] + zhenxi + content[zhenxi_end:]
        write("/tmp/traffic-override.conf", content)
        run("sudo cp /tmp/traffic-override.conf " + nginx)
        run("sudo nginx -t")
        run("sudo systemctl reload nginx")
    run(f"curl -s https://zhenxi.hk.cn/{ZHENXI_INDEXNOW_KEY}.txt", check=False)


def fix_after2am_localhost():
    override = "/etc/systemd/system/after2am.service.d/localhost.conf"
    desired = textwrap.dedent("""\
    [Service]
    Environment=HOSTNAME=127.0.0.1
    ExecStart=
    ExecStart=/data/www/after2am/frontend/node_modules/.bin/next start -H 127.0.0.1 -p 3003
    """)
    write("/tmp/after2am-localhost.conf", desired)
    run("sudo mkdir -p /etc/systemd/system/after2am.service.d")
    run("sudo cp /tmp/after2am-localhost.conf " + override)
    run("sudo systemctl daemon-reload")
    run("sudo systemctl restart after2am")
    run("sleep 3")
    run("ss -tlnp | grep 3003", check=False)


def patch_tracker_scroll():
    path = f"{BASE}/public/tracker.js"
    with open(path) as f:
        content = f.read()
    if "blog_read_50pct" in content:
        return
    extra = textwrap.dedent("""

  // Scroll depth: 50% on blog pages
  if (window.location.pathname.indexOf('/blog/') === 0) {
    var fired50 = false;
    window.addEventListener('scroll', function() {
      if (fired50) return;
      var doc = document.documentElement;
      var pct = (window.scrollY + window.innerHeight) / doc.scrollHeight;
      if (pct >= 0.5) {
        fired50 = true;
        send('blog_read_50pct', { page: window.location.pathname });
      }
    }, { passive: true });
  }
""")
    content = content.replace(
        "  window.trackEvent = function(event, data) {",
        extra + "\n  window.trackEvent = function(event, data) {",
    )
    write(path, content)


def patch_assessment_quiz_schema_and_afdian():
    layout_path = f"{BASE}/src/app/assessment/[type]/layout.tsx"
    with open(layout_path) as f:
        layout = f.read()
    if "application/ld+json" not in layout:
        layout = layout.replace(
            "export default function AssessmentLayout({ children }: { children: React.ReactNode }) {\n  return <>{children}</>;\n}",
            textwrap.dedent("""\
            export default async function AssessmentLayout({
              children,
              params,
            }: {
              children: React.ReactNode;
              params: Promise<{ type: string }>;
            }) {
              const { type } = await params;
              const title = TITLES[type] || "身心评估 | 真汐";
              const schema = {
                "@context": "https://schema.org",
                "@type": "Quiz",
                name: title,
                url: `https://zhenxi.hk.cn/assessment/${type}`,
                educationalLevel: "Beginner",
                provider: { "@type": "Organization", name: "真汐", url: "https://zhenxi.hk.cn" },
              };
              return (
                <>
                  <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
                  />
                  {children}
                </>
              );
            }
            """),
        )
        write(layout_path, layout)

    page_path = f"{BASE}/src/app/assessment/[type]/page.tsx"
    with open(page_path) as f:
        content = f.read()
    if "afdian.com" not in content:
        afdian = """
            <div className="mt-6 rounded-xl border border-primary/10 bg-white p-5 text-center">
              <p className="mb-3 text-sm text-warm-gray">真汐由爱发电支持，你的打赏让我们能持续创作</p>
              <a
                href="https://afdian.com/a/zhenxi"
                target="_blank"
                rel="noopener noreferrer"
                data-track-cta="assessment-afdian"
                className="inline-flex items-center gap-2 rounded-full border border-primary/30 px-5 py-2 text-sm font-medium text-primary hover:bg-primary/5"
              >
                支持真汐 · 爱发电
              </a>
            </div>"""
        content = content.replace(
            "            <EmailCapture assessmentType={params.type} resultLabel={result.label} />",
            "            <EmailCapture assessmentType={params.type} resultLabel={result.label} />" + afdian,
        )
        write(page_path, content)


def patch_homepage_crosspromo():
    path = f"{BASE}/src/app/page.tsx"
    with open(path) as f:
        content = f.read()
    if "cosgo.cn/activities" in content:
        return
    banner = textwrap.dedent("""

      <section className="border-y border-primary/10 bg-mist-light/40 py-3">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-6 text-center sm:flex-row sm:text-left">
          <p className="text-sm text-warm-gray">
            <span className="font-medium text-foreground">姐妹站推荐</span>
            · cosgo 漫展季 194+ 场活动攻略更新中
          </p>
          <a
            href="https://cosgo.cn/activities"
            target="_blank"
            rel="noopener noreferrer"
            data-track-cta="crosspromo-cosgo"
            className="text-sm font-medium text-primary hover:text-primary-dark"
          >
            查看近期漫展 →
          </a>
        </div>
      </section>
""")
    content = content.replace(
        "      </section>\n\n      {/* Advantages */}",
        "      </section>\n" + banner + "\n      {/* Advantages */}",
        1,
    )
    if "cosgo.cn/activities" not in content:
        content = content.replace(
            '      <section className="bg-white py-20">\n        <div className="mx-auto max-w-7xl px-6">\n          <div className="mb-12 text-center">',
            banner + '\n      <section className="bg-white py-20">\n        <div className="mx-auto max-w-7xl px-6">\n          <div className="mb-12 text-center">',
            1,
        )
    write(path, content)


def patch_blog_cta_email():
    path = f"{BASE}/src/components/blog-cta.tsx"
    with open(path) as f:
        content = f.read()
    if "BlogEmailCapture" in content:
        return
    # Keep server component - add link to assessment only, email stays on assessment
    # Add newsletter hint linking to assessment
    content = content.replace(
        '<p className="mb-6 text-sm text-warm-gray">3 分钟测评，获取专属疗愈建议</p>',
        '<p className="mb-6 text-sm text-warm-gray">3 分钟测评，获取专属疗愈建议 · 完成后可接收邮件报告</p>',
    )
    write(path, content)


def setup_backup_cron():
    write(
        "/opt/scripts/daily-backup.sh",
        textwrap.dedent("""\
        #!/bin/bash
        set -euo pipefail
        DIR=/opt/backups/$(date +%Y%m%d)
        mkdir -p "$DIR"
        sudo -u ubuntu bash -c 'set -a; source /opt/zhenxi/.env; set +a; pg_dump "${DATABASE_URL%%\?*}" | gzip' > "$DIR/zhenxi-pg.sql.gz"
        mysqldump --all-databases 2>/dev/null | gzip > "$DIR/mysql-all.sql.gz" || true
        find /opt/backups -maxdepth 1 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
        chown -R ubuntu:ubuntu /opt/backups
        echo "$(date) backup done -> $DIR"
        """),
    )
    run("sudo chmod +x /opt/scripts/daily-backup.sh")
    cron_line = "0 3 * * * /opt/scripts/daily-backup.sh >> /var/log/seoul-backup.log 2>&1"
    run(f'(sudo crontab -l 2>/dev/null | grep -v daily-backup; echo "{cron_line}") | sudo crontab -', check=False)
    run("sudo mkdir -p /opt/backups && sudo /opt/scripts/daily-backup.sh", check=False)


def run_indexnow():
    run("sudo sed -i 's/head -50/head -80/g' /opt/indexnow-submit.sh", check=False)
    run("sudo bash /opt/indexnow-submit.sh", check=False)
    run("tail -5 /var/log/indexnow.log", check=False)


def rebuild():
    run(f"cd {BASE} && export $(grep DATABASE_URL .env | xargs) && npx prisma generate")
    run(f"cd {BASE} && npm run build")
    run("sudo systemctl restart zhenxi")
    run("sleep 3 && systemctl is-active zhenxi")


def verify():
    run(f"curl -s -o /dev/null -w '%{{http_code}}' https://zhenxi.hk.cn/{ZHENXI_INDEXNOW_KEY}.txt", check=False)
    run("ss -tlnp | grep 3003", check=False)
    run("curl -s https://zhenxi.hk.cn/ | grep -c crosspromo-cosgo", check=False)
    run("curl -s https://zhenxi.hk.cn/assessment | grep -c FAQPage", check=False)


def main():
    fix_indexnow_key()
    fix_after2am_localhost()
    patch_tracker_scroll()
    patch_assessment_quiz_schema_and_afdian()
    patch_homepage_crosspromo()
    patch_blog_cta_email()
    setup_backup_cron()
    rebuild()
    run_indexnow()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/zhenxi-p3-phase2.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
