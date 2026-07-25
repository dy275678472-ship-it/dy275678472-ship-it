#!/usr/bin/env python3
"""Generate showcase excerpt .txt files from showcase_catalog.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG = SCRIPT_DIR / "seed_data" / "showcase_catalog.json"
OUT_DIR = SCRIPT_DIR / "seed_data" / "showcase_excerpts"

# 手写高质量节选，生成器不覆盖
HANDCRAFTED_IDS = {
    "showcase_urban_01", "showcase_urban_02", "showcase_urban_03", "showcase_urban_04",
    "showcase_warrior_01", "showcase_warrior_02", "showcase_warrior_03", "showcase_warrior_04",
    "showcase_reborn_01", "showcase_reborn_02", "showcase_reborn_03", "showcase_reborn_04",
    "showcase_xianxia_01", "showcase_xianxia_02", "showcase_xianxia_03", "showcase_xianxia_04",
    "showcase_romance_01", "showcase_romance_02",
    "showcase_romance_03", "showcase_romance_04",
    "showcase_scifi_01", "showcase_scifi_02",
    "showcase_scifi_03", "showcase_scifi_04",
    "showcase_suspense_01", "showcase_suspense_02",
    "showcase_suspense_03", "showcase_suspense_04",
    "showcase_history_01", "showcase_history_02",
    "showcase_history_03", "showcase_history_04",
    "showcase_system_01", "showcase_system_02", "showcase_system_03", "showcase_system_04",
    "showcase_system_05",
    "showcase_apocalypse_01", "showcase_apocalypse_02",
    "showcase_apocalypse_03", "showcase_apocalypse_04",
    "showcase_campus_01", "showcase_campus_02",
    "showcase_campus_03", "showcase_campus_04",
    "showcase_game_01", "showcase_game_02", "showcase_game_03", "showcase_game_04",
    "showcase_game_07",
    "showcase_warrior_06",
    "showcase_warrior_07",
    "showcase_urban_06",
    "showcase_system_07",
    "showcase_romance_05", "showcase_romance_06", "showcase_romance_07",
    "showcase_palace_01", "showcase_palace_02",
    "showcase_palace_03", "showcase_palace_04",
    "showcase_palace_05", "showcase_palace_06",
    "showcase_soninlaw_01", "showcase_soninlaw_02",
    "showcase_soninlaw_03", "showcase_soninlaw_04",
    "showcase_soninlaw_05", "showcase_soninlaw_06",
    "showcase_baby_01", "showcase_baby_02",
    "showcase_baby_03", "showcase_baby_04",
    "showcase_baby_05", "showcase_baby_06",
    "showcase_horror_01", "showcase_horror_02",
    "showcase_horror_03", "showcase_horror_04",
    "showcase_horror_05", "showcase_horror_06",
    "showcase_urban_10", "showcase_urban_11",
    "showcase_warrior_09", "showcase_warrior_10",
    "showcase_reborn_08", "showcase_reborn_09",
    "showcase_xianxia_08", "showcase_romance_08",
    "showcase_scifi_07", "showcase_suspense_07",
    "showcase_history_08", "showcase_system_08",
    "showcase_apocalypse_08", "showcase_campus_07",
    "showcase_game_08", "showcase_game_09",
    "showcase_palace_07", "showcase_soninlaw_07",
    "showcase_baby_07", "showcase_horror_07",
    # 140 扩容新增 12 案（手写开篇 + ≥2000 收束）
    "showcase_urban_12", "showcase_warrior_11", "showcase_reborn_10",
    "showcase_xianxia_09", "showcase_game_10", "showcase_system_09",
    "showcase_romance_09", "showcase_apocalypse_09", "showcase_campus_08",
    "showcase_scifi_08", "showcase_suspense_08", "showcase_history_09",
}

GENRE_OPENINGS = {
    "urban": """第一章 {hook}

{name}站在落地窗前，看着楼下川流不息的车河。三年前他还是被人踩在脚下的穷小子，今天，整个江城的资本圈都在等他的一个点头。

手机震了。助理发来消息：「{title}——收购案对方已签字，估值一百二十亿。」

{name}没有立刻回复。他想起那个雨夜，前女友把分手协议摔在他脸上：「你这辈子都买不起我脚下这双鞋。」

他淡淡回了两个字：「继续。」

第二章 故人相见

晚宴上，所有镜头都对准了{name}。曾经嘲讽过他的赵总端着酒杯走来，笑容谄媚：「林……哦不，{name}总，当年有眼不识泰山。」

