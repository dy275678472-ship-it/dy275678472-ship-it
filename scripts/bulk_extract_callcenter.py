#!/usr/bin/env python3
"""Bulk extract 国内呼叫中心业务 entries from MIIT and Anhui CA public notices."""

import csv
import io
import json
import re
import time
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
OUT_DIR = Path("/workspace/data/callcenter_extract")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROVINCES = [
    "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
    "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
    "广西", "西藏", "宁夏", "新疆",
]
CITY_MAP = {
    "深圳": "广东", "广州": "广东", "东莞": "广东", "南通": "江苏", "苏州": "江苏",
    "南京": "江苏", "无锡": "江苏", "常州": "江苏", "杭州": "浙江", "宁波": "浙江",
    "成都": "四川", "武汉": "湖北", "西安": "陕西", "郑州": "河南", "长沙": "湖南",
    "合肥": "安徽", "芜湖": "安徽", "蚌埠": "安徽", "淮南": "安徽", "马鞍山": "安徽",
    "淮北": "安徽", "铜陵": "安徽", "安庆": "安徽", "黄山": "安徽", "滁州": "安徽",
    "阜阳": "安徽", "宿州": "安徽", "六安": "安徽", "亳州": "安徽", "池州": "安徽",
    "宣城": "安徽", "福州": "福建", "厦门": "福建", "济南": "山东", "青岛": "山东",
    "大连": "辽宁", "沈阳": "辽宁", "哈尔滨": "黑龙江", "长春": "吉林", "昆明": "云南",
    "贵阳": "贵州", "南宁": "广西", "海口": "海南", "兰州": "甘肃", "银川": "宁夏",
    "乌鲁木齐": "新疆", "拉萨": "西藏", "呼和浩特": "内蒙古",
}
KNOWN_COMPANY_PROVINCE = {"中讯邮电咨询设计院有限公司": "北京"}


@dataclass
class Record:
    source: str
    page_type: str
    notice_title: str
    notice_date: str
    company: str
    license_no: str
    business: str
    province: str
    license_prefix: str
    notice_url: str
    year: str


def infer_province(company: str, default: str = "未知") -> str:
    if company in KNOWN_COMPANY_PROVINCE:
        return KNOWN_COMPANY_PROVINCE[company]
    for p in PROVINCES:
        if p in company:
            return p
    for city, prov in CITY_MAP.items():
        if city in company:
            return prov
    return default


def classify_prefix(license_no: str) -> str:
    if not license_no:
        return "未知"
    if license_no.startswith("合字B2-") or license_no.startswith("B2-"):
        return "B2-(全网)"
    if license_no.startswith("合字B1-") or license_no.startswith("B1-"):
        return "B1-(全网)"
    if "B1.B2-" in license_no or "A2.B2-" in license_no or "A2.B1-" in license_no:
        return "混合-(全网)"
    if re.match(r"^皖B2-", license_no):
        return "皖B2-(安徽地网)"
    if re.match(r"^皖B1-", license_no):
        return "皖B1-(安徽地网)"
    if re.match(r"^[\u4e00-\u9fff]{1,2}B2-", license_no):
        return "省B2-(地网)"
    if re.match(r"^[\u4e00-\u9fff]{1,2}B1-", license_no):
        return "省B1-(地网)"
    return "其他"


def extract_issue_date(html: str) -> str:
    m = re.search(r"(\d{4}).{0,20}?(\d{1,2}).{0,20}?(\d{1,2}).{0,20}?开始发放", html, re.S)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return ""


def extract_cancel_date(html: str) -> str:
    m = re.search(r"公示期为自\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", html, re.S)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"发布时间[：:]\s*(\d{4}-\d{2}-\d{2})", html)
    if m:
        return m.group(1)
    return ""


def parse_miit_issuance(html: str, meta: dict) -> list[Record]:
    soup = BeautifulSoup(html, "lxml")
    issue_date = extract_issue_date(html) or meta.get("newstime", "")
    title = meta.get("title", "")
    records = []
    section = ""
    for tr in soup.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if not cells:
            continue
        if len(cells) == 1:
            section = cells[0]
            continue
        if cells[0] in ("序号", "公司名称") or len(cells) < 4 or not cells[0].isdigit():
            continue
        company, business, license_no = cells[1], cells[2], cells[3]
        if "国内呼叫中心业务" not in business:
            continue
        year = (issue_date or meta.get("newstime", ""))[:4]
        records.append(
            Record(
                source="工信部",
                page_type="新发证名单",
                notice_title=title,
                notice_date=issue_date or meta.get("newstime", ""),
                company=company,
                license_no=license_no,
                business=business,
                province=infer_province(company),
                license_prefix=classify_prefix(license_no),
                notice_url=f"https://tsm.miit.gov.cn/dxxzsp/help/noticeDetail.jsp?id={meta['id']}",
                year=year,
            )
        )
    return records


