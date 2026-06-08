// ===== EASY CHINESE · Application =====

// ===== STATE =====
let savedWords = JSON.parse(localStorage.getItem('ec_saved')||'[]');
let streakData = JSON.parse(localStorage.getItem('ec_streak')||'{"count":0,"dates":[]}');
let quizCount = parseInt(localStorage.getItem('ec_quizCount')||'0');
let fcIndex = 0, fcData = [], hskLevel = 1, scIndex = 0, scStep = 0, quizState = null;

// ===== TOAST =====
function toast(msg, type='info'){
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div'); t.className=`toast ${type}`;
  t.innerHTML = msg; c.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';t.style.transform='translateX(40px)';setTimeout(()=>t.remove(),300)},2500);
}

// ===== NAVIGATION =====
function navigateTo(page){
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
  if(nav) nav.classList.add('active');
  const p = document.getElementById(`page-${page}`);
  if(p) p.classList.add('active');
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('show');
}

// ===== STREAK =====
function updateStreakUI(){
  const sn = document.getElementById('streakNum');
  if(sn) sn.textContent = streakData.count;
  const ps = document.getElementById('psStreak');
  if(ps) ps.textContent = streakData.count;
  const ss = document.getElementById('statStreak');
  if(ss) ss.textContent = streakData.count;
  const today = new Date();
  const week = [];
  for(let i=6;i>=0;i--){const d=new Date(today);d.setDate(d.getDate()-i);week.push(d.toDateString());}
  const wg = document.getElementById('weekGrid');
  if(wg) wg.innerHTML = week.map(d => {
    const isToday = d===today.toDateString();
    const done = streakData.dates.includes(d);
    return `<div class="week-day ${done?'done':''} ${isToday&&!done?'today':''}">${new Date(d).getDate()}</div>`;
  }).join('');
}
function doCheckin(){
  const today = new Date().toDateString();
  if(streakData.dates.includes(today)) { toast(t('practice.already_checked'),'info'); return; }
  streakData.dates.push(today);
  let count = 0; const d = new Date();
  while(streakData.dates.includes(d.toDateString())){count++;d.setDate(d.getDate()-1);}
  streakData.count = count;
  localStorage.setItem('ec_streak',JSON.stringify(streakData));
  const msg = document.getElementById('checkinMsg');
  if(msg) msg.textContent = t('practice.checked');
  toast('Check-in successful! 🔥','success');
  updateStreakUI(); updateHomeStats();
}

// ===== HOME STATS =====
function updateHomeStats(){
  const labels = {statVocab:'Words Learned',statStreak:'Day Streak',statQuizzes:'Quizzes Done'};
  ['statVocab','statStreak','statQuizzes'].forEach(id=>{
    const el = document.getElementById(id);
    if(!el) return;
    const val = id==='statVocab'?savedWords.length : id==='statStreak'?streakData.count : quizCount;
    el.textContent = val;
    if(!el.nextElementSibling) el.insertAdjacentHTML('afterend',`<div class="lbl">${labels[id]}</div>`);
  });
  const pw = document.getElementById('psWords'); if(pw) pw.textContent = savedWords.length;
  const pq = document.getElementById('psQuizzes'); if(pq) pq.textContent = quizCount;
  const pc = document.getElementById('psCheckins'); if(pc) pc.textContent = streakData.dates.length;
  const pd = document.getElementById('profileLevelDisplay');
  if(pd){
    const total = savedWords.length;
    pd.textContent = (total>500 ? '📈 ' + t('profile.level_advanced') : total>200 ? '📊 ' + t('profile.level_intermediate') : total>50 ? '📖 ' + t('profile.level_elementary') : '🌱 ' + t('profile.level_beginner'));
  }
}