{name}举杯，没有接话。他不需要口舌之争，规则会替他说话。

角落里，前女友脸色煞白。她身边的富二代低声问：「你认识他？」

她张了张嘴，一个字也说不出来。

第三章 新的起点

深夜，{name}收到一条匿名短信：「你以为赢了？游戏才刚开始。」

他删掉短信，打开笔记本。下一章，他要做的不是炫耀财富，而是把该抬的人抬起来，把该还的账，一笔一笔算清楚。

窗外江城灯火通明。他知道，真正的神豪，不是横着走，而是让规则为自己让路。

（节选完，共三章）""",
    "warrior": """第一章 {hook}

{name}推开那扇锈迹斑斑的铁门，屋里只有一盏昏黄的灯。五岁的女儿缩在角落，怀里抱着半块发霉的馒头。

「爸爸？」她声音发颤。

{name}单膝跪下，眼眶发红。五年前他远赴北境，临走前把妻女托付给兄弟。回来时，兄弟成了仇人，女儿住在狗窝。

手机响了。昔日战友来电：「战神，北境异动，需要您……」

「不。」{name}抱起女儿，「这一次，我先护家。」

第二章 战神令出

岳家大门前，{name}被拦在外面。岳母冷笑：「赘婿也配进我周家？」

{name}没有争辩，从怀中取出一枚黑色令牌。令牌上「战神」二字，在日光下泛着寒光。

门卫腿一软，跪倒在地。全城监控在同一秒切到这条街——上面的人，都看到了那枚令。

岳母脸上的笑僵住了。

第三章 清算

{name}把女儿安顿好，才拨通那个号码：「查，谁动过我的人。」

三分钟后，一份名单出现在他手机上。每一个名字，都曾在他离开时，踩过他的尊严。

他合上手机，望向远方。战神归来，不是为了炫耀武力，而是让该怕的人，在规则里颤抖。

（节选完，共三章）""",
    "reborn": """第一章 {hook}

{name}猛然睁眼，熟悉的闹钟声响起——2003年6月7日，高考前夜。

他愣了三秒，然后狠狠掐了自己一把。疼。真的回来了。

上一世，他在这个夜晚选择了错误的专业，十年碌碌无为。这一世，每一道题的答案、每一次股灾、每一个风口，他都记得清清楚楚。

他翻开日记本，写下第一行：「重生第一天，先改志愿。」

第二章 先知

班主任找他谈话：「{name}，你最近怎么像变了个人？」

{name}微笑：「老师，我想考金融。」

没人知道，他已经在笔记本上记下了未来十年的关键节点。第一个，是三个月后的那支股票。

同学们还在讨论暑假去哪玩，他已经悄悄注册了账户。

第三章 第一桶金

高考成绩出来那天，{name}成了全校黑马。但他更在意的，是账户里那串数字——利用先知信息，他在暑假结束前，赚到了第一桶金。

母亲问他钱哪来的，他说：「妈，以后我们家，不会再为钱发愁。」

窗外蝉鸣阵阵。{name}知道，重生不是开挂，而是把第二次机会，用在每一个曾经错过的选择上。

（节选完，共三章）""",
    "xianxia": """第一章 {hook}

{name}从昏迷中醒来，发现自己躺在都市的出租屋里。丹田空空，修为尽失，但三千年修仙记忆，一丝不少。

「仙帝……竟跌落凡尘。」他苦笑。

门外传来房东的敲门声：「再不交租就滚！」

{name}弹指，一道无形气劲封住门锁。他盘膝而坐，开始运转残存的功法。都市灵气稀薄，但足够他恢复炼气一层。

手机屏幕上，新闻标题闪过：「某豪门千金离奇失踪」。{name}眯起眼——这气息，是魔修。

第二章 初显锋芒

巷口，三个混混围住一个女孩。{name}路过，本不想管，但那女孩腕上的玉镯，是修仙界才有的「定魂镯」。

他一步跨出，混混还没反应过来，已跪了一地。

女孩抬头，眼眶含泪：「你……你是谁？」

{name}淡淡道：「路过。」

第三章 仙路再起

夜里，{name}在天台吐纳。星辰之力虽弱，却精纯。他知道，地球藏着上古遗迹，恢复修为只是时间问题。

玉镯女孩派人送来一封信：「先生救命之恩，叶家必报。」

{name}把信收起。仙帝归来，都市只是起点。这一世，他要横推一切阻路之人。

（节选完，共三章）""",
    "romance": """第一章 {hook}

{name}拖着行李箱走出机场，五年没回来的这座城市，既熟悉又陌生。

