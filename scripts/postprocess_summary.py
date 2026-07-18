#!/usr/bin/env python3
"""Post-process extracted records and generate summary tables."""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

IN_CSV = Path("/workspace/data/callcenter_extract/callcenter_2010_2026_miit_anhui.csv")
OUT_DIR = Path("/workspace/data/callcenter_extract")
OUT_CLEAN = OUT_DIR / "callcenter_clean_2020_2026.csv"
OUT_ANHUI = OUT_DIR / "callcenter_anhui_subset.csv"
OUT_SUMMARY = OUT_DIR / "summary_report.md"


def is_valid_license(license_no: str) -> bool:
    if not license_no:
        return False
    if "国内呼叫中心" in license_no or "信息服务" in license_no:
        return False
    return bool(re.search(r"(B[12]|皖B[12]|合字)", license_no))


def clean_rows(rows: list[dict]) -> list[dict]:
    cleaned = []
    for r in rows:
        # Drop malformed cancellation rows where business text landed in license_no
        if r["license_no"] and not is_valid_license(r["license_no"]) and r["page_type"] != "注销批准":
            continue
        if r["year"] == "0000":
            r["year"] = (r["notice_date"] or "")[:4]
        cleaned.append(r)
    return cleaned


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def main():
    rows = list(csv.DictReader(IN_CSV.open(encoding="utf-8-sig")))
    clean = clean_rows(rows)

    anhui = [
        r for r in clean
        if r["province"] == "安徽" or "安徽" in r["company"] or (r["license_no"] or "").startswith("皖")
    ]

    write_csv(OUT_CLEAN, clean)
    write_csv(OUT_ANHUI, anhui)

    by_year = Counter(r["year"] for r in clean if r["year"])
    by_type = Counter(r["page_type"] for r in clean)
    by_prefix = Counter(r["license_prefix"] for r in clean)
    by_province = Counter(r["province"] for r in clean)

    summary = {
        "total_clean_records": len(clean),
        "anhui_related_records": len(anhui),
        "year_range_available": "2020-2026",
        "year_range_requested": "2010-2026",
        "by_year": dict(sorted(by_year.items())),
        "by_page_type": dict(by_type),
        "by_prefix": dict(by_prefix),
        "top_provinces": dict(by_province.most_common(15)),
        "coverage_gaps": [
            "工信部电信业务市场综合管理信息系统(tsm.miit.gov.cn)在线公示最早可追溯至2020年11月，2010-2019年跨地区发证/注销名单未在该系统公开留存",
            "安徽管局(ahca.miit.gov.cn)市场管理栏目列表页无公开分页API，仅能抓取当前可见页面；历史归档页面暂未能批量获取",
            "安徽本地地网许可证(皖B2-/皖B1-)需从省管局公示单独提取，本次工信部跨地区名单不含皖字号编号",
        ],
    }
    (OUT_DIR / "summary_clean.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 国内呼叫中心业务 批量汇总报告（2010-2026 请求范围）",
        "",
        "## 数据覆盖说明",
        "",
        "| 数据源 | 可获取年份 | 说明 |",
        "|--------|-----------|------|",
        "| 工信部跨地区公示 (tsm.miit.gov.cn) | **2020-2026** | 已批量抓取 342 期公示，清洗后 **{}** 条 |".format(len(clean)),
        "| 安徽管局公示 (ahca.miit.gov.cn) | 部分 2026 | 市场管理栏目可见页面已抓取，**暂未发现含国内呼叫中心业务的安徽地网(皖B2-)公示条目** |",
        "| 2010-2019 | **缺失** | 官方在线系统未公开历史批次，需人工调取纸质/内部档案或第三方转载 |",
        "",
        "## 一、总体统计（工信部 2020-2026，清洗后）",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 符合条件记录总数 | {len(clean)} |",
        f"| 新发证名单 | {by_type.get('新发证名单', 0)} |",
        f"| 注销公示 | {by_type.get('注销公示', 0)} |",
        f"| 注销批准 | {by_type.get('注销批准', 0)} |",
        f"| B2-(全网) | {by_prefix.get('B2-(全网)', 0)} |",
        f"| 混合-(全网) | {by_prefix.get('混合-(全网)', 0)} |",
        "",
        "## 二、按年份统计",
        "",
        "| 年份 | 记录数 |",
        "|------|--------|",
    ]
    for y, c in sorted(by_year.items()):
        lines.append(f"| {y} | {c} |")

    lines += [
        "",
        "## 三、按省份 Top 15",
        "",
        "| 省份 | 记录数 |",
        "|------|--------|",
    ]
    for p, c in by_province.most_common(15):
        lines.append(f"| {p} | {c} |")

    lines += [
        "",
        "## 四、安徽相关子集（工信部跨地区名单中含安徽企业）",
        "",
        f"共 **{len(anhui)}** 条（企业名称或省份标注含「安徽」）",
        "",
        "| 年份 | 记录数 |",
        "|------|--------|",
    ]
    ah_year = Counter(r["year"] for r in anhui if r["year"])
    for y, c in sorted(ah_year.items()):
        lines.append(f"| {y} | {c} |")

    lines += [
        "",
        "## 五、输出文件",
        "",
        f"- 全量清洗数据：`{OUT_CLEAN.name}`",
        f"- 安徽子集：`{OUT_ANHUI.name}`",
        f"- 原始抓取：`callcenter_2010_2026_miit_anhui.csv`",
        "",
        "## 六、数据局限",
        "",
    ]
    for gap in summary["coverage_gaps"]:
        lines.append(f"- {gap}")

    OUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_CLEAN}, {OUT_ANHUI}, {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
