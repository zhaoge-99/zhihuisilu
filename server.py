#!/usr/bin/env python3
"""智慧丝路 AI 后端代理服务器
- 提供静态文件服务（chinese-learning.html）
- AI 对话（支持 SiliconFlow 和 DeepSeek 直连双模型）
- 个性化学习推荐接口
- 用户注册/登录（集中管理）
"""
import json, os, sys, hashlib, secrets, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ===== SiliconFlow 配置（DeepSeek 中转）=====
SILICONFLOW_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
if not SILICONFLOW_KEY:
    KEY_FILE = os.path.expanduser("~/.hermes/sf_key_tmp")
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            SILICONFLOW_KEY = f.read().strip().split("=", 1)[1]

SILICONFLOW_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_MODEL = "deepseek-ai/DeepSeek-V3"

# ===== DeepSeek 直连配置 =====
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_KEY:
    # 尝试从 OpenClaw 配置读取
    OCFILE = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    if os.path.exists(OCFILE):
        try:
            with open(OCFILE) as f:
                oc = json.load(f)
            DEEPSEEK_KEY = oc.get("profiles", {}).get("deepseek:default", {}).get("key", "")
        except Exception:
            pass

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 双模型名称映射
MODEL_NAMES = {
    "siliconflow": "丝路智联",
    "deepseek": "丝路极速",
}

# HTML 文件路径（与 server.py 同目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "chinese-learning.html")

# ---- 用户系统 ----
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
os.makedirs(DATA_DIR, exist_ok=True)

# 会话存储（内存）
sessions = {}  # token -> {"username": str, "created": float}

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": []}

