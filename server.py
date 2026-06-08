#!/usr/bin/env python3
"""智慧丝路 AI 后端代理服务器
- 提供静态文件服务（chinese-learning.html）
- 转发 AI 对话请求到 SiliconFlow DeepSeek API（流式 SSE）
- 个性化学习推荐接口
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# 读取 API Key（优先环境变量，次选文件）
KEY = os.environ.get("SILICONFLOW_API_KEY", "")
if not KEY:
    KEY_FILE = os.path.expanduser("~/.hermes/sf_key_tmp")
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            KEY = f.read().strip().split("=", 1)[1]

# SiliconFlow 兼容 OpenAI 格式
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3"

# HTML 文件路径（与 server.py 同目录）
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chinese-learning.html")


def stream_chat(messages):
    """调用 SiliconFlow API（流式）"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = Request(API_URL, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + KEY,
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
        # 健康检查
        if self.path == "/api/health":
            return self._send_json(200, {"status": "ok", "model": MODEL})

        # 个性化推荐
        if self.path.startswith("/api/recommend"):
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            saved_words = params.get("words", [""])[0] if "words" in params else ""
            level = params.get("level", ["hsk1"])[0]

            # 根据水平推荐学习内容
            recs = generate_recommendations(level, saved_words)
            return self._send_json(200, recs)

        # 提供静态 HTML
        if os.path.exists(HTML_FILE):
            with open(HTML_FILE, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json(404, {"error": "HTML file not found"})

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send_json(404, {"error": "Not found"})

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except Exception:
            return self._send_json(400, {"error": "Invalid JSON"})

        message = body.get("message", "")
        history = body.get("history", [])

        if not message:
            return self._send_json(400, {"error": "Message is required"})

        # 构建 messages：系统提示 + 历史 + 当前消息
        system_prompt = {
            "role": "system",
            "content": "你是一个汉语学习助手（名称：智慧丝路助手）。"
                       "你是面向外国留学生的AI辅助汉语学习平台的一部分。\n\n"
                       "你的职责：\n"
                       "1. 用中文回答学习者的汉语问题（语法、词汇、发音、文化等）\n"
                       "2. 如果学习者用母语问，你用中文回答并附上简单解释\n"
                       "3. 耐心、鼓励式的语气，适当纠正和引导\n"
                       "4. 回答控制在150字以内，简洁实用\n"
                       "5. 可以给出例句帮助理解\n\n"
                       "如果学习者问非学习问题，礼貌引导回学习话题。"
        }

        messages = [system_prompt]
        # 添加上下文历史（最多10轮）
        for h in history[-10:]:
            if isinstance(h, dict) and "role" in h and "content" in h:
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        # 返回 SSE 流
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        try:
            full_response = ""
            for chunk in stream_chat(messages):
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
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else "8833"))
    host = os.environ.get("HOST", "0.0.0.0")  # Railway 需要 0.0.0.0
    print(f"🌐 智慧丝路 AI 服务器启动")
    print(f"📁 服务页面: http://{host}:{port}")
    print(f"💬 AI 对话: http://{host}:{port}/api/chat")
    print(f"🔑 API Key: {'已配置' if KEY else '未配置 — 设置 SILICONFLOW_API_KEY 环境变量'}")
    print(f"📄 HTML: {HTML_FILE}")
    print(f"按 Ctrl+C 停止")
    HTTPServer((host, port), Handler).serve_forever()
