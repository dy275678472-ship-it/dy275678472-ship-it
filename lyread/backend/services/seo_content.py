"""SEO 内容集群：对比文、教程、题材聚合页（P1 增长）。"""

from __future__ import annotations

# slug -> category 名称（题材聚合页）
GENRE_PAGES: dict[str, dict] = {
    "dushi": {
        "category": "都市神豪",
        "title": "都市神豪 AI 小说 - 创作案例与工具推荐",
        "description": "都市神豪题材 AI 写小说指南：爆款套路、创作案例与 LyRead 按章计费工具，约 1 元/章续写。",
        "intro": "都市神豪是中文网文热门赛道，核心爽点在于身份反转、财富碾压与打脸逆袭。",
    },
    "zhanshen": {
        "category": "战神归来",
        "title": "战神归来 AI 小说 - 案例与创作指南",
        "description": "战神归来题材 AI 写作：归来打脸、护女/护家套路与长篇续写工具 LyRead。",
        "intro": "战神归来融合兵王、赘婿、都市异能等元素，开篇冲突强、情绪拉满。",
    },
    "chongsheng": {
        "category": "重生",
        "title": "重生流 AI 小说 - 创作案例与工具",
        "description": "重生题材 AI 写小说：利用前世记忆逆袭、商业/高考等经典设定与续写方案。",
        "intro": "重生文读者爱看「先知先觉」带来的碾压感，大纲与伏笔管理尤为重要。",
    },
    "xianxia": {
        "category": "仙侠玄幻",
        "title": "仙侠玄幻 AI 小说 - 长篇创作指南",
        "description": "仙侠玄幻 AI 写作：境界体系、修炼升级与长篇记忆工具，适合日更连载。",
        "intro": "玄幻仙侠需要稳定的力量体系与人物关系，写到后期最怕设定漂移。",
    },
    "yanqing": {
        "category": "言情甜宠",
        "title": "言情甜宠 AI 小说 - 案例与创作技巧",
        "description": "言情甜宠 AI 写小说：感情线、虐甜节奏与短篇/长篇创作工具推荐。",
        "intro": "言情重情绪共鸣与人物关系张力，适合短篇盐选与长篇连载双线布局。",
    },
    "xuanyi": {
        "category": "悬疑推理",
        "title": "悬疑推理 AI 小说 - 创作指南",
        "description": "悬疑推理 AI 写作：伏笔布局、线索管理与章节续写，LyRead 小说大脑记伏笔。",
        "intro": "悬疑类对伏笔一致性要求极高，需要工具辅助记录线索与人物动机。",
    },
    "xitong": {
        "category": "系统流",
        "title": "系统流 AI 小说 - 爆款套路与工具",
        "description": "系统流 AI 写小说：任务、奖励、升级节奏与长篇连载创作平台。",
        "intro": "系统文节奏快、爽点密集，适合日更与快速试错不同系统设定。",
    },
    "duanpian": {
        "category": "短篇故事",
        "title": "AI 短故事生成 - 盐选/公众号短篇工具",
        "description": "AI 一键生成约 3000 字完整短篇，适合盐选、公众号与知乎短篇赛道。",
        "intro": "短篇要求结构完整、反转有力，LyRead 提供独立短故事生成流程（约 15 点/篇）。",
    },
    "moshi": {
        "category": "末世求生",
        "title": "末世求生 AI 小说 - 囤货/异能创作指南",
        "description": "末世题材 AI 写作：极寒、丧尸、高温等设定与囤货流套路，LyRead 长篇续写工具。",
        "intro": "末世文开局节奏要快，囤货清单与异能体系是读者留存关键。",
    },
    "gongting": {
        "category": "宫廷权谋",
        "title": "宫廷权谋 AI 小说 - 宫斗/古言创作案例",
        "description": "古言宫斗 AI 写小说：妃嫔争斗、权谋布局与长篇记忆工具推荐。",
        "intro": "宫斗文重人物关系网与伏笔，写到后期需要工具辅助记恩怨。",
    },
    "saibo": {
        "category": "赛博朋克",
        "title": "赛博朋克 AI 小说 - 科幻短篇与长篇指南",
        "description": "赛博朋克 AI 写作：高科技低生活、义体改造与反乌托邦叙事创作工具。",
        "intro": "赛博朋克融合科幻与社会批判，适合中短篇试水再扩成长篇。",
    },
    "zhuixu": {
        "category": "赘婿逆袭",
        "title": "赘婿流 AI 小说 - 隐忍逆袭创作指南",
        "description": "赘婿题材 AI 写小说：忍辱三年、身份曝光、打脸岳家经典套路与续写方案。",
        "intro": "赘婿文情绪压抑后的爆发是核心爽点，章纲需标注每次打脸节点。",
    },
    "kehuan": {
        "category": "科幻脑洞",
        "title": "科幻脑洞 AI 小说 - 末世/星际创作指南",
        "description": "科幻脑洞 AI 写作：星际、末世、记忆交易等设定与长篇续写工具 LyRead。",
        "intro": "科幻脑洞重设定新颖与世界观自洽，适合中篇试水再扩成长篇。",
    },
    "xiaoyuan": {
        "category": "校园青春",
        "title": "校园青春 AI 小说 - 学霸/甜宠创作案例",
        "description": "校园青春 AI 写小说：学霸逆袭、校草甜宠、重生高三等经典套路与续写方案。",
        "intro": "校园文节奏轻快、代入感强，适合短篇盐选与青春长篇双线布局。",
    },
    "youxi": {
        "category": "游戏竞技",
        "title": "游戏竞技 AI 小说 - 电竞/网游创作指南",
        "description": "游戏竞技 AI 写作：电竞复出、隐藏职业、网游降临现实等爆款套路与续写工具。",
        "intro": "游戏文爽点密集、节奏快，章纲需标注每次高光操作与打脸节点。",
    },
    "lishi": {
        "category": "历史架空",
        "title": "历史架空 AI 小说 - 穿越/权谋创作指南",
        "description": "历史架空 AI 写小说：穿越大明、大唐、三国等经典设定与长篇记忆工具推荐。",
        "intro": "历史架空需兼顾史实与爽点，人物关系与朝堂势力网是长篇不崩盘关键。",
    },
    "mengbao": {
        "category": "萌宝甜宠",
        "title": "萌宝甜宠 AI 小说 - 带娃追妻创作案例",
        "description": "萌宝甜宠 AI 写作：带球跑、萌宝助攻、前夫追妻火葬场等经典套路与续写方案。",
        "intro": "萌宝文靠可爱与助攻制造甜虐节奏，感情线回收是读者留存关键。",
    },
    "lingyi": {
        "category": "灵异悬疑",
        "title": "灵异悬疑 AI 小说 - 无限流/恐怖创作指南",
        "description": "灵异悬疑 AI 写小说：凶宅轮回、镜中异象、废弃医院等恐怖设定与伏笔管理工具。",
        "intro": "灵异文重氛围营造与线索一致性，小说大脑可辅助记录伏笔与轮回规则。",
    },
}