def parse_miit_cancel_inline(html: str, meta: dict) -> list[Record]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    title = meta.get("title", "")
    cancel_date = extract_cancel_date(html) or meta.get("newstime", "")
    records = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if not cells or cells[0] in ("序号", "企业名称", "公司名称"):
            continue
        row = " | ".join(cells)
        if "国内呼叫中心业务" not in row:
            continue
        company = license_no = business = ""
        if len(cells) >= 4:
            if re.match(r"^[A-Z\u4e00-\u9fff]", cells[1]) and ("B1" in cells[1] or "B2" in cells[1]):
                license_no, company, business = cells[1], cells[2], cells[3]
            else:
                company, license_no, business = cells[1], cells[2], cells[3]
        elif len(cells) == 3:
            license_no, company, business = cells[0], cells[1], cells[2]
        if not company:
            continue
        year = (cancel_date or meta.get("newstime", ""))[:4]
        records.append(
            Record(
                source="工信部",
                page_type="注销公示",
                notice_title=title,
                notice_date=cancel_date or meta.get("newstime", ""),
                company=company,
                license_no=license_no,
                business=business,
                province=infer_province(company),
                license_prefix=classify_prefix(license_no),
                notice_url=f"https://tsm.miit.gov.cn/dxxzsp/help/noticeDetail.jsp?id={meta['id']}",
                year=year,
            )
        )
    # parse cancellation approval section in issuance notices
    if "注销业务种类" in text:
        blocks = re.split(r"经营许可注销申请批准名单|申请注销业务经营许可公司批准名单", text)
        if len(blocks) > 1:
            for block in blocks[1:]:
                for m in re.finditer(
                    r"([\u4e00-\u9fff（）()A-Za-z0-9·\-]+?)\s+.*?注销业务种类[：:]([^\n]+)",
                    block,
                ):
                    company, business = m.group(1).strip(), m.group(2).strip()
                    if "国内呼叫中心业务" not in business:
                        continue
                    records.append(
                        Record(
                            source="工信部",
                            page_type="注销批准",
                            notice_title=title,
                            notice_date=meta.get("newstime", ""),
                            company=company,
                            license_no="",
                            business=business,
                            province=infer_province(company),
                            license_prefix="未知",
                            notice_url=f"https://tsm.miit.gov.cn/dxxzsp/help/noticeDetail.jsp?id={meta['id']}",
                            year=meta.get("newstime", "")[:4],
                        )
                    )
    return records


def docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            xml = zf.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        return "\n".join("".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in root.findall(".//w:p", ns))
    except Exception:
        return ""


def download_miit_attachment(html: str) -> list[list[str]]:
    m_path = re.search(r"var _filepath = '([^']+)'", html)
    if not m_path:
        return []
    token_url = f"https://tsm.miit.gov.cn/dxxzsp/help/getPage.jsp?type=dowloadfile&token={m_path.group(1)}"
    try:
        r = requests.get(token_url, headers=HEADERS, timeout=30)
        token = r.json().get("tokenkey")
        if not token:
            return []
        fr = requests.get(f"https://file.miit.gov.cn/file/download?t={token}", headers=HEADERS, timeout=60)
        if fr.status_code != 200:
            return []
        text = docx_text(fr.content)
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if "国内呼叫中心" not in line:
                continue
            parts = re.split(r"\s{2,}|\t", line)
            rows.append(parts)
        # also parse as table-like groups of 4
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        parsed = []
        for i, line in enumerate(lines):
            if "国内呼叫中心" not in line:
                continue
            # try nearby lines for company/license
            context = lines[max(0, i - 2): i + 1]
            parsed.append(context)
        return parsed
    except Exception:
        return []


