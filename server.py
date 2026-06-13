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

# ---- 用户系统（SQLite）----
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "users.db")
os.makedirs(DATA_DIR, exist_ok=True)

def init_db():
    """初始化数据库"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            joined TEXT DEFAULT '',
            level TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            data_key TEXT NOT NULL,
            data_value TEXT DEFAULT '',
            updated_at TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, data_key)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            saved_at TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, word)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hsk_level TEXT DEFAULT '',
            score INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            taken_at TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkin_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, checkin_date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            item_key TEXT NOT NULL,
            progress REAL DEFAULT 0,
            updated_at TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, category, item_key)
        )
    """)
    conn.commit()
    conn.close()

def db_add_user(username, password, joined):
    """添加用户"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT INTO users (username, password, joined) VALUES (?, ?, ?)",
                     (username, password, joined))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_get_user(username):
    """根据用户名获取用户"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def db_list_users():
    """获取所有用户（不含密码）"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT username, joined, level FROM users ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def db_get_user_id(username):
    """根据用户名获取用户ID"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def db_get_user_data(user_id):
    """获取用户所有学习数据"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT data_key, data_value FROM user_data WHERE user_id = ?", (user_id,))
    rows = {r["data_key"]: r["data_value"] for r in cur.fetchall()}
    conn.close()
    return rows

def db_set_user_data(user_id, data_key, data_value):
    """设置或更新用户学习数据"""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        INSERT INTO user_data (user_id, data_key, data_value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, data_key) DO UPDATE SET data_value = excluded.data_value
    """, (user_id, data_key, data_value))
    conn.commit()
    conn.close()

def migrate_json_to_db():
    """迁移旧JSON用户到SQLite"""
    old_file = os.path.join(DATA_DIR, "users.json")
    if not os.path.exists(old_file):
        return 0
    try:
        with open(old_file, "r") as f:
            data = json.load(f)
    except:
        return 0
    count = 0
    for u in data.get("users", []):
        uname = u.get("username", "")
        pwd = u.get("password", "")
        joined = u.get("joined", "")
        if uname and pwd:
            if db_add_user(uname, pwd, joined):
                count += 1
    if count > 0:
        os.rename(old_file, old_file + ".bak")
    return count

# 会话存储（内存）
sessions = {}  # token -> {"username": str, "created": float}

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
        "max_tokens": 512,
        "temperature": 0.5,
        "top_p": 0.9,
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