COMPARE_PAGES: dict[str, dict] = {
    "biling": {
        "title": "LyRead vs 笔灵AI写作：写长篇网文哪个更合适？",
        "description": "对比 LyRead 与笔灵 AI 写作：长篇记忆、按章计费、大纲工作流与适用人群，帮你选对 AI 写小说工具。",
        "keywords": "LyRead,笔灵AI写作,AI写小说对比,网文创作工具",
        "h1": "LyRead vs 笔灵：长篇网文该选谁？",
        "sections": [
            ("一句话结论", """
            <p><strong>笔灵</strong>适合「不想搭结构、快速出稿」的通用写作场景；<strong>LyRead</strong>适合「要写长篇连载、在意设定一致性、希望按章透明计费」的网文作者。</p>
            """),
            ("核心差异", """
            <table style="width:100%;border-collapse:collapse;font-size:14px">
            <tr style="background:#f8fafc"><th style="padding:10px;text-align:left">维度</th><th>LyRead</th><th>笔灵 AI</th></tr>
            <tr><td style="padding:10px">定位</td><td>长篇网文工作流</td><td>通用 AI 写作助手</td></tr>
            <tr style="background:#f8fafc"><td style="padding:10px">长篇记忆</td><td>小说大脑（人物/伏笔）</td><td>有限</td></tr>
            <tr><td style="padding:10px">计费</td><td>按章点数，约 1 元/章</td><td>套餐/订阅为主</td></tr>
            <tr style="background:#f8fafc"><td style="padding:10px">上手难度</td><td>中等（7 步向导）</td><td>极低</td></tr>
            </table>
            """),
            ("什么时候选 LyRead", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>计划日更长篇、写到 50 章以上</li>
              <li>需要大纲 → 章纲 → 正文的标准网文流程</li>
              <li>希望按量付费，失败不扣点</li>
              <li>要写盐选短篇 + 长篇双线</li>
            </ul>
            """),
            ("什么时候选笔灵", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>偶尔写一篇、不想学工作流</li>
              <li>公文、简历、营销文案等混合需求</li>
              <li>追求一键出全文，对结构要求不高</li>
            </ul>
            """),
        ],
        "faqs": [
            ("LyRead 比笔灵贵吗？", "LyRead 按章约 1 元计费，无月费；笔灵多为套餐制。按写作量不同，各有优势。"),
            ("能否两个一起用？", "可以。用笔灵做灵感碰撞，用 LyRead 做长篇结构化连载。"),
        ],
    },
    "waqupin": {
        "title": "LyRead vs 蛙趣拼文：长篇 AI 写作工具对比",
        "description": "LyRead 与蛙趣拼文（蛙蛙写作）对比：云端 SaaS vs 本地工具、计费模式、长篇记忆与适用场景。",
        "keywords": "LyRead,蛙趣拼文,蛙蛙写作,AI小说软件对比",
        "h1": "LyRead vs 蛙趣拼文：云端连载 vs 本地重度工具",
        "sections": [
            ("产品形态", """
            <p><strong>蛙趣拼文</strong>偏本地客户端 + 自备 API，适合愿意折腾模型密钥、深度管控数据的作者。<strong>LyRead</strong>是开箱即用的 Web SaaS，注册即用，按点数计费。</p>
            """),
            ("长篇能力对比", """
            <ul style="line-height:1.9;padding-left:20px">
              <li><strong>设定管理：</strong>两者都强调世界观/角色/伏笔；LyRead 以「小说大脑」自动摘要同步</li>
              <li><strong>工作流：</strong>LyRead 提供书名→大纲→章纲→续写一条龙向导</li>
              <li><strong>成本：</strong>LyRead 10 元=100 点；蛙趣需自付 API + 软件费用</li>
            </ul>
            """),
            ("推荐选择", """
            <p>如果你要<strong>快速开书、不想配 API</strong>，选 LyRead；如果你要<strong>本地私有化、深度自定义模型</strong>，蛙趣拼文更合适。</p>
            """),
        ],
        "faqs": [
            ("LyRead 需要自备 API 吗？", "不需要。平台已接入模型，按点数扣费即可。"),
        ],
    },
    "chatgpt": {
        "title": "LyRead vs 直接用 ChatGPT 写小说：为什么要用专业工具？",
        "description": "ChatGPT 写小说的问题：设定漂移、无章纲工作流、成本难控。LyRead 如何解决长篇连载痛点。",
        "keywords": "ChatGPT写小说,LyRead,AI长篇创作,网文AI工具",
        "h1": "ChatGPT 能写小说，但很难写「长篇连载」",
        "sections": [
            ("ChatGPT 的三大短板", """
            <ol style="line-height:1.9;padding-left:20px">
              <li><strong>记忆有限：</strong>写到后期容易忘记人物设定与伏笔</li>
              <li><strong>无网文工作流：</strong>缺少章纲、爽点标签、批量规划</li>
              <li><strong>成本不透明：</strong>长对话 Token 消耗难估算</li>
            </ol>
            """),
            ("LyRead 的针对性设计", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>7 步创作向导：题材→灵感→书名→设定→大纲→章纲→续写</li>
              <li>小说大脑：自动维护人物档案与章节摘要</li>
              <li>按章计费：约 2000 字 = 10 点 ≈ 1 元，失败全额返还</li>
            </ul>
            """),
            ("最佳实践", """
            <p>用 ChatGPT 做头脑风暴与设定碰撞，用 LyRead 做<strong>结构化连载与正文生产</strong>，效率最高。</p>
            """),
        ],
        "faqs": [
            ("我还能用自己的 Prompt 吗？", "可以。LyRead 支持自定义题材、灵感与续写风格。"),
        ],
    },
    "kimi": {
        "title": "LyRead vs Kimi 写小说：专业连载工具对比",
        "description": "Kimi 长文本能力强，但缺少网文工作流。对比 LyRead 在章纲、伏笔记忆与按章计费上的优势。",
        "keywords": "Kimi写小说,LyRead,AI长篇创作,网文工具对比",
        "h1": "Kimi 能聊小说，LyRead 能连载小说",
        "sections": [
            ("Kimi 的优势", """
            <p>Kimi 擅长长上下文对话与资料整理，适合头脑风暴、设定碰撞与片段润色。</p>
            """),
            ("连载场景的缺口", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>缺少书名→大纲→章纲→续写的标准网文流程</li>
              <li>人物/伏笔需人工维护，写到后期易漂移</li>
              <li>长对话 Token 成本难估算</li>
            </ul>
            """),
            ("LyRead 的补位", """
            <p>用 Kimi 做灵感，用 LyRead 做<strong>结构化连载</strong>：小说大脑记伏笔，按章约 1 元透明计费，失败全额返还。</p>
            """),
        ],
        "faqs": [
            ("可以两个一起用吗？", "推荐。Kimi 碰撞设定，LyRead 落地大纲与正文续写。"),
        ],
    },
    "doubao": {
        "title": "LyRead vs 豆包写小说：哪个更适合网文作者？",
        "description": "豆包通用 AI 助手 vs LyRead 网文专用工作流：对比长篇记忆、计费模式与案例生态。",
        "keywords": "豆包写小说,LyRead,AI网文,小说续写工具",
        "h1": "豆包出稿快，LyRead 连载稳",
        "sections": [
            ("豆包适合什么", """
            <p>豆包是通用对话助手，适合快速生成片段、改写段落、头脑风暴书名与梗概。</p>
            """),
            ("网文作者的痛点", """
            <p>写到 30 章以后，设定一致性、章纲节奏、伏笔回收成为核心难题——这正是专业网文工具的价值所在。</p>
            """),
            ("为什么选 LyRead 做连载", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>7 步创作向导，专为中文网文设计</li>
              <li>40+ 公开案例可参考风格与节奏</li>
              <li>按章计费，无月费绑架</li>
            </ul>
            """),
        ],
        "faqs": [
            ("豆包写的能导入 LyRead 吗？", "可以。把已有大纲/设定粘贴进创作台，从章纲或续写步骤继续。"),
        ],
    },
    "tongyi": {
        "title": "LyRead vs 通义千问写小说：通用大模型 vs 网文工作流",
        "description": "通义千问适合对话与通用写作，LyRead 专为长篇网文连载设计。对比工作流、记忆与计费。",
        "keywords": "通义千问写小说,LyRead,AI网文工具对比",
        "h1": "通义千问聊得好，LyRead 连载稳",
        "sections": [
            ("通义千问的优势", "<p>阿里通义在中文理解与长对话上表现优秀，适合灵感碰撞与片段改写。</p>"),
            ("长篇连载缺口", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>无网文专用章纲/爽点标签工作流</li>
              <li>人物伏笔需自行维护</li>
              <li>API 按 Token 计费，长篇成本难控</li>
            </ul>
            """),
            ("推荐组合", "<p>通义做设定脑暴，LyRead 做<strong>大纲→章纲→续写</strong>结构化生产。</p>"),
        ],
        "faqs": [],
    },
    "wenxin": {
        "title": "LyRead vs 文心一言写小说：哪个更适合日更作者？",
        "description": "百度文心一言与 LyRead 对比：网文工作流、按章计费、案例库与长篇记忆能力。",
        "keywords": "文心一言写小说,LyRead,网文日更,AI写作",
        "h1": "文心通用，LyRead 专精网文",
        "sections": [
            ("文心一言", "<p>百度文心适合公文、营销、通用创作，一键出稿体验好。</p>"),
            ("日更作者需求", "<p>日更需要：稳定章纲、伏笔一致、成本可算——这是垂直工具的价值。</p>"),
            ("LyRead 差异", """
            <ul style="line-height:1.9;padding-left:20px">
              <li>60+ 公开案例可参考</li>
              <li>小说大脑自动记人物/伏笔</li>
              <li>约 1 元/章，失败返还</li>
            </ul>
            """),
        ],
        "faqs": [],
    },
}


