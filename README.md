# 特朗普 Truth Social 监控面板

实时追踪特朗普 Truth Social 发帖动态的 GitHub Pages 可视化面板。

## 在线访问

**[ivonyuan.github.io/trump-truth-monitor](https://ivonyuan.github.io/trump-truth-monitor/)**

## 功能特性

- **近3天动态** — 默认展示最近3天帖子（EST时区划分），帖子时间双时区显示
- **历史归档** — 按月/日折叠归档，点击展开查看
- **全文搜索** — 支持中英文关键词搜索全部帖子
- **中英翻译** — 点击帖子自动翻译（MyMemory API），带缓存
- **数据统计** — 每日发帖量柱状图、发帖时段分布、总览数据卡片
- **热力图** — GitHub 风格的90天发帖活跃度
- **词云** — 高频词可视化，点击可搜索
- **Trump Bingo** — 5x5 棋盘，阅读帖子自动标记，localStorage 持久化
- **关键词排行** — 20个预设正则匹配，柱状图排名
- **战争时间线** — 美以伊冲突追踪，7阶段进度条 + 46个关键事件
- **Trump 状态** — EST实时时钟 + 猜测当前活动 + AI头像
- **日夜主题** — 自动检测系统偏好，手动切换，localStorage 记忆

## 数据来源

| 来源 | 地址 | 说明 |
|------|------|------|
| CNN Truth Social Archive | `ix.cnn.io/data/truth-social/truth_archive.json` | 主数据源，32,000+ 条全量历史帖文 |
| trumpstruth.org | `trumpstruth.org/feed` | RSS 备用源，发帖时段统计数据 |
| StardustWhisper/iran-israel-us-timeline | GitHub | 战争时间线数据（347条事件） |

- 账号：`@realDonaldTrump`
- 数据范围：2026年2月至今
- 更新方式：手动抓取 CNN JSON → 保存 `data/posts.json` → 推送 GitHub Pages

## 技术栈

- 纯静态单文件 HTML/CSS/JS（无框架依赖）
- GitHub Pages 托管（Legacy 模式 + `.nojekyll`）
- awesome-design-md 设计标准
- DM Serif Display + Inter 字体
- CSS 变量主题系统（亮/暗双模式）

## 项目结构

```
trump-truth-monitor/
├── index.html              # 主页面（单文件应用）
├── data/
│   └── posts.json          # 帖子数据（2026-02 至今）
├── assets/
│   ├── trump-golf.jpg      # Trump 头像（高尔夫）
│   ├── trump-phone.jpg     # Trump 头像（刷手机）
│   ├── trump-speech.jpg    # Trump 头像（演讲）
│   ├── trump-tv.jpg        # Trump 头像（看电视）
│   ├── trump-eating.jpg    # Trump 头像（吃饭）
│   ├── trump-sleeping.jpg  # Trump 头像（睡觉）
│   └── trump-working.jpg   # Trump 头像（工作）
├── .nojekyll               # 跳过 Jekyll 构建
├── .gitignore
├── main.py                 # 数据抓取脚本
├── send_email.py           # 邮件通知（备用）
├── requirements.txt
└── README.md
```

## 更新数据

```bash
# 1. 抓取最新数据
python3 -c "
import requests, json
resp = requests.get('https://ix.cnn.io/data/truth-social/truth_archive.json')
archive = resp.json()
filtered = [p for p in archive if p['created_at'] >= '2026-02']
with open('data/posts.json', 'w') as f:
    json.dump(filtered, f, ensure_ascii=False)
print(f'Updated: {len(filtered)} posts')
"

# 2. 推送到 GitHub
git add data/posts.json
git commit -m "data: update posts.json"
git push origin main
```

## 时间说明

- **日期划分**：以华盛顿时间 (EST/EDT) 为准
- **帖子时间**：显示格式为 `EST时间 (本地时间)`，相同时区只显示一个
- **Trump 状态**：基于 EST 时区猜测当前活动

## 相关项目

- [StardustWhisper/iran-israel-us-timeline](https://github.com/StardustWhisper/iran-israel-us-timeline) — 战争时间线数据源
- [LewisLiu007/iran-war-info](https://github.com/LewisLiu007/iran-war-info) — 多源新闻聚合
- [Hzyhhh/iron-fetch-news](https://github.com/Hzyhhh/iron-fetch-news) — Next.js 战事追踪
- [zgywayy/iran-conflict](https://github.com/zgywayy/iran-conflict) — 冲突可视化
- [1837620622/connectX](https://github.com/1837620622/connectX) — Truth Social 监控 + 微信推送

## License

MIT
