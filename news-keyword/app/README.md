# 뉴스 키워드 추출 FastAPI 서비스 (AI 스마트 필터링 지원)

기간별 기업의 키워드 추출을 위한 FastAPI 웹 서비스입니다. OpenAI를 활용한 스마트 키워드 필터링 기능을 제공합니다.

## 🚀 주요 기능

- **기업별 키워드 추출**: 특정 기업과 관련된 뉴스에서 키워드를 추출합니다.
- **기간 필터링**: 시작일과 종료일을 지정하여 특정 기간의 데이터만 분석합니다.
- **🤖 OpenAI 기반 스마트 키워드 필터링**: OpenAI API를 활용해 주가와 관련된 키워드만 지능적으로 선별합니다.
- **AI 키워드 분석**: 추출된 키워드를 바탕으로 시장 트렌드와 주가 영향 요소를 분석합니다.
- **PySpark 기반**: 대용량 데이터 처리를 위해 PySpark를 사용합니다.
- **RESTful API**: 표준 HTTP API로 쉽게 연동할 수 있습니다.

## 📋 API 명세

### 1. 키워드 추출 API (AI 필터링 지원)

**엔드포인트**: `POST /extract-keywords`

**요청 형식**:
```json
{
    "company_name": "삼성전자",
    "start_date": "20200901",
    "end_date": "20200903",
    "top_keywords": 20,
    "use_ai_filter": true      // AI 필터링 사용 여부 (기본값: true)
}
```

**기본 응답 형식** (AI 필터링 비활성화 시):
```json
{
    "company_name": "삼성전자",
    "period": "20200901-20200903",
    "total_news_count": 15,
    "keywords": {
        "반도체": 8,
        "투자": 5,
        "기술": 3
    },
    "top_keywords": ["반도체", "투자", "기술"],
    "message": "성공적으로 키워드를 추출했습니다."
}
```

**AI 필터링 응답 형식** (AI 필터링 활성화 시):
```json
{
    "company_name": "삼성전자",
    "period": "20200901-20200903",
    "total_news_count": 15,
    "keywords": {
        "실적": 12,
        "매출증가": 8,
        "투자확대": 6
    },
    "top_keywords": ["실적", "매출증가", "투자확대"],
    "message": "AI 필터링 완료: 30개 → 15개 키워드 (주가 관련성 기준)",
    "ai_filtered": true,
    "ai_analysis": "긍정적인 실적 발표와 투자 확대가 주요 이슈로, 주가 상승 요인으로 작용할 것으로 예상됩니다.",
    "original_keyword_count": 30,
    "filtered_keyword_count": 15
}
```

### 2. 헬스체크 API

**엔드포인트**: `GET /health`

**응답 형식**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T14:30:25.123456"
}
```

## 🛠️ 설치 및 실행

### 사전 준비

1. **OpenAI API 키 설정** (AI 필터링 사용시 필요):
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 로컬 환경에서 실행

1. **의존성 설치**:
```bash
pip install -r requirements.txt
```

2. **서버 실행**:
```bash
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **API 문서 확인**:
브라우저에서 `http://localhost:8000/docs` 접속

### Docker로 실행

1. **Docker 이미지 빌드**:
```bash
docker-compose build
```

2. **서비스 실행**:
```bash
docker-compose up -d
```

3. **서비스 상태 확인**:
```bash
docker-compose ps
```

## 🧪 테스트

### 스마트 키워드 필터링 기능 테스트

```bash
# 통합 테스트 실행
python test_smart_keywords_integration.py

# 기존 키워드 추출 테스트
python test_smart_keywords.py
```

### 수동 테스트 (curl 사용)

1. **헬스체크**:
```bash
curl -X GET "http://localhost:8000/health"
```

2. **기본 키워드 추출**:
```bash
curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "삼성전자",
       "start_date": "20200901",
       "end_date": "20200903",
       "top_keywords": 10,
       "use_ai_filter": false
     }'
```

3. **AI 스마트 필터링된 주가 관련 키워드 추출**:
```bash
curl -X POST "http://localhost:8000/extract-keywords" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "삼성전자",
       "start_date": "20200901",
       "end_date": "20200903",
       "top_keywords": 10,
       "use_ai_filter": true
     }'
```

