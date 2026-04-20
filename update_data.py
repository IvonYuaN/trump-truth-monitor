#!/usr/bin/env python3
"""
Trump Truth Social 数据更新脚本
- 从CNN获取最新数据
- 筛选2026年2月至今的帖子
- 保存为 data/posts.json（供前端页面使用）
"""

import json
import requests
from pathlib import Path

DATA_URL = "https://ix.cnn.io/data/truth-social/truth_archive.json"
POSTS_FILE = Path("data/posts.json")

def main():
    print("Fetching CNN Truth Social archive...")
    resp = requests.get(DATA_URL, timeout=60)
    resp.raise_for_status()
    archive = resp.json()
    print(f"Total in CNN archive: {len(archive)}")

    # Filter 2026-02 onwards
    filtered = [p for p in archive if p.get("created_at", "") >= "2026-02"]
    filtered.sort(key=lambda x: x["created_at"], reverse=True)
    print(f"Filtered (2026-02+): {len(filtered)}")

    # Check if there are new posts
    new_count = 0
    if POSTS_FILE.exists():
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_ids = {p["id"] for p in existing}
        new_posts = [p for p in filtered if p["id"] not in existing_ids]
        new_count = len(new_posts)
        print(f"New posts: {new_count}")
    else:
        new_count = len(filtered)

    # Save
    POSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False)
    print(f"Saved to {POSTS_FILE}")

    # Output stats for GitHub Actions
    with open("output/stats.txt", "w") as f:
        f.write(f"TOTAL={len(filtered)}\n")
        f.write(f"NEW={new_count}\n")

    return new_count

if __name__ == "__main__":
    main()
