import re
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _build_style_instructions(style_profile: dict) -> str:
    if not style_profile:
        return ""

    parts = ["【문체 지침 — 반드시 준수】"]

    if "모방_지침" in style_profile:
        rules = style_profile["모방_지침"]
        if isinstance(rules, list):
            for r in rules:
                parts.append(f"- {r}")
        else:
            parts.append(f"- {rules}")

    if "말버릇" in style_profile:
        parts.append(f"- 자주 쓰는 표현: {style_profile['말버릇']}")

    if "어미_패턴" in style_profile:
        parts.append(f"- 어미 패턴: {style_profile['어미_패턴']}")

    if "특이점" in style_profile:
        parts.append(f"- 특이점 반영: {style_profile['특이점']}")

    if "유머_스타일" in style_profile:
        parts.append(f"- 유머 스타일: {style_profile['유머_스타일']}")

    return "\n".join(parts)


def generate_longform(
    category: str, topic: str, news_context: str, style_profile: dict
) -> str:
    print("\n📝 롱폼 생성 중", end="", flush=True)

    style_instructions = _build_style_instructions(style_profile)

    system_prompt = f"""너는 한국 트위터에서 바이럴 콘텐츠를 만드는 전문가야.
X(트위터) 프리미엄 유저를 위한 롱폼 포스트를 작성해.

【콘텐츠 원칙】
- 자극적인 훅으로 시작 (첫 2줄에서 스크롤 멈추게 만들기)
- 15금 수위 허용 (성적 암시 O, 노골적 묘사 X)
- 지식 60% + 자극 40% 비율 유지
- AI가 쓴 것처럼 느껴지면 절대 안 됨
- 논문체, 설명체 금지. 친구한테 카톡 보내듯
- 숫자, 통계, 구체적 사실 반드시 포함
- 읽다가 "헉" 하는 반전 포인트 최소 1개
- 마지막에 여운 남기는 한 줄로 마무리

【형식】
- 길이: 3000~5000자 (프리미엄 롱폼 최대 활용)
- 단락 구분 명확히
- 이모지 적절히 (과하지 않게, 강조 포인트에만)

{style_instructions}"""

    user_prompt = f"""카테고리: {category}
주제: {topic}
오늘의 관련 뉴스/트렌드: {news_context}

위 주제로 X(트위터) 롱폼 포스트를 써줘.
최신 사례나 통계가 있으면 웹검색해서 실제 팩트 포함해줘."""

    result = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(".", end="", flush=True)
            result += text

    print(" ✅")
    return result


def generate_mega_thread(
    category: str, topic: str, news_context: str, style_profile: dict
) -> str:
    print("🧵 메가 쓰레드 생성 중", end="", flush=True)

    style_instructions = _build_style_instructions(style_profile)

    system_prompt = f"""너는 한국 트위터 바이럴 쓰레드 전문가야.
X(트위터) 프리미엄 유저를 위한 메가 쓰레드를 작성해.

【쓰레드 구조】
1/n: 🔥 충격적인 훅 (숫자/통계/금기어 포함, 스크롤 멈추게)
2/n: "이게 사실이라고?" 부연 + 더 자극적인 디테일
3~n-2/n: 지식 챕터들 (각각 독립적으로 흥미로워야 함)
n-1/n: 충격 반전 or 실생활 연결
n/n: 여운 + 자연스러운 팔로우 유도

【규칙】
- 트윗 개수: 12~15개
- 각 트윗: 500~1000자 (프리미엄 최대 활용)
- 각 트윗은 단독으로도 흥미로워야 함
- cliffhanger로 다음 트윗까지 읽게 만들기
- 15금 수위 허용
- AI 문체 절대 금지
- 번호 표시: 1/13, 2/13 형식

{style_instructions}"""

    user_prompt = f"""카테고리: {category}
주제: {topic}
오늘의 관련 뉴스/트렌드: {news_context}

위 주제로 메가 쓰레드 써줘.
웹검색으로 최신 팩트 확인해서 실제 사례 포함해줘."""

    result = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=20000,
        thinking={"type": "adaptive"},
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(".", end="", flush=True)
            result += text

    print(" ✅")
    return result


def generate_shorts(breaking_news_list: list, style_profile: dict) -> list:
    """속보 숏폼 일괄 생성 — 뉴스 개수만큼 전부 뽑기"""
    if not breaking_news_list:
        return []

    count = len(breaking_news_list)
    print(f"⚡ 숏폼 속보 {count}개 생성 중", end="", flush=True)

    style_instructions = _build_style_instructions(style_profile)

    news_text = "\n".join(
        [
            f"{i+1}. 헤드라인: {item.get('헤드라인', '')} | 각도: {item.get('한줄_각도', '')}"
            for i, item in enumerate(breaking_news_list)
        ]
    )

    system_prompt = f"""너는 한국 트위터 바이럴 속보 전문가야.
짧고 강렬한 단발성 포스트를 만들어.

【속보 숏폼 규칙】
- 길이: 100~300자
- 첫 줄에서 반드시 멈추게 해야 함
- 충격 / 분노 / 공유욕 / 웃음 중 하나 이상 유발
- 이모지 1~3개 (포인트에만)
- "실화냐" "ㄹㅇ" "이거 봐" 등 자연스러운 한국어
- AI 냄새 절대 금지
- 각 포스트는 완전히 독립적

{style_instructions}"""

    user_prompt = f"""다음 뉴스들 각각에 대해 트위터 속보 숏폼 포스트를 써줘.
뉴스 하나당 포스트 하나씩, 전부 다 써줘.

각 포스트는 반드시 이 형식으로 구분해:
[1] 포스트:
(내용)

[2] 포스트:
(내용)

뉴스 목록:
{news_text}"""

    result = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=10000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(".", end="", flush=True)
            result += text

    print(" ✅")

    # [번호] 포스트: 기준으로 분리
    parts = re.split(r"\[\d+\]\s*포스트:", result)
    shorts = [p.strip() for p in parts if p.strip()]
    return shorts
