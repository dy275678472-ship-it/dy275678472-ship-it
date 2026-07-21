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
}


def all_static_seo_paths() -> list[tuple[str, str, str]]:
    """返回 (path, changefreq, priority) 供 sitemap 使用。"""
    today_paths = [
        ("/compare", "weekly", "0.85"),
        ("/guide", "weekly", "0.85"),
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
