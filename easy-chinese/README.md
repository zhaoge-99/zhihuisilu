# Easy Chinese · 汉语学堂

A modern, open-source Chinese learning web application for English speakers. Features a complete HSK 1–6 vocabulary system, interactive flashcards, quizzes, stroke order demos, pinyin training, and an AI tutor powered by DeepSeek.

## Features

| Feature | Description |
|---|---|
| **📚 HSK Vocabulary** | Full HSK 1–6 word lists (1,500+ words) with pinyin and English meanings |
| **📂 Themed Vocab** | 8 categories — Food, Travel, Shopping, Daily Life, Body & Health, Nature, Colors, Time |
| **🃏 Flashcards** | Smart flip cards with HSK 1–5 vocabulary |
| **✍️ Quizzes** | Multiple-choice vocabulary and tone identification quizzes |
| **🔊 Pinyin Course** | Complete pinyin table (initials + finals) + 4 tones explanation |
| **🖌️ Character Course** | Stroke order demo for 16 common characters, radicals chart, memory tips |
| **✅ Daily Check-in** | Track your learning streak with weekly calendar view |
| **🤖 AI Tutor** | Built-in AI assistant (Xiao Ming) powered by DeepSeek API |
| **⭐ Saved Words** | Bookmark words across all HSK levels for targeted review |
| **📖 Resources** | Grammar guides, survival phrases, idioms & culture notes |
| **📊 Progress Tracking** | All progress saved in browser (localStorage), no account needed |

## Quick Start

### Option 1: Open directly (no AI)

Just open `index.html` in any modern browser. All features work except the AI tutor.

### Option 2: With AI assistant (recommended)

```bash
# 1. Set your DeepSeek API key
export DEEPSEEK_API_KEY='your-api-key-here'

# 2. Start the server
python3 server.py

# 3. Open in browser
open http://localhost:8000
```

The AI tutor (小明) can help with:
- Explaining Chinese grammar 🇨🇳
- Translating phrases
- Teaching pronunciation and tones
- Answering HSK-related questions
- Cultural notes and tips

### Option 3: Using Doubao / other Chinese provider

Edit `server.py` and change the `API_URL` and `MODEL` variables:

```python
# For Doubao (ByteDance)
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL = "doubao-1.5-pro"

# For other OpenAI-compatible providers
API_URL = "https://your-provider.com/v1/chat/completions"
```

## Project Structure

```
easy-chinese/
├── index.html          # Main HTML (SPA shell)
├── css/
│   └── style.css       # Full stylesheet (responsive, dark/light)
├── js/
│   ├── data.js         # Vocabulary data (HSK 1-6 + Themed)
│   ├── app.js          # Application logic (navigation, quiz, flashcards, etc.)
│   └── chat.js         # AI chat assistant (DeepSeek API + built-in fallback)
├── server.py           # Python backend (static serving + AI proxy)
├── requirements.txt    # Python dependencies (none required — uses stdlib)
└── README.md           # This file
```

## Technical Details

- **Frontend**: Pure vanilla HTML/CSS/JS — no frameworks, no build tools
- **Backend**: Python 3 stdlib (`http.server`) — no pip install needed
- **AI API**: OpenAI-compatible (DeepSeek, Doubao, etc.)
- **Data persistence**: Browser localStorage
- **Vocabulary**: 2,000+ words across HSK 1–6 + 8 themed categories
- **Responsive**: Works on desktop and mobile

## Deploy to GitHub Pages

1. Push this repo to GitHub
2. Go to Settings → Pages → Deploy from branch `main`, folder `/`
3. Done! The frontend works fully on GitHub Pages
4. For AI features, deploy the Python backend separately (Render, Railway, or your own server)

## License

MIT — free to use, modify, and share.