def parse_miit_cancel_attachment(html: str, meta: dict) -> list[Record]:
    records = []
    m_path = re.search(r"var _filepath = '([^']+)'", html)
    if not m_path:
        return records
    try:
        token_url = f"https://tsm.miit.gov.cn/dxxzsp/help/getPage.jsp?type=dowloadfile&token={m_path.group(1)}"
        token = requests.get(token_url, headers=HEADERS, timeout=30).json().get("tokenkey")
        if not token:
            return records
        fr = requests.get(f"https://file.miit.gov.cn/file/download?t={token}", headers=HEADERS, timeout=60)
        if fr.status_code != 200:
            return records
        if fr.content[:2] == b"PK":
            text = docx_text(fr.content)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for i, line in enumerate(lines):
                if "国内呼叫中心" not in line:
                    continue
                # format: seq license company business OR seq company license business
                nums = []
                for j in range(max(0, i - 3), i + 1):
                    nums.append(lines[j])
                joined = " | ".join(nums)
                license_m = re.search(r"((?:合字)?B[12](?:\.B[12])?-\d+)", joined)
                license_no = license_m.group(1) if license_m else ""
                company = ""
                for part in nums:
                    if part.isdigit() or "B1" in part or "B2" in part or "国内" in part:
                        continue
                    if len(part) >= 4:
                        company = part
                business = line if "国内呼叫中心" in line else ""
                if not company:
                    # table row: seq, license, company, business
                    m = re.match(r"(\d+)\s+((?:合字)?B[12][\w\.-]+)\s+(.+?)\s+(国内.+)", joined)
                    if m:
                        license_no, company, business = m.group(2), m.group(3), m.group(4)
                if company:
                    cancel_date = extract_cancel_date(html) or meta.get("newstime", "")
                    records.append(
                        Record(
                            source="工信部",
                            page_type="注销公示",
                            notice_title=meta.get("title", ""),
                            notice_date=cancel_date,
                            company=company,
                            license_no=license_no,
                            business=business,
                            province=infer_province(company),
                            license_prefix=classify_prefix(license_no),
                            notice_url=f"https://tsm.miit.gov.cn/dxxzsp/help/noticeDetail.jsp?id={meta['id']}",
                            year=(cancel_date or meta.get("newstime", ""))[:4],
                        )
                    )
    except Exception:
        pass
    return records


def fetch_miit_notice(meta: dict) -> list[Record]:
    nid = meta["id"]
    url = f"https://tsm.miit.gov.cn/dxxzsp/help/noticeDetail.jsp?id={nid}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        html = r.text
    except Exception:
        return []
    title = meta.get("title", "")
    records = []
    if "发放名单" in title or "发放名单" in html:
        records.extend(parse_miit_issuance(html, meta))
        records.extend(parse_miit_cancel_inline(html, meta))
    elif "拟注销" in title or "注销" in title:
        records.extend(parse_miit_cancel_inline(html, meta))
        records.extend(parse_miit_cancel_attachment(html, meta))
    return records


def get_miit_notices() -> list[dict]:
    r = requests.get("https://tsm.miit.gov.cn/dxxzsp/help/getPage.jsp?type=tzgg", headers=HEADERS, timeout=30)
    data = r.json()
    relevant = []
    for item in data:
        t = item["title"]
        if "发放名单" in t or "拟注销" in t:
            relevant.append(item)
    # also probe IDs not in list but exist
    existing = {x["id"] for x in data}
    for nid in range(1, max(existing) + 1):
        if nid in existing:
            continue
    return relevant


def parse_ahca_page(html: str, url: str, title: str = "") -> list[Record]:
    soup = BeautifulSoup(html, "lxml")
    page_title = title or (soup.find("h1").get_text(strip=True) if soup.find("h1") else "")
    pub = ""
    pub_m = re.search(r"发布时间[：:]\s*(\d{4}-\d{2}-\d{2})", html)
    if pub_m:
        pub = pub_m.group(1)
    page_type = "注销公示" if "注销" in page_title else ("新发证名单" if any(k in page_title for k in ("领取", "发放", "核准")) else "公示")
    records = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if not cells or cells[0] in ("序号", "企业名称", "公司名称"):
            continue
        row = " | ".join(cells)
        if "国内呼叫中心业务" not in row:
            continue
        company = license_no = business = ""
        if len(cells) >= 4:
            if re.match(r"^\d+$", cells[0]):
                if "皖" in cells[1] or re.match(r"B[12]", cells[1]):
                    license_no, company, business = cells[1], cells[2], cells[3]
                else:
                    company, license_no, business = cells[1], cells[2], cells[3]
        if not company and len(cells) >= 3:
            license_no, company, business = cells[0], cells[1], cells[2]
        if not company:
            continue
        year = (pub or "")[:4]
        records.append(
            Record(
                source="安徽管局",
                page_type=page_type,
                notice_title=page_title,
                notice_date=pub,
                company=company,
                license_no=license_no,
                business=business if "国内呼叫中心" in business else row,
                province=infer_province(company, "安徽"),
                license_prefix=classify_prefix(license_no),
                notice_url=url,
                year=year,
            )
        )
    # plain text blocks
    text = soup.get_text("\n", strip=True)
    if "国内呼叫中心业务" in text and not records:
        for m in re.finditer(
            r"(皖B2-\d+|皖B1-\d+)\s+([\u4e00-\u9fff（）()A-Za-z0-9·]+?)\s+(国内[^\n]+呼叫中心[^\n]*)",
            text,
        ):
            license_no, company, business = m.group(1), m.group(2), m.group(3)
            records.append(
                Record(
                    source="安徽管局",
                    page_type=page_type,
                    notice_title=page_title,
                    notice_date=pub,
                    company=company,
                    license_no=license_no,
                    business=business,
                    province=infer_province(company, "安徽"),
                    license_prefix=classify_prefix(license_no),
                    notice_url=url,
                    year=(pub or "")[:4],
                )
            )
    return records


