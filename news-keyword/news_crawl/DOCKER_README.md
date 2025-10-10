# Docker를 사용한 BIG KINDS 뉴스 크롤링 자동화

## 🐳 Docker 환경에서 실행하기

Docker를 사용하면 환경 설정 없이도 쉽게 BIG KINDS 뉴스 크롤링 자동화를 실행할 수 있습니다.

**🚀 이제 Chromium 기반으로 실행되어 더욱 안정적입니다!**

## 📋 사전 요구사항

1. **Docker 설치**
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치
   - Docker Compose 포함

2. **Docker 실행 확인**
   ```bash
   docker --version
   docker-compose --version
   ```

## 🚀 빠른 시작

### 1. 프로젝트 클론 및 이동
```bash
git clone <repository-url>
cd news_crawl
```

### 2. Docker 이미지 빌드
```bash
docker-compose build
```

### 3. 자동화 실행
```bash
docker-compose up bigkinds-automation
```

## 📁 실행 방법

### 방법 1: Docker Compose 사용 (권장)

#### 헤드리스 모드 (백그라운드 실행)
```bash
docker-compose up bigkinds-automation
```

#### GUI 모드 (Linux에서만 작동)
```bash
docker-compose up bigkinds-automation-gui
```

#### 직접 실행 모드
```bash
docker-compose run --rm bigkinds-automation
```

### 방법 2: 실행 스크립트 사용

#### Linux/Mac
```bash
chmod +x docker-run.sh
./docker-run.sh
```

#### Windows
```cmd
docker-run.bat
```

### 방법 3: Docker 명령어 직접 사용

```bash
# 이미지 빌드
docker build -f Dockerfile.chromium -t bigkinds-automation .

# 컨테이너 실행
docker run -v $(pwd)/downloads:/app/downloads \
           -v $(pwd)/logs:/app/logs \
           bigkinds-automation
```

## 🔧 Docker 설정

### Dockerfile 주요 특징
- **Python 3.9-slim** 기반
- **Chromium 브라우저** 자동 설치 (Chrome 대신)
- **Selenium** 환경 최적화
- **헤드리스 모드** 지원
- **자동 실행 모드** (사용자 입력 불필요)

### docker-compose.yml 서비스
1. **bigkinds-automation**: 헤드리스 모드 실행
2. **bigkinds-automation-gui**: GUI 모드 실행 (Linux)

### 볼륨 마운트
- `./downloads` → `/app/downloads`: 다운로드된 파일 공유
- `./logs` → `/app/logs`: 로그 파일 공유

## 🌐 환경 변수

### 기본 환경 변수
```bash
DOCKER_ENV=true
LOG_DIR=/app/logs
DOWNLOAD_DIR=/app/downloads
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
SEARCH_PERIOD_DAYS=30
```

### 환경 변수 설정 방법
```bash
# 스크립트 실행
source docker-env.sh

# 또는 직접 설정
export DOCKER_ENV=true
export LOG_DIR=/app/logs
export SEARCH_PERIOD_DAYS=30
```

## 📊 모니터링 및 로그

### 로그 확인
```bash
# 실시간 로그 확인
docker-compose logs -f bigkinds-automation

# 특정 컨테이너 로그
docker logs bigkinds-news-crawler

# 호스트 로그 파일 확인
tail -f logs/bigkinds_automation.log
```

### 다운로드 파일 확인
```bash
# 다운로드된 파일 목록
ls -la downloads/

# 최신 파일 확인
ls -lt downloads/ | head -5
```

## 🛠️ 문제 해결

### 🚨 Chrome/Chromium 드라이버 문제 해결

`google-chrome: not found` 또는 `'NoneType' object has no attribute 'split'` 오류가 발생하는 경우:

#### 방법 1: 완전 재빌드 (권장)
```bash
# Linux/Mac
chmod +x rebuild-docker.sh
./rebuild-docker.sh

# Windows
rebuild-docker.bat
```

#### 방법 2: 문제 해결 스크립트 사용
```bash
# Linux/Mac
chmod +x fix-docker-build.sh
./fix-docker-build.sh

# Windows
fix-docker-build.bat
```