## 📁 프로젝트 구조

```
app/
├── main.py                             # FastAPI 메인 애플리케이션
├── keyword_extractor.py                # 키워드 추출 엔진
├── smart_keyword_filter.py             # 🤖 OpenAI 기반 스마트 키워드 필터링 모듈
├── test_smart_keywords_integration.py  # 🧪 스마트 키워드 통합 테스트
├── test_smart_keywords.py              # 🧪 기본 키워드 추출 테스트
├── requirements.txt                    # Python 의존성
├── .env                               # 환경 변수 (OpenAI API 키)
├── Dockerfile                         # Docker 이미지 설정
├── docker-compose.yml                 # Docker Compose 설정
└── README.md                          # 이 파일
```

## 🔧 주요 구성 요소

### KeywordExtractor 클래스

- **initialize_spark()**: SparkSession 초기화
- **find_csv_files()**: 날짜 범위에 해당하는 CSV 파일 검색
- **extract_keywords_from_csv()**: CSV에서 기본 키워드 추출 및 빈도 계산
- **extract_smart_keywords_from_csv()**: 🤖 AI 스마트 필터링을 포함한 키워드 추출

### SmartKeywordFilter 클래스

- **filter_stock_related_keywords()**: OpenAI를 활용한 주가 관련 키워드 필터링
- **get_keyword_analysis()**: 추출된 키워드에 대한 AI 분석 제공
- **is_available()**: OpenAI API 사용 가능 여부 확인

### API 엔드포인트

