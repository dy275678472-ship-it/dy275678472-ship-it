"""Knowledge base + industry cases content for KDGC static site.

Rules:
- Specs must match product pages (no invented metrics).
- Industry cases use customer pseudonyms only.
- Knowledge tone: rigorous, engineer-facing.
"""

from __future__ import annotations

# Baidu BD-09 approx for 合肥高新区望江西路5089号（科大先研院片区）
MAP_LAT = "31.83560"
MAP_LNG = "117.12885"
MAP_TITLE = "安徽中科国瓷新型元器件有限公司"
MAP_ADDRESS = "安徽省合肥市高新区望江西路5089号嵌入式研发楼103-C3（科大先研院-智源楼）"

KNOWLEDGE = [
    {
        "slug": "vf-vs-traditional-o2-sensor",
        "category": "原理",
        "category_en": "Principles",
        "date": "2026-07-01",
        "title": "变频氧传感器与传统氧传感器有何不同？",
        "title_en": "Variable-Frequency vs Traditional Oxygen Sensors",
        "summary": "从工作原理、输出特性到系统配套，说明变频氧传感与开关型/传统宽域氧传感的差异，以及选型时需关注的工程边界。",
        "summary_en": "Principles, output behavior, and system pairing differences between VF oxygen sensors and conventional switch/wideband types.",
        "cover": "news/understand-o2-sensor.jpg",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to", "mask-o2-sensor"],
        "body": """
<h2>一、传统氧传感器在做什么</h2>
<p>汽车与工业燃烧控制中常见的氧传感器，多基于氧化锆固体电解质的电化学效应。开关型（窄域）氧传感器在理论空燃比附近输出电压跳变，适合闭环修正；宽域（线性）氧传感器通过泵电流等方式给出连续空燃比/氧浓度信息，适合更精细的排放与燃烧控制。</p>
<p>无论开关型还是宽域型，工程关注点通常包括：工作温度窗口、响应时间、抗中毒能力、加热器功耗，以及与 ECU / 控制器的电气接口。</p>
<h2>二、变频氧传感器强调什么</h2>
<p>变频氧传感路线把测量重点放在<strong>氧分压</strong>的连续表征，并通过配套控制器完成激励、解调与信号输出。对中科国瓷 KD0100 系列而言，公开规格中的核心量程为氧分压 <strong>0.5–101 kPa</strong>，可覆盖空气、纯氧及氮氧混合气等工况评估场景。</p>
<p>与“仅判断浓稀跳变”的开关型传感器相比，变频方案更适合需要<strong>量化氧分压</strong>的系统集成；与部分车用宽域方案相比，其产品形态更贴近探头/插针模块 + 外置控制器（KD0100-03）的工业与特种装备集成方式。</p>
<h2>三、系统层面的差异</h2>
<ul>
<li><strong>信号形态</strong>：传统开关型输出阶跃电压；宽域型多为泵电流/线性信号；变频方案依赖配套控制器完成测量链路。</li>
<li><strong>集成方式</strong>：KD0100-02S-T1（线束探头）与 KD0100-02S-TO（插针）面向不同安装与电气连接约束；面罩低温型则服务航空生命保障等特殊温度环境。</li>
<li><strong>使用边界</strong>：允许气体温度（-50 ~ 200）℃、气流速率（0 ~ 10）m/s、加热电压约 4.5 V / 9 V（可选）等，必须按说明书执行，避免探头高温误触与错误加热导致永久损坏。</li>
</ul>
<h2>四、选型建议（简表）</h2>
<table>
<tr><th>需求</th><th>更合适的方向</th></tr>
<tr><td>仅需空燃比闭环跳变判断</td><td>传统开关型氧传感器（非本公司主推形态）</td></tr>
<tr><td>需要氧分压量化、模块化探头集成</td><td>KD0100-02S-T1 / TO + KD0100-03</td></tr>
<tr><td>航空面罩等低温生命保障监测</td><td>面罩用低温型变频氧传感器</td></tr>
</table>
<p class="article-note">本文参数均对齐公司公开产品规格；具体标定曲线与接口定义以交付资料与控制器说明书为准。</p>
""",
    },
    {
        "slug": "choose-t1-vs-to",
        "category": "选型",
        "category_en": "Selection",
        "date": "2026-07-02",
        "title": "KD0100-02S-T1 与 TO 如何选型？",
        "title_en": "How to Choose KD0100-02S-T1 vs TO",
        "summary": "从连接方式、重量、安装空间与产线装配角度，给出探头型与插针型的选型对照，避免只看量程忽视结构约束。",
        "summary_en": "Probe vs pin selection by interconnect, weight, envelope, and assembly constraints.",
        "cover": "products/kd0100-02s-t1.png",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>共同点（先对齐）</h2>
<p>两款传感器型号均为 <strong>KD0100-02S</strong>，配套控制器 <strong>KD0100-03</strong>，氧压范围均为 <strong>0.5–101 kPa</strong>，允许气体温度（-50 ~ 200）℃，气流速率（0 ~ 10）m/s，加热电压约 4.5 V / 9 V（可选）。精度分档（标准大气条件下）一致，例如 1～10 kPa 段 ≤±0.5 kPa，70～100 kPa 段 ≤±2.5 kPa。</p>
<h2>差异点（决定选型）</h2>
<table>
<tr><th>维度</th><th>T1 探头（线束）</th><th>TO 插针</th></tr>
<tr><td>电气连接</td><td>线束引出（白/蓝/红/灰/绿等定义见规格）</td><td>插针电气连接，便于板级/插座对接</td></tr>
<tr><td>探头重量</td><td>≦35 g（不含线束）</td><td>≦5 g（不含线束）</td></tr>
<tr><td>典型诉求</td><td>管路/腔体安装、线束走线灵活</td><td>紧凑设备、重量敏感、连接器化装配</td></tr>
<tr><td>尺寸公差</td><td>按图纸</td><td>尺寸公差 ≦0.5 mm（单位 mm）</td></tr>
</table>
<h2>推荐决策路径</h2>
<ol>
<li>先确认测量介质与氧分压是否落在 0.5–101 kPa；超出范围勿强行选型。</li>
<li>再确认机械接口：是否必须螺纹探头深入气流，或只需轻量化插针模块。</li>
<li>再确认电气：产线是否已有线束工艺，或希望直接插接到控制板/转接板。</li>
<li>最后与 KD0100-03 的加热电压档位、接地与屏蔽方案一并评审。</li>
</ol>
<p>若应用于航空面罩等低温生命保障场景，应评估<strong>面罩用低温型</strong>方案，而不是简单在 T1/TO 之间二选一。</p>
""",
    },
    {
        "slug": "o2-partial-pressure-range",
        "category": "选型",
        "category_en": "Selection",
        "date": "2026-07-03",
        "title": "氧分压 0.5–101 kPa 量程意味着什么？",
        "title_en": "What 0.5–101 kPa O₂ Partial Pressure Range Means",
        "summary": "解释氧分压量程与体积分数、总压的关系，并说明精度分档如何影响验收指标设计。",
        "summary_en": "Partial pressure vs mole fraction, and how accuracy bands affect acceptance tests.",
        "cover": "scenes/industrial-gas.jpg",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to", "mask-o2-sensor"],
        "body": """
<h2>氧分压与“氧浓度百分比”不是同一个数</h2>
<p>氧分压（partial pressure）是混合气体中氧气组分所对应的压力贡献。在理想气体近似下：</p>
<p><strong>氧分压 ≈ 总体压力 × 氧气体积分数</strong></p>
<p>因此，同一体积分数在不同总压下，氧分压会变化。KD0100 系列公开量程以氧分压 <strong>0.5–101 kPa</strong> 表述，便于跨工况（空气、富氧、氮氧混合）统一讨论测量范围。</p>
<h2>量程边界的工程含义</h2>
<ul>
<li><strong>靠近 0.5 kPa</strong>：低氧侧能力，适合缺氧/保护气氛等场景评估，但验收时需注意该段精度与标定方法。</li>
<li><strong>覆盖常压空气氧分压</strong>：标准大气下干燥空气氧分压约 21 kPa 量级，落在量程中段。</li>
<li><strong>上至 101 kPa</strong>：可覆盖接近纯氧、加压或高氧分压评估需求（仍须满足温度与气流速率限制）。</li>
</ul>
<h2>精度分档（公开规格）</h2>
<table>
<tr><th>氧分压</th><th>精度</th></tr>
<tr><td>1～10 kPa</td><td>≤±0.5 kPa</td></tr>
<tr><td>10～30 kPa</td><td>≤±1 kPa</td></tr>
<tr><td>30～50 kPa</td><td>≤±1.5 kPa</td></tr>
<tr><td>50～70 kPa</td><td>≤±2 kPa</td></tr>
<tr><td>70～100 kPa</td><td>≤±2.5 kPa</td></tr>
</table>
<p>编写技术协议时，建议按<strong>目标工作点所在分档</strong>定义验收限，而不是用单一百分比误差概括全量程。</p>
""",
    },
    {
        "slug": "kd0100-03-wiring-heater",
        "category": "工程",
        "category_en": "Engineering",
        "date": "2026-07-04",
        "title": "控制器 KD0100-03 接线与加热电压说明",
        "title_en": "KD0100-03 Wiring and Heater Voltage Notes",
        "summary": "梳理探头电气定义、加热电压可选档位与操作红线，降低误接线与错误加热导致的失效风险。",
        "summary_en": "Pin definitions, heater options, and hard operational limits for KD0100-03.",
        "cover": "products/controller-kd0100-03.webp",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>为什么必须“传感器 + 控制器”一起谈</h2>
<p>KD0100-02S 系列探头/插针需与配套控制器 <strong>KD0100-03</strong>（或经确认的外部接口板）配合工作。脱离说明书的激励与解调条件，可能导致测量无效，甚至造成传感器永久损坏。</p>
<h2>探头侧电气连接（公开定义）</h2>
<table>
<tr><th>端口</th><th>说明</th></tr>
<tr><td>Vh-</td><td>白线</td></tr>
<tr><td>Vh+</td><td>蓝线</td></tr>
<tr><td>Sense</td><td>红线</td></tr>
<tr><td>Common</td><td>灰线</td></tr>
<tr><td>Pump</td><td>绿线</td></tr>
</table>
<p>插针型（TO）在结构上改为插针互联，信号定义仍应对照交付图纸与控制器手册，不可凭经验对调加热与信号脚。</p>
<h2>加热电压</h2>
<p>公开可选加热电压约为 <strong>4.5 V / 9 V</strong>。选型阶段应明确：</p>
<ul>
<li>系统供电是否能稳定提供对应档位；</li>
<li>上电时序是否满足控制器要求；</li>
<li>线损与接插件压降是否会导致实际加热不足或过压。</li>
</ul>
<h2>操作红线（务必写入作业指导书）</h2>
<ul>
<li>工作时探头温度较高，防范误触烫伤；</li>
<li>必须按控制器说明书操作，错误使用可能导致传感器永久损坏失效；</li>
<li>气体温度与气流速率不得超过（-50 ~ 200）℃、（0 ~ 10）m/s 的公开允许范围。</li>
</ul>
""",
    },
    {
        "slug": "nox-scr-obd-role",
        "category": "应用",
        "category_en": "Applications",
        "date": "2026-07-05",
        "title": "车用氮氧传感器在 SCR / OBD 中的作用",
        "title_en": "Role of Automotive NOx Sensors in SCR / OBD",
        "summary": "从国Ⅵ排放与后处理闭环角度，说明氮氧/氧相关传感在 SCR 控制与 OBD 诊断中的位置，以及与氧分压测量能力的关系。",
        "summary_en": "How NOx/O₂ sensing supports SCR control and OBD under China VI constraints.",
        "cover": "scenes/automotive.jpg",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>排放法规推动后处理传感升级</h2>
<p>国Ⅵ阶段，柴油车与部分汽油车路线对 NOx 排放与车载诊断（OBD）提出更严要求。选择性催化还原（SCR）依赖尿素喷射与催化转化效率，控制系统需要可靠的排气侧气体信息用于闭环与监控。</p>
<h2>SCR / OBD 链路中的传感角色</h2>
<ul>
<li><strong>控制输入</strong>：为尿素剂量、催化器效率评估提供气体相关信息；</li>
<li><strong>诊断输入</strong>：支持超标、失效、传感器自身合理性等 OBD 逻辑；</li>
<li><strong>系统冗余与校验</strong>：常与温度、压力、尿素品质等信号交叉验证。</li>
</ul>
<h2>与氧分压测量能力的衔接</h2>
<p>排气氛围复杂，氧分压/氧相关信息常用于燃烧与后处理状态判断。中科国瓷在变频氧传感方向的产品能力（氧分压 0.5–101 kPa 量程、探头/插针形态）可为工业与特种场景的氧相关测量提供模块化选项；车规级氮氧传感器的台架数据、耐久与法规认证需按具体项目另行评估，不可把官网通用规格直接等同于某一车型的量产认可状态。</p>
<p class="article-note">涉及车规量产配套时，请通过咨询通道提交工况、接口与认证要求，由技术团队评估可行性。</p>
""",
    },
    {
        "slug": "aviation-mask-o2-metrics",
        "category": "应用",
        "category_en": "Applications",
        "date": "2026-07-06",
        "title": "航空面罩用低温氧传感器的关键指标",
        "title_en": "Key Metrics for Aviation Mask Low-Temperature O₂ Sensors",
        "summary": "围绕飞行员面罩供氧监测，梳理低温型变频氧传感器应关注的量程、环境与集成指标，并指向已试制成功的产品方向。",
        "summary_en": "Range, environment, and integration metrics for low-temperature mask O₂ sensing.",
        "cover": "scenes/aviation-mask.jpg",
        "related_products": ["mask-o2-sensor"],
        "body": """
<h2>应用场景特征</h2>
<p>战机/高性能航空生命保障系统中，面罩供氧监测对传感器提出与汽车排气完全不同的约束：工作温度更低、体积与线束受限、可靠性与响应要求高，且需与面罩气路结构协同设计。</p>
<h2>关键指标清单（评审用）</h2>
<ol>
<li><strong>测量范围</strong>：氧分压是否覆盖任务剖面（公司面罩用低温型公开方向为 0.5 ~ 101 kPa）。</li>
<li><strong>温度适应性</strong>：是否满足低温型定义与面罩附近微环境。</li>
<li><strong>结构集成</strong>：与软管/面罩腔体的安装方式、密封与维护可达性。</li>
<li><strong>电气与电磁环境</strong>：机载供电、接地、干扰与连接器规范。</li>
<li><strong>可靠性与维护</strong>：标定周期、失效可检测性、备件策略。</li>
</ol>
<h2>当前产品状态（公开信息）</h2>
<p>公司开发的战机飞行员面罩用低温型变频式氧传感器已<strong>试制成功</strong>，产品性能指标优异。具体项目指标、环境试验与交付状态需一事一议，以技术协议为准。</p>
""",
    },
    {
        "slug": "accuracy-curve-reading",
        "category": "工程",
        "category_en": "Engineering",
        "date": "2026-07-07",
        "title": "测量精度曲线解读（1–100 kPa）",
        "title_en": "Reading Accuracy Bands (1–100 kPa)",
        "summary": "按公开精度分档解释如何设计抽检点与判定准则，避免用单点误差否定全量程能力。",
        "summary_en": "How to design sampling points and pass/fail rules from published accuracy bands.",
        "cover": "products/exploded.webp",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>精度是“分档”而不是一条直线</h2>
<p>KD0100 系列在标准大气条件下的精度以氧分压区间给出。高氧分压段允许误差绝对值更大，这在气体传感中常见：同样 ±1 kPa，在 5 kPa 点与在 90 kPa 点的相对意义不同。</p>
<h2>建议的验收设计</h2>
<ul>
<li>在目标工况点附近至少设置 2–3 个抽检点；</li>
<li>每个点的判定限使用该点所在分档的公开精度；</li>
<li>记录总压、温度、气流速率，确保落在允许气体温度与气流速率范围内；</li>
<li>加热档位与控制器版本写入试验报告，保证可复现。</li>
</ul>
<h2>常见误判</h2>
<p>用“满量程百分比”一刀切、或在超量程/超气流条件下测试，都会造成不公正结论。若项目需要优于公开分档的指标，应在立项阶段作为定制开发需求提出，而不是默认官网规格已包含。</p>
""",
    },
    {
        "slug": "probe-burn-and-damage-prevention",
        "category": "维护",
        "category_en": "Maintenance",
        "date": "2026-07-08",
        "title": "探头高温烫伤与永久损坏的规避",
        "title_en": "Avoiding Probe Burns and Permanent Damage",
        "summary": "汇总安装、操作与维护中的高风险动作，形成可执行的作业检查单。",
        "summary_en": "A practical checklist to avoid tip burns and irreversible sensor damage.",
        "cover": "scenes/industrial-steam.webp",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to", "mask-o2-sensor"],
        "body": """
<h2>两类风险</h2>
<ol>
<li><strong>人身风险</strong>：工作时探头温度较高，误触可造成烫伤。</li>
<li><strong>产品风险</strong>：不按控制器说明书操作、错误加热或超工况使用，可能导致传感器永久损坏失效。</li>
</ol>
<h2>作业检查单（建议张贴于工位）</h2>
<ul>
<li>上电前确认加热电压档位与控制器型号匹配；</li>
<li>确认气体温度、气流速率在允许范围内；</li>
<li>维护时先断电并等待探头冷却；</li>
<li>禁止私自改线、对调加热与信号脚；</li>
<li>发现异常读数时，先检查气路泄漏、接线与控制器状态，再判断传感器本体。</li>
</ul>
<p>公司产品承诺质保 5 年，但人为违规操作、超规格使用不在正常质量责任范围内。具体以合同与说明书约定为准。</p>
""",
    },
    # ─── 5 new articles ────────────────────────────────────────────────
    {
        "slug": "oxygen-sensor-selection-guide",
        "category": "选型",
        "category_en": "Selection",
        "date": "2026-07-20",
        "title": "变频氧传感器完整选型指南：T1、TO 与面罩型如何选？",
        "title_en": "Complete Selection Guide: T1, TO, or Mask Oxygen Sensor?",
        "summary": "从气体环境、安装约束、量程、精度与控制器匹配四个维度系统梳理三款 KD0100 系列传感器的适用场景与差异，帮助工程师快速缩小选型范围。",
        "summary_en": "A systematic four-dimension framework—gas environment, mounting, range, accuracy, and controller matching—to narrow down T1, TO, or mask-type selections.",
        "cover": "products/kd0100-02s-t1.png",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to", "mask-o2-sensor"],
        "body": """
<h2>一、选型前必须明确的四个问题</h2>
<p>选型前，工程师需要先回答以下四个问题，任何一个答不出来都会导致选型失误或项目返工：</p>
<ol>
<li><strong>被测气体环境</strong>：是纯氧流、空气流、氮氧混合气，还是含有腐蚀性气体？温度范围？气压范围？</li>
<li><strong>安装与封装约束</strong>：允许的外形尺寸是多少？需要焊接/插针/线束中哪种接口？是否需要气密安装？</li>
<li><strong>量程与精度要求</strong>：目标量程是局部氧分压（kPa）还是百分比浓度？精度要求在哪个段最严？</li>
<li><strong>控制器与信号链</strong>：是否已有 KD0100-03 控制器？还是需要自制接口板？CAN / UART / 模拟输出？</li>
</ol>

<h2>二、三款传感器核心差异对比</h2>
<table>
<tr><th>参数</th><th>KD0100-02S-T1（探头）</th><th>KD0100-02S-TO（插针）</th><th>面罩用氧传感器</th></tr>
<tr><td>主要场景</td><td>工业气管路、气体分析仪</td><td>紧凑型仪器内嵌 OEM</td><td>航空/医疗面罩供氧监测</td></tr>
<tr><td>外形封装</td><td>线束探头，≦35g</td><td>4-pin TO 插针，≦5g</td><td>低温专用形态</td></tr>
<tr><td>氧分压量程</td><td>0.5–101 kPa</td><td>0.5–101 kPa</td><td>低温段优化</td></tr>
<tr><td>工作气体温度</td><td>-50~200 °C</td><td>-50~200 °C</td><td>低温侧优化</td></tr>
<tr><td>接口</td><td>线束（Vh-/Vh+/Sense/Common/Pump）</td><td>4-pin 插针</td><td>面罩专用接口</td></tr>
<tr><td>加热电压</td><td>~4.5V / 9V 可选</td><td>~4.5V / 9V 可选</td><td>—</td></tr>
<tr><td>适合集成方式</td><td>外挂、气路插入</td><td>PCB 直插或 SMT 过渡</td><td>面罩气腔密封安装</td></tr>
</table>

<h2>三、按场景的选型建议</h2>
<h3>场景 A：工业气体管路在线监测</h3>
<p>推荐 <strong>KD0100-02S-T1（探头型）</strong>。探头可插入气管路，线束便于布线，适配 KD0100-03 控制器。注意气流速率须在 0–10 m/s 范围，气体温度 -50~200 °C 以内。</p>

<h3>场景 B：仪器 OEM 内嵌，体积与重量约束严</h3>
<p>推荐 <strong>KD0100-02S-TO（插针型）</strong>。插针型仅 ≦5g，直接插 PCB 或通过转接架固定。适合气室容积小、整机空间有限的场景。需注意接线方式与控制电路设计。</p>

<h3>场景 C：航空面罩、高空供氧、呼吸器</h3>
<p>推荐<strong>面罩用氧传感器</strong>。针对低温和呼吸场景优化，安装需与面罩气腔密封配合。如有具体方案需求请联系工程师评估。</p>

<h3>场景 D：车用 SCR / 尾气氮氧检测</h3>
<p>目前三款产品针对的是氧分压（O₂）测量，而不是 NOx 浓度测量。若场景需要 NOx 传感（氮氧化物），请联系销售了解后续产品规划。</p>

<h2>四、控制器与接口配套</h2>
<p>T1 和 TO 均需配合 KD0100-03 控制器或等效接口电路使用。控制器负责加热管理、信号调理与数字输出。自制接口板的工程师请参阅接线说明文章，并严格按照加热电压规格设计，加热超压是传感器损坏的最常见原因。</p>

<h2>五、快速选型总结</h2>
<ul>
<li>有安装空间、需气路插入 → <a href="/products/kd0100-02s-t1.html">T1 探头型</a></li>
<li>体积紧凑、PCB 集成 → <a href="/products/kd0100-02s-to.html">TO 插针型</a></li>
<li>面罩 / 呼吸 / 低温 → <a href="/products/mask-o2-sensor.html">面罩用氧传感器</a></li>
<li>不确定？→ <a href="/contact/">联系工程师</a></li>
</ul>
""",
    },
    {
        "slug": "china-vi-oxygen-sensor-requirements",
        "category": "应用",
        "category_en": "Applications",
        "date": "2026-07-20",
        "title": "国六排放标准对氧传感器的要求与影响",
        "title_en": "China VI Emission Standards: Requirements and Impact on Oxygen Sensors",
        "summary": "梳理国六（GB18352.6-2016 / 重型 GB17691-2018）对排放后处理系统中氧传感器及氮氧传感器的具体要求，分析其对传感器选型和系统集成的影响。",
        "summary_en": "How China VI light- and heavy-duty emission standards drive oxygen and NOx sensor requirements in aftertreatment systems.",
        "cover": "news/nox-sensor-market.jpg",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>一、国六标准背景</h2>
<p>中国第六阶段机动车排放标准分为轻型车（GB18352.6-2016，2020 年起实施）和重型车（GB17691-2018，2021 年起国六 A，2023 年国六 B）两类。国六在国五基础上大幅收紧了 NOx、PM 与 HC 的排放限值，同时强化了车载排放检测（PEMS）和车载诊断（OBD）要求。</p>
<p>这些变化直接导致：后处理系统更复杂、传感器精度与寿命要求更高、OBD 监控覆盖传感器失效模式。</p>

<h2>二、对氧传感器的具体要求</h2>
<h3>1. SCR 闭环控制</h3>
<p>SCR（选择性催化还原）系统通过喷射尿素（AdBlue）将 NOx 还原为 N₂。精确控制喷射量需要 SCR 前后各安装一个 NOx 传感器，并配合氧分压传感器进行气氛修正。氧分压偏差过大会导致 NOx 转化效率下降、OBD 故障码触发。</p>

<h3>2. OBD 监控要求</h3>
<p>国六 OBD 明确要求监控氧传感器和 NOx 传感器的性能退化（响应慢、偏移、失效），传感器需满足规定寿命（轻型 ≥160,000 km / 重型按运营里程）。这对传感器的耐高温、耐振动与抗中毒能力提出了更高要求。</p>

<h3>3. 精度与响应速度</h3>
<p>国六后处理系统对传感器响应时间要求较国五更严（一般要求 t₉₀ &lt; 1s），以满足动态工况下的精确控制。固定量程偏差须经 OBD 软件判断是否超过阈值，超限则记录故障码。</p>

<h2>三、对选型的影响</h2>
<p>与国五相比，国六选型重点变化如下：</p>
<table>
<tr><th>维度</th><th>国五</th><th>国六</th></tr>
<tr><td>传感器精度</td><td>中等</td><td>更高，尤其 SCR 后端</td></tr>
<tr><td>寿命要求</td><td>较宽泛</td><td>明确里程/时间要求</td></tr>
<tr><td>OBD 监控</td><td>基本监控</td><td>传感器性能退化监控</td></tr>
<tr><td>安装数量</td><td>1–2 个</td><td>2–4 个（SCR 前后 + λ 传感）</td></tr>
</table>

<h2>四、中科国瓷产品的适配说明</h2>
<p>KD0100-02S 系列（T1/TO）为变频氧分压传感器，量程 0.5–101 kPa，适用于气体分析、面罩供氧等场景。该产品并非专为车用尾气 SCR 控制器（传统 LSU 型）设计，在选型时需确认接口与信号兼容性。</p>
<p>若您的项目涉及 SCR 系统用氧传感或 NOx 传感路线，欢迎<a href="/contact/">联系我们</a>进行技术评估。</p>

<h2>五、参考文献</h2>
<ul>
<li>GB18352.6-2016 《轻型汽车污染物排放限值及测量方法（中国第六阶段）》</li>
<li>GB17691-2018 《重型柴油车污染物排放限值及测量方法（中国第六阶段）》</li>
<li>GB17691-2018 附录及配套 OBD 监测要求（重型柴油车国六）</li>
</ul>
""",
    },
    {
        "slug": "zirconia-oxygen-sensor-principle",
        "category": "原理",
        "category_en": "Principles",
        "date": "2026-07-20",
        "title": "氧化锆（ZrO₂）固体电解质氧传感器工作原理",
        "title_en": "Working Principle of Zirconia (ZrO₂) Solid-Electrolyte Oxygen Sensors",
        "summary": "从能斯特方程与混合电位机制出发，系统说明氧化锆固体电解质的离子导电特性、传统开关型与宽域型氧传感器的工作差异，以及变频氧传感对传统路线的改进之处。",
        "summary_en": "From Nernst equation to mixed-potential mechanisms—how ZrO₂ ionic conductors power both conventional and variable-frequency oxygen sensors.",
        "cover": "products/exploded.webp",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>一、固体电解质的离子导电性</h2>
<p>氧化锆（ZrO₂）在掺杂氧化钇（Y₂O₃）稳定化后，形成稳定的立方萤石晶体结构。在 300 °C 以上，O²⁻ 氧离子可以在晶格氧空位间定向迁移，表现出显著的离子导电性。这是所有基于 YSZ（钇稳定氧化锆）的氧传感器的物理基础。</p>

<h2>二、能斯特方程与浓差电势</h2>
<p>当 YSZ 固体电解质两侧暴露在氧分压不同的气氛中时，O²⁻ 在两侧迁移速率不同，形成浓差电势 E：</p>
<p style="background:#f0f4f8;padding:12px;border-radius:8px;font-family:monospace">E = (RT/4F) × ln(P<sub>O₂,ref</sub> / P<sub>O₂,sample</sub>)</p>
<p>其中 R 为气体常数，T 为热力学温度，F 为法拉第常数，P 为氧分压。这就是传统开关型/宽域型氧传感器的理论基础——<strong>能斯特电池</strong>。</p>
<p>理论上，温度越高、两侧氧分压差越大，输出信号越强。但这也意味着传感器必须维持工作温度稳定（通常需要加热至 600–800 °C），否则读数漂移。</p>

<h2>三、开关型氧传感器（二值传感）</h2>
<p>传统开关型（Lambda）氧传感器将电化学电池的过渡点（空燃比 λ=1 时电压急剧跳变）作为判断依据，输出 ~0.1V 或 ~0.9V 两种状态。精度低、无法连续测量，但结构简单、成本极低，适用于三元催化器前后监控。</p>

<h2>四、宽域氧传感器（LSU 型）</h2>
<p>宽域氧传感（LSU/UEGO）引入额外泵浦电池，通过主动泵送维持参考腔氧浓度恒定，检测泵浦电流来推算样品气氧分压，从而实现连续线性测量。这是博世 LSU 4.x 系列的基本原理，广泛应用于国五以上排放控制系统。</p>

<h2>五、变频氧传感的技术路线</h2>
<p>中科国瓷 KD0100 系列采用<strong>变频检测</strong>路线：通过周期性改变施加在固体电解质上的交变激励信号频率，利用不同频率下 O²⁻ 迁移速率和界面阻抗的变化来推算氧分压，无需传统的恒流泵电路。其优点包括：</p>
<ul>
<li>减少对内置参考气腔的依赖，简化传感器结构；</li>
<li>可在较宽气体温度范围内（-50~200 °C）工作，不限于高温尾气场景；</li>
<li>适用于工业氧气管路、航空面罩等非尾气场景；</li>
<li>配合专用控制器（KD0100-03），量程可达 0.5–101 kPa。</li>
</ul>

<h2>六、加热与温度管理</h2>
<p>无论传统还是变频路线，YSZ 都需要一定工作温度以激活离子导电。KD0100-02S 配备加热元件，由 KD0100-03 控制器管理加热电压（~4.5V 或 9V 可选）。加热不足会导致响应慢、偏差大；过热则会加速电极老化甚至损坏。<strong>加热电压必须严格按照规格书设定，不得超压。</strong></p>

<h2>七、总结</h2>
<p>氧化锆氧传感器的核心是 YSZ 固体电解质的离子导电特性。开关型适合排放控制二值判断；宽域型适合连续空燃比闭环；变频型则适合更广泛的工业与特种气体场景，是中科国瓷 KD0100 系列的技术差异所在。</p>
""",
    },
    {
        "slug": "oxygen-sensor-fault-diagnosis",
        "category": "维护",
        "category_en": "Maintenance",
        "date": "2026-07-20",
        "title": "氧传感器故障诊断：常见问题与排查思路",
        "title_en": "Oxygen Sensor Fault Diagnosis: Common Issues and Troubleshooting",
        "summary": "梳理 KD0100 系列氧传感器常见故障现象（读数偏高/偏低/无响应/漂移），结合硬件检查、气路排查与控制器自检，给出系统性排查流程。",
        "summary_en": "Systematic troubleshooting for KD0100-series issues: high/low readings, no response, and drift—hardware check, gas-path inspection, and controller self-test.",
        "cover": "products/probe-alt.png",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>一、排查前提：先确认这三件事</h2>
<p>在判断传感器本体故障前，必须先排除以下三类外部原因，否则很容易误换好的传感器：</p>
<ol>
<li><strong>气路密封性</strong>：气路泄漏会导致读数系统性偏低或飘移，拧紧所有接头后重测；</li>
<li><strong>电气接线</strong>：线序错误（尤其加热与信号脚互换）是损坏传感器和控制器的主要原因，对照说明书逐线确认；</li>
<li><strong>控制器与供电</strong>：KD0100-03 加热电压是否在规格范围内？供电是否稳定？用万用表实测加热脚电压。</li>
</ol>

<h2>二、常见故障与排查表</h2>
<table>
<tr><th>故障现象</th><th>可能原因</th><th>排查步骤</th></tr>
<tr><td>读数异常偏高（远超实际氧分压）</td><td>气路有外部氧气渗入；样品气未稳定</td><td>检查气路密封；若条件允许，通纯氮气验证低氧点</td></tr>
<tr><td>读数异常偏低</td><td>气路泄漏；加热不足导致离子迁移率低</td><td>检查接头；实测加热电压（应在 4.3–4.7V 或 8.5–9.5V）</td></tr>
<tr><td>读数漂移（随温度或时间变化）</td><td>传感器预热未完成；电极老化</td><td>开机预热 ≥3 分钟再取读数；若老化则需更换</td></tr>
<tr><td>无响应 / 输出固定值</td><td>接线断路；传感器永久损坏（如超压烧毁）</td><td>用万用表测传感器阻抗；若短路或断路，传感器已损坏</td></tr>
<tr><td>输出噪声大</td><td>接地问题；EMC 干扰</td><td>检查信号屏蔽与接地；远离变频器/电机</td></tr>
<tr><td>精度在某段不符合规格</td><td>校准失效；超量程使用</td><td>对照精度表确认量程；联系厂家重新标定</td></tr>
</table>

<h2>三、控制器自检方法（KD0100-03）</h2>
<p>KD0100-03 提供内置自检与状态指示（详见控制器说明书）。若控制器报告加热异常、通信中断或量程超限，优先对照说明书排查接线与供电，不要直接更换传感器。</p>

<h2>四、防止传感器损坏的操作规范</h2>
<ul>
<li>严禁在传感器加热中途断电后立即通水气或液体，需等探头冷却；</li>
<li>不得用手触摸陶瓷探头，油脂会污染电极表面；</li>
<li>气体中若含硫化物、卤素或有机蒸气，会加速电极中毒，需提前评估；</li>
<li>安装时避免机械碰撞，陶瓷芯片脆性较高。</li>
</ul>

<h2>五、什么情况下需要联系厂家</h2>
<ul>
<li>按以上步骤排查后读数仍异常；</li>
<li>超过保修范围的物理损坏（如意外落摔、进液）；</li>
<li>需要定制标定或特殊气体适配评估。</li>
</ul>
<p><a href="/contact/" class="btn btn-primary">联系工程师</a></p>
""",
    },
    {
        "slug": "domestic-vs-imported-oxygen-sensors",
        "category": "选型",
        "category_en": "Selection",
        "date": "2026-07-20",
        "title": "国产变频氧传感器与进口产品对比分析",
        "title_en": "Domestic Variable-Frequency vs Imported Oxygen Sensors: A Comparative Analysis",
        "summary": "从技术路线、指标可比性、供应链安全、价格与技术支持五个维度，客观分析国产变频氧传感器与传统进口宽域氧传感器的差异，供工程师选型参考。",
        "summary_en": "A five-dimension comparison—technology, specs, supply chain, pricing, and support—between domestic VF and imported wideband oxygen sensors.",
        "cover": "news/nox-sensor-market.jpg",
        "related_products": ["kd0100-02s-t1", "kd0100-02s-to"],
        "body": """
<h2>一、前提说明</h2>
<p>本文对比的对象是：中科国瓷 KD0100 系列<strong>变频氧分压传感器</strong>（工业与特种场景）与传统进口宽域氧传感器（主要面向车用 SCR/尾气场景，如博世 LSU 系列）。两者的目标场景有交集但不完全重合，对比需在相同应用场景下进行。</p>

<h2>二、技术路线对比</h2>
<table>
<tr><th>维度</th><th>KD0100 变频型</th><th>典型进口宽域型（如 LSU）</th></tr>
<tr><td>检测原理</td><td>变频激励 + 阻抗分析</td><td>电化学泵电流（Nernst+极限电流）</td></tr>
<tr><td>工作温度范围</td><td>-50~200 °C（气体）</td><td>600~850 °C（尾气专用）</td></tr>
<tr><td>量程</td><td>0.5–101 kPa 氧分压</td><td>λ 0.65–∞ / 0–25% O₂</td></tr>
<tr><td>信号输出</td><td>数字（配 KD0100-03）</td><td>模拟电压 / CAN（需 ECU 配套）</td></tr>
<tr><td>主要应用场景</td><td>工业气体、面罩、仪器 OEM</td><td>车用发动机尾气 SCR 控制</td></tr>
</table>
<p><strong>结论：两者技术路线不同，不能简单互换。场景匹配优先于品牌比较。</strong></p>

<h2>三、指标可比性</h2>
<p>KD0100 的精度指标（±0.5–2.5 kPa 分段）以氧分压（kPa）为单位，而进口车用宽域型通常以空燃比（λ）或浓度（%）标注。在工业气体和面罩供氧场景下，kPa 单位更直接、更有意义。</p>
<p>不建议在不同场景下直接对比两者的"精度数字"，应以实际应用的气体范围和测量目的为准。</p>

<h2>四、供应链与国产化</h2>
<ul>
<li><strong>供货稳定性</strong>：进口传感器受全球供应链波动影响，近年交期延迟问题明显。国产传感器交期可控，支持按需生产。</li>
<li><strong>国产化要求</strong>：部分涉及航空、军工、能源等领域的项目有明确国产化采购要求，国产变频氧传感器可满足此类需求。</li>
<li><strong>技术支持响应</strong>：国内厂家可提供本土工程师支持、原厂标定服务和定制化评估，响应周期短于进口渠道。</li>
</ul>

<h2>五、价格区间参考</h2>
<p>进口宽域氧传感器（含车规型）批量价格视型号差异较大，国内代理价一般在数百元至千元以上。KD0100 系列价格请以官方报价为准，可联系销售获取。</p>
<p>综合考虑供应链风险、交期与本土技术支持，对非车用尾气场景，国产变频氧传感器是值得评估的选项。</p>

<h2>六、如何选择</h2>
<ul>
<li><strong>车用尾气 SCR 控制（国六配套）</strong>：仍需符合车规认证的专用型号，建议先确认 IATF 16949 与 OEM 认证要求。</li>
<li><strong>工业气体、面罩、实验室仪器、特种装备</strong>：KD0100 系列是可靠的国产方案，欢迎申请试样评估。</li>
</ul>
<p><a href="/contact/" class="btn btn-primary">申请试样 / 联系工程师</a></p>
""",
    },
]

CASES = [
    {
        "slug": "aviation-mask-life-support",
        "industry": "航空生命保障",
        "industry_en": "Aviation life support",
        "customer": "某航空生命保障设备厂商",
        "customer_en": "An aviation life-support equipment manufacturer",
        "date": "2024-11",
        "title": "飞行员面罩供氧监测：低温型氧传感器试制配套",
        "title_en": "Pilot Mask O₂ Monitoring — Low-Temperature Sensor Prototyping",
        "summary": "面向面罩气路的低温氧分压监测需求，完成低温型变频氧传感器试制与联调，验证量程与集成可行性。",
        "summary_en": "Low-temperature VF O₂ sensor prototyping for mask gas-path monitoring.",
        "cover": "scenes/aviation-mask.jpg",
        "product_slugs": ["mask-o2-sensor"],
        "challenge": "客户需在飞行员面罩供氧链路中增加氧相关监测能力：工作环境偏低温、安装空间受限，且必须与面罩/软管结构协同，不能简单套用汽车排气氧传感器方案。测量目标以氧分压表征，期望覆盖任务剖面相关范围。",
        "solution": "采用公司面罩用低温型变频式氧传感器试制件，围绕 0.5 ~ 101 kPa 氧分压能力与面罩气路接口进行结构适配；电气上按生命保障设备方提供的连接规范联调，形成“传感器样件 + 测试记录 + 问题闭环清单”的交付包。",
        "milestones": [
            "需求澄清：温度环境、安装包络、电气接口与验收点",
            "样件试制与气路工装适配",
            "台架/联调测试与问题闭环",
            "输出下一阶段小批与环境试验建议",
        ],
        "results": [
            "完成低温型变频氧传感器试制并实现与客户工装联调",
            "氧分压测量能力按 0.5 ~ 101 kPa 方向完成关键点验证（以联调记录为准）",
            "形成可复用的面罩集成检查单（安装、冷却、接线、验收点）",
        ],
        "body_note": "客户名已脱敏。数据与节点来自项目沟通与试制公开信息口径，细部指标以双方技术协议与试验记录为准。",
    },
    {
        "slug": "industrial-o2-online-monitoring",
        "industry": "工业气体监测",
        "industry_en": "Industrial gas monitoring",
        "customer": "某工业气体在线监测集成商",
        "customer_en": "An industrial gas online-monitoring integrator",
        "date": "2025-03",
        "title": "工艺气管路氧分压在线监测：探头型模块集成",
        "title_en": "Process Line O₂ Partial-Pressure Monitoring — Probe Integration",
        "summary": "在不锈钢工艺管路上集成 KD0100-02S-T1 探头与 KD0100-03，建立可验收的氧分压在线监测点。",
        "summary_en": "KD0100-02S-T1 + KD0100-03 integration for online O₂ partial-pressure points.",
        "cover": "scenes/industrial-gas.jpg",
        "product_slugs": ["kd0100-02s-t1"],
        "challenge": "集成商需要为客户工艺气体管路增加氧分压在线监测：介质可能为空气/氮氧混合，总压与组分变化导致“百分比显示”易误导；现场希望线束探头便于法兰/管接头改造，并能量化验收。",
        "solution": "选用 KD0100-02S-T1（线束探头）+ KD0100-03 控制器：以氧分压 0.5–101 kPa 为设计量程；安装点控制气流速率与气体温度处于公开允许范围；按白/蓝/红/灰/绿电气定义完成柜内接线，并按精度分档设计抽检点。",
        "milestones": [
            "现场勘测：管径、开孔、走线、供电与接地",
            "探头机械接口与密封方案确认",
            "控制器柜内安装与加热档位确认",
            "分档抽检与移交运维手册",
        ],
        "results": [
            "完成管路测点改造与连续监测联调",
            "按公开精度分档完成目标工况点抽检（记录归档）",
            "运维侧明确冷却后再维护、禁止私改加热线等红线",
        ],
        "body_note": "客户名已脱敏。案例描述基于典型工业集成需求与产品公开规格组织，具体项目数据以交付文档为准。",
    },
    {
        "slug": "compact-pin-oem-integration",
        "industry": "仪器仪表 OEM",
        "industry_en": "Instrumentation OEM",
        "customer": "某分析仪器 OEM 厂商",
        "customer_en": "An analytical instrument OEM",
        "date": "2025-06",
        "title": "紧凑型仪器内嵌：插针式氧传感模块减重集成",
        "title_en": "Compact Instrument Embedding — Pin-Type O₂ Module",
        "summary": "在重量与空间受限的仪器内部，采用 KD0100-02S-TO 插针方案完成板级化连接与样机验证。",
        "summary_en": "KD0100-02S-TO pin module for weight/space-constrained instrument OEM.",
        "cover": "products/kd0100-02s-to.png",
        "product_slugs": ["kd0100-02s-to"],
        "challenge": "OEM 仪器内部空间紧张，传统线束探头增加装配工时与重量；希望探头重量显著下降，并以插针方式对接内部转接板，同时保持与 T1 相同的氧分压量程与控制器生态。",
        "solution": "采用 KD0100-02S-TO（插针型，探头重量 ≦5 g）+ KD0100-03：在样机中验证插针定位、尺寸公差（≦0.5 mm）与抗振安装；电气上按控制器手册完成对接，避免加热/信号误插。",
        "milestones": [
            "结构堆叠与插针定位设计评审",
            "样机焊接/插座验证",
            "功能联调与精度抽检",
            "装配作业指导书固化",
        ],
        "results": [
            "探头侧重量按 ≦5 g 目标完成样机集成",
            "插针互联较线束方案减少柜内线束整理工时（产线反馈）",
            "形成防呆插接与上电检查步骤，降低误接线风险",
        ],
        "body_note": "客户名已脱敏。量化表述限于产品公开规格与样机集成结论，未披露客户内部商业数据。",
    },
    {
        "slug": "diesel-scr-obd-evaluation",
        "industry": "内燃机后处理",
        "industry_en": "Engine aftertreatment",
        "customer": "某柴油机后处理系统配套商",
        "customer_en": "A diesel aftertreatment system supplier",
        "date": "2025-09",
        "title": "柴油机 SCR / OBD 相关气体传感方案评估（进行中）",
        "title_en": "Diesel SCR / OBD Gas Sensing Evaluation (In Progress)",
        "summary": "围绕国Ⅵ后处理与 OBD 需求，开展氧/氮氧相关传感路线评估与台架方案设计，尚未进入车规量产认定。",
        "summary_en": "Evaluation of O₂/NOx-related sensing for China VI SCR/OBD — not yet series-production certified.",
        "cover": "scenes/automotive.jpg",
        "product_slugs": ["kd0100-02s-t1", "kd0100-02s-to"],
        "challenge": "配套商需评估排气侧气体传感在 SCR 闭环与 OBD 监控中的补充/替代路径：关注响应、耐久、抗污染与法规符合性，同时希望先用可量化的氧分压测量能力做台架方法验证。",
        "solution": "以 KD0100 系列氧分压测量能力作为台架方法验证工具之一，结合客户台架工况设计采样点；同步梳理车规级氮氧传感量产所需的认证、耐久与供应链条件，输出《可行性与缺口清单》。",
        "milestones": [
            "工况与法规条款对表",
            "台架取样与传感器安装方案",
            "数据方法验证（进行中）",
            "量产缺口与认证路径评审（规划）",
        ],
        "results": [
            "完成 SCR/OBD 相关需求与传感角色对表",
            "形成台架验证大纲与缺口清单（认证/耐久/数据包）",
            "明确：官网通用规格 ≠ 自动具备某一车型量产认可",
        ],
        "body_note": "客户名已脱敏。本案例标注为评估/进行中，不构成车规量产业绩声明。",
    },
]


def product_name(slug: str) -> str:
    names = {
        "kd0100-02s-t1": "KD0100-02S-T1 探头",
        "kd0100-02s-to": "KD0100-02S-TO 插针",
        "mask-o2-sensor": "面罩用氧传感器",
    }
    return names.get(slug, slug)