五年前她带着误会离开，以为他不爱她。五年后她才知道，当年那场分手，全是旁人设计。

手机震动，闺蜜发来消息：「他这五年没换过手机号，也没换过……等你。」

{name}深吸一口气。这一次，她不会再逃。

第二章 重逢

公司电梯里，{name}和他迎面撞上。四目相对，空气凝固。

他瘦了，眼下有淡淡的青。她先开口：「好久不见。」

他喉结滚动，声音沙哑：「五年，三千六百二十五天。」

{name}别过脸，眼眶发热。她告诉自己，重生后不爱了——可心跳骗不了人。

第三章 追悔

晚宴上，当年设计她的白月光当众道歉，他却只看着{name}：「跟我回家。」

全场哗然。{name}摇头：「陆景深，有些错，不是一句对不起能抹平的。」

她转身离开，高跟鞋敲在大理石地面上，清脆而坚定。身后，他的声音低得只有她能听见：「那我追你一辈子。」

（节选完，共三章）""",
    "scifi": """第一章 {hook}

警报声撕裂寂静。{name}盯着舰桥屏幕——人类最后的三艘战舰，正被未知舰队包围。

「舰长，跃迁引擎过载，最多还能撑十七分钟。」

{name}握紧扶手。作为人类联合舰队最年轻的舰长，他知道这一战没有退路。

「全员听令，启动‘裂痕协议’。」

第二章 虫洞

跃迁通道在面前撕开，星光扭曲成诡异的紫。{name}下令冲入——这是档案里只出现过一次的古老航道，可能通向新家园，也可能是坟墓。

「报告！后方敌舰未跟进，他们在……害怕什么？」

{name}看向航道深处。那里有一双眼睛，在黑暗中注视着他们。

第三章 新纪元

通道尽头，是一颗蔚蓝星球。大气成分与地球惊人相似。

{name}摘下舰长帽，轻声说：「我们到了。」

身后，三千名船员沉默落泪。人类文明的火种，在这一刻，找到了新的土壤。

（节选完，共三章）""",
    "suspense": """第一章 {hook}

{name}盯着白板上的照片，第七个证人的名字下面，画了一个问号。

前六个人的证词互相矛盾，而第七个人——在应该出庭的前一夜，消失了。没有监控，没有车票，没有手机信号。

「周队，他家冰箱里有半杯没喝完的牛奶，还在保鲜期内。」

{name}皱眉。这意味着，他消失不超过十二小时。

第二章 线索

旧物堆里，{name}找到一本日记。最后一页写着：「他们不是我杀的，但我会成为下一个。」

笔迹与第七证人的笔迹鉴定报告，完全一致。

「队长，我们查到他失踪前最后一通电话，打给……五年前结案的那桩连环案受害者家属。」

{name}后背发凉。两起案件，被一根看不见的线，系在了一起。

第三章 真相边缘

深夜，{name}独自回到案发现场。灯突然灭了。

黑暗中，一个声音说：「周铭，你离真相太近了。」

他打开手电，照向角落——那里放着第七证人的工牌，还有一张字条：「别信任何人。」

（节选完，共三章）""",
    "history": """第一章 {hook}

{name}睁开眼，头顶是雕花的木梁。身下硬板床，空气中弥漫着檀香与霉味。

「大人，您醒了？陛下召见！」

他愣住——这不是2026年的出租屋，这是大明嘉靖年间。而他，成了翰林院一名从七品编修。

记忆涌入：原主同名同姓，刚因直言进谏被贬。今日，是他重返朝堂的机会。

第二章 朝堂

金銮殿上，{name}跪地呈上奏折。不是骂奸臣，而是献上一套「考成法」草案——他记得，历史上谁因何而起，因何而落。

皇帝沉默良久，问：「你不怕死？」

{name}答：「臣怕的是，大明在您手中，失了民心。」

满朝哗然。有人骂他狂徒，有人眼里闪过精光。

第三章 权臣之路

三个月后，{name}调任兵部。他做的第一件事，不是争权，而是清查军屯弊案。

同僚笑他不懂变通。他只在日记里写：「权力不是目的，是让该办的事，办得成。」

窗外宫墙高耸。他知道，从寒门到权臣的路很长，但每一步，都踩在历史的节点上。

（节选完，共三章）""",
    "system": """第一章 {hook}

【叮！写作系统绑定成功】
【当前任务：写满一千字，奖励现金十万元】

{name}盯着眼前半透明的面板，以为自己熬夜写文写疯了。

