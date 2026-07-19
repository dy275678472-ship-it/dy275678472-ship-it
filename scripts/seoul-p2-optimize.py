#!/usr/bin/env python3
"""P2 server optimization for Seoul node: memory, nginx cache, PM2 cleanup."""
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


def remove_stale_pm2_cosgo():
    """Root PM2 cosgo points at /data/www/cosgo and crash-loops; cosgo runs via systemd."""
    r = run("sudo pm2 list 2>/dev/null | grep -c cosgo || true", check=False)
    if r.stdout.strip() != "0":
        run("sudo pm2 delete cosgo 2>/dev/null || true", check=False)
        run("sudo pm2 save", check=False)
        LOG.append("Removed stale root PM2 cosgo process")


def tune_swappiness():
  run("grep -q '^vm.swappiness' /etc/sysctl.d/99-seoul-tuning.conf 2>/dev/null || "
      "echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-seoul-tuning.conf")
  run("sudo sysctl -p /etc/sysctl.d/99-seoul-tuning.conf")
  run("cat /proc/sys/vm/swappiness")


def patch_nginx_zhenxi_cache():
    nginx = "/etc/nginx/sites-enabled/traffic-override.conf"
    with open(nginx) as f:
        content = f.read()

    static_block = """
    location ^~ /_next/static/ {
        proxy_pass http://127.0.0.1:3005;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    location ~* \\.(jpg|jpeg|png|gif|webp|svg|ico|woff2?|ttf|eot)$ {
        proxy_pass http://127.0.0.1:3005;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=604800, immutable";
    }
"""
    marker = "    location /v2ray {\n        proxy_pass http://127.0.0.1:10086;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n        proxy_set_header Host $host;\n        proxy_read_timeout 86400s;\n        proxy_send_timeout 86400s;\n    }\n\n    location / {"
    zhenxi_start = content.find("# 6. zhenxi.hk.cn")
    zhenxi_end = content.find("# 7. g.zhenxi.hk.cn")
    zhenxi_block = content[zhenxi_start:zhenxi_end]

    if "location ^~ /_next/static/" not in zhenxi_block:
        new_zhenxi = zhenxi_block.replace(
            "    location /v2ray {\n        proxy_pass http://127.0.0.1:10086;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n        proxy_set_header Host $host;\n        proxy_read_timeout 86400s;\n        proxy_send_timeout 86400s;\n    }\n\n    location / {",
            "    location /v2ray {\n        proxy_pass http://127.0.0.1:10086;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n        proxy_set_header Host $host;\n        proxy_read_timeout 86400s;\n        proxy_send_timeout 86400s;\n    }\n"
            + static_block
            + "\n    location / {",
            1,
        )
        content = content[:zhenxi_start] + new_zhenxi + content[zhenxi_end:]

    content = content.replace(
        'add_header Cache-Control "public, max-age=3600";\n        proxy_pass http://127.0.0.1:3005;',
        'add_header Cache-Control "public, s-maxage=3600, stale-while-revalidate=86400" always;\n        proxy_pass http://127.0.0.1:3005;',
        1,
    )

    with open("/tmp/traffic-override.conf", "w") as f:
        f.write(content)
    run("sudo cp /tmp/traffic-override.conf " + nginx)
    run("sudo nginx -t")
    run("sudo systemctl reload nginx")


def verify():
    run("free -h | head -3")
    run("cat /proc/sys/vm/swappiness")
    run("sudo pm2 list 2>/dev/null | head -10 || true", check=False)
    run("curl -sI https://zhenxi.hk.cn/_next/static/ 2>/dev/null | head -5 || true", check=False)
    run("curl -s -o /dev/null -w 'zhenxi TTFB: %{time_starttransfer}s\\n' https://zhenxi.hk.cn", check=False)
    run("curl -s -o /dev/null -w 'cosgo TTFB: %{time_starttransfer}s\\n' https://cosgo.cn", check=False)


def main():
    remove_stale_pm2_cosgo()
    tune_swappiness()
    patch_nginx_zhenxi_cache()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/seoul-p2-optimize.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
