#!/usr/bin/env python3
"""Generate KDGC static site from migrated www.kdgc.cc content (oxygen sensors).

Source of truth: https://www.kdgc.cc (Wanwang site: /sy about, /xwzx products, /lxwm news, /ahzkgcxxyqjyxgs contact)
Note: santa6.kdjc.cc does not resolve; content mirrored from www.kdgc.cc.
"""

from pathlib import Path

DIST = Path(__file__).parent / "frontend" / "dist"

BEIAN_ICP = "皖ICP备2021010166号"
BEIAN_GA = "皖公网安备34019202001633号"
BEIAN_GA_URL = "http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=34019202001633"
EMAIL = "guanwn@kdgc.cc"
PHONE = "15385884309"
PHONE_DISPLAY = "153-8588-4309"
ADDRESS = "安徽省合肥市高新区望江西路5089号嵌入式研发楼103-C3（科大先研院-智源楼）"
HOURS = "客服工作时间：09:00–21:00（7×24 响应）"

FOOTER = f"""<footer><div class="footer-grid container" style="padding:0">
<div><h4>中科国瓷</h4><p style="font-size:14px;margin-top:8px">变频氧传感器与氮氧传感技术 · 中科大技术转化</p>
<p style="font-size:13px;margin-top:8px;opacity:.8">恪守诚信为本，产品承诺质保 5 年</p></div>
<div><h4>产品</h4>
<a href="/products/kd0100-02s-t1.html">KD0100-02S-T1 探头</a>
<a href="/products/kd0100-02s-to.html">KD0100-02S-TO 插针</a>
<a href="/products/mask-o2-sensor.html">面罩用氧传感器</a></div>
<div><h4>公司</h4><a href="/products/">产品中心</a><a href="/news/">新闻资讯</a><a href="/knowledge/">知识库</a><a href="/cases/">产品案例</a><a href="/about/">关于中科国瓷</a><a href="/contact/">联系我们</a></div>
<div><h4>联系</h4><a href="mailto:{EMAIL}">{EMAIL}</a><br>
<a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
<p style="font-size:13px;margin-top:8px">{ADDRESS}</p></div>
</div>
<div class="footer-bottom">© 2026 安徽中科国瓷新型元器件有限公司<span class="sep">·</span><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{BEIAN_ICP}</a><span class="sep">·</span><a href="{BEIAN_GA_URL}" target="_blank" rel="noopener"><img src="/assets/images/ga_icon.png" alt="">{BEIAN_GA}</a><span class="sep">·</span><a href="/en/">English</a> <span class="sep">|</span> <a href="/">中文</a></div></footer>
<script src="/assets/js/main.js"></script>"""

NAV = """<nav class="nav"><div class="nav-inner">
<a href="/" class="nav-logo"><img src="/assets/images/logo.png" alt="中科国瓷" style="height:36px;width:auto">中科<span>国瓷</span><span class="nav-tagline">科技感知未来</span></a>
<div class="nav-links">
<a href="/products/">产品中心</a>
<a href="/news/">新闻资讯</a>
<a href="/knowledge/">知识库</a>
<a href="/cases/">产品案例</a>
<a href="/about/">关于中科国瓷</a>
<a href="/en/" style="opacity:.8">EN</a>
<a href="/contact/" class="nav-cta">联系我们</a>
</div>
<button class="menu-toggle" aria-label="菜单">☰</button>
</div></nav>"""

NAV_EN = """<nav class="nav"><div class="nav-inner">
<a href="/en/" class="nav-logo">ZK <span>Guoci</span><span class="nav-tagline">Oxygen Sensors</span></a>
<div class="nav-links">
<a href="/en/products.html">Products</a>
<a href="/en/news.html">News</a>
<a href="/en/knowledge.html">Knowledge</a>
<a href="/en/cases.html">Cases</a>
<a href="/en/about.html">About</a>
<a href="/" style="opacity:.8">中文</a>
<a href="/contact/" class="nav-cta">Contact</a>
</div>
<button class="menu-toggle" aria-label="Menu">☰</button>
</div></nav>"""

FOOTER_EN = f"""<footer><div class="footer-grid container" style="padding:0">
<div><h4>ZK Guoci</h4><p style="font-size:14px;margin-top:8px">Variable-frequency oxygen sensors · USTC tech transfer</p>
<p style="font-size:13px;margin-top:8px;opacity:.8">Integrity first · 5-year product warranty</p></div>
<div><h4>Products</h4>
<a href="/en/products.html">KD0100-02S-T1 Probe</a>
<a href="/en/products.html">KD0100-02S-TO Pin</a>
<a href="/en/products.html">Mask O₂ Sensor</a></div>
<div><h4>Company</h4>
<a href="/en/products.html">Products</a>
<a href="/en/news.html">News</a>
<a href="/en/knowledge.html">Knowledge</a>
<a href="/en/cases.html">Cases</a>
<a href="/en/about.html">About</a>
<a href="/contact/">Contact</a></div>
<div><h4>Contact</h4><a href="mailto:{EMAIL}">{EMAIL}</a><br>
<a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
<p style="font-size:13px;margin-top:8px">{ADDRESS}</p></div>
</div>
<div class="footer-bottom">© 2026 Anhui ZK Guoci New Components Co., Ltd.<span class="sep">·</span><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{BEIAN_ICP}</a><span class="sep">·</span><a href="{BEIAN_GA_URL}" target="_blank" rel="noopener"><img src="/assets/images/ga_icon.png" alt="">{BEIAN_GA}</a><span class="sep">·</span><a href="/en/">English</a> <span class="sep">|</span> <a href="/">中文</a></div></footer>
<script src="/assets/js/main.js"></script>"""


