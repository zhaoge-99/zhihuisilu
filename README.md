# 智慧丝路 — AI 辅助汉语学习平台

面向"一带一路"留学生的 AI 辅助汉语学习平台。

## 功能

- 📚 **HSK 词汇** 1-6 级完整词库
- 🔊 **拼音课程** 声母、韵母、四声
- 🖌️ **汉字学习** 笔顺演示、偏旁部首
- 🃏 **闪卡系统** 智能复习
- ✍️ **练习测验** 词汇、声调
- 📖 **学习资源** 语法指南、文化内容
- 🤖 **AI 对话助手** — 实时流式对话（DeepSeek API）
- 🎯 **个性化推荐** — 根据学习水平推荐内容

## 技术栈

- 前端：纯 HTML/CSS/JS（单页应用，支持中英文切换）
- 后端：Python（标准库，无外部依赖）
- AI：DeepSeek-V3 via SiliconFlow API
- 部署：Railway

## 快速启动

```bash
# 1. 设置 API Key
export SILICONFLOW_API_KEY=sk-xxx

# 2. 启动服务
python server.py

# 3. 打开浏览器
open http://localhost:8833
```

## 数据来源

本平台基于 200 份汉语学习者问卷调查结果设计。
调查覆盖 25+ 个国家，通过 K-Means 聚类识别出 4 类典型用户画像。

## 部署到 Railway

1. 上传代码到 GitHub 仓库
2. 登录 [Railway](https://railway.app)，创建新项目 → Deploy from GitHub repo
3. 在 Railway Dashboard → Variables 添加：
   - `SILICONFLOW_API_KEY` = 你的 API Key
4. 自动部署完成，Railway 会分配 `.railway.app` 域名