// ===== PINYIN =====
const PINYIN_INITIALS = ['b','p','m','f','d','t','n','l','g','k','h','j','q','x','zh','ch','sh','r','z','c','s','y','w'];
const PINYIN_FINALS = ['a','o','e','i','u','ü','ai','ei','ui','ao','ou','iu','ie','üe','er','an','en','in','un','ün','ang','eng','ing','ong'];
const TONES = [
  {mark:'mā',num:'1st',name:()=>t('tone1'),desc:()=>t('tone1.desc'),color:'#ef4444'},
  {mark:'má',num:'2nd',name:()=>t('tone2'),desc:()=>t('tone2.desc'),color:'#f59e0b'},
  {mark:'mǎ',num:'3rd',name:()=>t('tone3'),desc:()=>t('tone3.desc'),color:'#10b981'},
  {mark:'mà',num:'4th',name:()=>t('tone4'),desc:()=>t('tone4.desc'),color:'#3b82f6'},
];
function renderPinyin(){
  const ig = document.getElementById('initialsGrid');
  if(ig) ig.innerHTML = PINYIN_INITIALS.map(p => `<div class="pinyin-cell">${p}<span class="py-tone">initial</span></div>`).join('');
  const fg = document.getElementById('finalsGrid');
  if(fg) fg.innerHTML = PINYIN_FINALS.map(p => `<div class="pinyin-cell">${p}<span class="py-tone">final</span></div>`).join('');
  const tc = document.getElementById('toneCards');
  if(tc) tc.innerHTML = TONES.map(tone => `<div class="card" style="text-align:center;padding:16px">
    <div style="font-size:36px;font-weight:700;color:${tone.color}">${tone.mark}</div>
    <div style="font-size:13px;color:var(--secondary);font-weight:600;margin:4px 0">${tone.name()} (${tone.num})</div>
    <div style="font-size:12px;color:var(--text3)">${tone.desc()}</div></div>`).join('');
}

// ===== CHARACTERS =====
const STROKE_CHARS = [
  {char:'我',pinyin:'wǒ',meaning:'I / me',strokes:['一','亅','㇀','㇁','一','一','㇂','丿','丶']},
  {char:'你',pinyin:'nǐ',meaning:'You',strokes:['丿','丨','㇇','丶','㇂','丿','丶']},
  {char:'好',pinyin:'hǎo',meaning:'Good',strokes:['𡿨','丿','一','㇁','一','㇇','亅','丿','一']},
  {char:'爱',pinyin:'ài',meaning:'Love',strokes:['丿','丶','丶','丿','一','一','丿','㇇','㇏','丿','丶']},
  {char:'中',pinyin:'zhōng',meaning:'Middle',strokes:['丨','𠃍','一','丨','㇀','丨']},
  {char:'国',pinyin:'guó',meaning:'Country',strokes:['丨','𠃍','一','一','丨','㇀','一','一','丨','一','丶']},
  {char:'大',pinyin:'dà',meaning:'Big',strokes:['一','丿','㇏']},
  {char:'小',pinyin:'xiǎo',meaning:'Small',strokes:['亅','㇂','丿','丶']},
  {char:'水',pinyin:'shuǐ',meaning:'Water',strokes:['亅','㇇','丿','㇏']},
  {char:'山',pinyin:'shān',meaning:'Mountain',strokes:['丨','𠃊','丨']},
  {char:'日',pinyin:'rì',meaning:'Sun',strokes:['丨','𠃍','一','一','一']},
  {char:'月',pinyin:'yuè',meaning:'Moon',strokes:['丿','𠃍','一','一','一']},
  {char:'火',pinyin:'huǒ',meaning:'Fire',strokes:['丶','丿','丿','㇏']},
  {char:'人',pinyin:'rén',meaning:'Person',strokes:['丿','㇏']},
  {char:'木',pinyin:'mù',meaning:'Tree',strokes:['一','丨','丿','㇏']},
  {char:'口',pinyin:'kǒu',meaning:'Mouth',strokes:['丨','𠃍','一','一']},
];
const RADICALS = [
  {char:'口',pinyin:'kǒu',meaning:'mouth'},{char:'氵',pinyin:'shuǐ',meaning:'water'},
  {char:'火',pinyin:'huǒ',meaning:'fire'},{char:'木',pinyin:'mù',meaning:'tree'},
  {char:'亻',pinyin:'rén',meaning:'person'},{char:'扌',pinyin:'shǒu',meaning:'hand'},
  {char:'辶',pinyin:'chuò',meaning:'walk'},{char:'土',pinyin:'tǔ',meaning:'earth'},
  {char:'女',pinyin:'nǚ',meaning:'woman'},{char:'日',pinyin:'rì',meaning:'sun'},
  {char:'月',pinyin:'yuè',meaning:'moon'},{char:'心',pinyin:'xīn',meaning:'heart'},
];