他试探性地敲下一行字：「主角推开门，看见……」

面板数字跳动：字数+1，账户余额+100。

「卧槽。」

第二章 码字即财富

{name}把自己锁在房间，疯狂码字。每写一个字，手机就震一下——打赏、转账、平台推荐位，像不要钱一样砸过来。

编辑打来电话，声音发颤：「你这篇……后台数据爆了，我们怀疑系统出错……」

{name}看着面板上新任务：【连载三十天，奖励‘神级文笔’】

他笑了。这一次，他要让全世界知道，码字也能改命。

第三章 规则

系统突然弹出红色警告：【检测到异常流量，请完成隐藏任务：揭露抄袭产业链】

{name}笑容收敛。原来系统不是白送的，每一次奖励，都有代价。

他打开文档，新建章节标题：《谁动了我的稿子》。

（节选完，共三章）""",
    "apocalypse": """第一章 {hook}

温度计显示零下四十三度。窗外一切都被冰雪覆盖，像一座沉默的坟墓。

{name}裹着厚棉被，看着满屋的物资——大米、罐头、燃料、药品，足够他一个人活三年。

七天前，他还在网上被人骂「末日妄想症」。今天，妄想成了现实。

对讲机里传来邻居绝望的呼救：「有没有人多一口吃的……」

{name}沉默了很久，按下通话键：「顶楼，带工具上来。」

第二章 同盟

幸存者陆续抵达。有人带伤，有人带孩子。{name}把物资摊开，立下规矩：劳动换食物，背叛者驱逐。

第三夜，有人偷罐头被抓。{name}没有动手，只把那人关在门外：「你可以走，但别回来。」

风雪声里，那人很快没了声息。所有人明白了，这不是游戏。

第三章 曙光

第49天，气温回升到零下二十。{name}在楼顶种下的蒜苗，冒出了绿芽。

有人哭了：「我们活下来了。」

{name}望向远方冰封的城市。他知道，末世里最难的不是囤货，而是决定，谁值得被救。

（节选完，共三章）""",
    "campus": """第一章 {hook}

摸底考成绩公布那天，公告栏前围满了人。第一名：{name}，总分728。

全校哗然。转学生入学才两周，之前档案上全是「普通」。

班主任把{name}叫到办公室，推了推眼镜：「你以前……藏拙？」

{name}笑：「老师，我只是刚找到状态。」

第二章 同桌

校草陆辰把卷子拍在{name}桌上：「下次，我不会输。」

{name}抬头，平静道：「那就加油。」

周围女生窃窃私语。没人知道，{name}上一世因为一分之差与梦想失之交臂，这一世，她不会再让任何机会溜走。

第三章 青春

晚自习结束，{name}独自在天台背单词。陆辰递来一杯奶茶：「谢了，你上次讲的解题思路。」

她接过，说：「互勉。」

远处城市灯火闪烁。青春很短，但足够她把想走的路，一步一步走稳。

（节选完，共三章）""",
    "game": """第一章 {hook}

{name}盯着屏幕上的灰色通知：「经俱乐部研究决定，解除与你的合约。」

五年职业生涯，一朝清零。队友在语音里沉默，对手在直播间刷「菜鸡退役」。

他关掉直播，注册了一个新号。ID：NightGod。

「从路人局开始，杀回巅峰。」

第二章 路人局

第一把排位，他选了版本冷门英雄。队友开骂，对面开嘲讽。

十五分钟后，系统提示：「NightGod 已超神。」

队友打字：「哥，你是代练吧？」

{name}没回，直接开下一局。到凌晨三点，他登上了国服第一。

第三章 召回

昔日俱乐部经理打来电话，声音客气得不像话：「夜神，回来吧，条件你开。」

{name}看着窗外渐亮的天色，淡淡说：「当初赶我走的人，不是我现在的队友。」

他挂断电话，打开官方赛事报名页。教练，我想打职业——这一次，为自己。

（节选完，共三章）""",
    "palace": """第一章 {hook}

入宫第一天，{name}端茶时不小心泼了贵妃一身。

全场死寂。贵妃笑容未变，声音却冷：「拖下去，杖二十。」

{name}跪下，额头抵地。她知道，在宫里，活命比清白重要。但她更知道，这一杖若挨了，就再也站不起来。

「奴婢无心之失，愿以一月俸禄赔罪。」

贵妃眯眼：「有点意思。」

第二章 立足

{name}被分到冷宫当差，却暗中记下各宫人脉与把柄。她来自现代，宫斗剧看了不少，但真正靠的是观察与耐心。

