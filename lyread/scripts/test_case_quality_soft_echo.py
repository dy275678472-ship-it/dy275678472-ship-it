#!/usr/bin/env python3
"""本地校验：短母题融合回声 + 标点打断近义尾段 + 不误伤正常收束。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from services.case_quality import clean_preview_body  # noqa: E402


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: expected to keep {needle!r}")


def assert_not_contains(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"{label}: expected to drop {needle!r}")


def main() -> int:
    case953 = """第一章 赘婿

开篇。

傅临收笔，岳家灯亮，像新章。

沈清把新协议收进抽屉，像收一份迟到的信任。

傅临收笔，岳家灯亮，像新章。沈清把协议收进抽屉，不是收纸，是收一份迟到的并肩——历练完了，该过日子。

（节选完，共三章）
"""
    out953 = clean_preview_body(case953)
    assert_not_contains(out953, "迟到的并肩", "953")
    assert_contains(out953, "沈清把新协议收进抽屉", "953")
    assert_contains(out953, "傅临收笔，岳家灯亮，像新章。", "953")

    case1198 = """第一章 联姻

开篇。

终身版，从这一杯开始。

温言点头，终身有效。

温言端杯，顾沉接杯，终身版从这一杯开始，像把协议外的温度，终于说满。

（节选完，共三章）
"""
    out1198 = clean_preview_body(case1198)
    assert_not_contains(out1198, "终于说满", "1198")
    assert_contains(out1198, "温言点头，终身有效。", "1198")
    assert_contains(out1198, "终身版，从这一杯开始。", "1198")

    # 7 字核短母题（旧 min_core=8 会漏）：末段以前文短收束起笔再扩写
    case1200 = """第一章 转校

开篇。

最后一排，仍有光。

林知笑，继续讲题。

林知笑，继续讲题，像把金牌藏进抽屉，只留一支笔在桌上。

（节选完，共三章）
"""
    out1200 = clean_preview_body(case1200)
    assert_not_contains(out1200, "金牌藏进抽屉", "1200")
    assert_contains(out1200, "林知笑，继续讲题。", "1200")
    assert_contains(out1200, "最后一排，仍有光。", "1200")

    # 标点打断的 12 字核近义尾段（原文 ≥20 连续子串漏检）：case950
    case950 = """第一章 青训

开篇。

世界赛名单公布，小凯名字在列。老K在直播间说：「我粉丝他，他赢，我仍粉丝。」弹幕刷满，小凯在训练室回一句：「别刷，练。」他知道，吊打教练不是终点，是把青训营的规矩，带到更大的台上——赢人先赢规矩，这比五杀更值。

小凯关电脑，窗外天将明。世界赛在望，他仍记得青训营第一课：赢人先赢规矩——这比五杀更值，也比粉丝更久。

（节选完，共三章）
"""
    out950 = clean_preview_body(case950)
    assert_not_contains(out950, "也比粉丝更久", "950")
    assert_contains(out950, "赢人先赢规矩，这比五杀更值", "950")
    assert out950.count("赢人先赢规矩") == 1, out950

    # 去标点核 <12 不误伤（口号级短句）
    short_norm_ok = """第一章

他把「先赢规矩」四个字写在训练室白板上。

夜训结束，小凯关灯出门，街灯像未写完的下一局。

（节选完）
"""
    out_sn = clean_preview_body(short_norm_ok)
    assert_contains(out_sn, "未写完的下一局", "short_norm_ok")

    # 正常收束：末段不包含前窗短母题全文 → 保留
    normal = """第一章

开篇叙述很长，人物在夜里对话。

他望向窗外，城市灯火像未写完的下一章。

（节选完，共一章）
"""
    out_n = clean_preview_body(normal)
    assert_contains(out_n, "未写完的下一章", "normal")

    # 短于 7 字的口头禅不因「被包含」误删尾段
    short_ok = """第一章

他点头。

夜色沉下来，他把灯拧到最暗，只留窗缝一条细光。

（节选完）
"""
    out_short = clean_preview_body(short_ok)
    assert_contains(out_short, "只留窗缝一条细光", "short_ok")

    # ≥20 近义仍生效（保留首次）
    near = """第一章

苏灵儿擦净牌位，轻声说：「弟子等您，很久了。」

叶玄取剑。

苏灵儿擦净牌位，轻声说：「弟子等您，很久了。」又添一炷香。

（节选完）
"""
    out_near = clean_preview_body(near)
    assert out_near.count("弟子等您，很久了") == 1, out_near

    print("PASS soft-echo fusion(7) + punct-norm(12) + near-dup + normal/short close")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