function renderStroke(){
  const sc = STROKE_CHARS[scIndex]; if(!sc) return;
  const el = id => document.getElementById(id);
  if(el('scChar')) el('scChar').textContent = sc.char;
  if(el('scPinyin')) el('scPinyin').textContent = sc.pinyin;
  if(el('scMeaning')) el('scMeaning').textContent = `${sc.char} · ${sc.meaning}`;
  if(el('scStepNum')) el('scStepNum').textContent = scStep+1;
  if(el('scTotalSteps')) el('scTotalSteps').textContent = sc.strokes.length;
  const s = document.getElementById('scStrokes');
  if(s){
    s.innerHTML = sc.strokes.map((st,i) => `<div class="char-stroke-box ${i===scStep?'active':''}" data-si="${i}">${st}</div>`).join('');
    s.querySelectorAll('.char-stroke-box').forEach(el => {el.addEventListener('click',()=>{scStep=parseInt(el.dataset.si);renderStroke();});});
  }
}
function renderRadicals(){
  const g = document.getElementById('radicalsGrid');
  if(g) g.innerHTML = RADICALS.map(r => `<div class="card" style="text-align:center;padding:12px;cursor:default"><div style="font-size:28px">${r.char}</div><div style="font-size:12px;color:var(--secondary)">${r.pinyin}</div><div style="font-size:11px;color:var(--text3)">${r.meaning}</div></div>`).join('');
}

// ===== HSK VOCABULARY =====
function loadHSK(level){
  hskLevel = level;
  document.querySelectorAll('.hsk-tab').forEach(t=>{
    t.style.background = parseInt(t.dataset.hsk)===level?'linear-gradient(135deg,var(--primary),var(--primary-dark))':'';
    t.style.color = parseInt(t.dataset.hsk)===level?'#fff':'';
  });
  const themedBtn = document.querySelector('[data-themed="true"]');
  if(themedBtn){themedBtn.style.background='';themedBtn.style.color='';}
  const data = HSK_DATA[level]||[];
  if(data.length===0){renderVocabTable([]);return;}
  renderVocabTable(data);
}
function loadThemedVocab(){
  hskLevel = 0;
  document.querySelectorAll('.hsk-tab').forEach(t=>{t.style.background='';t.style.color='';});
  const themedBtn = document.querySelector('[data-themed="true"]');
  if(themedBtn){themedBtn.style.background='linear-gradient(135deg,var(--primary),var(--primary-dark))';themedBtn.style.color='#fff';}
  const cats = THEMED_VOCAB.map((c,i)=>`<button class="btn btn-secondary btn-sm themed-cat-tab" data-cat="${i}" onclick="loadThemedCategory(${i})">${c.category}</button>`).join('');
  const tb = document.getElementById('hskBody');
  if(tb) tb.innerHTML = `<tr><td colspan="5"><div style="display:flex;gap:8px;flex-wrap:wrap;padding:8px 0">${cats}</div><div id="themedVocabArea" style="margin-top:12px;text-align:center;color:var(--text3);padding:20px">📂 Select a category above</div></td></tr>`;
}
function loadThemedCategory(idx){
  const cat = THEMED_VOCAB[idx];
  document.querySelectorAll('.themed-cat-tab').forEach(t=>{
    t.style.background=parseInt(t.dataset.cat)===idx?'linear-gradient(135deg,var(--primary),var(--primary-dark))':'';
    t.style.color=parseInt(t.dataset.cat)===idx?'#fff':'';
  });
  renderVocabTable(cat.words);
}
function renderVocabTable(data){
  const tb = document.getElementById('hskBody');
  if(!tb) return;
  if(data.length===0){tb.innerHTML='<tr><td colspan="5" style="text-align:center;padding:24px;color:var(--text3)">No vocabulary found</td></tr>';return;}
  tb.innerHTML = data.map((w,i)=>{
    const saved=savedWords.includes(w.hanzi);
    return `<tr><td style="color:var(--text3);font-size:12px">${i+1}</td><td class="v-hanzi">${w.hanzi}</td><td class="v-pinyin">${w.pinyin}</td><td class="v-meaning">${w.meaning}</td><td><span style="cursor:pointer;font-size:18px" onclick="toggleSaveWord('${w.hanzi}')">${saved?'⭐':'☆'}</span></td></tr>`;
  }).join('');
}
function toggleSaveWord(hanzi){
  const idx = savedWords.indexOf(hanzi);
  if(idx>-1) savedWords.splice(idx,1); else savedWords.push(hanzi);
  localStorage.setItem('ec_saved',JSON.stringify(savedWords));
  toast(savedWords.includes(hanzi)?`⭐ ${t('hsk.save')}: ${hanzi}`:`✕ ${hanzi}`, savedWords.includes(hanzi)?'success':'info');
  if(hskLevel>0) loadHSK(hskLevel); else loadThemedVocab();
  updateHomeStats();
}

