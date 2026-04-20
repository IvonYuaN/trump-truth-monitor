#!/usr/bin/env python3
"""
美伊冲突时间线自动更新脚本
从 StardustWhisper/iran-israel-us-timeline 仓库抓取最新事件
转换为前端 WAR_EVENTS 格式，更新 index.html
"""

import json
import re
import requests
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/StardustWhisper/iran-israel-us-timeline/main/index.html"
INDEX_FILE = Path("index.html")


def fetch_source_data():
    """从StardustWhisper仓库获取事件数据"""
    print(f"Fetching from {SOURCE_URL}...")
    resp = requests.get(SOURCE_URL, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Extract the events array from JS
    match = re.search(r'const events = (\[[\s\S]*?\]);', html)
    if not match:
        print("ERROR: Could not find events array in source HTML")
        return []

    try:
        raw = match.group(1)
        # Source is JavaScript object literal, not valid JSON
        # Write to temp file and use node to convert
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(f"const data = {raw};\nconsole.log(JSON.stringify(data));")
            tmp_path = f.name
        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True, text=True, timeout=30
        )
        Path(tmp_path).unlink(missing_ok=True)
        if result.returncode != 0:
            print(f"Node parse error: {result.stderr[:200]}")
            return []
        events = json.loads(result.stdout)
        print(f"Fetched {len(events)} events from source")
        return events
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse events JSON: {e}")
        return []


def convert_event(evt):
    """将源格式转换为我们的WAR_EVENTS格式"""
    # Remove tag prefix from title, e.g. "[Trump] 美以..." -> "美以..."
    title = evt.get("title", "")
    title = re.sub(r'^\[\w+\]\s*', '', title)

    return {
        "date": evt.get("date", ""),
        "title": title,
        "tags": evt.get("tags", []),
    }


def load_existing_events():
    """从index.html中提取现有WAR_EVENTS"""
    content = INDEX_FILE.read_text(encoding="utf-8")

    # Extract WAR_EVENTS array
    match = re.search(r'const WAR_EVENTS = (\[[\s\S]*?\]);', content)
    if not match:
        print("ERROR: Could not find WAR_EVENTS in index.html")
        return []

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        print("ERROR: Failed to parse existing WAR_EVENTS")
        return []


def update_index_html(new_events):
    """更新index.html中的WAR_EVENTS"""
    content = INDEX_FILE.read_text(encoding="utf-8")

    # Build new WAR_EVENTS JS array
    events_js = "const WAR_EVENTS = [\n"
    for i, evt in enumerate(new_events):
        tags_str = ", ".join(f"'{t}'" for t in evt["tags"])
        comma = "," if i < len(new_events) - 1 else ""
        events_js += f"            {{ date: '{evt['date']}', title: '{evt['title']}', tags: [{tags_str}] }}{comma}\n"
    events_js += "        ];"

    # Replace existing WAR_EVENTS
    new_content = re.sub(
        r'const WAR_EVENTS = \[[\s\S]*?\];',
        events_js,
        content
    )

    if new_content == content:
        print("No changes to WAR_EVENTS")
        return False

    INDEX_FILE.write_text(new_content, encoding="utf-8")
    print(f"Updated WAR_EVENTS with {len(new_events)} events")
    return True


def main():
    # Fetch source data
    source_events = fetch_source_data()
    if not source_events:
        return 0

    # Convert to our format
    converted = [convert_event(e) for e in source_events]

    # Load existing events
    existing = load_existing_events()
    existing_count = len(existing)

    # Merge: use source as primary, keep our custom events that source doesn't have
    existing_keys = {e["date"] + "::" + e["title"] for e in existing}
    source_keys = {e["date"] + "::" + e["title"] for e in converted}

    # Events only in our local version (manually added)
    our_only = [e for e in existing if e["date"] + "::" + e["title"] not in source_keys]

    # Merge: source events + our-only events, sorted by date
    merged = converted + our_only
    merged.sort(key=lambda x: x["date"])

    new_count = len(merged)
    diff = new_count - existing_count

    print(f"\nExisting: {existing_count} events")
    print(f"Source: {len(converted)} events")
    print(f"Our-only: {len(our_only)} events")
    print(f"Merged: {new_count} events (diff: +{diff})")

    if diff == 0:
        # Check if content actually changed
        if merged == existing:
            print("No new events, skipping update")
            return 0

    # Update index.html
    updated = update_index_html(merged)

    # Output stats
    with open("output/timeline_stats.txt", "w") as f:
        f.write(f"SOURCE_EVENTS={len(converted)}\n")
        f.write(f"OUR_EVENTS={len(our_only)}\n")
        f.write(f"TOTAL_EVENTS={new_count}\n")
        f.write(f"DIFF={diff}\n")

    return diff if updated else 0


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    result = main()
    print(f"\n✅ Done (new events: {result})")
