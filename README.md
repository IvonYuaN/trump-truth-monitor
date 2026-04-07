# 特朗普 Truth Social 每日监控

自动获取特朗普 Truth Social 帖子，生成中英对照 Excel 报告，每天早上 10 点发送邮件通知。

## 功能特点

- ✅ **自动获取**：每天早上 10 点（北京时间）自动获取最新帖子
- ✅ **中英对照**：重要帖子已翻译，普通帖子使用词典翻译
- ✅ **邮件通知**：自动发送 Excel 到您的邮箱
- ✅ **历史保留**：所有历史数据永久保存，不自动删除
- ✅ **免费运行**：基于 GitHub Actions，完全免费

## 数据来源

- CNN Truth Social Archive: `https://ix.cnn.io/data/truth-social/truth_archive.json`
- 账号：@realDonaldTrump
- 更新频率：实时

## 快速开始

### 1. Fork 本仓库

点击右上角 `Fork` 按钮，将仓库复制到您的账号下。

### 2. 配置 Secrets

进入您的仓库 → Settings → Secrets and variables → Actions → New repository secret

添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `587` |
| `SMTP_USER` | 发件人邮箱 | `your_email@gmail.com` |
| `SMTP_PASSWORD` | 邮箱授权码（非密码） | Gmail 需要应用专用密码 |
| `TO_EMAIL` | 收件人邮箱 | `your_email@example.com` |

### 3. 常用邮箱 SMTP 配置

#### Gmail
```
SMTP_SERVER: smtp.gmail.com
SMTP_PORT: 587
```
⚠️ 需要开启两步验证后生成[应用专用密码](https://myaccount.google.com/apppasswords)

#### QQ 邮箱
```
SMTP_SERVER: smtp.qq.com
SMTP_PORT: 587
```
⚠️ 需要在邮箱设置中开启 SMTP 服务并获取授权码

#### 163 邮箱
```
SMTP_SERVER: smtp.163.com
SMTP_PORT: 465
```

### 4. 手动测试

进入 Actions → Trump Truth Social Daily Report → Run workflow → Run workflow

### 5. 查看结果

- **邮件**：检查收件箱
- **Artifacts**：Actions 运行页面 → Artifacts → truth-social-report
- **存档**：仓库 `data/truth_archive.json`

## 项目结构

```
trump-truth-monitor/
├── .github/
│   └── workflows/
│       └── daily.yml      # GitHub Actions 工作流
├── data/
│   └── truth_archive.json # 历史存档（自动更新）
├── output/
│   └── *.xlsx             # 生成的 Excel 文件
├── fetch_data.py          # 获取数据脚本
├── process_data.py        # 处理数据脚本
├── send_email.py          # 发送邮件脚本
├── requirements.txt       # Python 依赖
└── README.md              # 本文件
```

## 翻译说明

### 重要帖子（高质量翻译）
- 伊朗相关（霍尔木兹海峡、核谈判、军事威胁）
- 关税政策
- 北约、格陵兰岛
- UFO/外星生命
- 重大军事行动

### 普通帖子（词典翻译）
- 政治背书（选举支持类）
- 日常动态
- 媒体引用

## 自定义配置

### 修改运行时间

编辑 `.github/workflows/daily.yml`：

```yaml
schedule:
  - cron: '0 2 * * *'  # UTC 时间，北京时间 = UTC + 8
```

常用时间：
- 北京时间 8:00 → `cron: '0 0 * * *'`
- 北京时间 10:00 → `cron: '0 2 * * *'`
- 北京时间 18:00 → `cron: '0 10 * * *'`

### 修改数据保留

默认保留所有历史数据。如需自动清理，编辑 `process_data.py`：

```python
posts = load_posts(days=30)  # 改为需要的天数
```

## 故障排除

### 邮件发送失败
1. 检查 SMTP 配置是否正确
2. 确认使用的是授权码而非密码
3. 检查邮箱是否开启 SMTP 服务

### 数据获取失败
1. CNN 数据源可能临时不可用，等待下次运行
2. 检查 Actions 日志查看具体错误

### Excel 未生成
1. 确认 `data/truth_archive.json` 有数据
2. 检查 `output/` 目录权限

## 相关资源

- [CNN Truth Social Archive](https://ix.cnn.io/data/truth-social/)
- [stiles/trump-truth-social-archive](https://github.com/stiles/trump-truth-social-archive)
- [shawnholdings-creator/ntfy-alerts](https://github.com/shawnholdings-creator/ntfy-alerts)

## License

MIT