#### 방법 3: 수동 문제 해결
```bash
# 기존 리소스 완전 정리
docker-compose down
docker system prune -af
docker image prune -af

# 강제 재빌드
docker-compose build --no-cache --pull
```

### 🚨 Chromium 설치 문제 해결

Chromium 설치 중 문제가 발생하는 경우:

#### 방법 1: 문제 해결 스크립트 사용 (권장)
```bash
# Linux/Mac
chmod +x fix-docker-build.sh
./fix-docker-build.sh

# Windows
fix-docker-build.bat
```

#### 방법 2: 수동 문제 해결
```bash
# 기존 리소스 정리
docker-compose down
docker system prune -f
docker image prune -f

# 강제 재빌드
docker-compose build --no-cache --pull
```

### 🚨 EOF 오류 해결

`EOF when reading a line` 오류가 발생하는 경우:

#### 원인
- Docker 환경에서 사용자 입력 스트림 문제
- 인터랙티브 모드에서 발생

#### 해결 방법
1. **자동으로 해결됨**: 새로운 Docker 전용 스크립트 사용
2. **환경 변수 확인**: `DOCKER_ENV=true` 설정
3. **수동 설정**: `SEARCH_PERIOD_DAYS` 환경 변수로 검색 기간 조정

```bash
# 환경 변수로 검색 기간 설정
export SEARCH_PERIOD_DAYS=7  # 최근 7일
docker-compose up bigkinds-automation

# 또는 docker-compose.yml에서 직접 설정
environment:
  - SEARCH_PERIOD_DAYS=7
```

### 일반적인 문제들

#### 1. Chromium 드라이버 오류
```bash
# 컨테이너 재빌드
docker-compose build --no-cache

# Chromium 버전 확인
docker exec bigkinds-news-crawler chromium --version
```

#### 2. 권한 문제
```bash
# 볼륨 권한 설정
sudo chown -R $USER:$USER downloads/ logs/

# 또는 Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
```

#### 3. 메모리 부족
```bash
# Docker 메모리 제한 확인
docker stats bigkinds-news-crawler

# docker-compose.yml에서 메모리 제한 조정
mem_limit: 4g
```

#### 4. 네트워크 문제
```bash
# 네트워크 상태 확인
docker network ls
docker network inspect news_crawl_default

# 컨테이너 재시작
docker-compose restart
```

### 디버깅 모드

#### 컨테이너 내부 접근
```bash
# 실행 중인 컨테이너에 접근
docker exec -it bigkinds-news-crawler /bin/bash

# 또는 새 컨테이너로 디버깅
docker run -it --rm bigkinds-automation /bin/bash
```

#### 로그 레벨 조정
```bash
# 환경 변수로 로그 레벨 설정
export LOG_LEVEL=DEBUG
docker-compose up bigkinds-automation
```

## 🔄 업데이트 및 유지보수

### 이미지 업데이트
```bash
# 최신 코드로 재빌드
git pull
docker-compose build --no-cache

# 기존 컨테이너 정리
docker-compose down
docker system prune -f
```

### 의존성 업데이트
```bash
# requirements.txt 수정 후 재빌드
docker-compose build --no-cache
```

## 📈 성능 최적화

### 리소스 제한 조정
```yaml
# docker-compose.yml
services:
  bigkinds-automation:
    mem_limit: 4g      # 메모리 제한
    cpus: 2.0          # CPU 제한
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### 병렬 실행
```bash
# 여러 인스턴스 동시 실행
docker-compose up --scale bigkinds-automation=3
```

## 🔒 보안 고려사항

1. **로그인 정보**: 환경 변수나 별도 설정 파일 사용
2. **네트워크**: 필요한 포트만 노출
3. **볼륨**: 민감한 데이터는 호스트에 마운트하지 않음
4. **권한**: 최소 권한 원칙 적용

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Selenium Docker 가이드](https://github.com/SeleniumHQ/docker-selenium)

## 🤝 문제 신고

Docker 관련 문제가 발생하면 다음 정보와 함께 이슈를 등록해주세요:

1. Docker 버전
2. 운영체제 정보
3. 에러 로그
4. 실행 명령어
5. 환경 변수 설정
