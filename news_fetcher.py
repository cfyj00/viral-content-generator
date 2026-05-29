import json
import re
import os
import requests
import feedparser
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RSS_FEEDS = {
    "구글뉴스_한국": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "구글뉴스_글로벌": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "구글트렌드_한국": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR",
    "구글트렌드_글로벌": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
    "네이버_랭킹뉴스": "https://news.naver.com/main/ranking/popularDay.naver",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_rss_headlines(max_per_feed: int = 15) -> dict:
    """RSS 피드에서 헤드라인 수집"""
    results = {}
    for name, url in RSS_FEEDS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            feed = feedparser.parse(resp.content)
            headlines = [entry.title for entry in feed.entries[:max_per_feed]]
            results[name] = headlines
            print(f"  [{name}] {len(headlines)}개 수집")
        except Exception as e:
            print(f"  [{name}] 수집 실패: {e}")
            results[name] = []
    return results


def analyze_and_select(headlines: dict) -> dict:
    """Claude 웹검색으로 트렌드 분석 + 바이럴 주제 선별"""

    all_lines = []
    for source, items in headlines.items():
        for h in items:
            all_lines.append(f"[{source}] {h}")

    headlines_text = "\n".join(all_lines)

    print("  🤖 Claude 바이럴 분석 중...")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"""다음 뉴스 헤드라인들을 분석해줘.
한국 트위터에서 바이럴 될 콘텐츠 소재로 활용할 거야.

헤드라인 목록:
{headlines_text}

선별 기준:
1. 충격성 / 논쟁성 / 공유욕 유발 가능성
2. 지식(과학,심리,역사)과 결합 가능한 주제
3. 15금 자극 요소 접목 가능성
4. 현재 한국 트위터에서 반응 올 것 같은 것

필요하면 웹검색으로 최신 상황 확인해줘.

반드시 아래 JSON 형식으로만 출력해:
{{
  "롱폼_주제": {{
    "헤드라인": "원문 헤드라인",
    "바이럴_이유": "왜 터질 것 같은지",
    "지식_연결_포인트": "어떤 지식과 연결할지"
  }},
  "메가쓰레드_주제": {{
    "헤드라인": "원문 헤드라인",
    "바이럴_이유": "왜 터질 것 같은지",
    "챕터_아이디어": ["챕터1", "챕터2", "챕터3"]
  }},
  "속보_숏폼_목록": [
    {{"헤드라인": "뉴스 제목", "한줄_각도": "어떤 관점으로 자극할지"}},
    {{"헤드라인": "뉴스 제목", "한줄_각도": "어떤 관점으로 자극할지"}}
  ]
}}

속보_숏폼_목록은 최대한 많이 (15~20개) 뽑아줘. 짧고 자극적인 것 위주로.""",
            }
        ],
    )

    for block in response.content:
        if block.type == "text":
            text = block.text
            try:
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception:
                pass

    # 파싱 실패 시 빈 구조 반환
    return {
        "롱폼_주제": {},
        "메가쓰레드_주제": {},
        "속보_숏폼_목록": [],
    }


def get_trending_news() -> dict:
    """전체 뉴스 수집 파이프라인"""
    print("\n📡 뉴스 수집 중...")
    headlines = fetch_rss_headlines()
    print("🔍 바이럴 분석 중...")
    analysis = analyze_and_select(headlines)
    shorts_count = len(analysis.get("속보_숏폼_목록", []))
    print(f"  ✅ 속보 {shorts_count}개 선별 완료")
    return analysis
