// ===== AI 智能助手 =====
let chatHistory = [];
let chatInit = false;
const API_KEY='';
const API = 'https://api.deepseek.com/v1/chat/completions';
const MODEL = 'deepseek-chat';

function initChat() {
  if (chatInit) return;
  chatInit = true;
  const toggle = document.getElementById('aiToggle');
  const panel = document.getElementById('chatPanel');
  if (!toggle || !panel) return;

  toggle.addEventListener('click', () => {
    panel.classList.toggle('open');
    if (panel.classList.contains('open') && chatHistory.length === 0) {
      addMsg('你好！有什么可以帮你的？😊', 'ai');
    }
  });
  document.getElementById('chatClose')?.addEventListener('click', () => panel.classList.remove('open'));

  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSend');
  if (!input || !sendBtn) return;

  function send() {
    const t = input.value.trim();
    if (!t) return;
    addMsg(t, 'user');
    input.value = '';
    sendBtn.disabled = true;
    input.disabled = true;
    sendToAI(t);
  }
  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
}

function addMsg(text, role) {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.innerHTML = text.replace(/\n/g, '<br>') +
    `<div class="msg-time">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  chatHistory.push({ role, text });
}

function showTyping() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-msg ai';
  div.id = 'chatTyping';
  div.textContent = '...';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

async function sendToAI(text) {
  const typing = showTyping();

  const msgs = chatHistory.filter(h => h.role === 'user' || h.role === 'assistant')
    .slice(-10).map(h => ({ role: h.role === 'assistant' ? 'assistant' : 'user', content: h.text }));
  msgs.unshift({
    role: 'system',
    content: '你是一个专业的中文家教，帮助外国人学习中文。回答简洁清晰，用到中文时附带拼音和英文翻译。语气友好鼓励。',
  });
  msgs.push({ role: 'user', content: text });

  try {
    const resp = await fetch(API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: msgs,
        temperature: 0.7,
        max_tokens: 1000,
      }),
    });

    typing.remove();

    if (!resp.ok) {
      if (resp.status === 401) {
        addMsg('⚠️ API Key 无效，请联系管理员。', 'ai');
      } else {
        addMsg(`⚠️ 请求失败 (${resp.status})，请稍后重试。`, 'ai');
      }
      document.getElementById('chatSend').disabled = false;
      document.getElementById('chatInput').disabled = false;
      return;
    }

    const data = await resp.json();
    const reply = data.choices?.[0]?.message?.content;
    addMsg(reply || '抱歉，请换个方式问我😊', 'ai');

  } catch (e) {
    typing.remove();
    if (window.location.protocol === 'file:') {
      addMsg('⚠️ 请运行以下命令启动服务：\npython3 -m http.server 8000\n然后打开 http://localhost:8000', 'ai');
    } else {
      addMsg('⚠️ 网络错误，请检查连接。', 'ai');
    }
  }

  document.getElementById('chatSend').disabled = false;
  document.getElementById('chatInput').disabled = false;
  document.getElementById('chatInput').focus();
}