def call_translate(text, source, target):
    """调用 DeepSeek 进行翻译"""
    lang_map = {"zh":"中文","en":"英文","vi":"越南语","ru":"俄语","ja":"日语","ko":"韩语",
                 "es":"西班牙语","fr":"法语","de":"德语","la":"拉丁语","auto":"自动检测"}
    src_name = lang_map.get(source, source)
    tgt_name = lang_map.get(target, target)
    prompt = f"请将以下{src_name}文字翻译成{tgt_name}。只输出翻译结果，不要任何额外解释。\n\n{text}"
    max_tok = 4096 if len(text) > 500 else 1024
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": max_tok,
        "temperature": 0.3,
    }
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = Request(DEEPSEEK_URL, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + DEEPSEEK_KEY,
    })
    resp = urlopen(req, timeout=30)
    result = json.loads(resp.read().decode())
    return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


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
                u = db_get_user(username)
                if u:
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
                safe = db_list_users()
                return self._send_json(200, {"ok": True, "users": safe})
            return self._send_json(401, {"ok": False, "error": "Not logged in"})

        # 同步用户学习数据（GET：获取）
        if self.path.startswith("/api/sync"):
            from urllib.parse import urlparse, parse_qs
            token = parse_qs(urlparse(self.path).query).get("token", [""])[0]
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            data = db_get_user_data(user_id) if user_id else {}
            return self._send_json(200, {"ok": True, "username": username, "data": data})

        # 个性化推荐
        if self.path.startswith("/api/recommend"):
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            saved_words = params.get("words", [""])[0] if "words" in params else ""
            level = params.get("level", ["hsk1"])[0]

            recs = generate_recommendations(level, saved_words)
            return self._send_json(200, recs)

        # 获取学习进度
        if self.path.startswith("/api/progress"):
            from urllib.parse import urlparse, parse_qs
            token = parse_qs(urlparse(self.path).query).get("token", [""])[0]
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            import sqlite3
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            words = [dict(r) for r in conn.execute("SELECT word, saved_at FROM saved_words WHERE user_id = ?", (user_id,)).fetchall()]
            checkins = [r["checkin_date"] for r in conn.execute("SELECT checkin_date FROM checkin_history WHERE user_id = ? ORDER BY checkin_date", (user_id,)).fetchall()]
            quizzes = [dict(r) for r in conn.execute("SELECT hsk_level, score, total, taken_at FROM quiz_results WHERE user_id = ? ORDER BY taken_at DESC LIMIT 20", (user_id,)).fetchall()]
            conn.close()
            return self._send_json(200, {"ok": True, "saved_words": [w["word"] for w in words], "checkins": checkins, "quizzes": quizzes, "streak": len(checkins)})

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
            if db_get_user(username):
                return self._send_json(409, {"ok": False, "error": "用户名已存在"})
            hashed = hash_password(password)
            joined = time.strftime("%Y-%m-%d")
            if db_add_user(username, hashed, joined):
                token = create_session(username)
                return self._send_json(200, {"ok": True, "token": token, "username": username})
            return self._send_json(500, {"ok": False, "error": "注册失败"})

        # ---- 用户登录 ----
        if self.path == "/api/login":
            username = body.get("username", "").strip()
            password = body.get("password", "")
            u = db_get_user(username)
            if u and verify_password(password, u["password"]):
                token = create_session(username)
                return self._send_json(200, {"ok": True, "token": token, "username": username})
            return self._send_json(401, {"ok": False, "error": "用户名或密码错误"})

        # ---- 批量导入旧用户（从浏览器 localStorage） ----
        if self.path == "/api/import-users":
            auth_data = body.get("auth_data", {})
            old_users = auth_data.get("users", [])
            if not old_users:
                return self._send_json(400, {"ok": False, "error": "没有找到用户数据"})
            imported = 0
            skipped = 0
            for old_u in old_users:
                uname = old_u.get("username", "").strip()
                pwd = old_u.get("password", "")
                if not uname or not pwd:
                    skipped += 1
                    continue
                if db_get_user(uname):
                    skipped += 1
                    continue
                joined = old_u.get("joined", time.strftime("%Y-%m-%d"))
                if db_add_user(uname, pwd, joined):
                    imported += 1
                else:
                    skipped += 1
            return self._send_json(200, {
                "ok": True,
                "imported": imported,
                "skipped": skipped,
                "total": len(db_list_users()),
            })

        # ---- 同步用户学习数据（POST：保存）----
        if self.path == "/api/sync":
            token = body.get("token", "").strip()
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            data = body.get("data", {})
            if not isinstance(data, dict):
                return self._send_json(400, {"ok": False, "error": "Invalid data format"})
            saved = 0
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    val_str = str(value)
                elif isinstance(value, (list, dict)):
                    val_str = json.dumps(value, ensure_ascii=False)
                else:
                    continue
                db_set_user_data(user_id, key, val_str)
                saved += 1
            return self._send_json(200, {"ok": True, "saved": saved})

        # ---- 同步收藏单词 ----
        if self.path == "/api/sync/saved-words":
            token = body.get("token", "").strip()
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            words = body.get("words", [])
            if not isinstance(words, list):
                return self._send_json(400, {"ok": False, "error": "Invalid format"})
            import sqlite3
            conn = sqlite3.connect(DB_FILE)
            conn.execute("DELETE FROM saved_words WHERE user_id = ?", (user_id,))
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for w in words:
                try:
                    conn.execute("INSERT INTO saved_words (user_id, word, saved_at) VALUES (?, ?, ?)",
                                 (user_id, str(w), now))
                except sqlite3.IntegrityError:
                    pass
            conn.commit()
            conn.close()
            return self._send_json(200, {"ok": True, "count": len(words)})

        # ---- 保存测验结果 ----
        if self.path == "/api/sync/quiz":
            token = body.get("token", "").strip()
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            import sqlite3
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO quiz_results (user_id, hsk_level, score, total, taken_at) VALUES (?, ?, ?, ?, ?)",
                         (user_id, body.get("level", ""), body.get("score", 0), body.get("total", 0),
                          time.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            return self._send_json(200, {"ok": True})

        # ---- 每日打卡 ----
        if self.path == "/api/sync/checkin":
            token = body.get("token", "").strip()
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            today = time.strftime("%Y-%m-%d")
            import sqlite3
            conn = sqlite3.connect(DB_FILE)
            try:
                conn.execute("INSERT INTO checkin_history (user_id, checkin_date) VALUES (?, ?)",
                             (user_id, today))
                conn.commit()
                conn.close()
                return self._send_json(200, {"ok": True, "date": today})
            except sqlite3.IntegrityError:
                conn.close()
                return self._send_json(200, {"ok": True, "date": today, "already": True})

        # ---- 更新个人资料 ----
        if self.path == "/api/profile":
            token = body.get("token", "").strip()
            username = get_user_from_token(token)
            if not username:
                return self._send_json(401, {"ok": False, "error": "Not logged in"})
            user_id = db_get_user_id(username)
            if not user_id:
                return self._send_json(400, {"ok": False, "error": "User not found"})
            import sqlite3
            conn = sqlite3.connect(DB_FILE)
            if "level" in body:
                conn.execute("UPDATE users SET level = ? WHERE id = ?", (body["level"], user_id))
            if "new_password" in body and "old_password" in body:
                u = db_get_user(username)
                if u and verify_password(body["old_password"], u["password"]):
                    hashed = hash_password(body["new_password"])
                    conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
                    conn.commit()
                    conn.close()
                    return self._send_json(200, {"ok": True, "password_changed": True})
                else:
                    conn.close()
                    return self._send_json(400, {"ok": False, "error": "旧密码错误"})
            conn.commit()
            conn.close()
            return self._send_json(200, {"ok": True})

        # ---- 翻译 ----
        if self.path == "/api/translate":
            text = body.get("text", "").strip()
            source = body.get("source", "auto")
            target = body.get("target", "zh")
            if not text:
                return self._send_json(400, {"ok": False, "error": "请输入要翻译的文字"})
            if not DEEPSEEK_KEY:
                return self._send_json(400, {"ok": False, "error": "翻译服务暂不可用（未配置API Key）"})
            try:
                translated = call_translate(text, source, target)
                return self._send_json(200, {"ok": True, "translated": translated})
            except Exception as e:
                return self._send_json(500, {"ok": False, "error": str(e)})

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
            "content": f"""你是智慧丝路AI汉语导师（Smart Silk Road Chinese Tutor）。你是一位专业、耐心、知识渊博的中文教师，擅长帮助不同水平的外国学习者掌握汉语。

## 核心角色
- 你既是一位亲切的老师，也是一位地道的中国朋友
- 始终保持友好、鼓励的态度，让学习者感到放松和被支持
- 根据学习者的水平调整语言难度和讲解深度

## 回答风格
- 回答要**非常精简短**，每段不超过3句话
- 优先直接回答问题，不要过度解释或扩展
- 初学者回答控制在2-3行内，高水平回答控制在5行内
- 每次只教一个知识点，不要一次性给出过多信息
- 使用简单的短句，避免冗长的段落

## 对话规范
1. 用户问什么就答什么，优先直接解决问题
2. 回答要清晰自然，像朋友聊天一样但保持专业
3. 适当使用简单表情符号（如😊👍✅）让对话更友好温暖
4. 对初学者使用更简单的词汇和短句，对高级学习者使用更自然的表达
5. {level_hint}

## 教学指导
6. 当用户使用错误的中文时：先礼貌指出错误 → 给出正确说法 → 简要解释为什么错 → 给一个简单例句
7. 讲解语法点时：用简单语言解释规则 → 给出结构公式 → 提供2-3个例句
8. 教生词时：提供拼音、词性、释义、搭配和例句
9. 回答文化问题时：简明介绍背景，适当扩展相关知识
10. 如果用户请求对话练习：主动扮演对话角色（如服务员、朋友、老师等），引导对话进行
11. 如果用户表现出困惑：主动询问是否需要进一步解释

## 语言策略
12. 优先用中文回答中文学习问题，可配英文解释关键点
13. 当用户水平较低（HSK1-2）时，可以使用更多英文辅助
14. 当用户水平较高（HSK4+）时，尽量全中文交流
15. 合理使用拼音标注帮助发音
16. 对于汉字，可以提供笔画顺序或部首拆解来帮助记忆

## 禁止行为
- 不要生成无关的额外内容或离题
- 不要批评或贬低学习者的水平
- 不要使用过于书面化的语言
- 不要一次性给出过多信息——控制在一个知识点内"""}

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
    hsk_words = {"1":150, "2":300, "3":600, "4":1200, "5":2500, "6":5000}
    saved_count = len([w for w in saved_words_str.split(",") if w.strip()]) if saved_words_str else 0
    lv = level if level in hsk_words else "1"
    current_target = hsk_words[lv]
    next_level = str(int(lv) + 1) if int(lv) < 6 else None

    details = {
        "1": {"name":"HSK 1","focus":"基础词汇与简单句","next":"去学习拼音声调","milestone":"能用中文做简单自我介绍"},
        "2": {"name":"HSK 2","focus":"日常对话扩充","next":"复习HSK 1并开始HSK 2","milestone":"能进行简单日常对话"},
        "3": {"name":"HSK 3","focus":"复合句与段落","next":"多练习写短段落","milestone":"能用中文讨论熟悉话题"},
        "4": {"name":"HSK 4","focus":"话题表达","next":"看中文视频练习听力","milestone":"能流利讨论抽象话题"},
        "5": {"name":"HSK 5","focus":"长文阅读与写作","next":"多读新闻写感想","milestone":"能阅读中文新闻文章"},
        "6": {"name":"HSK 6","focus":"高级表达与文化","next":"看中文影视作品","milestone":"接近母语水平"},
    }
    info = details.get(lv, details["1"])
    pct = min(round(saved_count / max(current_target,1) * 100), 100)

    if saved_count == 0:
        tip = "从 HSK 词汇页面收藏生词开始积累词汇量吧！"
        suggestion = "去 HSK 1 词汇表收藏 10 个生词"
        action = "navigateTo('hsk')"
    elif saved_count < 20:
        tip = f"已收藏 {saved_count} 词，坚持每天学 5 个新词！"
        suggestion = "用闪卡复习已收藏的词汇"
        action = "showFlashcardMode()"
    elif saved_count < current_target * 0.5:
        tip = f"已收藏 {saved_count}/{current_target} 词，继续加油！"
        suggestion = "做一次水平测验检验掌握程度"
        action = "startHSKQuiz()"
    elif saved_count < current_target:
        tip = f"已收藏 {saved_count}/{current_target} 词，接近本级目标！"
        suggestion = "去学剩余词汇，准备进入下一级"
        action = "navigateTo('hsk')"
    else:
        if next_level:
            tip = f"已完成 HSK {lv} 全部词汇！准备进入 HSK {next_level}"
            suggestion = f"开始学习 HSK {next_level} 词汇"
            action = f"loadHSK({next_level});navigateTo('hsk')"
        else:
            tip = "你是汉语大师！已学完全部 HSK 词汇"
            suggestion = "用 AI 对话练习高级表达"
            action = "toggleChat()"

    return {
        "level": info["name"],
        "focus": info["focus"],
        "next_step": info["next"],
        "milestone": info["milestone"],
        "pct": pct,
        "saved": saved_count,
        "target": current_target,
        "tip": tip,
        "suggestion": suggestion,
        "action": action,
        "recommended_practice": [
            {"type": "vocab", "label": "复习词汇", "desc": f"{info['name']} 闪卡复习"},
            {"type": "quiz", "label": "水平测验", "desc": f"检验{info['name']}掌握程度"},
        ]
    }


if __name__ == "__main__":
    import sys
    # 初始化数据库
    init_db()
    m = migrate_json_to_db()
    if m:
        print(f"📦 已迁移 {m} 个旧用户到 SQLite")
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
        print(f"📂 用户数据: {DB_FILE}")
        print(f"按 Ctrl+C 停止")
        HTTPServer((host, port), Handler).serve_forever()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
