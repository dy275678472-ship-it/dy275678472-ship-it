#!/usr/bin/env python3
"""Patch backend: CRM sync on lead create + verify env."""
import sqlite3
import sys
from pathlib import Path

LEADS_PY = Path("/opt/kexun-token/routers/leads.py")
CRM_DB = Path("/opt/kexun-crm/crm.db")

SYNC_HOOK = '''
    # === CRM同步：线索同步到 crm.db ===
    try:
        _sync_lead_to_crm(lead_id, lead.name, lead.company, lead.phone, lead.industry, lead.source, lead.message, lead.page_url)
    except Exception as e:
        logger.warning(f"CRM同步失败: {e}")
'''

SYNC_FUNC = '''

def _sync_lead_to_crm(lead_id, name, company, phone, industry, source, message, page_url):
    """Sync new lead to CRM database."""
    import sqlite3 as _sq
    if not phone:
        return
    crm_path = "/opt/kexun-crm/crm.db"
    try:
        conn = _sq.connect(crm_path)
        conn.execute(
            """INSERT INTO leads (name, company, phone, industry, source, notes, status, created_at)
               VALUES (?,?,?,?,?,?,?,datetime('now'))""",
            (name, company or "", phone, industry or "", source or "website",
             f"{message or ''} | page:{page_url} | token_id:{lead_id}", "new"),
        )
        conn.commit()
        conn.close()
        logger.info(f"CRM同步成功: lead_id={lead_id} phone={phone}")
    except Exception as e:
        logger.warning(f"CRM sync error: {e}")
'''


def patch_leads():
    if not LEADS_PY.exists():
        print("leads.py not found")
        return False
    text = LEADS_PY.read_text(encoding="utf-8")
    changed = False
    if "_sync_lead_to_crm" not in text:
        text = text.replace(
            "def _notify_wecom(",
            SYNC_FUNC + "\ndef _notify_wecom(",
            1,
        )
        changed = True
    if "CRM同步" not in text and "lead_id = c.lastrowid" in text:
        text = text.replace(
            "    db.close()\n    \n    # Webhook: 推送线索到AI销售自动跟进",
            "    db.close()\n" + SYNC_HOOK + "\n    # Webhook: 推送线索到AI销售自动跟进",
            1,
        )
        changed = True
    if changed:
        LEADS_PY.write_text(text, encoding="utf-8")
        print("✅ leads.py patched with CRM sync")
    else:
        print("ℹ️  leads.py already patched")
    return changed


def ensure_crm_leads_table():
    if not CRM_DB.exists():
        print("⚠️  CRM DB not found")
        return
    conn = sqlite3.connect(CRM_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, company TEXT, phone TEXT, industry TEXT,
            source TEXT, notes TEXT, status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print("✅ CRM leads table ensured")


OWNER_HOOK = '''
    # === 线索自动分配 ===
    try:
        _assign_lead_owner(lead_id)
    except Exception as e:
        logger.warning(f"线索分配失败: {e}")
'''

OWNER_FUNC = '''

def _assign_lead_owner(lead_id):
    """Round-robin assign owner to new lead."""
    owners = ["sales_a", "sales_b", "sales_c"]
    import sqlite3 as _sq
    db_path = "/opt/kexun-token/token.db"
    conn = _sq.connect(db_path)
    row = conn.execute("SELECT COUNT(*) FROM leads").fetchone()
    count = row[0] if row else 0
    owner = owners[count % len(owners)]
    try:
        conn.execute("UPDATE leads SET owner=? WHERE id=?", (owner, lead_id))
        conn.commit()
    except Exception:
        pass
    conn.close()
'''


def ensure_owner_column():
    db = Path("/opt/kexun-token/token.db")
    if not db.exists():
        return
    conn = sqlite3.connect(db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
    if "owner" not in cols:
        conn.execute("ALTER TABLE leads ADD COLUMN owner TEXT")
        conn.commit()
        print("✅ Added owner column to leads")
    conn.close()


def patch_owner_assign():
    if not LEADS_PY.exists():
        return False
    text = LEADS_PY.read_text(encoding="utf-8")
    changed = False
    if "_assign_lead_owner" not in text:
        text = text.replace("def _notify_wecom(", OWNER_FUNC + "\ndef _notify_wecom(", 1)
        changed = True
    if "线索自动分配" not in text and "CRM同步" in text:
        text = text.replace(
            "    # Webhook: 推送线索到AI销售自动跟进",
            OWNER_HOOK + "\n    # Webhook: 推送线索到AI销售自动跟进",
            1,
        )
        changed = True
    if changed:
        LEADS_PY.write_text(text, encoding="utf-8")
        print("✅ leads.py patched with owner assignment")
    return changed


if __name__ == "__main__":
    ensure_crm_leads_table()
    ensure_owner_column()
    patch_leads()
    patch_owner_assign()
