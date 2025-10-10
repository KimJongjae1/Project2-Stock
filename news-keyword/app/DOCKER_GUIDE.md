# 🐳 Docker 환경에서 AI 스마트 키워드 필터링 사용 가이드

## 🚀 빠른 시작

### 1단계: OpenAI API 키 설정

**방법 A: .env 파일 사용 (권장)**
```bash
cd news-keyword/app

# .env 파일 생성
echo "OPENAI_API_KEY=sk-proj-your-actual-openai-key-here" > .env
echo "LOG_LEVEL=INFO" >> .env
echo "DEBUG=False" >> .env
```

**방법 B: 환경 변수 직접 설정**
```bash
export OPENAI_API_KEY="sk-proj-your-actual-openai-key-here"
```

### 2단계: Docker 컨테이너 빌드 및 실행

```bash
cd news-keyword/app

# Docker 이미지 빌드
docker-compose build

# 서비스 실행 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f keyword-api
```

### 3단계: AI 필터링 테스트

```bash
# 설정 및 테스트 도구 실행
python docker_test_setup.py

# 또는 직접 API 호출
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

## 🔍 문제 해결

### 문제 1: AI 필터링이 작동하지 않음

**증상:**
```json
{
  "keywords": {"삼성전자": 278, "기업": 212, ...},
  "ai_filtered": true,
  "ai_analysis": ""
}
```

**해결 방법:**

1. **환경 변수 확인:**
```bash
# 컨테이너 내부 환경 변수 확인
docker-compose exec keyword-api env | grep OPENAI

# 또는
docker-compose exec keyword-api python -c "import os; print('API Key:', os.getenv('OPENAI_API_KEY', 'NOT_SET')[:10] + '...')"
```

2. **컨테이너 내부에서 직접 테스트:**
```bash
# 컨테이너 내부 접속
docker-compose exec keyword-api bash

# AI 필터링 테스트
python quick_test_ai_filter.py

# 상세 디버깅
python debug_smart_filter.py
```

3. **로그 확인:**
```bash
# 상세 로그 보기
docker-compose logs --tail=50 keyword-api

# 실시간 로그 모니터링
docker-compose logs -f keyword-api
```

### 문제 2: OpenAI API 키 오류

**증상:**
```
WARNING - OpenAI API를 사용할 수 없습니다. .env 파일의 OPENAI_API_KEY를 확인해주세요.
```

**해결 방법:**

1. **.env 파일 재확인:**
```bash
cat .env
# 출력 예시:
# OPENAI_API_KEY=sk-proj-실제키값
# LOG_LEVEL=INFO
```

2. **Docker 다시 빌드:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

3. **직접 환경 변수 설정:**
```yaml
# docker-compose.yml에서 직접 설정
environment:
  - OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 문제 3: 컨테이너 시작 실패

**증상:**
```
Error response from daemon: container failed to start
```

**해결 방법:**

1. **의존성 문제 확인:**
```bash
# 이미지 빌드 로그 확인
docker-compose build

# 컨테이너 실행 로그 확인
docker-compose up
```

2. **Java 환경 확인:**
```bash
docker-compose exec keyword-api java -version
docker-compose exec keyword-api python -c "import pyspark; print('PySpark 사용 가능')"
```

## 🛠️ 개발 모드

### 코드 변경 시 자동 재시작

```bash
# 개발 모드로 실행 (코드 변경 시 자동 재시작)
docker-compose up --build

# 또는 볼륨 마운트로 실시간 코드 반영
# (이미 docker-compose.yml에 설정됨)
```

### 컨테이너 내부 디버깅

```bash
# 컨테이너 내부 쉘 접속
docker-compose exec keyword-api bash

# Python 대화형 모드에서 테스트
python3 -c "
from smart_keyword_filter import SmartKeywordFilter
sf = SmartKeywordFilter()
print('AI 필터 사용 가능:', sf.is_available())
"
```

## 📊 성능 모니터링

### 리소스 사용량 확인

```bash
# 컨테이너 리소스 사용량
docker stats keyword-api

# 컨테이너 상태 확인
docker-compose ps
```

### API 응답 시간 측정

```bash
# 시간 측정과 함께 API 호출
time curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{"company_name": "삼성전자", "start_date": "20201001", "end_date": "20201005", "top_keywords": 10, "use_ai_filter": true}'
```

## 🎯 예상 AI 필터링 결과

**올바른 AI 필터링 결과:**
```json
{
  "company_name": "삼성전자",
  "keywords": {
    "투자": 106,
    "주식": 86,
    "출시": 162,
    "시장": 166,
    "소송": 76
  },
  "ai_filtered": true,
  "ai_analysis": "투자 확대와 신제품 출시가 주요 이슈로, 주가 상승 요인으로 작용할 것으로 예상됩니다.",
  "original_keyword_count": 20,
  "filtered_keyword_count": 5
}
```

**❌ 문제가 있는 결과:**
```json
{
  "keywords": {
    "삼성전자": 278,  // 기업명이 그대로 포함
    "기업": 212,      // 일반적 용어가 포함
    "TV": 126         // 단순 제품명이 포함
  },
  "ai_filtered": true,  // AI 필터링됐다고 표시되지만 실제로는 안됨
  "ai_analysis": ""     // 분석 결과 없음
}
```

## 🔧 고급 설정

### 환경별 설정

**개발 환경:**
```yaml
# docker-compose.dev.yml
environment:
  - LOG_LEVEL=DEBUG
  - DEBUG=True
```

**프로덕션 환경:**
```yaml
# docker-compose.prod.yml
environment:
  - LOG_LEVEL=WARNING
  - DEBUG=False
```

### 볼륨 설정 최적화

```yaml
volumes:
  # 읽기 전용 데이터
  - ../spark/data:/app/spark/data:ro
  
  # 개발 시에만 코드 마운트
  - .:/app:rw
  
  # 로그 영구 저장
  - ./logs:/app/logs
```

## 📝 명령어 요약

```bash
# 1. 환경 설정
echo "OPENAI_API_KEY=sk-proj-your-key" > .env

# 2. 서비스 시작
docker-compose up -d

# 3. 로그 확인
docker-compose logs -f keyword-api

# 4. AI 필터링 테스트
python docker_test_setup.py

# 5. 직접 API 테스트
curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{"company_name": "삼성전자", "start_date": "20201001", "end_date": "20201005", "top_keywords": 10, "use_ai_filter": true}'

# 6. 컨테이너 내부 디버깅
docker-compose exec keyword-api python quick_test_ai_filter.py

# 7. 서비스 종료
docker-compose down
```

## 💡 팁

1. **API 키 보안**: 프로덕션에서는 `.env` 파일을 `.gitignore`에 추가하세요.
2. **로그 레벨**: 디버깅 시에는 `LOG_LEVEL=DEBUG`로 설정하세요.
3. **캐시 클리어**: 문제 발생 시 `docker-compose build --no-cache`로 캐시 없이 빌드하세요.
4. **메모리 최적화**: 대용량 데이터 처리 시 Docker 메모리 제한을 늘리세요.

---

**마지막 업데이트:** 2024년 9월 16일
