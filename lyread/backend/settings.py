"""集中管理生产配置；敏感值只从环境变量读取。"""
import os

APP_ENV = os.getenv("APP_ENV", "development").lower()
APP_VERSION = os.getenv("APP_VERSION", "1.9.1")


def csv_env(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


ALLOWED_ORIGINS = csv_env(
    "ALLOWED_ORIGINS",
    "http://localhost:5173" if APP_ENV != "production" else "",
)


def database_config() -> dict:
    required = {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"缺少数据库环境变量: {', '.join(missing)}")
    return {**required, "port": int(os.getenv("MYSQL_PORT", "3306"))}


def validate_production_settings() -> None:
    if APP_ENV != "production":
        return
    if not ALLOWED_ORIGINS:
        raise RuntimeError("生产环境必须配置 ALLOWED_ORIGINS")
    if len(os.getenv("JWT_SECRET", "")) < 32:
        raise RuntimeError("生产环境 JWT_SECRET 必须至少 32 个字符")
    database_config()

