"""
주제 선택 + 로그 업데이트 — API 호출 없음, 표준 라이브러리만 사용
Claude Code 예약 작업에서 호출됨
"""
import json
import random
import os
import sys
from datetime import date

from categories import CATEGORIES

LOG_FILE = "log.json"


def load_log():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def pick_topic():
    log = load_log()
    today = date.today().isoformat()

    all_topics = []
    for category, topics in CATEGORIES.items():
        for topic in topics:
            all_topics.append((category, topic))

    # 당일 사용된 주제 제외
    filtered = [
        (cat, topic) for cat, topic in all_topics
        if log.get(topic, {}).get("last_used") != today
    ]
    if not filtered:
        filtered = all_topics

    # 가중치: 적게 쓸수록 높은 확률
    weights = [1.0 / (log.get(topic, {}).get("count", 0) + 1) for _, topic in filtered]
    chosen_cat, chosen_topic = random.choices(filtered, weights=weights, k=1)[0]

    # 로그 업데이트
    if chosen_topic not in log:
        log[chosen_topic] = {"count": 0, "last_used": None, "category": chosen_cat}
    log[chosen_topic]["count"] += 1
    log[chosen_topic]["last_used"] = today
    save_log(log)

    # 문체 프로필 로드
    style = {}
    if os.path.exists("style_profile.json"):
        with open("style_profile.json", "r", encoding="utf-8") as f:
            style = json.load(f)

    result = {
        "category": chosen_cat,
        "topic": chosen_topic,
        "style_profile": style,
        "today": today,
    }
    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    pick_topic()