// ===== FLASHCARD =====
function showFlashcardMode(){
  fcData = [...(HSK_DATA[1]||[]),...(HSK_DATA[2]||[]),...(HSK_DATA[3]||[]),...(HSK_DATA[4]||[]),...(HSK_DATA[5]||[])].sort(()=>Math.random()-.5).slice(0,200);
  fcIndex=0;
  const area = document.getElementById('flashcardArea');
  if(area) area.classList.remove('hidden');
  renderFlashcard();
  navigateTo('practice');
}
function renderFlashcard(){
  const v = fcData[fcIndex]; if(!v) return;
  ['fcFront','fcBackChar','fcPinyin','fcMeaning','fcCounter'].forEach(id=>{
    const el = document.getElementById(id);
    if(!el) return;
    if(id==='fcFront') el.textContent=v.hanzi;
    else if(id==='fcBackChar') el.textContent=v.hanzi;
    else if(id==='fcPinyin') el.textContent=v.pinyin;
    else if(id==='fcMeaning') el.textContent=v.meaning;
    else if(id==='fcCounter') el.textContent=`${fcIndex+1}/${fcData.length}`;
  });
  const fc = document.getElementById('flashcardEl');
  if(fc) fc.classList.remove('flipped');
}
function toggleFlashcard(){document.getElementById('flashcardEl')?.classList.toggle('flipped');}
function prevFlashcard(){fcIndex=(fcIndex-1+fcData.length)%fcData.length;renderFlashcard();}
function nextFlashcard(){fcIndex=(fcIndex+1)%fcData.length;renderFlashcard();}

// ===== QUIZ =====
function startHSKQuiz(){
  const level = hskLevel||1;
  const pool = HSK_DATA[level]?.slice()||HSK_DATA[1]?.slice()||[];
  if(pool.length===0){toast('No vocab available for quiz','error');return;}
  const shuffled = pool.sort(()=>Math.random()-.5).slice(0,10);
  const questions = shuffled.map(v => {
    const wrong = pool.filter(x=>x.hanzi!==v.hanzi).sort(()=>Math.random()-.5).slice(0,3);
    const opts = [{text:v.meaning,correct:true},...wrong.map(w=>({text:w.meaning,correct:false}))].sort(()=>Math.random()-.5);
    return {hanzi:v.hanzi,pinyin:v.pinyin,options:opts,answered:false,selected:-1};
  });
  quizState={questions,idx:0,score:0,done:false};
  document.getElementById('quizArea')?.classList.remove('hidden');
  renderQuiz();
  navigateTo('practice');
}
function startToneQuiz(){
  const chars = [
    {hanzi:'妈',pinyin:'mā',tone:1},{hanzi:'麻',pinyin:'má',tone:2},{hanzi:'马',pinyin:'mǎ',tone:3},{hanzi:'骂',pinyin:'mà',tone:4},
    {hanzi:'汤',pinyin:'tāng',tone:1},{hanzi:'糖',pinyin:'táng',tone:2},{hanzi:'躺',pinyin:'tǎng',tone:3},{hanzi:'烫',pinyin:'tàng',tone:4},
  ].sort(()=>Math.random()-.5).slice(0,6);
  const questions = chars.map(v => {
    const tones=[1,2,3,4];
    const opts = tones.map(t=>({text:['1st (mā)','2nd (má)','3rd (mǎ)','4th (mà)'][t-1],correct:t===v.tone})).sort(()=>Math.random()-.5);
    return {hanzi:v.hanzi,pinyin:v.pinyin,options:opts,answered:false,selected:-1};
  });
  quizState={questions,idx:0,score:0,done:false};
  document.getElementById('quizArea')?.classList.remove('hidden');
  renderQuiz();
  navigateTo('practice');
}
function renderQuiz(){
  const card = document.getElementById('quizCard'); if(!card||!quizState) return;
  const {questions,idx,done}=quizState;
  if(done){
    const pct=Math.round(quizState.score/questions.length*100);
    const msg=pct===100?t('practice.perfect') : pct>=70?t('practice.good') : t('practice.keep_going');
    card.innerHTML=`<div style="text-align:center;padding:20px"><div style="font-size:56px;font-weight:900;background:linear-gradient(135deg,var(--primary),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">${quizState.score}/${questions.length}</div><div style="color:var(--text3);margin:8px 0 16px">${pct}% correct</div><div style="font-size:18px;margin-bottom:20px">${msg}</div><button class="btn btn-primary" onclick="document.getElementById('quizArea').classList.add('hidden')">✕ Close</button></div>`;
    return;
  }
  const q=questions[idx];
  const dots=questions.map((q,i)=>{let c='quiz-dot';if(q.answered)c+=q.selected>=0&&q.options[q.selected].correct?' correct':' wrong';if(i===idx)c+=' current';return `<div class="${c}"></div>`;}).join('');
  const opts=q.options.map((o,i)=>{let c='quiz-opt';if(q.answered){if(o.correct)c+=' correct';else if(i===q.selected)c+=' wrong';}return `<button class="${c}" data-oi="${i}" ${q.answered?'disabled':''}>${o.text}</button>`;}).join('');
  card.innerHTML=`<div class="quiz-progress">${dots}</div><div style="text-align:center;margin-bottom:16px"><div class="quiz-question"><div class="q-char">${q.hanzi}</div><div class="q-hint">${q.pinyin}</div></div></div><div class="quiz-options">${opts}</div>${q.answered?`<div style="text-align:center;margin-top:16px"><button class="btn btn-primary" onclick="nextQuizQ()">${idx<questions.length-1?'Next ▶':'See Results 🎯'}</button></div>`:''}`;
  if(!q.answered) card.querySelectorAll('.quiz-opt').forEach(el=>{el.addEventListener('click',()=>{const oi=parseInt(el.dataset.oi);if(q.answered)return;q.selected=oi;q.answered=true;if(q.options[oi].correct)quizState.score++;renderQuiz();});});
}
function nextQuizQ(){
  quizState.idx++;
  if(quizState.idx>=quizState.questions.length){quizState.done=true;quizCount++;localStorage.setItem('ec_quizCount',quizCount);}
  renderQuiz();updateHomeStats();
}

