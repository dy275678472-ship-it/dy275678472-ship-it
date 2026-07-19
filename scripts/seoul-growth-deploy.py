#!/usr/bin/env python3
"""Seoul server: P1 security + zhenxi/cosgo growth optimizations."""
import os
import subprocess
import textwrap

LOG = []


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:2000])
    if check and r.returncode != 0:
        raise RuntimeError(f"Command failed ({r.returncode}): {cmd}\n{out}")
    return r


def setup_systemd_localhost():
    out = run("sudo ss -tlnp | grep -E '127.0.0.1:300[45]'", check=False).stdout
    if "127.0.0.1:3004" in out and "127.0.0.1:3005" in out:
        LOG.append("Security hardening already applied — skipping")
        return


def upgrade_indexnow():
    path = "/opt/indexnow-submit.sh"
    if os.path.exists(path):
        run(f"sudo sed -i 's/head -10/head -50/g' {path}")
        run("sudo bash /opt/indexnow-submit.sh", check=False)


def patch_zhenxi():
    page = "/opt/zhenxi/src/app/page.tsx"
    with open(page) as f:
        content = f.read()
    if "最新疗愈文章" not in content:
        section = textwrap.dedent("""

      {/* Latest Blog Posts */}
      <section className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 flex items-end justify-between gap-4">
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-primary">LATEST READS</p>
              <h2 className="text-3xl font-light tracking-tight text-foreground md:text-4xl">
                最新<span className="text-primary">疗愈文章</span>
              </h2>
              <p className="mt-2 text-warm-gray">深夜可读 · 循证撰写 · 归于真实</p>
            </div>
            <Link href="/blog" className="hidden text-sm font-medium text-primary hover:text-primary-dark sm:inline-flex sm:items-center sm:gap-1">
              全部文章 <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { slug: "shoulder-neck", title: "肩颈舒缓完全指南", excerpt: "针对久坐伏案导致的肩颈紧张，从成因到实操，一步步释放疲劳与压力。", category: "身体疗愈" },
              { slug: "sleep-recovery", title: "睡眠恢复完全指南", excerpt: "结合芳香疗法与渐进式放松，从神经科学角度解析失眠，重建健康睡眠节律。", category: "睡眠科学" },
              { slug: "stress-release", title: "压力释放指南", excerpt: "通过呼吸训练与正念冥想，学习识别并释放身体中储存的压力与情绪。", category: "心灵疗愈" },
            ].map((post) => (
              <Link key={post.slug} href={`/blog/${post.slug}`} className="group flex flex-col rounded-2xl border border-primary/10 bg-cream/40 p-6 card-hover">
                <span className="text-xs font-medium text-primary">{post.category}</span>
                <h3 className="mt-2 text-lg font-semibold text-foreground group-hover:text-primary">{post.title}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-warm-gray line-clamp-3">{post.excerpt}</p>
                <span className="mt-4 text-xs text-primary">阅读全文 →</span>
              </Link>
            ))}
          </div>
        </div>
      </section>
""")
        marker = '      {/* CTA */}\n      <section className="bg-white py-20">'
        content = content.replace(marker, section + "\n" + marker, 1)
    old_cta = """            <Link
              href="/services"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-3.5 text-base font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary-dark hover:shadow-xl"
            >
              浏览指南
              <ArrowRight className="h-4 w-4" />
            </Link>"""
    new_cta = """            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/assessment" className="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-3.5 text-base font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary-dark hover:shadow-xl">
                3分钟找到你的疗愈方式 <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/blog" className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-white/80 px-8 py-3.5 text-base font-medium text-primary transition-all hover:border-primary hover:bg-white">
                浏览文章
              </Link>
            </div>"""
    if old_cta in content:
        content = content.replace(old_cta, new_cta, 1)
    with open(page, "w") as f:
        f.write(content)
    run("cd /opt/zhenxi && npm run build", check=False)
    run("sudo systemctl restart zhenxi")
    run("systemctl is-active zhenxi")


def patch_cosgo():
    page = "/opt/cosgo/src/app/page.tsx"
    with open(page) as f:
        content = f.read()
    content = content.replace('export const dynamic = "force-dynamic";', 'export const revalidate = 3600;', 1)
    content = content.replace("take: 3,", "take: 6,", 1)
    if "漫展季" not in content:
        banner = textwrap.dedent("""

      <section className="bg-pink-50 border-y border-pink-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-sm text-gray-700"><span className="font-semibold text-[#E91E63]">🎀 漫展季</span> · 全国 194+ 场活动正在更新，出发前先看攻略</p>
          <Link href="/activities" className="inline-flex items-center gap-1 text-sm font-semibold text-[#FF5A8A] hover:text-pink-600 whitespace-nowrap">查看近期漫展 →</Link>
        </div>
      </section>
""")
        marker = '      <section className="relative overflow-hidden bg-gradient-to-br from-gray-900'
        content = content.replace(marker, banner + "\n" + marker, 1)
    with open(page, "w") as f:
        f.write(content)
    run("cd /opt/cosgo && npm run build", check=False)
    run("sudo systemctl restart cosgo")
    run("systemctl is-active cosgo")


def verify_sites():
    for url in ["https://zhenxi.hk.cn", "https://cosgo.cn"]:
        code = run(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", check=False).stdout.strip()
        LOG.append(f"{url} -> {code}")


def main():
    setup_systemd_localhost()
    upgrade_indexnow()
    patch_zhenxi()
    patch_cosgo()
    verify_sites()
    report = "\n".join(LOG)
    with open("/tmp/seoul-growth-deploy.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
