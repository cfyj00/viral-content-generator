import json
import os
import random
from datetime import datetime, date
from pathlib import Path

LOG_FILE = "log.json"
RESULT_DIR = "result"


def load_log() -> dict:
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(log: dict):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def update_log(topic: str, category: str):
    log = load_log()
    today = date.today().isoformat()
    if topic not in log:
        log[topic] = {"count": 0, "last_used": None, "category": category}
    log[topic]["count"] += 1
    log[topic]["last_used"] = today
    save_log(log)


def pick_topic(categories: dict) -> tuple:
    """가중치 역비례 선택 + 당일 중복 방지"""
    log = load_log()
    today = date.today().isoformat()

    all_topics = []
    for category, topics in categories.items():
        for topic in topics:
            all_topics.append((category, topic))

    # 당일 사용된 주제 제외
    filtered = [
        (cat, topic) for cat, topic in all_topics
        if log.get(topic, {}).get("last_used") != today
    ]

    if not filtered:
        filtered = all_topics  # 모두 썼으면 전체에서 선택

    # 가중치: 적게 쓸수록 높은 확률
    weights = [
        1.0 / (log.get(topic, {}).get("count", 0) + 1)
        for _, topic in filtered
    ]

    chosen = random.choices(filtered, weights=weights, k=1)[0]
    return chosen  # (category, topic)


def save_content(
    category: str,
    topic: str,
    content_long: str,
    content_thread: str,
    shorts: list,
    timestamp_str: str,
):
    today = date.today().isoformat()
    folder = Path(RESULT_DIR) / today
    folder.mkdir(parents=True, exist_ok=True)

    slug = topic.replace(" ", "_")[:20]
    base = folder / f"{timestamp_str}_{slug}"

    # 롱폼
    with open(f"{base}_롱폼.txt", "w", encoding="utf-8") as f:
        f.write(f"카테고리: {category}\n주제: {topic}\n생성: {datetime.now()}\n\n")
        f.write("=" * 50 + " [롱폼] " + "=" * 50 + "\n\n")
        f.write(content_long)

    # 메가 쓰레드
    with open(f"{base}_쓰레드.txt", "w", encoding="utf-8") as f:
        f.write(f"카테고리: {category}\n주제: {topic}\n생성: {datetime.now()}\n\n")
        f.write("=" * 50 + " [메가 쓰레드] " + "=" * 50 + "\n\n")
        f.write(content_thread)

    # 숏폼 속보
    if shorts:
        with open(f"{base}_속보숏폼.txt", "w", encoding="utf-8") as f:
            f.write(f"생성: {datetime.now()}\n속보 {len(shorts)}개\n\n")
            f.write("=" * 60 + "\n\n")
            for i, short in enumerate(shorts, 1):
                f.write(f"[{i}]\n{short}\n\n{'─' * 40}\n\n")

    print(f"\n✅ 저장 완료: {folder}/")
    print(f"   ├── {timestamp_str}_{slug}_롱폼.txt")
    print(f"   ├── {timestamp_str}_{slug}_쓰레드.txt")
    if shorts:
        print(f"   └── {timestamp_str}_{slug}_속보숏폼.txt ({len(shorts)}개)")
