#!/usr/bin/env bash
# LyRead 资源与健康巡检（建议 cron: */15 * * * *）
set -euo pipefail

LOG="${LYREAD_MONITOR_LOG:-/var/log/lyread_monitor.log}"
BASE_URL="${BASE_URL:-https://lyread.cn}"
DISK_WARN="${DISK_WARN:-85}"
MEM_WARN="${MEM_WARN:-90}"

ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG"; }

disk_pct=$(df / --output=pcent | tail -1 | tr -dc '0-9')
mem_pct=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')

if [ "$disk_pct" -ge "$DISK_WARN" ]; then
  log "WARN disk usage ${disk_pct}% (threshold ${DISK_WARN}%)"
fi
if [ "$mem_pct" -ge "$MEM_WARN" ]; then
  log "WARN memory usage ${mem_pct}% (threshold ${MEM_WARN}%)"
fi

for c in lyread-backend-fix lyread-mysql lyread-redis; do
  if ! docker ps --format '{{.Names}}' | grep -qx "$c"; then
    log "WARN container not running: $c"
  fi
done

if ! curl -sf --max-time 8 "$BASE_URL/health/live" | grep -q '"status":"ok"'; then
  log "WARN health/live failed for $BASE_URL"
fi

if ! curl -sf --max-time 8 "$BASE_URL/health/config" | grep -q '"version"'; then
  log "WARN health/config failed"
fi

log "OK disk=${disk_pct}% mem=${mem_pct}%"