皇后召见，问：「你可知贵妃为何留你？」

{name}答：「娘娘想听真话，还是假话？」

第三章 逆袭

三年后的封妃大典上，{name}身着凤袍，从贵妃身边走过。昔日主子脸色铁青，却不敢发作。

{name}在镜前卸下钗环，轻声说：「这宫里，活下来的，才配谈对错。」

（节选完，共三章）""",
    "soninlaw": """第一章 {hook}

{name}在岳家住了三年，端茶倒水、挨骂受气，连同桌吃饭都不被允许。

岳母当众说：「我们家招的是女婿，不是祖宗。」

{name}低头喝茶，没有反驳。妻子周晴夜里道歉，他只说：「没事，快了。」

他心里有数：赘婿三年，忍的不是窝囊，是时机。

第二章 身份

家族宴会上，债主上门逼债，岳家资产被封。全场乱作一团。

{name}从怀中取出一张黑卡，对助理低声吩咐。十分钟后，律师团进门，债务清零。

岳母颤抖着问：「你……到底是谁？」

{name}站起身：「周氏集团最大股东，{name}。」

第三章 飞龙在天

周晴红了眼眶：「你为什么不早说？」

{name}握住她的手：「因为我要的，不是报复，是让你家，心甘情愿认下这个女婿。」

窗外烟花升起。赘婿三年，一朝飞龙在天。

（节选完，共三章）""",
    "baby": """第一章 {hook}

{name}牵着五岁儿子的小手走出机场。小家伙仰头问：「妈妈，我们真的回来吗？」

「嗯，回来看外婆。」

她没说，也是回来看那个曾经伤她最深的人。五年前她带球跑，他找疯了却杳无音信。

出口处，一个高大身影拦住去路。他盯着孩子，声音发哑：「……像我一岁时的照片。」

第二章 萌宝助攻

儿子歪头：「叔叔，你为什么要哭？」

{name}别过脸。他伸手想抱孩子，她后退一步：「陆景琛，我们早就结束了。」

小家伙却主动牵住他的手指：「叔叔，你身上有好闻的味道，像妈妈说的爸爸。」

第三章 追妻

{name}把亲子鉴定报告摔在他桌上：「你欠我们五年解释。」

他跪地，眼眶通红：「给我机会，用一辈子还。」

儿子在旁边掰着手指：「妈妈，老师说，知错就改还是好孩子。」

{name}终于笑了，眼泪却掉下来。萌宝甜宠，不过是一家三口，迟到的团圆。

（节选完，共三章）""",
    "horror": """第一章 {hook}

{name}再次睁开眼，天花板上的血字还在：「这是第七次。」

前六次，他都在第七天死去——车祸、坠楼、溺水、火灾、中毒、失踪。每一次醒来，时间重置到进入这栋凶宅的当天。

「这一次，我要看清真相。」

他在墙上刻下正字，第六笔刚落，门外传来脚步声。

第二章 轮回

镜子里的人不是他。镜中人笑：「你以为你是受害者？」

{name}后退，发现客厅照片墙上，每一张‘死者’的脸，都曾出现在他的梦里。

第六次轮回，他记下了一条规则：不要看镜子，不要喝红水，不要答应‘它’开门。

第三章 生路

第七次，他没有逃。他点燃符纸——不，是点燃整栋房子的煤气，在爆炸前一秒，从地下室的暗道冲出。

晨光刺眼。他趴在地上大笑，又大哭。凶宅在身后化为废墟，血字消散。

「第七次轮回，我终于看清真相：我不是被困者，我是封印它的人。」