def page(title, desc, body, canonical="", lang="zh"):
    nav = NAV if lang == "zh" else NAV_EN
    footer = FOOTER if lang == "zh" else FOOTER_EN
    lang_attr = "zh-CN" if lang == "zh" else "en"
    canon = f'<link rel="canonical" href="https://kdgc.cc{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="{lang_attr}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
{canon}<link rel="stylesheet" href="/assets/css/style.css">
<link rel="icon" href="/assets/images/favicon.ico">
</head><body>{nav}<main>{body}</main>{footer}</body></html>"""


PRODUCTS = [
    {
        "slug": "kd0100-02s-t1",
        "name": "KD0100-02S-T1 氧气传感器-探头",
        "name_en": "KD0100-02S-T1 Oxygen Sensor — Probe",
        "tagline": "氧压范围 0.5–101 kPa · 线束探头型",
        "tagline_en": "O₂ partial pressure 0.5–101 kPa · Cable probe type",
        "summary": "氧压范围 0.5kPa–101kPa，与外部接口板配合工作，可测试空气、纯氧及氮氧混合气等气体的氧分压。",
        "summary_en": "Measures oxygen partial pressure from 0.5–101 kPa. Works with an external interface board / KD0100-03 controller for air, pure oxygen, and N₂/O₂ mixtures.",
        "image": "/assets/images/products/kd0100-02s-t1.png",
        "advantages": [
            "氧压范围：0.5kPa–101kPa",
            "与外部接口板 / 配套控制器 KD0100-03 配合工作",
            "可测试空气、纯氧及氮氧混合气等气体的氧分压",
            "线束探头结构，便于系统集成",
        ],
        "advantages_en": [
            "O₂ partial pressure range: 0.5–101 kPa",
            "Works with external interface board / KD0100-03 controller",
            "Measures air, pure O₂, and N₂/O₂ mixed gases",
            "Cable-harness probe design for easy system integration",
        ],
        "specs": [
            ("传感器型号", "KD0100-02S"),
            ("配套控制器", "KD0100-03"),
            ("加热电压", "~4.5V / 9V（可选）"),
            ("允许气体温度", "（-50 ~ 200）℃"),
            ("气流速率", "（0 ~ 10）m/s"),
            ("探头重量", "≦35g（不包括线束）"),
        ],
        "specs_en": [
            ("Sensor model", "KD0100-02S"),
            ("Controller", "KD0100-03"),
            ("Heater voltage", "~4.5V / 9V (optional)"),
            ("Gas temperature", "(-50 ~ 200) °C"),
            ("Gas flow rate", "(0 ~ 10) m/s"),
            ("Probe weight", "≦35 g (excl. harness)"),
        ],
        "wiring": [
            ("Vh-", "白线"),
            ("Vh+", "蓝线"),
            ("Sense", "红线"),
            ("Common", "灰线"),
            ("Pump", "绿线"),
        ],
        "wiring_en": [
            ("Vh-", "White"),
            ("Vh+", "Blue"),
            ("Sense", "Red"),
            ("Common", "Gray"),
            ("Pump", "Green"),
        ],
        "accuracy": [
            ("氧分压 1～10 kPa", "≤±0.5 kPa"),
            ("氧分压 10～30 kPa", "≤±1 kPa"),
            ("氧分压 30～50 kPa", "≤±1.5 kPa"),
            ("氧分压 50～70 kPa", "≤±2 kPa"),
            ("氧分压 70～100 kPa", "≤±2.5 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤±0.5 kPa"),
            ("10–30 kPa", "≤±1 kPa"),
            ("30–50 kPa", "≤±1.5 kPa"),
            ("50–70 kPa", "≤±2 kPa"),
            ("70–100 kPa", "≤±2.5 kPa"),
        ],
        "notes": [
            "工作时传感器探头温度较高，注意防范误触探头导致烫伤",
            "须按控制器说明书进行操作使用，否则可能会造成传感器永久损坏失效",
        ],
        "notes_en": [
            "Probe tip is hot during operation — avoid burns from accidental contact",
            "Operate only per the controller manual; misuse may permanently damage the sensor",
        ],
    },
    {
        "slug": "kd0100-02s-to",
        "name": "KD0100-02S-TO 氧气传感器-插针",
        "name_en": "KD0100-02S-TO Oxygen Sensor — Pin Header",
        "tagline": "氧压范围 0.5–101 kPa · 插针型 · ≦5g",
        "tagline_en": "O₂ partial pressure 0.5–101 kPa · Pin type · ≦5 g",
        "summary": "氧压范围 0.5kPa–101kPa，插针电气连接，探头重量 ≦5g，与配套控制器 KD0100-03 配合工作。",
        "summary_en": "Pin-header electrical connection, probe weight ≦5 g, O₂ range 0.5–101 kPa, paired with KD0100-03 controller.",
        "image": "/assets/images/products/kd0100-02s-to.png",
        "advantages": [
            "氧压范围：0.5kPa–101kPa",
            "轻量化插针结构，探头重量 ≦5g",
            "可测试空气、纯氧及氮氧混合气等气体的氧分压",
            "尺寸公差 ≦0.5mm（单位 mm）",
        ],
        "advantages_en": [
            "O₂ partial pressure range: 0.5–101 kPa",
            "Lightweight pin design, probe ≦5 g",
            "Measures air, pure O₂, and N₂/O₂ mixed gases",
            "Dimensional tolerance ≦0.5 mm",
        ],
        "specs": [
            ("传感器型号", "KD0100-02S"),
            ("配套控制器", "KD0100-03"),
            ("加热电压", "~4.5V / 9V（可选）"),
            ("允许气体温度", "（-50 ~ 200）℃"),
            ("气流速率", "（0 ~ 10）m/s"),
            ("探头重量", "≦5g（不包括线束）"),
        ],
        "specs_en": [
            ("Sensor model", "KD0100-02S"),
            ("Controller", "KD0100-03"),
            ("Heater voltage", "~4.5V / 9V (optional)"),
            ("Gas temperature", "(-50 ~ 200) °C"),
            ("Gas flow rate", "(0 ~ 10) m/s"),
            ("Probe weight", "≦5 g (excl. harness)"),
        ],
        "wiring": [
            ("1", "Pump"),
            ("2", "Common"),
            ("3", "Sense"),
            ("7", "Vh-"),
            ("9", "Vh+"),
            ("其余", "NC，无连接"),
        ],
        "wiring_en": [
            ("1", "Pump"),
            ("2", "Common"),
            ("3", "Sense"),
            ("7", "Vh-"),
            ("9", "Vh+"),
            ("Others", "NC"),
        ],
        "accuracy": [
            ("氧分压 1～10 kPa", "≤±0.5 kPa"),
            ("氧分压 10～30 kPa", "≤±1 kPa"),
            ("氧分压 30～50 kPa", "≤±1.5 kPa"),
            ("氧分压 50～70 kPa", "≤±2 kPa"),
            ("氧分压 70～100 kPa", "≤±2.5 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤±0.5 kPa"),
            ("10–30 kPa", "≤±1 kPa"),
            ("30–50 kPa", "≤±1.5 kPa"),
            ("50–70 kPa", "≤±2 kPa"),
            ("70–100 kPa", "≤±2.5 kPa"),
        ],
        "notes": [
            "工作时传感器探头温度较高，注意防范误触探头导致烫伤",
            "须按控制器说明书进行操作使用，否则可能会造成传感器永久损坏失效",
            "注：所有单位均为 mm，尺寸公差 ≦0.5mm",
        ],
        "notes_en": [
            "Probe tip is hot during operation — avoid burns",
            "Operate only per the controller manual",
            "All dimensions in mm; tolerance ≦0.5 mm",
        ],
    },
    {
        "slug": "mask-o2-sensor",
        "name": "面罩用氧传感器",
        "name_en": "Mask Oxygen Sensor",
        "tagline": "战机飞行员面罩用低温型变频式氧传感器",
        "tagline_en": "Low-temperature VF oxygen sensor for pilot oxygen masks",
        "summary": "公司开发的战机飞行员面罩用低温型变频式氧传感器已试制成功，产品各项性能指标优异。",
        "summary_en": "A low-temperature variable-frequency oxygen sensor for fighter-pilot oxygen masks has been successfully prototyped with excellent performance metrics.",
        "image": "/assets/images/products/mask-o2-sensor.png",
        "advantages": [
            "面向航空面罩应用的低温型变频式氧传感器",
            "氧分压测量范围 0.5 ~ 101 kPa",
            "响应时间 t90 ＜15 s，启动时间 65 s",
            "封装外壳温度 ＜60℃",
        ],
        "advantages_en": [
            "Low-temperature VF oxygen sensor for aviation masks",
            "O₂ partial pressure range 0.5–101 kPa",
            "Response time t90 <15 s; warm-up 65 s",
            "Package shell temperature <60 °C",
        ],
        "specs": [
            ("氧分压测量范围", "0.5 ~ 101 kPa"),
            ("工作电压", "3~4V / ≤1A"),
            ("工作温度", "-40 ~ +125 ℃"),
            ("允许气体温度", "-50 ~ +200 ℃"),
            ("启动时间", "65 s"),
            ("响应时间 (t90)", "＜15 s"),
            ("封装外壳温度", "＜60 ℃"),
        ],
        "specs_en": [
            ("O₂ range", "0.5 ~ 101 kPa"),
            ("Supply", "3–4 V / ≤1 A"),
            ("Operating temp.", "-40 ~ +125 °C"),
            ("Gas temperature", "-50 ~ +200 °C"),
            ("Warm-up time", "65 s"),
            ("Response t90", "<15 s"),
            ("Shell temperature", "<60 °C"),
        ],
        "wiring": [],
        "wiring_en": [],
        "accuracy": [
            ("1~10 kPa", "≤0.5 kPa"),
            ("10~30 kPa", "≤1 kPa"),
            ("30~70 kPa", "≤1.5 kPa"),
            ("70~101 kPa", "≤2 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤0.5 kPa"),
            ("10–30 kPa", "≤1 kPa"),
            ("30–70 kPa", "≤1.5 kPa"),
            ("70–101 kPa", "≤2 kPa"),
        ],
        "notes": [],
        "notes_en": [],
    },
]

NEWS = [
    {
        "slug": "team-building-2022",
        "date": "2022-01-16",
        "title": "2022年1月国瓷团建户外活动！新年新气象！虎年虎虎生威！",
        "title_en": "ZK Guoci 2022 Outdoor Team Building — New Year, New Energy",
        "summary": "新年伊始，国瓷公司进行周末全员户外团建，增强部门协作与凝聚力。",
        "summary_en": "At the start of 2022, ZK Guoci held a full-company outdoor team-building day to strengthen cross-team collaboration.",
        "body": """<p>2022年1月16日新年伊始，国瓷公司进行了一次周末全员户外团建活动。此次活动围绕着“敞开胸怀，接纳、认同、相信、团队，目标一致、实现自我。”为主题进行开展，目的是“增强部门与部门间、同事与同事间的沟通、交流与合作，增强公司的凝聚力，提高大家的积极性和效率。”通过活动的开展，让新员工迅速融入到了团队中，找到集体归属感，收到了良好的效果。</p>
