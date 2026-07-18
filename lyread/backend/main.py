"""
V1.9 流量自进化系统 - 核心入口
🧠 内容-流量自进化系统 (Content Intelligence Loop)
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api import behavior, hot_model, evolution, seo, scheduler, story, auth, seo_page, stats, creator, credits, cases, orders, admin
from settings import ALLOWED_ORIGINS, APP_ENV, APP_VERSION, validate_production_settings
from api.auth import get_current_user

app = FastAPI(
    title="LyRead V1.9 流量自进化系统",
    description="🧠 AI内容智能循环系统 - 自动学习+自动优化",
    version=APP_VERSION,
    docs_url=None if APP_ENV == "production" else "/docs",
    redoc_url=None if APP_ENV == "production" else "/redoc",
    openapi_url=None if APP_ENV == "production" else "/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 注册路由
app.include_router(behavior.router, prefix="/behavior", tags=["行为采集"])
app.include_router(hot_model.router, prefix="/hot", tags=["爆款识别"], dependencies=[Depends(get_current_user)])
app.include_router(evolution.router, prefix="/evolution", tags=["内容进化"], dependencies=[Depends(get_current_user)])
app.include_router(seo.router, prefix="/seo", tags=["SEO自进化"], dependencies=[Depends(get_current_user)])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(scheduler.router, prefix="/scheduler", tags=["调度器"], dependencies=[Depends(get_current_user)])
app.include_router(story.router, prefix="/api/story", tags=["创作中心"])
# 统计 / 创作者中心（接口内部按需鉴权）
app.include_router(stats.router, prefix="/api/stats", tags=["统计"])
app.include_router(creator.router, prefix="/api/creator", tags=["创作者中心"])
app.include_router(credits.router, prefix="/api/credits", tags=["点数计费"])
app.include_router(cases.router, prefix="/api/cases", tags=["案例阅读"])
app.include_router(orders.router, prefix="/api/orders", tags=["充值订单"])
app.include_router(admin.router, prefix="/api/admin", tags=["运营后台"])
app.include_router(seo_page.router, prefix="", tags=["SEO落地页"])

# 前端统一使用 /api 前缀；保留上面的旧路径，避免破坏已有调用。
app.include_router(behavior.router, prefix="/api/behavior", include_in_schema=False)
app.include_router(hot_model.router, prefix="/api/hot", include_in_schema=False, dependencies=[Depends(get_current_user)])
app.include_router(evolution.router, prefix="/api/evolution", include_in_schema=False, dependencies=[Depends(get_current_user)])
app.include_router(seo.router, prefix="/api/seo", include_in_schema=False, dependencies=[Depends(get_current_user)])
app.include_router(scheduler.router, prefix="/api/scheduler", include_in_schema=False, dependencies=[Depends(get_current_user)])


# 启动进化调度器
@app.on_event("startup")
async def startup_event():
    """启动时初始化并（按配置）自动开启调度器"""
    validate_production_settings()
    try:
        from evolution.evolution_scheduler import start_if_enabled
        start_if_enabled()
    except Exception as exc:
        print(f"[Startup] 调度器初始化失败(不影响主服务): {type(exc).__name__}: {exc}")
    try:
        import mysql.connector
        from settings import database_config
        from services.story_cleanup import sweep_stale_jobs
        conn = mysql.connector.connect(**database_config())
        c = conn.cursor(dictionary=True)
        n = sweep_stale_jobs(c)
        conn.commit()
        conn.close()
        if n:
            print(f"[Startup] 已清理 {n} 个超时生成任务并退款")
    except Exception as exc:
        print(f"[Startup] 任务清理跳过: {type(exc).__name__}: {exc}")


@app.get("/")
def root():
    """系统状态"""
    return {
        "system": "LyRead V1.9 流量自进化系统",
        "status": "🧠 running",
        "version": APP_VERSION,
        "core": "Content Intelligence Loop",
        "capabilities": [
            "用户行为采集",
            "爆款AI识别", 
            "内容自动进化",
            "SEO自学习",
            "标题自进化",
            "流量自动放大"
        ]
    }


@app.get("/health/live")
def liveness():
    return {"status": "ok", "version": APP_VERSION}


@app.get("/health/config")
def config_status():
    """非敏感配置状态，供运维巡检。"""
    import os
    from services.email import smtp_status
    from services.alipay import is_configured as alipay_configured

    return {
        "version": APP_VERSION,
        "env": APP_ENV,
        "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
        "smtp": smtp_status(),
        "alipay": {
            "configured": alipay_configured(),
            "sandbox": os.getenv("ALIPAY_SANDBOX", "0") == "1",
            "notify_url": os.getenv("ALIPAY_NOTIFY_URL", "https://lyread.cn/api/orders/alipay/notify"),
        },
        "auto_evolution": os.getenv("AUTO_EVOLUTION", "0") == "1",
        "expose_reset_token": os.getenv("EXPOSE_RESET_TOKEN", "0") == "1",
    }


@app.get("/health/ready")
def readiness():
    conn = auth.get_db()
    if not conn:
        raise HTTPException(status_code=503, detail="服务尚未就绪")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return {"status": "ready", "version": APP_VERSION}
    except Exception:
        raise HTTPException(status_code=503, detail="服务尚未就绪")
    finally:
        if conn.is_connected():
            conn.close()


@app.get("/health")
def health():
    return readiness()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