GUIDE_PAGES: dict[str, dict] = {
    "ai-novel-start": {
        "title": "AI写小说入门教程（2026）- 从灵感到第一章",
        "description": "AI 写小说完整入门：选题材、生成书名大纲、写第一章正文。LyRead 免费试用书名生成，注册送 30 点。",
        "keywords": "AI写小说入门,AI小说教程,网文创作,智能写作",
        "h1": "AI 写小说入门：5 步开书",
        "sections": [
            ("第 1 步：确定题材与爽点", "选择都市、玄幻、重生等赛道，明确核心爽点（打脸、逆袭、升级等）。"),
            ("第 2 步：生成书名与钩子", "用 AI 一次生成 5 个爆款书名，选点击欲望最强的。"),
            ("第 3 步：写宏观大纲", "起承转合 + 分卷结构，避免写到中期崩盘。"),
            ("第 4 步：批量章纲", "一次规划 10–30 章，每章标注爽点标签。"),
            ("第 5 步：正文续写", "按章生成约 2000 字，利用小说大脑保持前后一致。"),
        ],
    },
    "outline-chapters": {
        "title": "AI 小说大纲与章纲怎么写？附工作流模板",
        "description": "网文大纲、章纲写法与 AI 辅助流程。如何用 LyRead 批量生成章纲并标注爽点。",
        "keywords": "AI小说大纲,章纲生成,网文结构,写作模板",
        "h1": "大纲 + 章纲：长篇不崩盘的骨架",
        "sections": [
            ("宏观大纲要包含什么", "主线目标、反派势力、感情线、高潮节点与结局走向。"),
            ("章纲颗粒度", "每章 50 字内写清：冲突、爽点、伏笔埋设/回收。"),
            ("AI 辅助技巧", "先锁定大纲再生成章纲；章纲不满意可单章重写，成本低（5 点/批）。"),
        ],
    },
    "daily-update": {
        "title": "网文日更 AI 续写技巧 - 如何稳定产出 6000 字",
        "description": "日更作者如何用 AI 续写：节奏控制、一致性检查、点数成本估算（约 3 元/天）。",
        "keywords": "网文日更,AI续写,章节续写,长篇小说",
        "h1": "日更 6000 字：AI 续写实操",
        "sections": [
            ("成本估算", "6000 字 ≈ 3 章 × 10 点 = 30 点 ≈ 3 元/天；注册送 30 点可试跑一天。"),
            ("节奏建议", "上午章纲、下午正文；每 10 章做一次一致性检查（2 点）。"),
            ("避免 AI 味", "续写后人工改对话与细节；保持人称与时态统一。"),
        ],
    },
    "monetize": {
        "title": "AI 写小说怎么赚钱？2026 实战路径",
        "description": "网文投稿、盐选短篇、公众号连载……用 AI 辅助创作变现的 4 条路径与工具选择。",
        "keywords": "AI写小说赚钱,网文变现,盐选短篇,AI创作",
        "h1": "AI 写小说变现：4 条可走路径",
        "sections": [
            ("路径 1：长篇连载投稿", "番茄、起点等平台日更连载，AI 辅助章纲与续写，人工润色降 AI 味。"),
            ("路径 2：盐选/知乎短篇", "3000 字完整短篇，结构紧凑、反转有力；LyRead 短故事流程约 15 点/篇。"),
            ("路径 3：公众号/自媒体", "日更 2000–4000 字连载文，靠流量与广告分成；成本约 1–2 元/天。"),
            ("路径 4：工作室批量产出", "标准化大纲+章纲模板，团队分工：AI 出稿、人工质检、多账号分发。"),
        ],
    },
    "consistency": {
        "title": "AI 写长篇小说如何保持设定一致？",
        "description": "人物漂移、伏笔遗忘是长篇 AI 写作最大痛点。LyRead 小说大脑 + 一致性检查实操指南。",
        "keywords": "AI小说一致性,伏笔管理,长篇记忆,小说大脑",
        "h1": "长篇不崩盘：设定一致性指南",
        "sections": [
            ("三大常见翻车点", "人物性格突变、时间线矛盾、伏笔有头无尾。"),
            ("小说大脑怎么用", "每章续写后自动更新人物档案与章节摘要；每 10 章手动做一次一致性检查（2 点）。"),
            ("人工必做清单", "续写后检查：人称、关键道具、势力关系、未回收伏笔列表。"),
        ],
    },
    "platform-submit": {
        "title": "AI 小说投稿平台指南：番茄/起点/盐选怎么选？",
        "description": "2026 中文网文投稿平台对比：长篇连载、短篇盐选、AI 辅助创作注意事项与工具推荐。",
        "keywords": "AI小说投稿,番茄小说,起点,盐选,网文平台",
        "h1": "AI 辅助创作，投稿平台怎么选？",
        "sections": [
            ("长篇连载：番茄/起点/七猫", "日更 4000–6000 字，AI 辅助章纲+续写，人工润色降 AI 味；注意各平台签约与分成规则。"),
            ("短篇盐选：知乎/番茄短篇", "3000 字完整结构，反转结尾；LyRead 短故事流程可快速试错多个梗。"),
            ("投稿前检查清单", "人称统一、无敏感内容、开篇 3 章钩子足够强、人工修改对话与细节。"),
        ],
    },
    "reduce-ai-taste": {
        "title": "AI 写小说如何降 AI 味？7 个实操技巧",
        "description": "降低 AI 生成小说机械感：对话润色、细节植入、节奏人工调整，附 LyRead 续写后处理流程。",
        "keywords": "降AI味,AI小说润色,网文人工修改,AI写作技巧",
        "h1": "降 AI 味：续写后的 7 步人工处理",
        "sections": [
            ("1. 改对话", "AI 对话常过于书面，改成口语化、加语气词与停顿。"),
            ("2. 加感官细节", "每段补 1 个视觉/听觉/嗅觉细节，增强画面感。"),
            ("3. 删套话", "去掉「不禁」「竟然」「顿时」等 AI 高频词。"),
            ("4. 调整节奏", "爽点前铺垫可缩短，高潮后加余韵段落。"),
            ("5. 统一人称", "检查「他/她」与视角是否一致。"),
            ("6. 植入个人风格", "固定几个口头禅、比喻习惯，形成作者辨识度。"),
            ("7. 用工具辅助", "LyRead 章纲标注爽点，续写后集中做一轮人工润色，比逐句改更高效。"),
        ],
    },
}


def all_static_seo_paths() -> list[tuple[str, str, str]]:
    """返回 (path, changefreq, priority) 供 sitemap 使用。"""
    today_paths = [
        ("/compare", "weekly", "0.85"),
        ("/guide", "weekly", "0.85"),
        ("/genre", "weekly", "0.8"),
    ]
    for slug in COMPARE_PAGES:
        today_paths.append((f"/compare/{slug}", "monthly", "0.8"))
    for slug in GUIDE_PAGES:
        today_paths.append((f"/guide/{slug}", "monthly", "0.8"))
    for slug in GENRE_PAGES:
        today_paths.append((f"/genre/{slug}", "weekly", "0.75"))
    return today_paths


def compare_slugs() -> list[str]:
    return list(COMPARE_PAGES.keys())


def guide_slugs() -> list[str]:
    return list(GUIDE_PAGES.keys())


def genre_slugs() -> list[str]:
    return list(GENRE_PAGES.keys())