<p>户外拓展第一项就是带大家一起体验骑马活动，温顺的马儿载着初体验的伙伴绕着马场观光，有的慢行散步体会马背上风光，有的伙伴追求策马扬鞭的感觉，通过管理员的现场教学，体验了一把歌词里的策马奔腾，潇潇洒洒。骑马活动也正式开始了热场，让大家已经进入到了活跃的状态。</p>
<p>体验完了骑马活动，接下来的一场拓展也正式拉开比赛的序幕——射箭比赛！这次比赛的赛制规则为：所有人分为两组：一组、二组，先行热身，让大家熟悉下靶场、箭弓，每个人都参与试射，找准位置和感觉，大家跃跃欲试，各组内队员每射中一次靶子都会带来一阵欢呼，射中箭靶的队员也被称为“种子选手”！当然比赛有惩罚，最后经过两组协商，输的队男生俯卧撑、女生深蹲作为惩罚！正式比赛开始！三局制，最后得分最高的队伍胜利。比赛中大家为每一次的中靶跳跃欢呼，为每一次的脱靶鼓舞打劲，加深了团队配合，懂得如何发挥团队最大的力量，互相鼓励、不气不馁。</p>
<p>在如火如荼的射箭比赛后，大家兴致高昂，意犹未尽，这时候正是进行刺激战场——CS射击战的时候。比赛同样分为两组，第一局对战为“斩首行动”，第二局要求必须团灭一组分输赢。这次CS的比赛大家都明白了团队的力量，确定了一个目标，既要有部署又要有冲劲，并且坚定不移的执行。</p>
<p>在一系列的比赛结束后，大家中午调整休息，美餐一顿，下午又开展了一系列团队活动：一起划竹筏船、一起开卡丁车。这两项活动都让团队认知到任何一件事都要脚踏实地去做，纸上谈兵只是空谈，只有实际去做去学习去感受才能走好后面的路。</p>
<p>团建尾声，大家将自己喜欢的活动又体验了一遍，最后以“摔碗酒”作为句号，带着美好的祝福开始新一年的辉煌。2022年国瓷在全体伙伴的努力下，全力以赴，共同进步，必将展开更加恢弘的篇章！最后国瓷祝大家新年快乐！虎年虎虎生威！！</p>""",
    },
    {
        "slug": "nox-sensor-market",
        "date": "2021-06-01",
        "title": "国内车用氮氧传感器市场超百亿元",
        "title_en": "China Automotive NOx Sensor Market Exceeds RMB 10 Billion",
        "summary": "气体传感器是机动车尾气后处理系统关键零部件，国Ⅵ排放标准下国内氮氧传感器市场空间超百亿元。",
        "summary_en": "Gas sensors are critical to vehicle aftertreatment. Under China VI, the domestic NOx sensor market is projected above RMB 10 billion.",
        "body": """<p>气体传感器作为汽车电子控制系统的信息源，是机动车尾气后处理系统中的关键零部件，决定了汽车排放物的控制水平。车用气体传感器的应用，为汽车尾气处理带来了新的变革，成为机动车节能减排的重要推手。</p>
<p>据了解，目前，我国每年需要近千万个氮氧传感器。柴油机所产生的微粒（PM）和氮氧化物（NOx）是排放中两种最主要的污染物。</p>
<p>当前针对 PM 及 NOx 排放控制的柴油机排放后处理技术有两种方法：</p>
<p>一种是通过废气再循环（EGR）技术降低发动机缸内燃烧的 NOx 排放，然后用柴油机颗粒捕集器（DPF）控制 PM。</p>
<p>另一种是通过燃油高压喷射技术降低发动机缸内燃烧的 PM 排放，然后用选择催化还原技术（SCR，喷射车用尿素液，以中和 NOx）控制 NOx。SCR 技术因为具有更高的燃油经济性和良好的耐硫性能，被认为是最有优势的技术路线，在欧洲已经得到了广泛的应用，而 SCR 技术中必然会用到氮氧传感器。</p>
<p>氮氧传感器是一种由固体电解质陶瓷及氮氧化物敏感电极材料，利用半导体技术制备的传感器，通过精密控制检测氮氧化物的电极表面的纳米复合结构，实现了极高的氮氧化物分子选择性。通过适当电极显微结构，提高了传感器对氮氧气体敏感性。</p>
<p>氮氧传感器由传感器探头和电控单元组成，二者之间通过一个线束连接，可测量尾气中氮氧化物的浓度、氧气的浓度。它可用于柴油发动机的 SCR 系统中实现氮氧化物的闭环控制，或汽油和柴油发动机的车载诊断（OBD）中。</p>
<p>传感器的探头，是将氧敏陶瓷材料制成的陶瓷芯片装配在金属外壳中。实际应用时，探头被安装在汽车的尾气管道中，陶瓷芯片会将尾气中的浓度值以电压的形式反馈到电控单元中。电控单元控制传感器探头的加热温度，并经过一系列信号调理，最后确定泵中氮氧化物浓度。电控单元通过 CAN 总线通讯，将测量气体的数值实时发送给汽车总控制中心（ECU），为 SCR 喷射量提供依据，以减少氮氧化物的排放。</p>
<p>市场分析认为，目前，在新车车用氮氧传感器市场领域，我国将至少需要 320 万个氮氧传感器。在旧车改造售后市场，将需要约 560 万个氮氧传感器，我国每年需要近千万个氮氧传感器。我国将实施国Ⅵ排放标准，届时每辆柴油车将安装 2 个氮氧传感器，我国年均将至少需要 1700 万个氮氧传感器，这将是一个超百亿元的国内市场。</p>""",
    },
    {
        "slug": "understand-o2-sensor",
        "date": "2021-05-01",
        "title": "一文读懂氧传感器",
        "title_en": "Oxygen Sensors Explained",
        "summary": "从发动机故障灯到氧化锆/氧化钛氧传感器原理、结构、分类与未来发展方向的科普解读。",
        "summary_en": "From check-engine lights to zirconia/titania oxygen sensor principles, structure, types, and future directions.",
        "body": """<p>开车的朋友有时会发现汽车发动机仪表盘上突然出现故障灯。如果车辆年限较久，很多情况下这个故障灯会和发动机氧传感器相关。接下来，我们就和大家一起聊一聊这个与汽车发动机紧密相关的氧传感器。</p>