def discover_ahca_urls() -> list[tuple[str, str]]:
  """Collect Anhui CA URLs from known columns and search-result seeds."""
  seeds = set()
  columns = [
      ("5714e6c867df4d86ac0eccddd7384145", "市场管理"),
      ("04a262c1767e41a9a016081d59cab5f8", "通知公告"),
  ]
  base = (
      "https://ahca.miit.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit"
      "?parseType=buildstatic&webId=eb31cdc9f10d4d169377d773df1de2ea"
      "&tplSetId=ed6e0503693241b48b228a4875653ced&pageType=column"
      "&tagId=%E5%8F%B3%E4%BE%A7%E5%86%85%E5%AE%B9&editType=null&pageId={page_id}"
  )
  for page_id, _ in columns:
      try:
          r = requests.get(base.format(page_id=page_id), headers=HEADERS, timeout=30)
          html = r.json()["data"]["html"]
          soup = BeautifulSoup(html, "lxml")
          for a in soup.select("a[href]"):
              href = a.get("href", "")
              title = a.get("title") or a.get_text(strip=True)
              if "/art/" in href and any(k in title for k in ("增值电信", "经营许可", "呼叫中心", "许可证")):
                  seeds.add((requests.compat.urljoin("https://ahca.miit.gov.cn", href), title))
      except Exception:
          pass
  # extra seeds from manual curation / search discovery
  extra = [
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_03724ed390b0461dae1c889d26fcc98c.html",
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_9fe9d6e58f8b4c6ead3dada77ed77fa9.html",
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_eb18a3e3d91949749d31f925a1df016f.html",
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_767bfe813ec544c1b56ea25222d79142.html",
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_c1c357c5f59e4af3b58f35600663e224.html",
      "https://ahca.miit.gov.cn/xxgkdxgl/scgl/art/2026/art_2fe9f24757b843e48f2199d44bfe0764.html",
  ]
  for u in extra:
      seeds.add((u, ""))
  return sorted(seeds)


def main():
    print("Fetching MIIT notice index...")
    notices = get_miit_notices()
    print(f"MIIT relevant notices: {len(notices)}")

    all_records: list[Record] = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_miit_notice, n): n for n in notices}
        done = 0
        for f in as_completed(futs):
            done += 1
            recs = f.result()
            all_records.extend(recs)
            if done % 25 == 0:
                print(f"  MIIT processed {done}/{len(notices)}, records so far: {len(all_records)}")

    print(f"MIIT records with 国内呼叫中心业务: {len(all_records)}")

    print("Discovering Anhui CA URLs...")
    ahca_urls = discover_ahca_urls()
    print(f"Anhui seed URLs: {len(ahca_urls)}")
    for url, title in ahca_urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                continue
            recs = parse_ahca_page(r.text, url, title)
            all_records.extend(recs)
            time.sleep(0.2)
        except Exception:
            pass

    # dedupe
    seen = set()
    deduped = []
    for r in all_records:
        key = (r.source, r.company, r.license_no, r.business, r.notice_title, r.page_type)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    csv_path = OUT_DIR / "callcenter_2010_2026_miit_anhui.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(deduped[0]).keys()) if deduped else [])
        if deduped:
            w.writeheader()
            for r in deduped:
                w.writerow(asdict(r))

    # summary stats
    summary = {
        "total_records": len(deduped),
        "by_source": dict(Counter(r.source for r in deduped)),
        "by_year": dict(sorted(Counter(r.year for r in deduped if r.year).items())),
        "by_page_type": dict(Counter(r.page_type for r in deduped)),
        "by_province": dict(Counter(r.province for r in deduped).most_common()),
        "by_prefix": dict(Counter(r.license_prefix for r in deduped)),
        "miit_notices_scraped": len(notices),
        "ahca_urls_scraped": len(ahca_urls),
        "data_coverage_note": "工信部在线公示系统(tsm.miit.gov.cn)仅保留约2020年至今名单；2010-2019年跨地区名单未在该系统公开归档",
    }
    summary_path = OUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"CSV written to {csv_path}")


if __name__ == "__main__":
    main()
