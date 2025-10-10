# AI 스마트 키워드 필터링 문제 해결 가이드

## 🔍 현재 문제

AI 필터링이 활성화되어 있다고 표시되지만 (`ai_filtered: true`), 실제로는 원본 키워드가 그대로 반환되는 문제가 발생하고 있습니다.

```json
{
  "keywords": {
    "삼성전자": 278,  // 🚫 기업명이 그대로 포함됨
    "기업": 212,      // 🚫 일반적인 단어가 포함됨
    "TV": 126,        // 🚫 단순 제품명이 포함됨
    ...
  },
  "ai_filtered": true,  // ⚠️ AI 필터링이 됐다고 표시되지만 실제로는 안됨
}
```

## 🎯 예상 결과

AI 필터링이 제대로 작동하면 다음과 같은 결과가 나와야 합니다:

```json
{
  "keywords": {
    "투자": 106,      // ✅ 주가 관련 키워드
    "주식": 86,       // ✅ 주가 관련 키워드  
    "출시": 162,      // ✅ 사업 관련 키워드
    "시장": 166,      // ✅ 시장 관련 키워드
    "소송": 76        // ✅ 주가 영향 키워드
  },
  "ai_filtered": true,
  "ai_analysis": "투자 확대와 신제품 출시가 주요 이슈..."
}
```

## 🔧 해결 방법

### 1단계: OpenAI API 키 설정 확인

```bash
# 1. .env 파일이 올바른 위치에 있는지 확인
ls -la news-keyword/app/.env

# 2. .env 파일 내용 확인 (실제 키가 들어있는지)
cat news-keyword/app/.env
```

**올바른 .env 파일 형태:**
```bash
OPENAI_API_KEY=sk-proj-실제_OpenAI_API_키_여기에_입력
DEBUG=False
LOG_LEVEL=INFO
```

**❌ 잘못된 설정:**
```bash
OPENAI_API_KEY=your_openai_api_key_here  # 기본값 그대로
OPENAI_API_KEY=                          # 빈 값
# OPENAI_API_KEY가 아예 없음
```

### 2단계: OpenAI API 키 발급

1. [OpenAI 플랫폼](https://platform.openai.com/account/api-keys)에 로그인
2. "Create new secret key" 클릭
3. 생성된 키를 복사 (sk-proj-로 시작)
4. .env 파일에 붙여넣기

### 3단계: 빠른 테스트 실행

```bash
cd news-keyword/app

# AI 필터링 단독 테스트
python quick_test_ai_filter.py

# 전체 통합 테스트  
python debug_smart_filter.py
```

### 4단계: API 테스트

```bash
# 서버 실행
python main.py

# 다른 터미널에서 API 테스트
curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "삼성전자",
       "start_date": "20201001",
       "end_date": "20201005",
       "top_keywords": 10,
       "use_ai_filter": true
     }'
```

## 🔍 문제 진단

### 케이스 1: API 키 없음
**증상:** `ai_filtered: false`, `"OpenAI API 키가 설정되지 않았습니다"`
**해결:** .env 파일에 올바른 API 키 설정

### 케이스 2: API 키 잘못됨
**증상:** OpenAI API 호출 오류, 401 Unauthorized
**해결:** 올바른 API 키로 교체

### 케이스 3: 크레딧 부족
**증상:** OpenAI API 호출 오류, 429 Rate Limit
**해결:** OpenAI 계정에 크레딧 충전

### 케이스 4: 키워드 매칭 실패
**증상:** `ai_filtered: true`이지만 원본 키워드 그대로 반환
**해결:** 로그 확인하여 AI 응답과 키워드 매칭 과정 점검

## 📊 로그 확인 방법

```bash
# 상세 로그와 함께 서버 실행
LOG_LEVEL=DEBUG python main.py

# 또는 
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from smart_keyword_filter import SmartKeywordFilter
sf = SmartKeywordFilter()
print('Available:', sf.is_available())
"
```

## 🎯 예상 AI 필터링 결과

제공된 키워드 예시에서 다음과 같이 필터링될 것으로 예상됩니다:

**✅ 유지될 키워드:**
- `투자` (106) - 직접적 주가 영향
- `주식` (86) - 주식시장 관련  
- `출시` (162) - 신제품/사업 관련
- `시장` (166) - 시장 동향 관련
- `소송` (76) - 주가 영향 요소

**🗑️ 제거될 키워드:**
- `삼성전자` (278) - 기업명 자체
- `삼성` (72) - 기업명 자체
- `기업` (212) - 일반적 용어
- `회사` (92) - 일반적 용어
- `업체` (86) - 일반적 용어
- `TV` (126) - 단순 제품명
- `냉장고` (82) - 단순 제품명
- `취업` (92) - 주가와 무관
- `소비자` (72) - 주가와 무관

## 📞 추가 도움

여전히 문제가 해결되지 않으면:

1. `quick_test_ai_filter.py` 실행 결과 공유
2. 서버 로그 (특히 ERROR, WARNING 메시지) 공유
3. .env 파일 설정 상태 확인 (API 키는 가린 채로)

---

**마지막 업데이트:** 2024년 9월 16일