<h3>氧传感器与电喷发动机</h3>
<p>对汽车发动机而言，氧传感器并不是一开始就存在的。为满足环保部门日益严格的汽车排放要求，电喷发动机越来越得到广泛应用，氧传感器则是电喷发动机中的一个非常重要的部件。</p>
<p>在使用三元催化转换器减少排气污染的发动机上，氧传感器是必不可少的元件。由于混合气的空燃比一旦偏离理论空燃比，三元催化剂对 CO、HC 和 NOx 的净化能力将急剧下降，故在排气管中安装氧传感器，用以检测排气中氧的浓度，并向 ECU 发出反馈信号，再由 ECU 控制喷油持续时间。</p>
<p>同时，氧传感器还能弥补由于机械及其它件磨损而引起空燃比的误差。可以说，它是电喷系统中唯一有“智能”的传感器。</p>
<h3>概念及工作原理</h3>
<p>氧传感器是利用陶瓷敏感元件测量各类加热炉或排气管道中的氧电势，由化学平衡原理计算出对应的氧浓度，从而达到监测和控制燃烧空燃比，以保证产品质量及尾气排放达标的测量元件。它还广泛应用于各类煤燃烧、油燃烧、气燃烧等炉体的气成分控制。</p>
<p>氧传感器利用了 Nernst 原理。其核心元件是一种多孔的 ZrO₂ 陶瓷管，它是一种固态电解质，两侧面分别烧结上多孔铂（Pt）电极。在一定温度下，由于两侧氧浓度不同产生电位差，浓度差越大，电位差越大。</p>
<p>根据氧传感器的电压信号，电脑按照尽可能接近 14.7：1 的理论最佳空燃比来稀释或加浓混合气。氧传感器只有在高温时（端部达到 300°C 以上）其特性才能充分体现；约 800°C 时，对混合气的变化反应最快。</p>
<h3>分类及特点</h3>
<p>实际应用的氧传感器有氧化锆式氧传感器和氧化钛式氧传感器两种。常见又有单引线、双引线和三根引线之分；原则上三种引线方式的氧传感器不能替代使用。</p>
<p><strong>氧化锆式氧传感器</strong>优点：结构简单、响应迅速、维护容易、使用方便、测量准确。缺点：特性只有在温度较高时（约 600℃）才充分体现。</p>
<p><strong>氧化钛式氧传感器</strong>利用多孔状导体 TiO₂ 的导电性随排气中氧含量的变化而变化，又称电阻性氧传感器。结构简单、体积小、成本低，但电阻值随温度变化较大，须用温度补偿提高精度。</p>
<h3>未来发展方向</h3>
<p>从目前情况看，针对氧传感器材料的研究重点包括：改进保护层材料提高抗劣化性；提高环境适应性与使用寿命；扩大空/燃比控制测量区域实现广域反馈控制；提高测量与反馈信号精确度。</p>""",
    },
]

TEAM = [
    {
        "name": "陈初升",
        "role": "首席科学家",
        "items": [
            "中国科学技术大学教授，博士生导师",
            "长期从事无机非金属材料和固体化学的教学和研究工作",
            "历任中国科学技术大学化学与材料学院院长，中国科学技术大学副校长；亚洲固态离子学会理事，中国固态离子学会副理事长",
            "国家杰出青年基金获得者",
            "国务院特殊津贴",
        ],
    },
    {
        "name": "李超",
        "role": "总经理",
        "items": [
            "中国科学技术大学近代物理系本科、硕士",
            "曾任 MXIC 研发经理，Creative Technology 研发经理，清华公共安全研究院（泽众安全科技有限公司）副总经理",
        ],
    },
    {
        "name": "李彤",
        "role": "总工程师",
        "items": [
            "中国科学技术大学计算机系本科、博士，高级工程师",
            "曾任中国电科 38 所某重大航天项目副总设计师，长期从事军工产品研制和项目管理工作",
        ],
    },
]

HONORS = [
    {"title": "2022年度合肥高新区深科技企业", "img": "/assets/images/honors/deep-tech-2022.png", "desc": "合肥高新技术产业开发区管理委员会 · 2022年12月"},
    {"title": "第十一届中国创新创业大赛安徽赛区合肥市赛三等奖", "img": "/assets/images/honors/innovation-2022.png", "desc": "初创企业组 · 合肥市科学技术局 · 2022年8月"},
    {"title": "ISO 9001:2015 质量管理体系认证", "img": "/assets/images/honors/iso9001.png", "desc": "证书号 50322Q4558R0S · 覆盖氮氧传感器研发和生产"},
    {"title": "发明专利：变频氧传感器", "img": "/assets/images/honors/patent-grant.png", "desc": "申请号 202110555297.8 · 国家知识产权局授予发明专利权通知书"},
    {"title": "专利权人变更为中科国瓷", "img": "/assets/images/honors/patent-transfer.png", "desc": "变频氧传感器专利由中科大先进技术研究院变更为本公司"},
]

PARTNERS = [
    {"name": "汇智新材料", "img": "/assets/images/partners/huizhi.png"},
    {"name": "AMPRON", "img": "/assets/images/partners/ampron.png"},
]


def product_detail_html(p):
    specs_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in p["specs"])
    acc_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in p["accuracy"])
    wiring = ""
    if p["wiring"]:
        wiring = "<h3>电气连接</h3><table><tr><th>端口</th><th>说明</th></tr>" + "".join(
            f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in p["wiring"]
        ) + "</table>"
    notes = ""
    if p["notes"]:
        notes = "<h3>注意事项</h3><ul>" + "".join(f"<li>{n}</li>" for n in p["notes"]) + "</ul>"
    adv = "".join(f"<li>{a}</li>" for a in p["advantages"])
    return f"""<section class="page-hero"><div class="container"><h1>{p['name']}</h1><p>{p['tagline']}</p></div></section>
<section><div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start">
<div><img src="{p['image']}" alt="{p['name']}" style="width:100%;border-radius:12px;background:#fff;border:1px solid var(--border)"></div>
<div class="content-block" style="margin:0">
<p>{p['summary']}</p>
<h3>产品优势</h3><ul>{adv}</ul>
<p style="margin-top:20px"><a href="/contact/?product={p['slug']}" class="btn btn-primary">咨询此产品</a>
<a href="/products/" class="btn btn-ghost" style="margin-left:8px;color:var(--navy);border-color:var(--border)">返回产品中心</a></p>
</div></div>
<div class="container" style="margin-top:32px">
<div class="content-block"><h2>规格参数</h2><table>{specs_rows}</table>
{wiring}
<h3 style="margin-top:24px">测量精度（标准大气条件下）</h3>
<table><tr><th>氧分压范围</th><th>精度</th></tr>{acc_rows}</table>
{notes}
</div></div></section>
<style>@media(max-width:800px){{section .container[style*="grid-template"]{{display:block!important}}}}</style>"""


def main():
    pages = {}

    # Homepage
    prod_cards = "".join(
        f"""<a href="/products/{p['slug']}.html" class="card">
<img src="{p['image']}" alt="{p['name']}" class="card-img" loading="lazy">
<div class="card-body"><h3>{p['name']}</h3><p>{p['tagline']}</p>
<span class="tag">氧传感器</span></div></a>"""
        for p in PRODUCTS
    )
    news_cards = "".join(
        f"""<a href="/news/{n['slug']}.html" class="card"><div class="card-body">
<span class="tag">{n['date']}</span><h3>{n['title']}</h3><p>{n['summary']}</p></div></a>"""
        for n in NEWS
    )
    pages["index.html"] = page(
        "中科国瓷 — 变频氧传感器与氮氧传感技术",
        "安徽中科国瓷新型元器件有限公司，专注变频氧传感器、氮氧传感器研发与生产。中科大技术转化，科技感知未来。",
        f"""<section class="hero"><div class="hero-bg"></div><div class="hero-content">
