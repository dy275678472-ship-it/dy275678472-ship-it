"""SMTP 邮件发送（找回密码等通知）。"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_FROM"))


def smtp_status() -> dict:
    """返回 SMTP 配置状态（不含密钥）。"""
    return {
        "configured": smtp_configured(),
        "host": os.getenv("SMTP_HOST") or None,
        "port": int(os.getenv("SMTP_PORT", "587")),
        "from": os.getenv("SMTP_FROM") or None,
        "user_set": bool(os.getenv("SMTP_USER")),
        "password_set": bool(os.getenv("SMTP_PASSWORD")),
        "ssl_mode": os.getenv("SMTP_SSL", "0") == "1",
    }


def _site_url() -> str:
    return os.getenv("SITE_URL", "https://lyread.cn").rstrip("/")


def _smtp_connect(host: str, port: int, use_ssl: bool):
    if use_ssl:
        return smtplib.SMTP_SSL(host, port, timeout=15)
    return smtplib.SMTP(host, port, timeout=15)


def send_email(to: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """发送邮件；未配置 SMTP 时返回 False。"""
    if not smtp_configured():
        return False
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_addr = os.getenv("SMTP_FROM", "")
    use_ssl = os.getenv("SMTP_SSL", "0") == "1"
    use_tls = os.getenv("SMTP_TLS", "1") != "0" and not use_ssl

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    with _smtp_connect(host, port, use_ssl) as server:
        if use_tls:
            server.starttls()
        if user and password:
            server.login(user, password)
        server.sendmail(from_addr, [to], msg.as_string())
    return True


def send_password_reset_email(to: str, reset_path: str, token: str) -> bool:
    url = f"{_site_url()}{reset_path}"
    subject = "LyRead 密码重置"
    text = (
        f"您好，\n\n"
        f"您申请了 LyRead 账号密码重置。请点击以下链接设置新密码（1 小时内有效）：\n\n"
        f"{url}\n\n"
        f"如非本人操作，请忽略此邮件。\n"
    )
    html = (
        f"<p>您好，</p>"
        f"<p>您申请了 LyRead 账号密码重置。请点击以下链接设置新密码（1 小时内有效）：</p>"
        f'<p><a href="{url}">{url}</a></p>'
        f"<p>如非本人操作，请忽略此邮件。</p>"
    )
    return send_email(to, subject, text, html)
