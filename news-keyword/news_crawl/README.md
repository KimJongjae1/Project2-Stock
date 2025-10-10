# BIG KINDS 뉴스 크롤링 자동화

BIG KINDS 웹사이트에서 뉴스 검색 분석을 자동화하는 Python 프로그램입니다.

**🚀 Docker 환경에서 Chromium 기반으로 실행되어 더욱 안정적입니다!**

## 주요 기능

- BIG KINDS 웹사이트 자동 로그인
- 뉴스 검색 분석 페이지 자동 이동
- 검색 기간 설정 (사용자 지정 가능)
- 경제 카테고리 자동 선택
- 분석 결과 및 시각화 페이지 자동 이동
- 엑셀 파일 자동 다운로드
- **🆕 CSV 파일 자동 변환**
- **🆕 S3 클라우드 자동 업로드**

## 설치 방법

### 1. Python 설치
Python 3.7 이상이 설치되어 있어야 합니다.

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. Chrome/Chromium 브라우저 설치
- **로컬 실행**: Chrome 브라우저가 설치되어 있어야 합니다
- **Docker 실행**: Chromium이 자동으로 설치됩니다

### 4. AWS S3 설정 (S3 업로드 기능 사용시)
S3 업로드 기능을 사용하려면 AWS 자격 증명을 설정해야 합니다.

#### 환경 변수 설정
```bash
# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_DEFAULT_REGION="ap-northeast-2"

# Linux/Mac
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_DEFAULT_REGION="ap-northeast-2"
```

#### Docker 환경에서 사용
```bash
# 환경 변수와 함께 실행
AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret docker-compose up
```

## 사용 방법

### Docker 실행 (권장)
```bash
# Docker 이미지 빌드
docker-compose build

# 자동화 실행
docker-compose up bigkinds-automation
```

### 로컬 실행
```bash
# 간단한 실행
python run_automation.py

# 직접 실행
python bigkinds_automation.py
```

## 설정 파일

`config.py` 파일에서 다음 설정을 변경할 수 있습니다:

- 로그인 정보 (이메일, 비밀번호)
- 기본 검색 기간
- 브라우저 옵션
- 대기 시간 설정

## 프로그램 구조

```
news_crawl/
├── bigkinds_automation.py    # 메인 자동화 클래스
├── run_automation.py         # 사용자 친화적 실행 스크립트
├── run_automation_docker.py  # Docker 전용 실행 스크립트
├── config.py                 # 설정 파일
├── requirements.txt          # 필요한 패키지 목록
├── Dockerfile               # Docker 이미지 설정
├── docker-compose.yml       # Docker Compose 설정
└── README.md                # 이 파일
```

## 주요 클래스 및 메서드

### BigKindsAutomation 클래스

- `setup_driver()`: Chrome/Chromium 드라이버 설정
- `login()`: BIG KINDS 로그인
- `navigate_to_news_analysis()`: 뉴스 검색 분석 페이지로 이동
- `set_search_period()`: 검색 기간 설정
- `select_economy_category()`: 경제 카테고리 선택
- `navigate_to_visualization()`: 시각화 페이지로 이동
- `download_excel()`: 엑셀 파일 다운로드

## 로그 파일

프로그램 실행 시 `bigkinds_automation.log` 파일에 상세한 로그가 기록됩니다.

## 주의사항

1. **인터넷 연결**: 안정적인 인터넷 연결이 필요합니다.
2. **브라우저**: Chrome 또는 Chromium 브라우저가 필요합니다.
3. **로그인 정보**: 올바른 BIG KINDS 계정 정보를 사용해야 합니다.
4. **웹사이트 변경**: BIG KINDS 웹사이트 구조가 변경될 경우 프로그램 수정이 필요할 수 있습니다.

## 문제 해결

### 일반적인 문제들

1. **ChromeDriver 오류**
   - Chrome 브라우저를 최신 버전으로 업데이트
   - Docker 환경에서는 Chromium 사용 (권장)

2. **로그인 실패**
   - 계정 정보 확인
   - BIG KINDS 웹사이트 접속 가능 여부 확인

3. **요소를 찾을 수 없음**
   - 웹사이트 로딩 시간 증가
   - 네트워크 상태 확인

### Docker 관련 문제

Docker 실행 중 문제가 발생하면 `DOCKER_README.md`를 참조하세요.

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

## 문의사항

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해 주세요.