<div class="hero-badge">中科大技术转化 · 科技感知未来</div>
<h1>安徽中科国瓷<br><em>变频氧传感器</em>方案商</h1>
<p>氧压范围 0.5–101 kPa · 车用 / 航空面罩 / 工业气体检测 · 产品承诺质保 5 年</p>
<div class="hero-actions">
<a href="/products/" class="btn btn-primary">进入产品中心</a>
<a href="/contact/" class="btn btn-ghost">联系我们</a>
</div></div></section>
<div class="trust-bar"><div class="container trust-items">
<span><strong>ISO 9001</strong> 氮氧传感器研发生产</span>
<span><strong>发明专利</strong> 变频氧传感器</span>
<span><strong>深科技企业</strong> 合肥高新区 2022</span>
<span><strong>质保 5 年</strong> 诚信为本</span>
</div></div>
<section><div class="container">
<div class="section-header"><div class="section-label">Products</div><h2>产品中心</h2><p>与 www.kdgc.cc 产品中心一致，完整规格与详情</p></div>
<div class="grid-3">{prod_cards}</div>
</div></section>
<section style="background:var(--white)"><div class="container">
<div class="section-header"><div class="section-label">News</div><h2>新闻资讯</h2></div>
<div class="grid-3">{news_cards}</div>
</div></section>
<section class="cta-section"><div class="container">
<h2>获取氧传感器技术方案</h2>
<p style="margin-bottom:24px;opacity:.9">填写需求，技术团队将尽快与您联系</p>
<a href="/contact/" class="btn btn-white">立即咨询</a>
</div></section>""",
        "/",
    )

    # Products index + details
    pages["products/index.html"] = page(
        "产品中心 — 中科国瓷",
        "KD0100 系列氧气传感器探头/插针、面罩用氧传感器",
        f"""<section class="page-hero"><div class="container"><h1>产品中心</h1><p>Product Center · 完整复刻 www.kdgc.cc 已上架产品</p></div></section>
<section><div class="container grid-3">{prod_cards}</div></section>""",
        "/products/",
    )
    for p in PRODUCTS:
        pages[f"products/{p['slug']}.html"] = page(
            f"{p['name']} — 中科国瓷", p["summary"], product_detail_html(p), f"/products/{p['slug']}.html"
        )

    # About
    team_html = ""
    for t in TEAM:
        items = "".join(f"<li>{i}</li>" for i in t["items"])
        team_html += f"""<div class="content-block"><h3>{t['name']} <span class="tag">{t['role']}</span></h3><ul>{items}</ul></div>"""
    honor_html = "".join(
        f"""<a href="{h['img']}" target="_blank" class="card">
<img src="{h['img']}" alt="{h['title']}" class="card-img" style="object-fit:contain;background:#f8fafc;padding:12px;height:240px">
<div class="card-body"><h3 style="font-size:15px">{h['title']}</h3><p>{h['desc']}</p></div></a>"""
        for h in HONORS
    )
    partner_html = "".join(
        f"""<div class="content-block" style="text-align:center;padding:24px">
<img src="{p['img']}" alt="{p['name']}" style="max-height:80px;margin:0 auto 12px;object-fit:contain">
<p>{p['name']}</p></div>"""
        for p in PARTNERS
    )
    pages["about/index.html"] = page(
        "关于中科国瓷 — 中科国瓷",
        "安徽中科国瓷新型元器件有限公司：首席科学家、总经理、总工程师团队介绍，荣誉资质与合作伙伴。",
        f"""<section class="page-hero"><div class="container"><h1>关于中科国瓷</h1><p>科技感知未来 · 中科大技术转化平台</p></div></section>
<section><div class="container">
<div class="content-block">
<p>安徽中科国瓷新型元器件有限公司聚焦变频氧传感器、氮氧传感器的研发与生产，统一社会信用代码 91340100MA8LLE5K9H。公司地址位于中国（安徽）自由贸易试验区合肥市高新区望江西路 5089 号嵌入式研发楼 103-C3。</p>
<p>公司秉承以人为本、追求超越的经营理念；恪守诚信为本，产品承诺质保 5 年。通过坚持不懈地开拓创新、与时俱进，不断开创新局面、实现新跨越。</p>
</div>
<h2 style="margin:32px 0 16px">核心团队</h2>
{team_html}
<h2 style="margin:40px 0 16px">荣誉资质</h2>
<div class="grid-3">{honor_html}</div>
<h2 style="margin:40px 0 16px">合作伙伴</h2>
<div class="grid-3">{partner_html}</div>
<p style="margin-top:24px;font-size:13px;color:var(--muted)">内容来源：www.kdgc.cc 关于中科国瓷栏目（产品、证书与团队公开信息）</p>
</div></section>""",
        "/about/",
    )

    # News
    news_list = "".join(
        f"""<a href="/news/{n['slug']}.html" class="content-block" style="display:block">
<span class="tag">{n['date']}</span><h3 style="margin:8px 0">{n['title']}</h3><p>{n['summary']}</p></a>"""
        for n in NEWS
    )
    pages["news/index.html"] = page(
        "新闻资讯 — 中科国瓷",
        "中科国瓷新闻资讯：团建活动、氮氧传感器市场、氧传感器科普",
        f"""<section class="page-hero"><div class="container"><h1>新闻资讯</h1><p>全部来自 www.kdgc.cc 新闻资讯栏目</p></div></section>
<section><div class="container">{news_list}</div></section>""",
        "/news/",
    )
    for n in NEWS:
        pages[f"news/{n['slug']}.html"] = page(
            f"{n['title']} — 中科国瓷",
            n["summary"],
            f"""<section class="page-hero"><div class="container"><h1>{n['title']}</h1><span class="tag">{n['date']}</span></div></section>
<section><div class="container content-block">{n['body']}
<p style="margin-top:24px"><a href="/news/">← 返回新闻列表</a></p></div></section>""",
            f"/news/{n['slug']}.html",
        )

    # Contact
    pages["contact/index.html"] = page(
        "联系我们 — 中科国瓷",
        f"联系中科国瓷：{PHONE_DISPLAY} {EMAIL} {ADDRESS}",
        f"""<section class="page-hero"><div class="container"><h1>联系我们</h1><p>科技感知未来 · 快速响应</p></div></section>
<section><div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:32px">
<div class="content-block">
<h2>联系方式</h2>
<p><strong>邮箱</strong><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p style="margin-top:12px"><strong>电话</strong><br><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></p>
<p style="margin-top:12px"><strong>地址</strong><br>{ADDRESS}</p>
<p style="margin-top:12px"><strong>{HOURS}</strong><br>我们提供 7×24 小时的全天候响应速度，随时随地为您服务。</p>
<img src="/assets/images/wechat-qr.png" alt="微信二维码" style="max-width:160px;margin-top:16px">
</div>
<form id="lead-form" class="form-box">
<div class="form-hp"><input name="website" tabindex="-1" autocomplete="off"></div>
<div class="form-group"><label>公司名称 *</label><input name="company" required></div>
<div class="form-group"><label>联系人 *</label><input name="contact_name" required></div>
<div class="form-group"><label>手机 *</label><input name="phone" type="tel" required></div>
<div class="form-group"><label>邮箱</label><input name="email" type="email"></div>
<div class="form-group"><label>产品兴趣</label><select name="product_interest">
<option value="">请选择</option>
<option>KD0100-02S-T1 探头</option>
<option>KD0100-02S-TO 插针</option>
<option>面罩用氧传感器</option>
<option>其他</option></select></div>
<div class="form-group"><label>需求描述</label><textarea name="requirement"></textarea></div>
<button type="submit" class="btn btn-primary" style="width:100%">提交咨询</button>
<div class="form-msg"></div>
</form>
</div></section>
<style>@media(max-width:800px){{section .container[style*="grid-template"]{{display:block!important}}}}</style>""",
        "/contact/",
    )

    # Knowledge plan page
    pages["knowledge/index.html"] = page(
        "知识库建设规划 — 中科国瓷",
        "中科国瓷知识库建设规划：氧传感器选型、原理、应用与维护",
        """<section class="page-hero"><div class="container"><h1>知识库建设规划</h1><p>当前栏目为规划稿；正式文章将按下列结构持续补充</p></div></section>
