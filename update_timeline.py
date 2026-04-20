#!/usr/bin/env python3
"""
美伊冲突时间线自动更新脚本
使用 Google Gemini AI + Google Search Grounding 获取最新事件
"""

import json
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path

GEMINI_API_KEY = "YOUR_API_KEY"  # Will be replaced by env var in CI
GEMINI_MODEL = "gemini-2.0-flash"
TIMELINE_FILE = Path("data/war_timeline.json")
INDEX_FILE = Path("index.html")

PROMPT = """请搜索最近3天美国-伊朗-以色列冲突的最新重要事件。
我们已有的最新事件日期是 {latest_date}。

请返回一个JSON数组，只包含 {latest_date} 之后的新事件。
如果没有新事件，返回空数组 []。
每个事件格式：{{"date": "YYYY-MM-DD", "title": "事件描述", "tags": ["Trump"]}}
可选标签：Trump, Iran, Israel, US, Mediator, China, Economy, UN
只输出JSON，不要输出其他任何文字。"""


def get_latest_event_date():
    """从index.html中提取最新事件日期"""
    if not INDEX_FILE.exists():
        return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    content = INDEX_FILE.read_text(encoding="utf-8")
    # Find all dates in WAR_EVENTS
    dates = re.findall(r"\{ date: '(\d{4}-\d{2}-\d{2})'", content)
    if dates:
        return max(dates)
    return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")


def call_gemini(latest_date):
    """调用Gemini API获取最新事件"""
    api_key = GEMINI_API_KEY
    # Check env var
    import os
    api_key = os.environ.get("GEMINI_API_KEY", api_key)
    
    if api_key == "YOUR_API_KEY":
        print("ERROR: GEMINI_API_KEY not set")
        return []
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": PROMPT.format(latest_date=latest_date)
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048,
        },
        "tools": [{
            "google_search": {}
        }]
    }
    
    print(f"Calling Gemini API (latest event: {latest_date})...")
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    
    data = resp.json()
    
    # Extract text from response
    text = ""
    if "candidates" in data and data["candidates"]:
        parts = data["candidates"][0].get("content", {}).get("parts", [])
        for part in parts:
            text += part.get("text", "")
    
    if not text:
        print("No response from Gemini")
        return []
    
    print(f"Gemini response length: {len(text)} chars")
    
    # Extract JSON from response
    # Gemini with google_search may return duplicated content
    # Find the first complete JSON array
    text_clean = text.strip()
    # Remove markdown code block markers if present
    text_clean = re.sub(r'^```\w*\s*', '', text_clean)
    text_clean = re.sub(r'\s*```$', '', text_clean)
    
    # Try to find a valid JSON array
    # Use non-greedy match to find first complete array
    events = []
    for match in re.finditer(r'\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]', text_clean, re.DOTALL):
        try:
            raw = match.group()
            raw = re.sub(r'[\x00-\x1f\x7f]', ' ', raw)
            parsed = json.loads(raw)
            if isinstance(parsed, list) and len(parsed) > 0:
                events = parsed
                break  # Use first valid array
        except json.JSONDecodeError:
            continue
    
    if not events:
        print("No valid JSON array found in response")
        return []

    # Validate structure
    valid_events = []
    for evt in events:
        if "date" in evt and "title" in evt:
            evt.setdefault("tags", [])
            valid_events.append(evt)
    return valid_events


def load_existing_timeline():
    """加载已有时间线数据"""
    if TIMELINE_FILE.exists():
        with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_timeline(events):
    """保存时间线数据"""
    TIMELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(events)} events to {TIMELINE_FILE}")


def main():
    latest_date = get_latest_event_date()
    print(f"Latest existing event: {latest_date}")
    
    # Get new events from Gemini
    new_events = call_gemini(latest_date)
    
    if not new_events:
        print("No new events found")
        return 0
    
    # Load existing events
    existing = load_existing_timeline()
    existing_dates = {e["date"] + e["title"] for e in existing}
    
    # Filter out duplicates
    truly_new = []
    for evt in new_events:
        key = evt["date"] + evt["title"]
        if key not in existing_dates:
            truly_new.append(evt)
            existing.append(evt)
    
    if not truly_new:
        print("All events already exist, no update needed")
        return 0
    
    # Sort by date
    existing.sort(key=lambda x: x["date"])
    
    # Save
    save_timeline(existing)
    
    # Output for GitHub Actions
    with open("output/timeline_stats.txt", "w") as f:
        f.write(f"NEW_EVENTS={len(truly_new)}\n")
        f.write(f"TOTAL_EVENTS={len(existing)}\n")
        for evt in truly_new:
            f.write(f"EVENT: {evt['date']} - {evt['title']}\n")
    
    print(f"\n✅ Added {len(truly_new)} new events:")
    for evt in truly_new:
        print(f"  {evt['date']}: {evt['title']}")
    
    return len(truly_new)


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    main()
