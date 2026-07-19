import os, json, time, re
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("ATTYFLOW_DATA_DIR", APP_ROOT))
LEADS_FILE = DATA_DIR / "leads.json"
EVENTS_FILE = DATA_DIR / "events.jsonl"
WELCOME_QUEUE = DATA_DIR / "welcome_queue.jsonl"

app = FastAPI(title="Attyflow Contract Risk Engine", version="1.2.0")

allowed = os.getenv("ALLOWED_ORIGINS", "https://attyflow.com,https://www.attyflow.com,http://localhost:8001,http://localhost:8000,http://127.0.0.1:8001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Attyflow-Client"],
)

class AuditPayload(BaseModel):
    text: str = Field(..., min_length=20, max_length=12000)
    client_role: str = Field("Buyer", pattern="^(Buyer|Seller|Mutual)$")

class LeadPayload(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    firm: Optional[str] = Field(default="", max_length=160)
    team_size: Optional[str] = Field(default="", max_length=80)
    source: Optional[str] = Field(default="website", max_length=80)
    message: Optional[str] = Field(default="", max_length=2000)

DEEPSEEK_ENDPOINT = os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_KEY:
    try:
        DEEPSEEK_KEY = Path("/tmp/ds_key.txt").read_text().strip()
    except Exception:
        DEEPSEEK_KEY = ""

RATE = {}

def ip_of(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")

def rate_limit(request: Request, limit: int = 30, window: int = 3600):
    ip = ip_of(request)
    now = time.time()
    bucket = [t for t in RATE.get(ip, []) if now - t < window]
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later or contact sales for higher limits.")
    bucket.append(now)
    RATE[ip] = bucket

def enqueue_welcome(email: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with WELCOME_QUEUE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"email": email, "day": 0, "queued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")

SYSTEM_PROMPT = """You are an expert US common-law transactional attorney assisting with contract review workflow software.
You are not providing legal advice. Produce a strict clause risk audit from the protection perspective of: {client_role}.
Focus on indemnity, limitation of liability, confidentiality, IP assignment, termination, data protection, assignment, and change of control issues.
Preserve placeholders like [Client_Individual] or [Company_Corporate].
Return only valid JSON with this schema:
{
 "risk_score": 0-100,
 "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
 "loophole_analysis": "Two to four sentences explaining the practical contract risk.",
 "redline_suggestion": "Draft replacement language suitable for attorney review."
}
"""

@app.get("/api/health")
async def health():
    return {"ok": True, "service": "attyflow", "model_configured": bool(DEEPSEEK_KEY), "version": "1.2.0"}

@app.post("/api/lead")
async def create_lead(payload: LeadPayload, request: Request):
    rate_limit(request, limit=60, window=3600)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    leads = []
    if LEADS_FILE.exists():
        try:
            leads = json.loads(LEADS_FILE.read_text())
        except Exception:
            leads = []
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", payload.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    record = payload.model_dump()
    record.update({"created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "ip": ip_of(request), "user_agent": request.headers.get("user-agent", "")[:300]})
    is_new = not any(l.get("email") == payload.email for l in leads)
    if is_new:
        leads.append(record)
        LEADS_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=2))
        enqueue_welcome(payload.email)
    return {"success": True, "message": "Lead captured", "welcome_queued": is_new}

@app.post("/api/event")
async def event(payload: dict, request: Request):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in payload.items() if isinstance(k, str)}
    payload["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload["ip"] = ip_of(request)
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return {"ok": True}

@app.post("/api/audit")
async def process_audit(payload: AuditPayload, request: Request):
    rate_limit(request, limit=25, window=3600)
    if not DEEPSEEK_KEY:
        raise HTTPException(status_code=503, detail="AI provider key is not configured. Set DEEPSEEK_API_KEY before production use.")
    text = re.sub(r"\s+", " ", payload.text).strip()
    system_instruction = SYSTEM_PROMPT.replace("{client_role}", payload.client_role)
    api_body = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": text}],
        "response_format": {"type": "json_object"},
        "temperature": 0.15,
        "max_tokens": 1800,
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(DEEPSEEK_ENDPOINT, json=api_body, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="AI provider returned an error. Please retry or contact support.")
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        for key in ["risk_score", "risk_level", "loophole_analysis", "redline_suggestion"]:
            if key not in parsed:
                raise ValueError(f"missing {key}")
        return parsed
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Audit failed safely. No legal risk score was generated.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8001")))
