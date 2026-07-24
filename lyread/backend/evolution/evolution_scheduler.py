"""
Evolution Scheduler — 基于 APScheduler 的后台自动进化调度。
在应用启动时按 EVOLUTION_INTERVAL_SECONDS 周期性调用 scheduler.execute_cycle()。
可通过 AUTO_EVOLUTION=0 关闭自动启动。
"""

import os

from apscheduler.schedulers.background import BackgroundScheduler

_scheduler: BackgroundScheduler | None = None
_JOB_ID = "evolution_cycle"


def _run_cycle_safe():
    """APScheduler 任务入口：捕获所有异常，避免任务被移除。"""
    try:
        from api.scheduler import execute_cycle
        result = execute_cycle()
        print(f"[EvolutionScheduler] 周期 #{result.get('cycle')} 完成: "
              f"scanned={result['tasks'][0].get('scanned')} evolved={result['tasks'][2].get('evolved')}")
    except Exception as exc:
        print(f"[EvolutionScheduler] 周期异常: {type(exc).__name__}: {exc}")


def set_interval(seconds: int) -> None:
    from api.scheduler import SCHEDULER_STATE
    seconds = max(30, int(seconds))
    SCHEDULER_STATE["interval_seconds"] = seconds
    if _scheduler and _scheduler.get_job(_JOB_ID):
        _scheduler.reschedule_job(_JOB_ID, trigger="interval", seconds=seconds)


def start_scheduler() -> dict:
    """启动后台调度器（幂等）。"""
    global _scheduler
    from api.scheduler import SCHEDULER_STATE, ensure_history_table

    ensure_history_table()

    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        _scheduler.start()

    interval = SCHEDULER_STATE.get("interval_seconds", 900)
    if _scheduler.get_job(_JOB_ID):
        _scheduler.reschedule_job(_JOB_ID, trigger="interval", seconds=interval)
    else:
        _scheduler.add_job(
            _run_cycle_safe,
            trigger="interval",
            seconds=interval,
            id=_JOB_ID,
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    SCHEDULER_STATE["running"] = True
    print(f"[EvolutionScheduler] 已启动，每 {interval}s 执行一次进化周期")
    return {"status": "started", "interval_seconds": interval}


def stop_scheduler() -> dict:
    from api.scheduler import SCHEDULER_STATE
    if _scheduler and _scheduler.get_job(_JOB_ID):
        _scheduler.remove_job(_JOB_ID)
    SCHEDULER_STATE["running"] = False
    print("[EvolutionScheduler] 已停止")
    return {"status": "stopped"}


def start_if_enabled() -> None:
    """按环境变量决定是否在应用启动时自动开启（默认开启）。"""
    if os.getenv("AUTO_EVOLUTION", "1") not in ("0", "false", "False"):
        start_scheduler()
    else:
        from api.scheduler import ensure_history_table
        ensure_history_table()
        print("[EvolutionScheduler] AUTO_EVOLUTION 已关闭，仅初始化不自动运行")
