import json
import re
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

STYLE_FILE = "style_profile.json"


def collect_essay() -> str:
    print("\n" + "=" * 60)
    print("✍️  문체 학습 — 에세이를 자유롭게 써주세요")
    print("=" * 60)
    print("주제 상관없이 평소 말투 그대로, 최소 200자 이상.")
    print("트위터에 쓰는 말투면 더 좋음.")
    print("다 쓰면 빈 줄에서 Enter 두 번 입력하세요.")
    print("-" * 60 + "\n")

    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break

    return "\n".join(lines).strip()


def analyze_style(essay: str) -> dict:
    print("\n🔍 문체 분석 중...")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3000,
        thinking={"type": "adaptive"},
        messages=[
            {
                "role": "user",
                "content": f"""다음 에세이를 분석해서 이 사람의 글쓰기 스타일을 정확히 파악해줘.
트위터 포스팅 생성에 쓸 거야. AI 냄새 없애는 게 목표.

에세이:
---
{essay}
---

아래 JSON 형식으로 출력해:
{{
  "문장_길이": "짧게 끊음 / 보통 / 길게 이어씀 — 특징 설명",
  "어미_패턴": ["자주 쓰는 어미 예시들"],
  "말버릇": ["자주 쓰는 표현, 감탄사, 강조어 목록"],
  "유머_스타일": "블랙유머 / 자조적 / 관찰형 / 과장형 등",
  "감정_표현": "감정 드러내는 방식 설명",
  "리듬감": "문장 리듬과 템포 특징",
  "특이점": "이 사람만의 독특한 글쓰기 특징",
  "모방_지침": [
    "이 스타일 따라 쓸 때 반드시 지킬 규칙 1",
    "규칙 2",
    "규칙 3",
    "규칙 4",
    "규칙 5"
  ]
}}""",
            }
        ],
    )

    for block in response.content:
        if block.type == "text":
            try:
                json_match = re.search(r"\{.*\}", block.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception:
                pass

    return {}


def save_style_profile(profile: dict):
    with open(STYLE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"✅ 문체 프로필 저장 완료: {STYLE_FILE}")


def load_style_profile() -> dict:
    if not os.path.exists(STYLE_FILE):
        return {}
    with open(STYLE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_setup():
    essay = collect_essay()
    if len(essay.strip()) < 50:
        print("❌ 너무 짧습니다. 다시 실행해주세요.")
        return

    profile = analyze_style(essay)
    if profile:
        save_style_profile(profile)
        print("\n📋 분석된 문체 특징:")
        for key, value in profile.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 분석 실패. 다시 시도해주세요.")
