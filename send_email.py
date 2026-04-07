#!/usr/bin/env python3
"""
发送邮件通知
支持多种邮件服务：Gmail、QQ邮箱、163邮箱等
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path

def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
    smtp_user: str = None,
    smtp_password: str = None,
):
    """
    发送邮件
    
    参数:
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
        attachment_path: 附件路径
        smtp_server: SMTP服务器地址
        smtp_port: SMTP端口
        smtp_user: SMTP用户名
        smtp_password: SMTP密码/授权码
    """
    
    # 从环境变量获取配置
    smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        raise ValueError("请设置 SMTP_USER 和 SMTP_PASSWORD 环境变量")
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 添加正文
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加附件
    if attachment_path and Path(attachment_path).exists():
        with open(attachment_path, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=Path(attachment_path).name
            )
        msg.attach(attachment)
    
    # 发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"邮件发送成功: {to_email}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def create_email_body(stats: dict) -> str:
    """创建邮件正文"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    body = f"""
特朗普 Truth Social 每日整理报告
{'=' * 40}

📅 日期: {today}
📊 数据统计:
   - 历史总帖子数: {stats.get('TOTAL_POSTS', 0)} 条
   - 最近30天帖子: {stats.get('RECENT_POSTS', 0)} 条
   - 今日新帖: {stats.get('TODAY_POSTS', 0)} 条
   - 本次新增: {stats.get('NEW_POSTS', 0)} 条

📎 附件说明:
   Excel 文件包含以下内容:
   - 全部帖子（中英对照）
   - 发布时间、互动数据（回复/转发/点赞）
   - 帖子链接（可点击跳转 Truth Social）

🔗 数据来源:
   - CNN Truth Social Archive
   - https://ix.cnn.io/data/truth-social/

{'=' * 40}
此邮件由 GitHub Actions 自动发送
"""
    return body.strip()

def load_stats():
    """从 main.py 输出的 stats.txt 读取统计信息"""
    stats_file = Path("output") / "stats.txt"
    stats = {}
    if stats_file.exists():
        for line in stats_file.read_text().strip().splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                stats[key] = int(val)
    return stats

def main():
    """主函数"""
    to_email = os.getenv("TO_EMAIL")
    if not to_email:
        print("请设置 TO_EMAIL 环境变量")
        return False
    
    # 获取附件路径
    output_dir = Path("output")
    excel_files = list(output_dir.glob("*.xlsx"))
    if not excel_files:
        print("没有找到 Excel 文件")
        return False
    
    attachment = str(excel_files[-1])
    
    # 从 stats.txt 读取统计信息
    stats = load_stats()
    
    # 发送邮件
    today = datetime.now().strftime("%Y年%m月%d日")
    subject = f"特朗普 Truth Social 每日整理 - {today}"
    body = create_email_body(stats)
    
    return send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment_path=attachment,
    )

if __name__ == "__main__":
    main()