- **POST /extract-keywords**: 메인 키워드 추출 기능 (🤖 OpenAI 스마트 필터링 지원)
- **GET /**: API 정보 및 사용 가능한 엔드포인트 목록
- **GET /health**: 서비스 상태 확인

## 📊 데이터 처리 흐름

### 스마트 엔진 선택
1. **요청 접수**: 클라이언트에서 기업명과 날짜 범위 전송
2. **파일 검색**: S3에서 해당 기간의 CSV 파일 찾기
3. **파일 크기 계산**: S3에서 파일들의 총 크기 확인
4. **엔진 선택**: 
   - **15GB 이상**: PySpark 사용 (대용량 데이터 처리)
   - **15GB 미만**: Pandas 사용 (빠른 처리)

### 기본 키워드 추출 (use_ai_filter=false)
1. **데이터 로드**: 선택된 엔진으로 CSV 파일 읽기
2. **필터링**: 기관 컬럼에서 해당 기업이 포함된 행 추출
3. **키워드 추출**: 키워드 컬럼에서 키워드 분리 및 정리
4. **빈도 계산**: 각 키워드의 출현 빈도 계산
5. **결과 반환**: JSON 형식으로 결과 반환

### 🤖 OpenAI 스마트 키워드 필터링 (use_ai_filter=true)
1. **1단계**: 위의 기본 키워드 추출 과정 실행
2. **2단계 OpenAI 스마트 필터링**:
   - **빈도수 기반 사전 필터링**: 상위 50개 키워드만 선택 (API 비용 절약)
   - **OpenAI GPT 분석**: 키워드들을 주가 관련성 기준으로 분석
   - **스마트 필터링**: 주가에 직접적 영향을 미치는 키워드만 선별
   - **기업명 제거**: 해당 기업명 자체는 자동 제외
3. **3단계 키워드 분석**: 필터링된 키워드에 대한 시장 분석 제공
4. **결과 구성**: 필터링된 키워드 + AI 분석 결과 + 통계 정보 반환

## ⚠️ 주의사항

1. **CSV 파일 위치**: `spark/data` 디렉토리에 CSV 파일들이 있어야 합니다.
2. **OpenAI API 키**: AI 필터링 기능 사용시 `.env` 파일에 `OPENAI_API_KEY` 설정이 필요합니다.
3. **API 비용**: OpenAI API 사용시 토큰 기반으로 비용이 발생합니다. (키워드당 약 $0.001)
4. **메모리 사용량**: 대용량 CSV 파일 처리 시 충분한 메모리가 필요합니다 (권장: 4GB 이상).
5. **날짜 형식**: YYYYMMDD 형식만 지원합니다 (예: 20200901).
6. **Java 환경**: PySpark 실행을 위해 Java 8이 필요합니다 (Docker에 포함됨).
7. **처리 시간**: AI 필터링 사용시 OpenAI API 호출로 인해 추가 시간이 소요됩니다 (보통 2-5초).

## 📁 데이터 구조

API는 S3 버킷에서 CSV 파일들을 동적으로 읽습니다:

### S3 설정

API는 다음 환경 변수를 통해 S3 설정을 관리합니다:

```bash
# AWS 자격 증명
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=ap-northeast-2

# S3 버킷 설정
S3_BUCKET=cheesecrust-spark-data-bucket
S3_PREFIX=outputs/data/
```

### 파일명 패턴
- `NewsResult_YYYYMMDD-YYYYMMDD.csv` 
- `NewsResult_YYYYMMDD-YYYYMMDD__sheet.csv`

### 지원 기간
- **2019년부터 2025년까지**의 뉴스 데이터
- 사용자가 입력한 날짜 범위에 해당하는 모든 CSV 파일을 S3에서 자동으로 찾아서 병합 처리

### 예시 S3 파일 경로
```
s3://cheesecrust-spark-data-bucket/outputs/data/NewsResult_20200102-20200105.csv
s3://cheesecrust-spark-data-bucket/outputs/data/NewsResult_20210301-20210304.csv
s3://cheesecrust-spark-data-bucket/outputs/data/NewsResult_20220101-20220105.csv
```

### 사용 예시
```json
{
    "company_name": "삼성전자",
    "start_date": "20210301",    // 2021년 3월 1일부터
    "end_date": "20210331",      // 2021년 3월 31일까지
    "top_keywords": 20
}
```

위 요청은 2021년 3월 전체 기간의 모든 관련 CSV 파일을 S3에서 읽어서 처리합니다.

## 🚀 확장 계획

- [x] **여러 CSV 파일을 자동으로 찾아서 처리** ✅ 완료
- [x] **🤖 OpenAI 기반 스마트 키워드 필터링** ✅ 완료
- [x] **AI 키워드 분석 및 시장 트렌드 해석** ✅ 완료
- [x] **S3에서 직접 CSV 파일 읽기** ✅ 완료
- [x] **파일 크기 기반 스마트 엔진 선택** ✅ 완료
- [ ] 캐싱 기능 추가로 응답 속도 개선  
- [ ] 키워드 추출 알고리즘 개선 (Word2Vec, BERT 등)
- [ ] 비동기 처리로 대용량 데이터 처리 성능 향상
- [ ] 인증 및 권한 관리 기능
- [ ] 로그 및 모니터링 기능 강화
- [ ] 다양한 AI 모델 지원 (Claude, Gemini 등)
- [ ] 한국어 전용 금융 AI 모델 통합

## 🎯 OpenAI 스마트 키워드 필터링 특징

### 📈 주가 관련 키워드 식별 기준
- **실적 및 재무**: 실적, 매출, 이익, 손실, 영업이익, 순이익 등
- **투자 및 사업**: 투자, 계약, 신제품, 기술개발, 특허, R&D 등
- **시장 동향**: 경쟁, 시장점유율, 규제, 정책, 산업동향 등
- **기업 경영**: 인수합병, 임원진 변화, 조직개편, 전략발표 등
- **주식 시장**: 상장, 증자, 배당, 주주총회, 공시 등

### 🤖 OpenAI 스마트 필터링 과정
1. **컨텍스트 이해**: 기업명과 키워드 리스트를 종합적으로 분석
2. **의미적 분석**: 각 키워드가 주가에 미치는 직간접적 영향 평가
3. **관련성 판단**: 단순 언급이 아닌 실질적 주가 영향 요소 식별
4. **스마트 필터링**: 주가와 무관한 일반적 단어들 자동 제외
5. **트렌드 분석**: 필터링된 키워드를 바탕으로 시장 전망 제공