def save_users(data):
    """保存用户数据"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password, salt=None):
    """SHA256 哈希密码"""
    if salt is None:
        salt = secrets.token_hex(8)
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${h}"

def verify_password(password, stored):
    """验证密码"""
    salt = stored.split("$")[0]
    return hash_password(password, salt) == stored

def create_session(username):
    """创建会话 token"""
    token = secrets.token_hex(32)
    sessions[token] = {"username": username, "created": time.time()}
    # 清理过期会话（7天）
    now = time.time()
    expired = [t for t, s in sessions.items() if now - s["created"] > 604800]
    for t in expired:
        del sessions[t]
    return token

def get_user_from_token(token):
    """通过 token 获取用户名"""
    s = sessions.get(token)
    if s and time.time() - s["created"] < 604800:
        return s["username"]
    return None


def stream_chat(messages, provider="siliconflow"):
    """调用 AI API（流式），支持 siliconflow / deepseek 双模型"""
    if provider == "deepseek":
        api_url = DEEPSEEK_URL
        api_key = DEEPSEEK_KEY
        model = DEEPSEEK_MODEL
    else:
        api_url = SILICONFLOW_URL
        api_key = SILICONFLOW_KEY
        model = SILICONFLOW_MODEL

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": 4096,
        "temperature": 0.85,
        "top_p": 0.95,
    }
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = Request(api_url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    })
    resp = urlopen(req, timeout=120)
    for line in resp:
        line = line.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        if line.startswith("data: "):
            chunk = line[6:]
            if chunk == "[DONE]":
                break
            try:
                obj = json.loads(chunk)
                delta = obj.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content
            except json.JSONDecodeError:
                continue


class Handler(BaseHTTPRequestHandler):

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, event, data):
        self.wfile.write(f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8"))
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # 分离路径和查询参数
        path_only = self.path.split("?", 1)[0]

        # 健康检查
        if path_only == "/api/health":
            return self._send_json(200, {"status": "ok", "models": {
                "siliconflow": SILICONFLOW_MODEL,
                "deepseek": DEEPSEEK_MODEL,
                "available": ["siliconflow", "deepseek"],
                "names": MODEL_NAMES,
            }})

        # 获取当前用户信息
        if path_only == "/api/me":
            from urllib.parse import urlparse, parse_qs
            token = parse_qs(urlparse(self.path).query).get("token", [""])[0]
            username = get_user_from_token(token)
            if username:
                data = load_users()
                for u in data["users"]:
                    if u["username"] == username:
                        return self._send_json(200, {
                            "ok": True,
                            "username": username,
                            "joined": u.get("joined", ""),
                            "level": u.get("level", ""),
                        })
            return self._send_json(401, {"ok": False, "error": "Not logged in"})

        # 管理员：列出所有用户
        if path_only == "/api/users":
            from urllib.parse import urlparse, parse_qs
            token = parse_qs(urlparse(self.path).query).get("token", [""])[0]
            username = get_user_from_token(token)
            if username:
                data = load_users()
                # 不返回密码
                safe = []
                for u in data["users"]:
                    safe.append({
                        "username": u["username"],
                        "joined": u.get("joined", ""),
                        "level": u.get("level", ""),
                    })
                return self._send_json(200, {"ok": True, "users": safe})
            return self._send_json(401, {"ok": False, "error": "Not logged in"})

        # 个性化推荐
        if self.path.startswith("/api/recommend"):
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            saved_words = params.get("words", [""])[0] if "words" in params else ""
            level = params.get("level", ["hsk1"])[0]

            recs = generate_recommendations(level, saved_words)
            return self._send_json(200, recs)

        # 提供静态文件
        file_path = self.path.split("?", 1)[0].lstrip("/")

        # 登录页路由
        if file_path in ("login", "login.html"):
            full_path = os.path.join(BASE_DIR, "login.html")
            if not os.path.exists(full_path):
                return self._send_json(404, {"error": "login.html not found"})
            content_type = "text/html; charset=utf-8"
            with open(full_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if file_path == "":
            file_path = "chinese-learning.html"
        full_path = os.path.normpath(os.path.join(BASE_DIR, file_path))
        if not full_path.startswith(BASE_DIR):
            return self._send_json(403, {"error": "Forbidden"})
        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            mime_map = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
                ".json": "application/json; charset=utf-8",
                ".webp": "image/webp",
            }
            content_type = mime_map.get(ext, "application/octet-stream")
            with open(full_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json(404, {"error": "File not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except Exception:
            return self._send_json(400, {"error": "Invalid JSON"})

        # ---- 用户注册 ----
        if self.path == "/api/register":
            username = body.get("username", "").strip()
            password = body.get("password", "")
            if len(username) < 3 or len(username) > 20:
                return self._send_json(400, {"ok": False, "error": "用户名需3~20个字符"})
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return self._send_json(400, {"ok": False, "error": "用户名只能包含字母、数字和下划线"})
            if len(password) < 8:
                return self._send_json(400, {"ok": False, "error": "密码至少8位"})
            if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
                return self._send_json(400, {"ok": False, "error": "密码必须包含字母和数字"})
            data = load_users()
            for u in data["users"]:
                if u["username"] == username:
                    return self._send_json(409, {"ok": False, "error": "用户名已存在"})
            new_user = {
                "username": username,
                "password": hash_password(password),
                "joined": time.strftime("%Y-%m-%d"),
                "level": "",
            }
            data["users"].append(new_user)
            save_users(data)
            token = create_session(username)
            return self._send_json(200, {"ok": True, "token": token, "username": username})

        # ---- 用户登录 ----
        if self.path == "/api/login":
            username = body.get("username", "").strip()
            password = body.get("password", "")
            data = load_users()
            for u in data["users"]:
                if u["username"] == username and verify_password(password, u["password"]):
                    token = create_session(username)
                    return self._send_json(200, {"ok": True, "token": token, "username": username})
            return self._send_json(401, {"ok": False, "error": "用户名或密码错误"})

        # ---- 批量导入旧用户（从浏览器 localStorage） ----
        if self.path == "/api/import-users":
            auth_data = body.get("auth_data", {})
            old_users = auth_data.get("users", [])
            if not old_users:
                return self._send_json(400, {"ok": False, "error": "没有找到用户数据"})

            data = load_users()
            imported = 0
            skipped = 0
            existing = {u["username"] for u in data["users"]}

            for old_u in old_users:
                username = old_u.get("username", "").strip()
                password = old_u.get("password", "")
                if not username or not password:
                    skipped += 1
                    continue
                if username in existing:
                    skipped += 1
                    continue
                data["users"].append({
                    "username": username,
                    "password": hash_password(password),
                    "joined": old_u.get("joined", time.strftime("%Y-%m-%d")),
                    "level": "",
                })
                existing.add(username)
                imported += 1

            save_users(data)
            return self._send_json(200, {
                "ok": True,
                "imported": imported,
                "skipped": skipped,
                "total": len(data["users"]),
            })

        # ---- 聊天 ----
        if self.path != "/api/chat":
            return self._send_json(404, {"error": "Not found"})

        message = body.get("message", "")
        history = body.get("history", [])
        if not message:
            return self._send_json(400, {"error": "Message is required"})

        level = body.get("level", "")
        saved_words = body.get("savedWords", "")
        provider = body.get("provider", "siliconflow")
        saved_count = len([w for w in saved_words.split(",") if w.strip()]) if saved_words else 0

        level_hint = ""
        if level:
            level_names = {"1": "HSK1（零基础）", "2": "HSK2", "3": "HSK3", "4": "HSK4", "5": "HSK5", "6": "HSK6"}
            lname = level_names.get(level, f"HSK{level}")
            level_hint = f"学习者的汉语水平大约是{lname}。请根据这个水平调整你的用语难度——对低水平学习者用更简单的词和短句，对高水平学习者可以用更自然的表达。"
        if saved_count > 0:
            level_hint += f" ta已经收藏了{saved_count}个词汇。你可以在回答中适当引用或拓展ta已学的词汇。"

        system_prompt = {
            "role": "system",
            "content": f"""你是「智慧丝路助手」——一个温暖、有趣、像朋友一样的AI汉语学习导师。