// ===== PROFILE =====
function renderProfile(){
  const area = document.getElementById('savedWordsArea');
  if(!area) return;
  if(savedWords.length===0){area.innerHTML='<div style="text-align:center;padding:16px;color:var(--text3)">Save words from HSK vocabulary to review them here. 🌟</div>';return;}
  const all = [...Object.values(HSK_DATA).flat(), ...THEMED_VOCAB.flatMap(c=>c.words)];
  const words = savedWords.map(w => all.find(v=>v.hanzi===w)||{hanzi:w,pinyin:'?',meaning:'Saved word'});
  area.innerHTML = `<div style="display:grid;gap:8px">${words.map(w=>`<div style="display:flex;align-items:center;gap:12px;padding:8px 12px;border-radius:8px;background:var(--surface2)"><span style="font-size:20px;font-weight:500">${w.hanzi}</span><span style="color:var(--secondary);font-size:13px">${w.pinyin}</span><span style="color:var(--text3);font-size:13px;flex:1">${w.meaning}</span><span style="cursor:pointer;font-size:16px" onclick="toggleSaveWord('${w.hanzi}');renderProfile();updateHomeStats()">✕</span></div>`).join('')}</div>`;
}


// ===== AUTH SYSTEM =====
const auth = JSON.parse(localStorage.getItem('ec_auth') || '{"users":[],"current":null}');

function saveAuth() {
  localStorage.setItem('ec_auth', JSON.stringify(auth));
}

function isLoggedIn() {
  return auth.current !== null;
}

function getCurrentUser() {
  return auth.current;
}

function openLogin() {
  document.getElementById('loginOverlay').style.display = 'flex';
  document.getElementById('loginError').style.display = 'none';
  document.getElementById('regError').style.display = 'none';
}

function closeLogin() {
  document.getElementById('loginOverlay').style.display = 'none';
}

function showRegister() {
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('registerForm').style.display = 'block';
  document.getElementById('regError').style.display = 'none';
}

function showLogin() {
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('registerForm').style.display = 'none';
  document.getElementById('loginError').style.display = 'none';
}

function doLogin() {
  const user = document.getElementById('loginUser').value.trim();
  const pass = document.getElementById('loginPass').value.trim();
  const err = document.getElementById('loginError');
  if (!user || !pass) { err.textContent = '请填写用户名和密码'; err.style.display = 'block'; return; }
  const found = auth.users.find(u => u.username === user && u.password === pass);
  if (!found) { err.textContent = '用户名或密码错误'; err.style.display = 'block'; return; }
  auth.current = { username: found.username, joined: found.joined };
  saveAuth();
  closeLogin();
  renderAuthUI();
  updateHomeStats();
  toast('✅ 登录成功，欢迎回来！', 'success');
}