<section><div class="container content-block">
<h2>一、建设目标</h2>
<p>围绕公司真实产品线（变频氧传感器 / 氮氧传感器），建立可检索、可转化线索的技术内容资产，服务工程师选型与采购决策，并与新闻、产品详情互相内链。</p>
<h2>二、栏目结构（建议 4 层）</h2>
<ol>
<li><strong>原理基础</strong>：氧化锆/氧化钛氧传感器、Nernst 原理、空燃比与三元催化、变频氧传感与传统氧传感差异</li>
<li><strong>产品选型</strong>：探头型 vs 插针型、面罩低温型适用场景、控制器 KD0100-03 配套说明、电气连接与线束规范</li>
<li><strong>应用场景</strong>：车用尾气 / SCR / OBD、航空面罩供氧监测、工业燃烧气氛控制、医疗与特种气体检测</li>
<li><strong>安装与维护</strong>：加热电压选择、允许气体温度/气流速率边界、常见失效模式、质保与注意事项</li>
</ol>
<h2>三、首批 12 篇选题（可直接立项）</h2>
<table>
<tr><th>#</th><th>标题</th><th>类型</th><th>优先级</th></tr>
<tr><td>1</td><td>变频氧传感器与传统氧传感器有何不同？</td><td>原理</td><td>P0</td></tr>
<tr><td>2</td><td>KD0100-02S-T1 与 TO 如何选型？</td><td>选型</td><td>P0</td></tr>
<tr><td>3</td><td>氧分压 0.5–101 kPa 量程意味着什么？</td><td>选型</td><td>P0</td></tr>
<tr><td>4</td><td>控制器 KD0100-03 接线与加热电压说明</td><td>工程</td><td>P0</td></tr>
<tr><td>5</td><td>车用氮氧传感器在 SCR / OBD 中的作用</td><td>应用</td><td>P1</td></tr>
<tr><td>6</td><td>航空面罩用低温氧传感器的关键指标</td><td>应用</td><td>P1</td></tr>
<tr><td>7</td><td>测量精度曲线解读（1–100 kPa）</td><td>工程</td><td>P1</td></tr>
<tr><td>8</td><td>探头高温烫伤与永久损坏的规避</td><td>维护</td><td>P1</td></tr>
<tr><td>9</td><td>固体电解质陶瓷在气体传感中的角色</td><td>原理</td><td>P2</td></tr>
<tr><td>10</td><td>国Ⅵ排放与氮氧传感器市场机遇</td><td>行业</td><td>P2</td></tr>
<tr><td>11</td><td>常见故障灯与氧传感器关系排查</td><td>维护</td><td>P2</td></tr>
<tr><td>12</td><td>如何阅读产品规格书与尺寸公差</td><td>工程</td><td>P2</td></tr>
</table>
<h2>四、内容规范</h2>
<ul>
<li>每篇 1200–2500 字，配 1 张产品/原理图，文末 CTA「咨询选型」</li>
<li>参数必须与产品详情页一致，禁止编造未公开指标</li>
<li>已有新闻《一文读懂氧传感器》《氮氧传感器市场》可拆分为知识库长文并互相引用</li>
</ul>
<h2>五、上线节奏</h2>
<p>先完成 P0 四篇并挂到导航；再按应用行业补 P1；P2 作为 SEO 长尾持续产出。知识库列表页增加分类筛选与站内搜索。</p>
</div></section>""",
        "/knowledge/",
    )

    # Cases plan page
    pages["cases/index.html"] = page(
        "产品案例建设方案 — 中科国瓷",
        "中科国瓷产品案例栏目完整建设方案：结构、素材、模板与上线节奏",
        """<section class="page-hero"><div class="container"><h1>产品案例建设方案</h1><p>当前案例过简；以下为可执行的完整建设方案</p></div></section>
<section><div class="container content-block">
<h2>一、问题诊断</h2>
<p>现有案例仅少量文字、无现场图/产品图、缺量化结果与客户场景，无法支撑 B2B 信任转化。官网 www.kdgc.cc 亦未单独开设案例库，本站需新建高质量案例栏目，而不是继续用占位文案。</p>
<h2>二、案例页标准结构（每篇必须具备）</h2>
<ol>
<li><strong>封面图</strong>：产品实拍或应用场景图（≥1200px）</li>
<li><strong>客户与行业</strong>：可脱敏（如「某航空配套单位」「某柴油机后处理 Tier1」）</li>
<li><strong>挑战</strong>：工况温度、量程、响应时间、可靠性/体积约束</li>
<li><strong>方案</strong>：选用哪款传感器 + 控制器 + 电气/机械接口要点</li>
<li><strong>实施</strong>：打样→标定→小批→量产节点（含时间）</li>
<li><strong>结果</strong>：至少 2 个量化指标（精度、响应、失效率、供货周期等）</li>
<li><strong>产品入口</strong>：链到对应产品详情 + 咨询 CTA</li>
</ol>
<h2>三、首批建议案例（需业务方确认素材）</h2>
<table>
<tr><th>案例</th><th>对应产品</th><th>需补充素材</th></tr>
<tr><td>航空面罩供氧监测试制项目</td><td>面罩用氧传感器</td><td>试制照片、性能对比表、节点时间</td></tr>
<tr><td>工业气体氧分压在线监测</td><td>KD0100-02S-T1</td><td>安装位置图、量程工况、精度验收</td></tr>
<tr><td>紧凑型设备插针式集成</td><td>KD0100-02S-TO</td><td>结构尺寸、重量优势、接线定义</td></tr>
<tr><td>柴油机 SCR / OBD 气体传感配套（规划）</td><td>氮氧/氧传感路线</td><td>客户许可、台架数据、排放相关指标</td></tr>
</table>
<h2>四、视觉与交互</h2>
<ul>
<li>列表：左图右文卡片，行业标签 + 关键结果数字</li>
<li>详情：顶部大图 + sticky「咨询同款方案」；中部挑战/方案/结果三栏；底部相关产品</li>
<li>禁止纯文字无图上线；无客户授权时使用自有实验室/产品图并标注「示意」</li>
</ul>
<h2>五、生产流程</h2>
<p>销售/项目经理提交《案例采集表》→ 技术审核参数 → 市场撰写 → 法务脱敏 → 上线。每月至少新增 1 篇；季度复盘转化（案例页 → 咨询表单）。</p>
<h2>六、近期交付</h2>
<p>在业务方提供 1 组真实项目素材后，48 小时内按本模板上线首个完整案例页，并替换本规划页为正式案例列表。</p>
</div></section>""",
        "/cases/",
    )

    # Remove old ceramic tech/applications or redirect-style pages → sensor oriented
    pages["technology/index.html"] = page(
        "技术能力 — 中科国瓷",
        "变频氧传感器与氮氧传感技术能力",
        """<section class="page-hero"><div class="container"><h1>技术能力</h1><p>固体电解质陶瓷 · 变频氧传感 · 氮氧敏感电极</p></div></section>
<section><div class="container content-block">
<p>公司掌握氧敏陶瓷材料、变频氧传感结构设计与控制器配套能力，产品覆盖探头型、插针型及航空面罩低温型等形态。</p>
<p>核心专利方向：<strong>变频氧传感器</strong>（申请号 202110555297.8）。质量管理体系覆盖氮氧传感器研发和生产（ISO 9001:2015）。</p>
<p><a href="/products/" class="btn btn-primary">查看产品规格</a></p>
</div></section>""",
        "/technology/",
    )
    pages["applications/index.html"] = page(
        "应用场景 — 中科国瓷",
        "氧传感器应用：汽车尾气、航空面罩、工业燃烧气氛",
        """<section class="page-hero"><div class="container"><h1>应用场景</h1></div></section>
<section><div class="container grid-3">
<div class="content-block"><h3>汽车尾气 / SCR / OBD</h3><p>监测排气氧浓度与氮氧化物相关气体信息，服务节能减排与排放法规。</p></div>
<div class="content-block"><h3>航空面罩供氧</h3><p>战机飞行员面罩用低温型变频式氧传感器，响应快、外壳温升可控。</p></div>
<div class="content-block"><h3>工业气体与燃烧控制</h3><p>空气、纯氧及氮氧混合气氧分压测量，服务炉窑与工艺气氛控制。</p></div>
</div></section>""",
        "/applications/",
    )

    pages["privacy.html"] = page(
        "隐私政策 — 中科国瓷",
        "隐私政策",
        """<section class="page-hero"><div class="container"><h1>隐私政策</h1></div></section>
