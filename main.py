import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from categories import CATEGORIES
from storage import pick_topic, update_log, save_content
from news_fetcher import get_trending_news
from style_learner import run_setup, load_style_profile
from generator import generate_longform, generate_mega_thread, generate_shorts


def run_generation():
    timestamp_str = datetime.now().strftime("%H%M")

    print(f"\n{'=' * 60}")
    print(f"🔥 바이럴 콘텐츠 생성 시작  ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"{'=' * 60}")

    # 1. 문체 프로필 로드
    style_profile = load_style_profile()
    if not style_profile:
        print("⚠️  문체 프로필 없음 — 기본 스타일로 생성합니다.")
        print("    (더 정확한 문체 학습: python main.py --setup)\n")

    # 2. 뉴스 수집 + 바이럴 분석
    news_analysis = get_trending_news()

    # 3. 롱폼/쓰레드 주제 선택 (카테고리 풀 + 뉴스 컨텍스트 블렌딩)
    category, topic = pick_topic(CATEGORIES)
    print(f"\n📌 선택 주제: [{category}] {topic}")

    longform_news = news_analysis.get("롱폼_주제", {})
    news_context = (
        longform_news.get("헤드라인", "")
        + " — "
        + longform_news.get("바이럴_이유", "")
        + " / "
        + longform_news.get("지식_연결_포인트", "")
    )

    # 4. 롱폼 생성
    content_long = generate_longform(category, topic, news_context, style_profile)

    # 5. 메가 쓰레드 생성
    content_thread = generate_mega_thread(category, topic, news_context, style_profile)

    # 6. 속보 숏폼 전부 생성
    breaking_list = news_analysis.get("속보_숏폼_목록", [])
    shorts = generate_shorts(breaking_list, style_profile)

    # 7. 저장 + 로그 업데이트
    save_content(category, topic, content_long, content_thread, shorts, timestamp_str)
    update_log(topic, category)

    print(f"\n🎉 완료! result/{datetime.now().strftime('%Y-%m-%d')}/ 폴더 확인하세요\n")


if __name__ == "__main__":
    if "--setup" in sys.argv:
        run_setup()
    else:
        if not os.path.exists("style_profile.json"):
            print("\n⚠️  문체 학습이 아직 안 됐습니다.")
            print("   python main.py --setup  으로 먼저 실행하세요.\n")
            sys.exit(1)
        run_generation()
