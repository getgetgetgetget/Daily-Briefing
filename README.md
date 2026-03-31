# 🐦 Tivismac — 주주행동주의 데일리 브리핑 봇

매일 오후 9시(KST) 한국 주주행동주의 뉴스를 자동으로 수집·정리해서 X(트위터)에 포스팅하는 봇.

## 구조

```
GitHub Actions (매일 21:00 KST)
  → Claude API (web search) → 당일 뉴스 검색 + 브리핑 생성
  → tweepy → X 스레드 포스팅
```

## 셋업

### 1. GitHub repo 생성

이 폴더의 파일들을 새 GitHub repo에 push:

```bash
cd tivismac
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<네아이디>/tivismac.git
git branch -M main
git push -u origin main
```

### 2. GitHub Secrets 설정

repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `X_API_KEY` | X API Key (Consumer Key) |
| `X_API_SECRET` | X API Secret (Consumer Secret) |
| `X_ACCESS_TOKEN` | X Access Token |
| `X_ACCESS_SECRET` | X Access Token Secret |

### 3. 끝!

- 자동: 매일 21:00 KST에 실행됨
- 수동: Actions 탭 → "Tivismac Daily Briefing" → "Run workflow" 클릭

## 로컬 테스트

```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-..."
export X_API_KEY="..."
export X_API_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_SECRET="..."

python generate_and_post.py
```

## 비용

- **GitHub Actions**: 무료 (public repo 기준, private도 월 2,000분 무료)
- **Claude API**: Sonnet 4 기준 1회 실행당 ~$0.02-0.05 (web search 포함)
- **X API**: Free tier (월 1,500 트윗)
