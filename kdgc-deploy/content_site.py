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
MAP_ADDRESS = "安徽省合肥市高新区望江西路5089号嵌入式研发楼103-C3"

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
        "cover": "news/nox-sensor-market.png",
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
