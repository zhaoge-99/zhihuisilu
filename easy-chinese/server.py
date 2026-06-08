#!/usr/bin/env python3
"""Easy Chinese Server — serves static files + proxies AI chat to DeepSeek API."""
import os, json, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError
from pathlib import Path

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"
PORT = int(os.environ.get("PORT", 8000))
STATIC_DIR = Path(__file__).parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(STATIC_DIR), **kw)
    def do_POST(self):
        if self.path == "/api/chat": self.handle_chat()
        else: self.send_error(404)
    def handle_chat(self):
        if not API_KEY:
            self._json({"error": "Set DEEPSEEK_API_KEY env var first"}, 503); return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except: self._json({"error":"Invalid JSON"},400); return
        msgs = body.get("messages", [])
        if not msgs: self._json({"error":"No messages"},400); return
        full = [{"role":"system","content":"You are an expert Chinese tutor named 小明. You help English speakers learn Mandarin. Keep responses concise. Always provide: characters + pinyin + English. Be encouraging and patient."}] + msgs
        payload = json.dumps({"model":MODEL,"messages":full,"temperature":0.7,"max_tokens":800}).encode()
        req = Request(API_URL, data=payload, headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"})
        try:
            with urlopen(req, timeout=30) as r: data = json.loads(r.read())
            self._json({"reply": data["choices"][0]["message"]["content"]})
        except URLError as e: self._json({"error":str(e)},502)
        except Exception as e: self._json({"error":str(e)},502)
    def _json(self, d, s=200):
        self.send_response(s); self.send_header("Content-Type","application/json;charset=utf-8")
        self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
        self.wfile.write(json.dumps(d,ensure_ascii=False).encode())
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    def log_message(self, f, *a):
        m = f % a; tag = "🤖 AI" if "/api/chat" in m else "📄"
        print(f"  {tag} {a[0]} {a[1]} {a[2]}")

if __name__ == "__main__":
    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║     Easy Chinese · Learning Server   ║")
    print(f"  ╠══════════════════════════════════════╣")
    print(f"  ║  Open:  http://localhost:{PORT}            ║")
    print(f"  ║  Stop:  Ctrl+C                      ║")
    print(f"  ╠══════════════════════════════════════╣")
    print(f"  ║  {'✅ DeepSeek AI: Connected' if API_KEY else '⚠️  Set DEEPSEEK_API_KEY for AI'}      ║")
    print(f"  ╚══════════════════════════════════════╝\n")
    try: HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt: print("\n  👋 Server stopped.\n")
