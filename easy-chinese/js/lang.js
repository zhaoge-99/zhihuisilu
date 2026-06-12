// ===== EASY CHINESE · Language System (Complete) =====
// Default: Chinese (zh-CN). Switch to English (en) via dropdown.
// Usage in HTML: <span data-i18n="key">默认文本</span>
// Usage in JS:   t('key')

const LANG = {
  zh: {
    // App
    'app.title':'智慧丝路','app.subtitle':'轻松学中文','app.footer':'© 2026 智慧丝路 · 开源项目','app.loading':'加载中...',
    // Navigation
    'nav.home':'首页','nav.pinyin':'拼音课程','nav.characters':'汉字','nav.hsk':'HSK 词汇','nav.practice':'练习工具','nav.resources':'学习资源','nav.profile':'个人中心',
    // Home
    'home.hero.title':'轻松学中文，<span>从这里开始</span>',
    'home.hero.desc':'从零开始——掌握拼音、汉字、词汇和日常会话。专为外国初学者设计。',
    'home.start':'🎯 开始学习','home.quiz':'✍️ 做测验','home.ask_ai':'🤖 问AI',
    'home.stats.vocab':'已学单词','home.stats.streak':'连续天数','home.stats.quizzes':'完成测验','home.stats.hsk':'HSK 词汇',
    'home.level.question':'你是什么水平？',
    'home.level.beginner':'🌟 零基础','home.level.beginner.desc':'从未学过中文',
    'home.level.hsk':'📚 备考 HSK','home.level.hsk.desc':'准备 HSK 1-6 考试',
    'home.level.practice':'✍️ 练习复习','home.level.practice.desc':'测试你的水平',
    'home.path':'学习路径','home.explore':'探索功能',
    'home.feature.pinyin':'拼音与声调','home.feature.pinyin.desc':'掌握声母、韵母和四声',
    'home.feature.hsk':'HSK 词汇','home.feature.hsk.desc':'完整的 HSK 1-6 词库',
    'home.feature.daily':'每日练习','home.feature.daily.desc':'闪卡、测验和连续打卡',
    'home.feature.flashcard':'智能闪卡','home.feature.flashcard.desc':'高效记忆汉字和单词',
    'home.feature.stroke':'笔顺演示','home.feature.stroke.desc':'一步一步学写汉字',
    'home.feature.grammar':'语法与短语','home.feature.grammar.desc':'简单易懂的解释',
    // Pinyin
    'pinyin.title':'🔊 拼音与声调','pinyin.desc':'掌握普通话发音——声母、韵母和四声。',
    'pinyin.tones':'🎵 四声','pinyin.initials':'声母','pinyin.finals':'韵母','pinyin.tips':'💡 发音小技巧',
    'pinyin.tip1':'• zh/ch/sh — 卷舌音，舌尖向上颚卷',
    'pinyin.tip2':'• z/c/s — 舌尖抵住下齿背',
    'pinyin.tip3':'• j/q/x — 舌面贴下齿，咧嘴笑',
    'pinyin.tip4':'• r — 像英文 "pleasure" 里的 s',
    'pinyin.tip5':'• ü — 像法语的 "tu"，嘴唇圆起',
    // Characters
    'char.title':'🖌️ 汉字','char.desc':'了解汉字的构成——笔画、偏旁部首和记忆技巧。',
    'char.stroke_demo':'📖 笔顺演示','char.basic_strokes':'🔤 基础笔画',
    'char.horizontal':'横','char.vertical':'竖','char.left_falling':'撇','char.right_falling':'捺',
    'char.rising':'提','char.hook':'钩','char.turn':'折','char.curve':'弯','char.slant':'斜',
    'char.radicals':'🔎 常见偏旁','char.tips':'💡 记忆技巧','char.step':'第','char.of':'步，共',
    'char.memory1':'人 (rén) — 像一个走路的人',
    'char.memory2':'山 (shān) — 三个山峰',
    'char.memory3':'火 (huǒ) — 一个人围着火焰张开手臂',
    'char.memory4':'口 (kǒu) — 张开的口',
    'char.memory5':'日 (rì) — 圆太阳加地平线',
    'char.memory6':'月 (yuè) — 弯弯的月亮',
    'char.memory7':'水 (shuǐ) — 流动的水滴',
    'char.memory8':'木 (mù) — 树有枝有根',
    // HSK
    'hsk.title':'📚 HSK 词汇','hsk.desc':'HSK 1-6 完整词汇表 + 主题分类。收藏单词便于复习。',
    'hsk.themed':'📂 主题分类','hsk.flashcards':'🃏 闪卡','hsk.quiz':'✍️ 测验',
    'hsk.search':'搜索词汇...','hsk.save':'收藏','hsk.select_category':'📂 点击上方选择分类','hsk.no_words':'暂无词汇',
    // Practice
    'practice.title':'✍️ 练习工具','practice.desc':'闪卡、每日打卡和测验——巩固所学内容。',
    'practice.flashcards':'🃏 闪卡','practice.flashcards.desc':'翻转卡片，记忆汉字和单词',
    'practice.vocab_quiz':'📝 词汇测验','practice.vocab_quiz.desc':'HSK 各等级选择题',
    'practice.tone_quiz':'🎯 声调练习','practice.tone_quiz.desc':'辨别正确的声调',
    'practice.flip':'🔄 翻转','practice.close':'✕ 关闭',
    'practice.checkin':'✅ 每日打卡','practice.streak':'连续学习',
    'practice.checked':'🎉 打卡成功！继续加油！','practice.already_checked':'今天已打卡！✅',
    'practice.next':'下一题 ▶','practice.result':'查看结果 🎯',
    'practice.perfect':'🎉 太棒了！满分！','practice.good':'👏 做得好！继续加油！','practice.keep_going':'💪 继续练习！',
    // Quiz
    'quiz.choose_meaning':'选择正确的意思','quiz.score':'得分','quiz.correct_rate':'正确率',
    // Flashcard
    'fc.tap_hint':'点击翻转','fc.counter':'张',
    // Resources
    'res.title':'📖 学习资源','res.desc':'语法指南、常用短语、文化知识——一应俱全。',
    'res.grammar':'📘 语法基础',
    'res.grammar1.title':'语序：主谓宾','res.grammar1.desc':'主语 + 时间 + 方式 + 地点 + 动词 + 宾语',
    'res.grammar2.title':'动词不变形','res.grammar2.desc':'动词不变——用 了/过/在 表时态',
    'res.grammar3.title':'量词','res.grammar3.desc':'个、条、张、本、杯——量词不可少',
    'res.grammar4.title':'吗字疑问句','res.grammar4.desc':'陈述句加 吗 变成疑问句',
    'res.grammar5.title':'是…的 结构','res.grammar5.desc':'强调过去动作的时间、地点或方式',
    'res.survival':'💬 生存短语',
    'res.survival1':'你好 (nǐ hǎo)','res.survival1.desc':'问候',
    'res.survival2':'谢谢 (xiè xiè)','res.survival2.desc':'感谢',
    'res.survival3':'对不起 (duì bu qǐ)','res.survival3.desc':'道歉',
    'res.survival4':'多少钱 (duō shao qián)','res.survival4.desc':'询问价格',
    'res.survival5':'这个怎么读 (zhè ge zěn me dú)','res.survival5.desc':'请教读音',
    'res.idioms':'🎯 成语与文化',
    'res.idiom1.title':'马马虎虎 (mǎ mǎ hǔ hǔ)','res.idiom1.desc':'一般般，凑合',
    'res.idiom2.title':'一路顺风 (yí lù shùn fēng)','res.idiom2.desc':'祝你旅途顺利',
    'res.idiom3.title':'加油 (jiā yóu)','res.idiom3.desc':'加把劲，你可以的！',
    'res.idiom4.title':'吃了吗 (chī le ma)','res.idiom4.desc':'中国人常用的问候方式',
    'res.downloads':'📎 开源数据来源',
    'res.source1':'HSK 2025 开源词库','res.source1.desc':'github.com/chelsea6502/hsk-2025 — HSK1-6 完整 JSON 词库',
    'res.source2':'汉字笔顺数据库','res.source2.desc':'GitHub: chinese-characters-database — 3500 常用汉字 + 笔顺',
    'res.source3':'拼音数据','res.source3.desc':'GitHub: pinyin-data — 拼音组合 + 汉字映射',
    'res.source4':'Chinese Grammar Wiki','res.source4.desc':'resources.allsetlearning.com — 语法百科',
    'res.source5':'HSK 模拟真题','res.source5.desc':'goeastmandarin.com — 免费 HSK1-6 真题 + 解析',
    
    'login.title':'登录 / 注册','login.username':'用户名','login.password':'密码',
    'login.confirm':'确认密码','login.loginBtn':'登录','login.registerBtn':'注册',
    'login.noAccount':'没有账号？','login.registerLink':'注册新账号',
    'login.hasAccount':'已有账号？','login.loginLink':'去登录',
    // Profile
    'profile.title':'👤 个人中心','profile.desc':'跟踪学习进度、收藏单词和学习记录。',
    'profile.level_beginner':'🌱 新手入门','profile.level_elementary':'📖 初级学者',
    'profile.level_intermediate':'📊 中级学者','profile.level_advanced':'📈 高级学者',
    'profile.saved_words':'⭐ 已收藏单词','profile.no_saved':'在 HSK 词汇表中收藏单词后，它们会出现在这里。',
    'profile.tips':'📊 学习建议',
    'profile.tip1':'💡 <strong>每天练习 10 分钟</strong> — 坚持比强度更重要',
    'profile.tip2':'💡 <strong>使用 AI 助教</strong>（右下角 💬 按钮）获得即时解答',
    'profile.tip3':'💡 <strong>收藏不熟的生词</strong>，在本页集中复习',
    'profile.tip4':'💡 <strong>每个 HSK 等级后做测验</strong>，检验学习成果',
    // Check-in
    'checkin.btn':'✅ 今日打卡',
    // Learning path
    'level.pinyin':'拼音','level.characters':'汉字','level.words':'词汇','level.grammar':'语法','level.speaking':'口语',
    // Tone names
    'tone1':'第一声','tone1.desc':'高平调',
    'tone2':'第二声','tone2.desc':'上升调 ↗',
    'tone3':'第三声','tone3.desc':'先降后升',
    'tone4':'第四声','tone4.desc':'下降调 ↘',
  },

  en: {
    'app.title':'Easy Chinese','app.subtitle':'Learn Mandarin','app.footer':'© 2026 Easy Chinese · Open Source','app.loading':'Loading...',
    'nav.home':'Home','nav.pinyin':'Pinyin Course','nav.characters':'Characters','nav.hsk':'HSK Vocabulary','nav.practice':'Practice Tools','nav.resources':'Resources','nav.profile':'My Page',
    'home.hero.title':'Learn Chinese the <span>Easy Way</span>',
    'home.hero.desc':'Start from zero — master Pinyin, characters, vocabulary, and real-life conversation. Designed for absolute beginners.',
    'home.start':'🎯 Start Learning','home.quiz':'✍️ Take Quiz','home.ask_ai':'🤖 Ask AI',
    'home.stats.vocab':'Words Learned','home.stats.streak':'Day Streak','home.stats.quizzes':'Quizzes Done','home.stats.hsk':'HSK Words',
    'home.level.question':"What's your level?",
    'home.level.beginner':'🌟 Absolute Beginner','home.level.beginner.desc':'Never studied Chinese',
    'home.level.hsk':'📚 HSK Test Prep','home.level.hsk.desc':'Preparing for HSK 1-6',
    'home.level.practice':'✍️ Practice & Review','home.level.practice.desc':'Test what you know',
    'home.path':'Learning Path','home.explore':'Explore',
    'home.feature.pinyin':'Pinyin & Tones','home.feature.pinyin.desc':'Master initials, finals, and tones',
    'home.feature.hsk':'HSK Vocabulary','home.feature.hsk.desc':'Complete HSK 1-6 word lists',
    'home.feature.daily':'Daily Practice','home.feature.daily.desc':'Flashcards, quizzes, and streak',
    'home.feature.flashcard':'Smart Flashcards','home.feature.flashcard.desc':'Memorize characters effectively',
    'home.feature.stroke':'Stroke Order','home.feature.stroke.desc':'Learn to write step by step',
    'home.feature.grammar':'Grammar & Phrases','home.feature.grammar.desc':'Simple explanations in English',
    'pinyin.title':'🔊 Pinyin & Tones','pinyin.desc':'Master Mandarin pronunciation — initials, finals, and 4 tones.',
    'pinyin.tones':'🎵 The Four Tones','pinyin.initials':'Initials (声母)','pinyin.finals':'Finals (韵母)','pinyin.tips':'💡 Quick Tips',
    'pinyin.tip1':'• zh/ch/sh — curl tongue back to the roof',
    'pinyin.tip2':'• z/c/s — tip touches bottom front teeth',
    'pinyin.tip3':'• j/q/x — tongue flat against teeth, smile wide',
    'pinyin.tip4':'• r — like the "s" in "pleasure"',
    'pinyin.tip5':'• ü — round lips like French "tu"',
    'char.title':'🖌️ Chinese Characters','char.desc':'Understand how characters work — strokes, radicals, and memory tricks.',
    'char.stroke_demo':'📖 Stroke Order Demo','char.basic_strokes':'🔤 Basic Strokes',
    'char.horizontal':'Horizontal','char.vertical':'Vertical','char.left_falling':'Left-falling','char.right_falling':'Right-falling',
    'char.rising':'Rising','char.hook':'Hook','char.turn':'Turn','char.curve':'Curve','char.slant':'Slant',
    'char.radicals':'🔎 Common Radicals','char.tips':'💡 Memory Tips','char.step':'Step','char.of':'of',
    'char.memory1':'人 (rén, person) — looks like a walking figure',
    'char.memory2':'山 (shān, mountain) — three peaks',
    'char.memory3':'火 (huǒ, fire) — a person with arms raised around flames',
    'char.memory4':'口 (kǒu, mouth) — an open square like a mouth',
    'char.memory5':'日 (rì, sun) — a round sun with a horizon line',
    'char.memory6':'月 (yuè, moon) — like a crescent moon',
    'char.memory7':'水 (shuǐ, water) — flowing water drops',
    'char.memory8':'木 (mù, tree) — tree with branches and roots',
    'hsk.title':'📚 HSK Vocabulary','hsk.desc':'Complete HSK 1-6 word lists + themed categories. Save words to review later.',
    'hsk.themed':'📂 Themed','hsk.flashcards':'🃏 Flashcards','hsk.quiz':'✍️ Quiz Me',
    'hsk.search':'Search words...','hsk.save':'Save','hsk.select_category':'📂 Select a category above','hsk.no_words':'No vocabulary found',
    'practice.title':'✍️ Practice Tools','practice.desc':'Flashcards, daily check-in, and quizzes to reinforce what you have learned.',
    'practice.flashcards':'🃏 Flashcards','practice.flashcards.desc':'Flip and memorize characters and words',
    'practice.vocab_quiz':'📝 Vocabulary Quiz','practice.vocab_quiz.desc':'Multiple choice from any HSK level',
    'practice.tone_quiz':'🎯 Tone Practice','practice.tone_quiz.desc':'Identify the correct tone',
    'practice.flip':'🔄 Flip','practice.close':'✕ Close',
    'practice.checkin':'✅ Daily Check-in','practice.streak':'Day Streak',
    'practice.checked':'🎉 Checked in! Keep going!','practice.already_checked':'Already checked in today! ✅',
    'practice.next':'Next ▶','practice.result':'See Results 🎯',
    'practice.perfect':'🎉 Perfect! Excellent!','practice.good':'👏 Good job! Keep going!','practice.keep_going':'💪 Keep practicing!',
    'quiz.choose_meaning':'Choose the correct meaning','quiz.score':'Score','quiz.correct_rate':'correct',
    'fc.tap_hint':'Tap to reveal','fc.counter':'cards',
    'res.title':'📖 Resources','res.desc':'Grammar guides, phrase books, cultural notes — all in one place.',
    'res.grammar':'📘 Grammar Basics',
    'res.grammar1.title':'Word Order: SVO','res.grammar1.desc':'Subject + Time + Manner + Place + Verb + Object',
    'res.grammar2.title':'No Verb Conjugation','res.grammar2.desc':"Verbs don't change — use 了, 过, 在 for tense",
    'res.grammar3.title':'Measure Words (量词)','res.grammar3.desc':'个, 条, 张, 本, 杯 — always between number and noun',
    'res.grammar4.title':'Questions with 吗','res.grammar4.desc':'Add 吗 at the end to make yes/no questions',
    'res.grammar5.title':'是…的 Structure','res.grammar5.desc':'Emphasizing time, place, or manner in past actions',
    'res.survival':'💬 Survival Phrases',
    'res.survival1':'你好 (nǐ hǎo)','res.survival1.desc':'Hello / Greeting',
    'res.survival2':'谢谢 (xiè xiè)','res.survival2.desc':'Thank you',
    'res.survival3':'对不起 (duì bu qǐ)','res.survival3.desc':'Sorry / Excuse me',
    'res.survival4':'多少钱 (duō shao qián)','res.survival4.desc':'How much does it cost?',
    'res.survival5':'这个怎么读 (zhè ge zěn me dú)','res.survival5.desc':"How do you read this?",
    'res.idioms':'🎯 Idioms & Culture',
    'res.idiom1.title':'马马虎虎 (mǎ mǎ hǔ hǔ)','res.idiom1.desc':'"Horse horse tiger tiger" — so-so',
    'res.idiom2.title':'一路顺风 (yí lù shùn fēng)','res.idiom2.desc':'"Smooth winds" — Bon voyage',
    'res.idiom3.title':'加油 (jiā yóu)','res.idiom3.desc':'"Add oil" — Go for it! / You can do it!',
    'res.idiom4.title':'吃了吗 (chī le ma)','res.idiom4.desc':'"Have you eaten?" — A common Chinese greeting',
    'res.downloads':'📎 Open Source Resources',
    'res.source1':'HSK 2025 Word List','res.source1.desc':'github.com/chelsea6502/hsk-2025 — Complete HSK1-6 JSON',
    'res.source2':'Chinese Characters DB','res.source2.desc':'GitHub: chinese-characters-database — 3500 chars + strokes',
    'res.source3':'Pinyin Data','res.source3.desc':'GitHub: pinyin-data — Pinyin combinations + character mapping',
    'res.source4':'Chinese Grammar Wiki','res.source4.desc':'resources.allsetlearning.com — Grammar reference',
    'res.source5':'HSK Mock Tests','res.source5.desc':'goeastmandarin.com — Free HSK1-6 tests',
    
    'login.title':'Login / Register','login.username':'Username','login.password':'Password',
    'login.confirm':'Confirm Password','login.loginBtn':'Login','login.registerBtn':'Register',
    'login.noAccount':"Don't have an account?",'login.registerLink':'Register now',
    'login.hasAccount':'Already have an account?','login.loginLink':'Login',
    'profile.title':'👤 My Page','profile.desc':'Track your progress, saved words, and learning history.',
    'profile.level_beginner':'🌱 Beginner','profile.level_elementary':'📖 Elementary',
    'profile.level_intermediate':'📊 Intermediate','profile.level_advanced':'📈 Advanced',
    'profile.saved_words':'⭐ Saved Words','profile.no_saved':'Save words from HSK vocabulary to review them here.',
    'profile.tips':'📊 Quick Tips',
    'profile.tip1':'💡 <strong>Practice 10 minutes daily</strong> — consistency beats intensity',
    'profile.tip2':'💡 <strong>Use the AI tutor</strong> (bottom-right 💬 button) for instant answers',
    'profile.tip3':'💡 <strong>Save difficult words</strong> and review them here',
    'profile.tip4':'💡 <strong>Take quizzes after each HSK level</strong> to test progress',
    'profile.tip5':'💡 All progress saved in browser — no account needed!',
    'checkin.btn':'✅ Check In Today',
    'level.pinyin':'Pinyin','level.characters':'Characters','level.words':'Words','level.grammar':'Grammar','level.speaking':'Speaking',
    'tone1':'First Tone','tone1.desc':'High & flat',
    'tone2':'Second Tone','tone2.desc':'Rising ↗',
    'tone3':'Third Tone','tone3.desc':'Dip then rise',
    'tone4':'Fourth Tone','tone4.desc':'Falling ↘',
  }
};

let currentLang = localStorage.getItem('ec_lang') || 'zh';

function t(key) {
  return LANG[currentLang]?.[key] || LANG['zh']?.[key] || key;
}

function switchLang(lang) {
  if (!LANG[lang]) return;
  currentLang = lang;
  localStorage.setItem('ec_lang', lang);
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    el.innerHTML = t(key);
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.dataset.i18nPh;
    el.placeholder = t(key);
  });
  document.querySelectorAll('.lang-option').forEach(el => {
    el.classList.toggle('active', el.dataset.lang === lang);
  });
  updateHomeStats();
  updateStreakUI();
  document.dispatchEvent(new CustomEvent('langchange', {detail: {lang}}));
}

document.addEventListener('DOMContentLoaded', () => {
  switchLang(currentLang);
});