<section><div class="container content-block"><p>我们仅将您通过表单提交的信息用于商务沟通与技术方案回复，不会出售给第三方。</p></div></section>""",
        "/privacy.html",
    )
    pages["404.html"] = page(
        "页面未找到 — 中科国瓷",
        "",
        """<section class="page-hero"><div class="container"><h1>404</h1><p>页面未找到</p>
<a href="/" class="btn btn-primary" style="margin-top:20px">返回首页</a></div></section>""",
        "",
    )

    # —— English site (full content) ——
    en_prod_cards = "".join(
        f"""<a href="/en/products/{p['slug']}.html" class="card">
<img src="{p['image']}" alt="{p['name_en']}" class="card-img" loading="lazy">
<div class="card-body"><h3>{p['name_en']}</h3><p>{p['tagline_en']}</p>
<span class="tag">Oxygen sensor</span></div></a>"""
        for p in PRODUCTS
    )
    en_news_cards = "".join(
        f"""<a href="/news/{n['slug']}.html" class="card"><div class="card-body">
<span class="tag">{n['date']}</span><h3>{n['title_en']}</h3><p>{n['summary_en']}</p>
<p style="font-size:13px;color:var(--muted);margin:0">Full article available in Chinese →</p></div></a>"""
        for n in NEWS
    )

    pages["en/index.html"] = page(
        "ZK Guoci — Variable-Frequency Oxygen Sensors",
        "Anhui ZK Guoci New Components Co., Ltd. — variable-frequency oxygen sensors and NOx sensing technology. USTC tech transfer.",
        f"""<section class="hero"><div class="hero-bg"></div><div class="hero-content">
<div class="hero-badge">USTC Tech Transfer · Sensing the Future</div>
<h1>Anhui ZK Guoci<br><em>Variable-Frequency Oxygen Sensors</em></h1>
<p>0.5–101 kPa · Automotive / Aviation mask / Industrial gas · 5-year warranty</p>
<div class="hero-actions">
<a href="/en/products.html" class="btn btn-primary">Product Center</a>
<a href="/contact/" class="btn btn-ghost">Contact Us</a>
</div></div></section>
<div class="trust-bar"><div class="container trust-items">
<span><strong>ISO 9001</strong> NOx sensor R&amp;D &amp; production</span>
<span><strong>Patent</strong> Variable-frequency O₂ sensor</span>
<span><strong>Deep Tech</strong> Hefei High-tech Zone 2022</span>
<span><strong>5-year</strong> product warranty</span>
</div></div>
<section><div class="container">
<div class="section-header"><div class="section-label">Products</div><h2>Product Center</h2>
<p>Same catalog as www.kdgc.cc — probe, pin, and mask oxygen sensors</p></div>
<div class="grid-3">{en_prod_cards}</div>
</div></section>
<section style="background:var(--white)"><div class="container">
<div class="section-header"><div class="section-label">News</div><h2>News &amp; Insights</h2></div>
<div class="grid-3">{en_news_cards}</div>
</div></section>
<section class="cta-section"><div class="container">
<h2>Request an Oxygen Sensor Solution</h2>
<p style="margin-bottom:24px;opacity:.9">Tell us your range, interface, and application — our team will reply soon.</p>
<a href="/contact/" class="btn btn-white">Contact</a>
</div></section>""",
        "/en/",
        lang="en",
    )

    pages["en/products.html"] = page(
        "Products — ZK Guoci",
        "KD0100 probe/pin oxygen sensors and aviation mask oxygen sensors",
        f"""<section class="page-hero"><div class="container"><h1>Product Center</h1>
<p>Full specs mirrored from www.kdgc.cc product catalog</p></div></section>
<section><div class="container grid-3">{en_prod_cards}</div></section>""",
        "/en/products.html",
        lang="en",
    )

    for p in PRODUCTS:
        specs_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in p["specs_en"])
        acc_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in p["accuracy_en"])
        wiring = ""
        if p["wiring_en"]:
            wiring = "<h3>Electrical connections</h3><table><tr><th>Pin</th><th>Signal</th></tr>" + "".join(
                f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in p["wiring_en"]
            ) + "</table>"
        notes = ""
        if p["notes_en"]:
            notes = "<h3>Notes</h3><ul>" + "".join(f"<li>{n}</li>" for n in p["notes_en"]) + "</ul>"
        adv = "".join(f"<li>{a}</li>" for a in p["advantages_en"])
        pages[f"en/products/{p['slug']}.html"] = page(
            f"{p['name_en']} — ZK Guoci",
            p["summary_en"],
            f"""<section class="page-hero"><div class="container"><h1>{p['name_en']}</h1><p>{p['tagline_en']}</p></div></section>
<section><div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start">
<div><img src="{p['image']}" alt="{p['name_en']}" style="width:100%;border-radius:12px;background:#fff;border:1px solid var(--border)"></div>
<div class="content-block" style="margin:0">
<p>{p['summary_en']}</p>
<h3>Advantages</h3><ul>{adv}</ul>
<p style="margin-top:20px"><a href="/contact/?product={p['slug']}" class="btn btn-primary">Inquire</a>
<a href="/en/products.html" class="btn btn-ghost" style="margin-left:8px;color:var(--navy);border-color:var(--border)">Back to products</a></p>
</div></div>
<div class="container" style="margin-top:32px">
<div class="content-block"><h2>Specifications</h2><table>{specs_rows}</table>
{wiring}
<h3 style="margin-top:24px">Accuracy (standard atmosphere)</h3>
<table><tr><th>O₂ partial pressure</th><th>Accuracy</th></tr>{acc_rows}</table>
{notes}
</div></div></section>
<style>@media(max-width:800px){{section .container[style*="grid-template"]{{display:block!important}}}}</style>""",
            f"/en/products/{p['slug']}.html",
            lang="en",
        )

    team_en = [
        ("Chen Chusheng", "Chief Scientist", [
            "Professor & PhD supervisor, University of Science and Technology of China (USTC)",
            "Long-term research in inorganic non-metallic materials and solid-state chemistry",
            "Former Dean of Chemistry & Materials, USTC; former Vice President of USTC; council roles in solid-state ionics societies",
            "Recipient of the National Science Fund for Distinguished Young Scholars",
            "Special Government Allowance of the State Council",
        ]),
        ("Li Chao", "General Manager", [
            "B.S. & M.S., Department of Modern Physics, USTC",
            "Former R&D Manager at MXIC and Creative Technology; former Deputy GM at Tsinghua Public Safety Research Institute (Zezhong Security Tech)",
        ]),
        ("Li Tong", "Chief Engineer", [
            "B.S. & PhD, Computer Science, USTC; Senior Engineer",
            "Former Deputy Chief Designer on a major aerospace program at CETC 38th Institute; long experience in defense product R&D and program management",
        ]),
    ]
    team_en_html = ""
    for name, role, items in team_en:
        team_en_html += f"""<div class="content-block"><h3>{name} <span class="tag">{role}</span></h3>
<ul>{''.join(f'<li>{i}</li>' for i in items)}</ul></div>"""
    honor_en = "".join(
        f"""<a href="{h['img']}" target="_blank" class="card">
<img src="{h['img']}" alt="{h['title']}" class="card-img" style="object-fit:contain;background:#f8fafc;padding:12px;height:240px">
<div class="card-body"><h3 style="font-size:15px">{h['title']}</h3><p>{h['desc']}</p></div></a>"""
        for h in HONORS
    )
    partner_en = "".join(
        f"""<div class="content-block" style="text-align:center;padding:24px">
<img src="{p['img']}" alt="{p['name']}" style="max-height:80px;margin:0 auto 12px;object-fit:contain">
<p>{p['name']}</p></div>"""
        for p in PARTNERS
    )
    pages["en/about.html"] = page(
        "About ZK Guoci — Oxygen Sensors",
        "Anhui ZK Guoci leadership, certifications, partners, and contact.",
        f"""<section class="page-hero"><div class="container"><h1>About ZK Guoci</h1>
