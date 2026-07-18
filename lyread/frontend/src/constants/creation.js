/** 创作向导预设：题材灵感、爽点、续写风格 */

export const HOT_POINTS = [
  '打脸', '逆袭', '装逼', '升级', '获宝', '救人', '表白', '复仇', '暴富', '系统任务',
]

export const WRITE_STYLES = [
  { id: 'shuang', name: '网文爽文', desc: '节奏快、冲突强、打脸逆袭' },
  { id: 'sweet', name: '甜宠言情', desc: '感情线为主、互动细腻' },
  { id: 'suspense', name: '悬疑推理', desc: '伏笔密集、氛围紧张' },
  { id: 'xianxia', name: '玄幻修仙', desc: '境界升级、世界观宏大' },
  { id: 'urban', name: '都市现实', desc: '贴近生活、细节真实' },
]

export const IDEA_TEMPLATES = {
  urban: [
    '主角意外获得神豪系统，在都市纵横，打脸看不起他的人',
    '被前女友羞辱后，主角身份曝光竟是隐藏豪门继承人',
    '普通上班族绑定任务系统，每完成一个任务就获得一项神级技能',
  ],
  fantasy: [
    '废柴少年觉醒上古血脉，从宗门底层一路逆袭成仙',
    '穿越到修仙世界，带着现代知识炼制出逆天丹药',
    '被逐出师门后，偶得上古神器，开启复仇之路',
  ],
  reborn: [
    '重生回到十年前，利用前世记忆抓住所有风口成为首富',
    '重生到高考前，改写人生轨迹弥补所有遗憾',
    '重生后发现自己前世错过的机缘，这一世全部拿下',
  ],
  warrior: [
    '战神归来发现女儿住狗窝，一声令下十万将士集结',
    '退役兵王回归都市，保护家人对抗地下势力',
    '隐藏身份的顶级特工，被迫重新出山',
  ],
  brainhole: [
    '全世界人类突然能看见彼此的寿命倒计时',
    '我写的小说情节会在现实中同步发生',
    '每次睡觉都会穿越到平行世界当不同身份',
  ],
  default: [
    '主角获得特殊能力，在逆境中崛起改变命运',
    '两个对立阵营的继承人意外结盟，共同对抗幕后黑手',
    '一场意外让普通人卷入惊天阴谋，必须靠智慧求生',
  ],
}

export function templatesForGenre(genreId) {
  return IDEA_TEMPLATES[genreId] || IDEA_TEMPLATES.default
}

export const WIZARD_STEPS = [
  { id: 'genre', title: '选择题材', hint: '热门题材或自定义' },
  { id: 'idea', title: '故事灵感', hint: '选模板或自己写' },
  { id: 'title', title: '书名', hint: 'AI 推荐 5 个，可自选' },
  { id: 'setup', title: '设定', hint: '金手指与爽点' },
  { id: 'outline', title: '大纲', hint: '起承转合结构' },
  { id: 'chapters', title: '章纲', hint: '批量章纲规划' },
  { id: 'write', title: '正文', hint: '续写与一致性检查' },
]