function doRegister() {
  const user = document.getElementById('regUser').value.trim();
  const pass = document.getElementById('regPass').value.trim();
  const confirm = document.getElementById('regConfirm').value.trim();
  const err = document.getElementById('regError');
  if (!user || !pass) { err.textContent = '请填写用户名和密码'; err.style.display = 'block'; return; }
  if (pass !== confirm) { err.textContent = '两次密码不一致'; err.style.display = 'block'; return; }
  if (pass.length < 3) { err.textContent = '密码至少3位'; err.style.display = 'block'; return; }
  if (auth.users.find(u => u.username === user)) { err.textContent = '用户名已存在'; err.style.display = 'block'; return; }
  const newUser = { username: user, password: pass, joined: new Date().toISOString().slice(0,10) };
  auth.users.push(newUser);
  auth.current = { username: user, joined: newUser.joined };
  saveAuth();
  closeLogin();
  renderAuthUI();
  updateHomeStats();
  toast('🎉 注册成功！欢迎 ' + user, 'success');
}

function logout() {
  auth.current = null;
  saveAuth();
  renderAuthUI();
  toast('已退出登录', 'info');
}

function renderAuthUI() {
  const sidebar = document.querySelector('.sidebar-nav');
  if (!sidebar) return;
  const existing = document.getElementById('authSidebar');
  if (existing) existing.remove();
  const div = document.createElement('div');
  div.id = 'authSidebar';
  if (isLoggedIn()) {
    const u = getCurrentUser();
    div.innerHTML = '<div class="user-info-sidebar"><div class="avatar">' + u.username[0].toUpperCase() + '</div><span>' + u.username + '</span><button class="logout-btn" onclick="logout()">退出</button></div>';
    // Update profile
    const pn = document.getElementById('profileName');
    if (pn) pn.textContent = u.username;
    const pj = document.getElementById('profileJoined');
    if (pj) pj.textContent = '加入于 ' + (u.joined || '2026');
  } else {
    div.innerHTML = '<button class="login-btn-sidebar" onclick="openLogin()">👤 登录 / 注册</button>';
    const pn = document.getElementById('profileName');
    if (pn) pn.textContent = '未登录';
  }
  sidebar.after(div);
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded',()=>{
  // Sidebar nav
  document.querySelectorAll('.nav-item').forEach(item=>{
    item.addEventListener('click',()=>navigateTo(item.dataset.page));
  });
  // Mobile toggle
  const mt = document.getElementById('mobileToggle');
  const so = document.getElementById('sidebarOverlay');
  if(mt) mt.addEventListener('click',()=>{
    document.getElementById('sidebar')?.classList.toggle('open');
    so?.classList.toggle('show');
  });
  if(so) so.addEventListener('click',()=>{
    document.getElementById('sidebar')?.classList.remove('open');
    so.classList.remove('show');
  });
  // Stroke nav
  const scP = document.getElementById('scPrev');
  const scN = document.getElementById('scNext');
  if(scP) scP.addEventListener('click',()=>{scIndex=(scIndex-1+STROKE_CHARS.length)%STROKE_CHARS.length;scStep=0;renderStroke();});
  if(scN) scN.addEventListener('click',()=>{scIndex=(scIndex+1)%STROKE_CHARS.length;scStep=0;renderStroke();});
  // Flashcard
  const fc = document.getElementById('flashcardEl');
  if(fc) fc.addEventListener('click',(e)=>{if(!e.target.closest('.btn'))toggleFlashcard();});
  document.getElementById('fcFlip')?.addEventListener('click',toggleFlashcard);
  document.getElementById('fcPrev')?.addEventListener('click',prevFlashcard);
  document.getElementById('fcNext')?.addEventListener('click',nextFlashcard);
  // Render all
  renderPinyin(); renderStroke(); renderRadicals(); loadHSK(1);
  updateStreakUI(); updateHomeStats(); renderProfile();
  // Auth
  renderAuthUI();
  // Clean up any remaining AI references
  const aiRemnants = document.querySelectorAll(".ai-toggle, .chat-panel, .chat-presets");
  aiRemnants.forEach(el => el.remove());
  // Re-render
  renderAuthUI();
  // Re-render on language change
  document.addEventListener('langchange', () => {
    renderPinyin();
    renderStroke();
    renderRadicals();
    renderProfile();
    updateHomeStats();
    updateStreakUI();
    if(hskLevel>0) loadHSK(hskLevel);
  });
});