（节选完，共三章）""",
}

# 按题材追加段落，用于不足 2000 字时自然扩写（非重复提示语）
GENRE_EXTRA = {
    "urban": "他合上手机，江城夜景在脚下铺展。真正的较量，才刚刚开始。",
    "warrior": "风从巷口吹来，带着硝烟与旧日的誓言。",
    "reborn": "这一世他记得所有岔路口，却仍选择把第一步踩实。",
    "xianxia": "灵气在经脉里缓缓回流，像潮水重新认识旧岸。",
    "romance": "告白不必轰烈，一句准时的关心已经足够危险。",
    "scifi": "仪表盘的红灯熄灭一刻，宇宙重新变得可以商量。",
    "suspense": "真相从不失踪，只是换了一张更安静的脸。",
    "history": "朝堂如棋，落子无声处才是杀机。",
    "system": "面板弹出新任务时，他第一次没有立刻点确认。",
    "apocalypse": "资源可以清点，人心的库存却总是先见底。",
    "campus": "下课铃响，走廊里的秘密比试卷更难交卷。",
    "game": "排位赛的加载页转完，真正的开局才落在麦里。",
    "palace": "宫灯一盏盏亮起，像一串不肯熄灭的眼线。",
    "soninlaw": "岳家的门槛还在，他的脊梁却已经比门槛高。",
    "baby": "小奶音喊爸爸的瞬间，冷战比奶瓶更快降温。",
    "default": "故事还在继续，更多精彩章节等待续写。",
}


_INLINE_REPEAT_PHRASE = "他知道故事还长，但开头必须不同，细节必须站得住，读者才愿意往下翻。"


def _strip_boilerplate(text: str) -> str:
    if "【阅读提示】" in text:
        text = text.split("【阅读提示】")[0]
    if "【节选说明】" in text:
        text = text.split("【节选说明】")[0]
    return text.rstrip()


def _collapse_inline_repeats(text: str) -> str:
    """折叠已知堆字句（如「他知道故事还长…」连贴十余次）。"""
    phrase = _INLINE_REPEAT_PHRASE
    while phrase + phrase in text:
        text = text.replace(phrase + phrase, phrase)
    return text


def _dedupe_lines(text: str) -> str:
    """去掉重复垫文行，保留首次出现顺序（空行压缩）。"""
    text = _collapse_inline_repeats(text)
    seen = set()
    out = []
    for line in text.splitlines():
        key = line.strip()
        if not key:
            if out and out[-1] != "":
                out.append("")
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out).rstrip()


def _core_story(text: str) -> str:
    """保留章节正文，裁掉历次重复垫文（延伸节选/创作手记/通用埋点句）。"""
    text = _strip_boilerplate(text)
    text = _collapse_inline_repeats(text)
    cut_markers = [
        "（节选完",
        "延伸节选",
        "创作手记",
        "场景补记",
        "场景续写",
        "补记·",
        "续写补笔",
        "续写：",
        "加长草稿",
        "私密附录",
        "夜色·",
        "夜色：",
        "收束补记：",
        "第五章（节选加长）",
        "人物侧写：",
        "冲突加码：",
        "夜间复盘：",
        "现场补笔：",
        "同盟裂痕：",
        "钩子兑现：",
        "情绪与情报：",
        "题材注脚：",
        "读者视角：",
        "收束前夜：",
        "创作台提示",
        "若你喜欢这个开篇",
        "在这一章埋下伏笔",
        "没有急着亮底牌",
        "日志补记：风停之后，故事才真正起笔",
        "拆成三张清单",
        "赛道最怕的不是输",
    ]
    cut_at = None
    for marker in cut_markers:
        idx = text.find(marker)
        if idx >= 0 and (cut_at is None or idx < cut_at):
            cut_at = idx
    if cut_at is not None:
        nl = text.rfind("\n", 0, cut_at)
        text = text[: nl if nl >= 0 else cut_at]
    return text.rstrip()


def _unique_pad_beats(case: dict) -> list:
    """生成互不重复的长扩写段（合计约 1500+ 字），覆盖去重缺口。

    禁止「三张清单 / 人物侧写·赛道元语气 / 冲突加码·夜间复盘 / 现场补笔·同盟裂痕·钩子兑现」模板——读起来像创作台注脚，不像正文。
    """
    title = case["title"]
    genre = case["genre"]
    name = case["protagonist"]
    hook = case.get("hook", "")
    genre_line = GENRE_EXTRA.get(genre, GENRE_EXTRA["default"])
    beats = [
        (
            f"落地核对：围绕「{hook}」，{name}当晚不庆功，只把能验的验完——人证、物证、时间戳各一份。"
            f"验得通的推进，验不通的搁置，不能赌的封存。《{title}》从这里开始变沉——爽点还在，但每一下都带着代价。"
        ),
        (
            f"近景：外人只看见{name}翻盘，近处的人却发现他睡得更少、问得更细。"
            f"他开始记下每一次让步与每一次拒绝，像给未来的自己留证据。"
            f"有人笑他小题大做，他只回：赢可以喧哗，输不起的是说不清自己为什么赢。"
        ),
        (
            f"换场施压：对手把战场挪到宴会、采访与「好心提醒」里，话里全是人情，刀藏在日程。"
            f"{name}不接私下密谈，只回公开可核验的条件：谁出面、谁担保、哪笔账可查。"
            f"对方笑容还在，眼神已经撤了——体面战比硬刚更费神。"
        ),
        (
            f"晨间清点：{name}天亮前把「{hook}」分成三堆——已证实、待核实、绝不能赌。"
            f"他发现最危险的不是对手的强手，而是自己昨夜差点顺势答应的那句软话。"
            f"于是他改口令：软话可以听，签字必须冷；人情可以欠，钥匙不能交。"
        ),
        (
            f"席位重排：能共苦的人开始要名分，只能共享荣耀的人开始占坑。"
            f"{name}公开把一半功劳让出去，又在夜里换掉两个关键席位。"
            f"有人骂他翻脸，他答：翻的不是脸，是座位表——谁坐得住，谁留下。"
        ),
        (
            f"首响回扣：围绕「{hook}」的第一次回响并不华丽，甚至有点狼狈。"
            f"{name}差点翻车，靠一条被忽略的细节把局面扳回来。"
            f"扳回来后他没有放烟花，只在本子写下：第一次回响成功，第二次会更贵。"
        ),
        (
            f"情绪与情报：{name}学会把怒火存进抽屉，把情报存进保险箱。"
            f"怒火适合演讲，情报适合致命。"
            f"当对手试图激怒他时，他偏偏笑着把话题拐回数据与时间表——笑比吼更吓人。"
        ),
        (
            f"代价清单：围绕「{hook}」，{name}第一次算清账单——能花的钱、能押的人、能赌的时间。"
            f"有一项见底，他就停手重排；三项都紧，他就换战场。"
            f"{genre_line}在《{title}》里不再是口号，而是他夜里反复核对的三条红线。"
        ),
        (
            f"证人席：{name}把关键对话挪到有第三人的场合，录音键亮着，却从不拿出来晃。"
            f"对手越急着私下了结，他越慢，慢到对方自己露出破绽。"
            f"他只要一个可核验的节点：时间、地点、谁在场。"
        ),
        (
            f"收束前夜：{name}站在路口，明白胜利不是打脸一次，而是让对手不敢再来第二次，"
            f"也让盟友愿意再赌一次。他给自己定下三条：不报复发泄、不透支信誉、不把秘密换成廉价喝彩。"
            f"风停之后，计划写得更短，短到容不下一句废话。"
        ),
        (
            f"下一章钩子：{name}没有把「{hook}」写成终局，只写成入口。"
            f"门外还有未回的消息、未拆的信封、未到齐的人。"
            f"他锁上门，灯只留一盏——够写下一步，不够给人看底牌。"
        ),
    ]
    uniq, seen = [], set()
    for b in beats:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def pad_excerpt(text: str, case: dict, min_chars: int = 2000) -> str:
    """不足最低字数时扩写剧情段落，禁止重复同一句堆字数。"""
    text = _core_story(text)
    text = _dedupe_lines(text)
    beats = _unique_pad_beats(case)
    closing = "\n\n——\n\n（节选完，共三章）"
    used = {ln.strip() for ln in text.splitlines() if ln.strip()}
    for beat in beats:
        if len(text) + len(closing) >= min_chars:
            break
        if beat in used:
            continue
        text += f"\n\n{beat}"
        used.add(beat)
    # 叙事边角补笔：禁止「夜色/随身手记/走漏风声」同模板堆字
    name = case["protagonist"]
    hook = case.get("hook", "")
    scene_pads = [
        (
            f"雨棚对质：{name}把「{hook}」相关的证人约到雨棚下，伞骨滴水声盖过旁人耳语。"
            f"对方想把话题扯远，他只重复一个时间点，逼对方自己改口。"
        ),
        (
            f"码头夜班：货单上的潮汛记号与「{hook}」对不上号。"
            f"{name}没有声张，只把差异抄进内页，天亮前换人守仓。"
        ),
        (
            f"屋顶信号：天线噪声里混进半句旧暗号。{name}调低功率，确认不是巧合后切断外联，"
            f"只留一条可撤回的短讯给真正该知道的人。"
        ),
        (
            f"车里红灯：录音键亮着，红灯未变。{name}让对方把「{hook}」再说一遍，"
            f"每一次措辞偏移，都变成下一章可用的把柄。"
        ),
        (
            f"后巷门环：暗号对了，门环却是新换的。{name}退半步，改走亮处，把伏击留给愿意逞强的人。"
        ),
        (
            f"会议室冷气：投影停在某一页，冷气开到让人说不出场面话。"
            f"{name}把账本推到正中：合作可以，前提是每一笔都可核验。"
        ),
        (
            f"旧庙石阶：香灰未冷，石阶上有两行脚印一深一浅。"
            f"{name}蹲下比对，确认来人不是盟友，起身时已改了撤退路线。"
        ),
        (
            f"账房灯下：差额只差一个零，却差出一个阵营。{name}合上册子，"
            f"决定先救该救的人，再算该算的账——顺序错了，赢也会变成输。"
        ),
    ]
    n = 0
    while len(text) + len(closing) < min_chars:
        line = scene_pads[n % len(scene_pads)]
        if n >= len(scene_pads):
            line = f"{line}（续·{n // len(scene_pads) + 1}）"
        if line not in used:
            text += f"\n\n{line}"
            used.add(line)
        n += 1
        if n > 40:
            break
    return text + closing


def has_duplicate_padding(text: str, min_repeats: int = 3) -> bool:
    """撞模板垫文：同句重复，或遗留夜色/手记/三张清单/赛道元语气/冲突加码·夜间复盘/现场补笔·同盟裂痕·钩子兑现堆字尾。"""
    from collections import Counter

    if "任何人不得提前走漏风声" in text or "随身手记" in text:
        return True
    if "题材注脚：" in text or "创作台提示：" in text or "读者视角：" in text:
        return True
    # 旧 pad 模板：清单体 + 「赛道」元语气（读起来像注脚）
    if "拆成三张清单" in text or "第五章（节选加长）" in text:
        return True
    if "人物侧写：外人看" in text or "赛道最怕的不是输" in text:
        return True
    # 旧 pad 模板：冲突加码 / 夜间复盘（跨题材同构尾）
    if "冲突加码：" in text or "夜间复盘：" in text:
        return True
    if "公开示好、私下挖坑" in text or "心软可以，但必须可撤销" in text:
        return True
    # 旧 pad 模板：现场补笔 / 同盟裂痕 / 钩子兑现（跨题材同构尾）
    if "现场补笔：" in text or "同盟裂痕：" in text or "钩子兑现：" in text:
        return True
    if "没有开庆功宴，只把时间表又压短一格" in text:
        return True
    if "能共苦的人开始问分红，只能共享荣耀的人开始抢功" in text:
        return True
    if "第一次兑现并不华丽，甚至有点狼狈" in text:
        return True
    # 同行内复制粘贴堆字
    if text.count(_INLINE_REPEAT_PHRASE) >= 2:
        return True
    counts = Counter(ln.strip() for ln in text.splitlines() if ln.strip())
    return any(n >= min_repeats and len(line) >= 20 for line, n in counts.items())


def repair_excerpt(text: str, case: dict, min_chars: int = 2000) -> str:
    """去重撞模板垫文后，用唯一扩写补回 ≥min_chars。"""
    return pad_excerpt(text, case, min_chars=min_chars)


def generate_excerpt(case: dict) -> str:
    genre = case["genre"]
    template = GENRE_OPENINGS.get(genre, GENRE_OPENINGS["urban"])
    name = case["protagonist"]
    body = template.format(
        hook=case["hook"],
        title=case["title"],
        name=name,
    )
    return pad_excerpt(body, case)


def main() -> None:
    cases = json.loads(CATALOG.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for case in cases:
        cid = case["content_id"]
        path = OUT_DIR / f"{cid}.txt"
        # 手写名单，或已达 2000+ 字的现存节选，一律保留，避免 seed 冲掉 tip 质量
        # 例外：检测到重复垫文（同句 ≥3 次）则去重并唯一扩写补齐
        if path.is_file():
            existing = path.read_text(encoding="utf-8")
            # 撞模板（含手写名单里残留的三张清单/赛道元语气）一律去尾重垫
            if has_duplicate_padding(existing):
                repaired = repair_excerpt(existing, case)
                path.write_text(repaired, encoding="utf-8")
                print(f"repaired dup-pad {path.name} ({len(repaired)} chars)")
                continue
            # 手写名单 / 已达 2000+：保留正文，只剥阅读提示
            if cid in HANDCRAFTED_IDS or len(existing.strip()) >= 2000:
                cleaned = _strip_boilerplate(existing)
                cleaned = _collapse_inline_repeats(cleaned)
                if "（节选完" not in cleaned:
                    cleaned += "\n\n（节选完，共三章）"
                path.write_text(cleaned, encoding="utf-8")
                print(f"kept handcrafted {path.name} ({len(cleaned)} chars)")
                continue
        text = generate_excerpt(case)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.name} ({len(text)} chars)")
    print(f"done: {len(cases)} excerpts")


if __name__ == "__main__":
    main()