你的风格：
- 像一位耐心的中国朋友在聊天，而不是教科书或考试机器
- 回答简洁精炼——用最少的话说清楚，不啰嗦不绕弯
- 说话自然、有温度，偶尔带点幽默感
- 先认真听懂学习者的需求，再给出有帮助的回答
- 如果学习者用英语或其他语言提问，用中文回答并附上简单解释

你的能力：
- 教语法、词汇、发音、汉字书写
- 解释中国文化、成语、俗语背后的故事
- 纠正学习者的中文句子，告诉ta怎么改更好
- 用例句帮助理解

{level_hint}

对话要领：
- 回答简短直接，能用一句话说清楚的不用两句话
- 不要急着把回答结束——可以反问学习者"你明白了吗？"、"要不要我举个例子？"
- 回答自然流畅，不要生硬拼凑要点
- 学习者可以问任何问题——生活中、文化上、考试相关——都欢迎
- 如果学习者用错了词或语法，温柔地指出来并给出正确说法

最重要的是：让学习者感觉在和一个真人聊天，而不是面对一个问答机器。"""}

        messages = [system_prompt]
        for h in history[-10:]:
            if isinstance(h, dict) and "role" in h and "content" in h:
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        try:
            full_response = ""
            for chunk in stream_chat(messages, provider):
                full_response += chunk
                self._send_sse("chunk", {"text": chunk})

            self._send_sse("done", {"full": full_response})
            self.wfile.write(b"\n")
            self.wfile.flush()
        except HTTPError as e:
            err_text = e.read().decode("utf-8", errors="replace")[:200]
            self._send_sse("error", {"message": f"API error {e.code}: {err_text}"})
        except Exception as e:
            self._send_sse("error", {"message": f"Server error: {str(e)[:100]}"})


def generate_recommendations(level, saved_words_str):
    """根据学习水平生成个性化推荐"""
    level_map = {
        "1": {"name": "HSK 1", "focus": "基础词汇与简单句", "next": "去学习拼音声调"},
        "2": {"name": "HSK 2", "focus": "日常对话扩充", "next": "复习HSK 1并开始HSK 2"},
        "3": {"name": "HSK 3", "focus": "复合句与段落", "next": "多练习写短段落"},
        "4": {"name": "HSK 4", "focus": "话题表达", "next": "看中文视频练习听力"},
        "5": {"name": "HSK 5", "focus": "长文阅读与写作", "next": "多读新闻，练习写感想"},
        "6": {"name": "HSK 6", "focus": "高级表达与文化", "next": "看中文影视作品"},
    }
    info = level_map.get(level, {"name": "HSK 1", "focus": "基础", "next": "从拼音开始"})

    saved_count = len([w for w in saved_words_str.split(",") if w.strip()]) if saved_words_str else 0

    if saved_count == 0:
        tip = "试试从 HSK 词汇页面收藏一些生词开始复习吧！"
    elif saved_count < 10:
        tip = f"你已经收藏了 {saved_count} 个单词，继续加油！建议每天复习一遍。"
    else:
        tip = f"你已经收藏了 {saved_count} 个单词，建议用闪卡模式巩固记忆。"

    return {
        "level": info["name"],
        "focus": info["focus"],
        "next_step": info["next"],
        "tip": tip,
        "saved_count": saved_count,
        "recommended_practice": [
            {"type": "vocab", "label": "今日复习词汇", "desc": f"{info['name']} 收藏单词闪卡"},
            {"type": "quiz", "label": "水平测验", "desc": f"检验{info['name']}掌握程度"},
            {"type": "chat", "label": "AI 对话练习", "desc": "和 AI 练习日常对话"},
        ]
    }


if __name__ == "__main__":
    import sys
    try:
        port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else "8833"))
        host = os.environ.get("HOST", "0.0.0.0")
        print(f"🌐 智慧丝路 AI 服务器启动")
        print(f"📁 服务页面: http://{host}:{port}")
        print(f"💬 AI 对话: http://{host}:{port}/api/chat")
        print(f"👤 用户注册: http://{host}:{port}/api/register")
        print(f"🔑 用户登录: http://{host}:{port}/api/login")
        print(f"📋 用户列表: http://{host}:{port}/api/users?token=xxx")
        print(f"🔑 API Key 硅基: {'已配置' if SILICONFLOW_KEY else '未配置'}")
        print(f"🔑 API Key DeepSeek: {'已配置' if DEEPSEEK_KEY else '未配置'}")
        print(f"🤖 双模型: {MODEL_NAMES['siliconflow']} / {MODEL_NAMES['deepseek']}")
        print(f"📄 HTML: {HTML_FILE}")
        print(f"📂 用户数据: {USERS_FILE}")
        print(f"按 Ctrl+C 停止")
        HTTPServer((host, port), Handler).serve_forever()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
