"""
Tivismac — 주주행동주의 데일리 브리핑 자동화
GitHub Actions에서 매일 21:00 KST (12:00 UTC)에 실행됨.
1) Claude API (web search tool)로 당일 뉴스 수집 + 브리핑 생성
2) tweepy v2로 X에 단일 포스트로 게시 (X Premium 긴 글 지원)
"""

import os
import datetime
import textwrap
import anthropic
import tweepy

# ── 환경변수 ──────────────────────────────────────────────
X_API_KEY = os.environ["X_API_KEY"]
X_API_SECRET = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]

# ── 날짜 (KST) ───────────────────────────────────────────
KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST)
date_str = today.strftime("%Y년 %-m월 %-d일")
weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]
date_header = f"{date_str} ({weekday_kr})"


# ── 1. Claude API로 브리핑 생성 ───────────────────────────
def generate_briefing() -> str:
    """Claude API + web_search tool로 당일 행동주의 뉴스를 검색하고 브리핑을 생성한다."""

    system_prompt = textwrap.dedent(f"""\
        너는 한국 주주행동주의 전문 리서처다.
        오늘 날짜는 {date_header}이다.

        아래 지침에 따라 오늘의 데일리 브리핑을 작성하라.

        ■ 완성 예시 (이 포맷을 정확히 따를 것):

        📋 주주행동주의 데일리 — 2026년 3월 27일 (금)
        ━━━━━━━━━━━━━━━━━━━━
        🔴 신규 충돌
        ━━━━━━━━━━━━━━━━━━━━
        오늘은 신규 충돌 없음.
        ━━━━━━━━━━━━━━━━━━━━
        🔵 업데이트
        ━━━━━━━━━━━━━━━━━━━━
        ⚔️ 고려아연 (#010130) — 주총 후속: 법적 공방 준비 중
        이번 주 후반 주요 동향 요약:
        📌 증거보전 신청 임박 — 영풍·MBK가 이르면 이달 안으로 서울중앙지법에 주총 투표용지·위임장 등 증거보전을 신청할 예정. 출석 주주 수가 당일 세 차례 이상 바뀌어 공지된 점, 해외 기관 의결권 '프로라타' 재배분 방식이 핵심 쟁점.
        📌 분쟁 장기화 구조 확정 — 이번 주총으로 분쟁이 종결되기는커녕 ▲9월 상법 시행 전 임시주총 ▲증거보전 및 결의 효력 다툼 ▲기존 10개 이상 진행 중 소송 등 복수의 전선이 동시에 가동 중.
        → https://www.sedaily.com/article/20024025
        → https://www.ezyeconomy.com/news/articleView.html?idxno=233848
        ━━━━━━━━━━━━━━━━━━━━
        🟢 행동주의 후보
        ━━━━━━━━━━━━━━━━━━━━
        오늘은 신규 후보 없음.
        ━━━━━━━━━━━━━━━━━━━━
        📅 다음 주요 모니터링 포인트
        - 영풍·MBK 증거보전 신청 여부 (이달 내)
        - 고려아연 9월 임시주총 일정 공표 여부
        - 얼라인파트너스 등 행동주의 펀드 2분기 캠페인 동향
        #주주행동주의 #고려아연 #010130 #MBK파트너스 #경영권분쟁 #밸류업 #기업지배구조 #한국주식 #재테크

        ■ 포맷 규칙 (매우 중요):
        - 이모지(📌, ⚔️, 📋 등)와 텍스트는 반드시 같은 줄에 붙여 쓴다. 이모지만 단독으로 한 줄을 차지하면 안 된다.
        - 📌 뒤에 바로 핵심 내용을 이어서 쓴다. 줄바꿈 하지 않는다.
        - 불필요한 빈 줄을 넣지 않는다. 단, 해시태그 줄 바로 앞에는 빈 줄 하나를 넣는다.
        - 구분선(━━━)은 정확히 20개를 사용한다.

        ■ 작성 규칙:
        1. 반드시 web_search를 사용해서 오늘 날짜 기준 한국 행동주의/경영권분쟁 뉴스를 검색하라.
           검색어 예시: "주주행동주의 2026", "경영권 분쟁", "행동주의 펀드",
           "주주제안", "5% 지분 공시", "얼라인파트너스", "KCGI",
           "트러스톤", "고려아연", "밸류업" 등을 조합해서 여러 번 검색.
        2. 검색 결과에서 오늘 또는 최근 1-2일 이내 기사만 사용하라.
        3. 각 뉴스 항목에 반드시 출처 기사 URL을 포함하라 (→ URL 형태).
        4. 뉴스가 전혀 없으면 각 섹션에 "없음"으로 표기하되, 모니터링 포인트는 기존 이슈 기반으로 작성.
        5. 해시태그는 마지막에 관련 종목코드/키워드를 포함하라.
        6. 종목코드는 #010130 같은 형태로.
        7. 말투는 간결하고 팩트 중심. 반말 X, 존칭 X, ~임, ~함, ~됨 체.
        8. 하나의 긴 포스트로 올라가므로 충분히 상세하게 작성.
        9. 출력은 반드시 "📋 주주행동주의 데일리"로 시작해야 한다. 그 앞에 검색 과정 설명, 인사말, 사전 안내 등 어떤 텍스트도 넣지 마라. 브리핑 본문만 출력하라.
    """)

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"오늘은 {date_header}이다. "
                    "한국 주주행동주의 관련 오늘자 뉴스를 web_search로 충분히 검색한 뒤, "
                    "위 형식에 맞춰 데일리 브리핑을 작성해줘. "
                    "검색어를 다양하게 해서 최소 5회 이상 검색하고, "
                    "찾은 기사 URL을 반드시 포함해."
                ),
            }
        ],
    )

    # content 블록에서 텍스트만 추출
    text_parts = []
    for block in response.content:
        if block.type == "text" and block.text:
            text_parts.append(block.text)

    briefing = "\n".join(text_parts).strip()

    if not briefing:
        raise ValueError("Claude API가 빈 브리핑을 반환했습니다.")

    return briefing


# ── 2. X 포스팅 (단일 포스트) ─────────────────────────────
def post_to_x(text: str) -> None:
    """tweepy v2 Client로 단일 포스트를 게시한다."""
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET,
    )

    resp = client.create_tweet(text=text)
    tweet_id = resp.data["id"]
    print(f"  ✅ 게시 완료 (ID: {tweet_id})")


# ── main ──────────────────────────────────────────────────
def main():
    print(f"🚀 Tivismac 데일리 브리핑 — {date_header}")
    print("─" * 40)

    print("📡 뉴스 검색 + 브리핑 생성 중...")
    briefing = generate_briefing()
    print("✅ 브리핑 생성 완료")
    print("─" * 40)
    print(briefing)
    print("─" * 40)

    print("🐦 X에 포스팅 중...")
    post_to_x(briefing)
    print("─" * 40)
    print("🎉 완료!")


if __name__ == "__main__":
    main()