<p>Sensing the future · USTC technology transfer</p></div></section>
<section><div class="container">
<div class="content-block">
<p>Anhui ZK Guoci New Components Co., Ltd. focuses on R&amp;D and production of variable-frequency oxygen sensors and NOx-related sensing technologies. Unified Social Credit Code: 91340100MA8LLE5K9H.</p>
<p>Address: Room 103-C3, Embedded R&amp;D Building, No. 5089 Wangjiang West Road, High-tech District, Hefei, Anhui (China (Anhui) Pilot Free Trade Zone).</p>
<p>We pursue excellence with integrity and offer a <strong>5-year product warranty</strong>.</p>
</div>
<h2 style="margin:32px 0 16px">Leadership</h2>
{team_en_html}
<h2 style="margin:40px 0 16px">Honors &amp; Certifications</h2>
<div class="grid-3">{honor_en}</div>
<h2 style="margin:40px 0 16px">Partners</h2>
<div class="grid-3">{partner_en}</div>
<p style="margin-top:24px;font-size:13px;color:var(--muted)">Source: public information on www.kdgc.cc</p>
</div></section>""",
        "/en/about.html",
        lang="en",
    )

    pages["en/news.html"] = page(
        "News — ZK Guoci",
        "ZK Guoci news: team building, NOx sensor market, oxygen sensor primer",
        f"""<section class="page-hero"><div class="container"><h1>News &amp; Insights</h1>
<p>All articles from the www.kdgc.cc news center (full text in Chinese)</p></div></section>
<section><div class="container">{"".join(
            f"""<a href="/news/{n['slug']}.html" class="content-block" style="display:block">
<span class="tag">{n['date']}</span><h3 style="margin:8px 0">{n['title_en']}</h3>
<p>{n['summary_en']}</p>
<p style="font-size:13px;color:var(--muted)">Original Chinese title: {n['title']}</p></a>"""
            for n in NEWS
        )}</div></section>""",
        "/en/news.html",
        lang="en",
    )

    pages["en/knowledge.html"] = page(
        "Knowledge Base Plan — ZK Guoci",
        "Knowledge base roadmap for oxygen sensor selection, principles, and applications",
        """<section class="page-hero"><div class="container"><h1>Knowledge Base Roadmap</h1>
<p>Planning page — articles will be published following this structure</p></div></section>
<section><div class="container content-block">
<h2>Goals</h2>
<p>Build searchable technical content around variable-frequency / NOx oxygen sensing to support engineer selection and lead conversion, with cross-links to products and news.</p>
<h2>Pillars</h2>
<ol>
<li><strong>Principles</strong> — zirconia/titania, Nernst, air-fuel ratio, VF vs traditional sensors</li>
<li><strong>Selection</strong> — probe vs pin, mask low-temp type, KD0100-03 pairing, wiring</li>
<li><strong>Applications</strong> — automotive SCR/OBD, aviation masks, industrial combustion atmospheres</li>
<li><strong>Install &amp; care</strong> — heater voltage, temperature/flow limits, failure modes, warranty notes</li>
</ol>
<h2>First 12 topics (P0–P2)</h2>
<table>
<tr><th>#</th><th>Topic</th><th>Priority</th></tr>
<tr><td>1</td><td>VF oxygen sensors vs traditional types</td><td>P0</td></tr>
<tr><td>2</td><td>How to choose KD0100-02S-T1 vs TO</td><td>P0</td></tr>
<tr><td>3</td><td>What 0.5–101 kPa range means</td><td>P0</td></tr>
<tr><td>4</td><td>KD0100-03 controller wiring &amp; heater voltage</td><td>P0</td></tr>
<tr><td>5</td><td>NOx sensors in SCR / OBD</td><td>P1</td></tr>
<tr><td>6</td><td>Key metrics for aviation mask O₂ sensors</td><td>P1</td></tr>
<tr><td>7</td><td>Reading accuracy curves (1–100 kPa)</td><td>P1</td></tr>
<tr><td>8</td><td>Avoiding tip burns and permanent damage</td><td>P1</td></tr>
<tr><td>9–12</td><td>Materials, China VI market, diagnostics, datasheet reading</td><td>P2</td></tr>
</table>
<p style="margin-top:20px"><a href="/knowledge/" class="btn btn-primary">View Chinese plan</a></p>
</div></section>""",
        "/en/knowledge.html",
        lang="en",
    )

    pages["en/cases.html"] = page(
        "Case Studies Plan — ZK Guoci",
        "Case study structure and first verticals for ZK Guoci oxygen sensors",
        """<section class="page-hero"><div class="container"><h1>Case Studies Roadmap</h1>
<p>www.kdgc.cc has no case library yet — this site will build one with full structure</p></div></section>
<section><div class="container content-block">
<h2>Required structure per case</h2>
<ol>
<li>Cover image (≥1200px)</li>
<li>Customer &amp; industry (may be anonymized)</li>
<li>Challenge — range, response, reliability, size constraints</li>
<li>Solution — sensor + controller + interface</li>
<li>Delivery milestones — sample → calibration → pilot → volume</li>
<li>Results — ≥2 quantified metrics</li>
<li>CTA to product detail + inquiry form</li>
</ol>
<h2>First case pipeline</h2>
<table>
<tr><th>Case</th><th>Product</th><th>Assets needed</th></tr>
<tr><td>Aviation mask O₂ monitoring prototype</td><td>Mask O₂ sensor</td><td>Prototype photos, metrics, timeline</td></tr>
<tr><td>Industrial O₂ partial-pressure online monitoring</td><td>KD0100-02S-T1</td><td>Install photos, duty cycle, acceptance data</td></tr>
<tr><td>Compact pin-header OEM integration</td><td>KD0100-02S-TO</td><td>Dimensions, weight, pinout</td></tr>
<tr><td>Diesel SCR / OBD gas sensing (planned)</td><td>NOx / O₂ path</td><td>Customer approval, dyno data</td></tr>
</table>
<p style="margin-top:20px"><a href="/cases/" class="btn btn-primary">View Chinese plan</a>
<a href="/contact/" class="btn btn-ghost" style="margin-left:8px;color:var(--navy);border-color:var(--border)">Share a case</a></p>
</div></section>""",
        "/en/cases.html",
        lang="en",
    )

    # Write all
    for rel, html in pages.items():
        out = DIST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("wrote", rel)

    # Remove obsolete ceramic product/news pages if present
    for obsolete in [
        "products/aln-substrate.html",
        "products/dbc-amb.html",
        "products/alumina.html",
        "news/ceramic-summit-2025.html",
        "news/iso9001-certification.html",
        "news/alumina-mass-production.html",
        "news/aln-thermal-test.html",
        "news/ev-partnership.html",
        "knowledge/aln-vs-alumina.html",
        "knowledge/dbc-vs-amb.html",
        "knowledge/igbt-substrate-guide.html",
        "cases/semiconductor-packaging.html",
        "cases/ev-power-module.html",
        "en/technology.html",
        "en/applications.html",
    ]:
        p = DIST / obsolete
        if p.exists():
            p.unlink()
            print("removed", obsolete)

    urls = [
        "/",
        "/products/",
        "/about/",
        "/news/",
        "/knowledge/",
        "/cases/",
        "/contact/",
        "/technology/",
        "/applications/",
        "/en/",
        "/en/products.html",
        "/en/news.html",
        "/en/knowledge.html",
        "/en/cases.html",
        "/en/about.html",
    ]
    urls += [f"/products/{p['slug']}.html" for p in PRODUCTS]
    urls += [f"/en/products/{p['slug']}.html" for p in PRODUCTS]
    urls += [f"/news/{n['slug']}.html" for n in NEWS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sm += f"  <url><loc>https://kdgc.cc{u}</loc><changefreq>weekly</changefreq></url>\n"
    sm += "</urlset>"
    (DIST / "sitemap.xml").write_text(sm)
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://kdgc.cc/sitemap.xml\n")
    print("done", len(urls), "urls")


if __name__ == "__main__":
    main()
