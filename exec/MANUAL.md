# 주식 나침반

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [환경 요구사항](#환경-요구사항)
4. [설치 및 배포 가이드](#설치-및-배포-가이드)
5. [환경 설정](#환경-설정)
6. [서비스별 구성](#서비스별-구성)
7. [데이터베이스 설정](#데이터베이스-설정)
8. [모니터링 및 로깅](#모니터링-및-로깅)
9. [문제 해결](#문제-해결)
10. [성능 최적화](#성능-최적화)

---

## 프로젝트 개요

### 🎯 프로젝트 목적
주식을 잘 모르는 사람들을 위한 **모의투자 플랫폼**으로, 다음과 같은 기능을 제공합니다:
- **모의투자**: 실제 돈 없이 주식 투자 경험
- **투자성향 파악**: AI 기반 투자 성향 분석
- **뉴스 키워드 분석**: Spark를 활용한 뉴스 데이터 처리
- **AI 기반 주가 영향 분석**: 뉴스 기사 요약 및 주가 영향도 분석

### 🔧 주요 기술 스택
- **백엔드**: Spring Boot 3.5.5 (Java 17)
- **프론트엔드**: React 19.1.1 + TypeScript + Vite
- **데이터베이스**: MySQL 8.0
- **캐시**: Redis
- **빅데이터 처리**: Apache Spark 3.4.1
- **AI/ML**: OpenAI API, Pandas, NumPy
- **컨테이너화**: Docker + Docker Compose
- **CI/CD**: Jenkins
- **웹서버**: Nginx
- **모니터링**: Prometheus + Grafana

---

## 시스템 아키텍처

### 🏗️ 전체 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   News Crawl    │
│   (React/Vite)  │◄──►│   (Spring Boot) │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │     MySQL       │    │   Spark Cluster │
         │              │   (Database)    │    │   (Big Data)    │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         └──────────────►│     Redis       │    │  Keyword API    │
                        │    (Cache)      │    │   (FastAPI)    │
                        └─────────────────┘    └─────────────────┘
```

### 🔄 데이터 플로우
1. **뉴스 수집**: Python 기반 뉴스 크롤링
2. **데이터 처리**: Spark를 통한 CSV 데이터 분석 및 키워드 추출
3. **AI 분석**: OpenAI API를 통한 주식 관련 키워드 필터링 및 뉴스 요약
4. **API 제공**: FastAPI를 통한 키워드 및 분석 결과 제공
5. **웹 서비스**: Spring Boot 백엔드와 React 프론트엔드를 통한 사용자 인터페이스

---

## 환경 요구사항

### 💻 하드웨어 요구사항
- **CPU**: 최소 4코어 (권장 8코어 이상)
- **메모리**: 최소 8GB RAM (권장 16GB 이상)
- **저장공간**: 최소 50GB 여유 공간
- **네트워크**: 안정적인 인터넷 연결

### 🖥️ 소프트웨어 요구사항
- **운영체제**: Ubuntu 20.04+ / CentOS 8+ / Windows 10+ / macOS 10.15+
- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+
- **Git**: 2.25.0+

### 🌐 외부 서비스 요구사항
- **OpenAI API**: GPT 모델 사용을 위한 API 키
- **AWS S3**: 데이터 저장을 위한 S3 버킷
- **OAuth 제공자**: Google, Kakao OAuth 설정

---

## 설치 및 배포 가이드

### 1️⃣ 저장소 클론
```bash
git clone https://lab.ssafy.com/s13-bigdata-dist-sub1/S13P21A301.git
cd S13P21A301
```

### 2️⃣ 환경 변수 설정
```bash
# 환경 변수 파일 복사
cp env.example .env

# 환경 변수 편집
nano .env
```

### 3️⃣ Docker 환경 확인
```bash
# Docker 설치 확인
docker --version
docker-compose --version

# Docker 서비스 시작 (Linux)
sudo systemctl start docker
sudo systemctl enable docker
```

### 4️⃣ 자동 배포 실행
```bash
# 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

### 5️⃣ 수동 배포 (단계별)
```bash
# 1. 기존 컨테이너 정리
docker-compose down --remove-orphans

# 2. 이미지 빌드
docker-compose build --no-cache

# 3. 서비스 시작
docker-compose up -d

# 4. 헬스체크
docker-compose ps
```

---

## 환경 설정

### 🔧 필수 환경 변수

#### 기본 설정
```bash
# Timezone
TZ=Asia/Seoul

# Domain (실제 도메인으로 변경)
DOMAIN=your-domain.com

# Database Configuration
DB_NAME=survive_stock
DB_USER=root
DB_PASSWORD=your_secure_password
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_DATABASE=survive_stock
```

#### Spring Boot 설정
```bash
# Spring Boot Configuration
SPRING_PROFILE=prod
SERVER_PORT=8080

# JWT 설정
JWT_SECRET=your_jwt_secret_key_here
JWT_ACCESS_EXP_MINUTES=60
JWT_REFRESH_EXP_DAYS=14
```

#### OAuth 설정
```bash
# Kakao OAuth
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### Redis 설정
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=your_redis_password
REDIS_SSL=false
```

#### AI/ML 서비스 설정
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# AWS S3 (키워드 분석용)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=ap-northeast-2
S3_BUCKET=your_s3_bucket_name
S3_PREFIX=outputs/pagerank/data/
```

### 🌐 네트워크 설정

#### 포트 매핑
- **80/443**: Nginx (웹 서버)
- **8080**: Spring Boot 백엔드
- **3306**: MySQL 데이터베이스
- **6379**: Redis 캐시
- **8000**: Spark Master Web UI
- **8081/8082**: Spark Worker Web UI
- **8888**: Keyword API (FastAPI)
- **9090**: Prometheus
- **3000**: Grafana
- **9091**: Pushgateway

#### 방화벽 설정 (Linux)
```bash
# 필요한 포트 열기
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8080
sudo ufw allow 3306
sudo ufw allow 6379
sudo ufw allow 8000
sudo ufw allow 8081
sudo ufw allow 8082
sudo ufw allow 8888
sudo ufw allow 9090
sudo ufw allow 3000
sudo ufw allow 9091
```

---

## 서비스별 구성

### 🖥️ 백엔드 (Spring Boot)

#### 주요 의존성
- Spring Boot 3.5.5
- Spring Security + OAuth2
- Spring Data JPA
- Spring Data Redis
- MySQL Connector
- JWT (JSON Web Token)
- Spring Boot Actuator

#### 설정 파일 위치
- `back/src/main/resources/application.yml`
- `back/.env` (환경별 설정)

#### 빌드 및 실행
```bash
cd back
./gradlew clean bootJar
java -jar build/libs/*.jar
```

### 🌐 프론트엔드 (React + Vite)

#### 주요 의존성
- React 19.1.1
- TypeScript 5.8.3
- Vite 7.1.7
- Tailwind CSS 4.1.13
- Chart.js 4.5.0
- Axios 1.11.0
- Zustand 5.0.8

#### 빌드 및 실행
```bash
cd frontend
npm install
npm run build
npm run preview
```

### 🔍 키워드 분석 API (FastAPI)

#### 주요 의존성
- FastAPI 0.104.1
- PySpark 3.3.0
- Pandas 1.5.3
- OpenAI API
- Boto3 (AWS S3)

#### 설정 파일 위치
- `news-keyword/app/requirements.txt`
- `news-keyword/app/.env`

#### 실행
```bash
cd news-keyword/app
pip install -r requirements.txt
python run_api.py
```

### ⚡ Spark 클러스터

#### 구성
- **Master**: 1개 노드 (포트 8000)
- **Worker**: 2개 노드 (포트 8081, 8082)
- **Client**: 작업 실행용 컨테이너

#### 실행
```bash
cd news-keyword/spark
docker-compose up -d
```

### 📊 모니터링 시스템

#### Prometheus + Grafana
- **Prometheus**: 메트릭 수집 (포트 9090)
- **Grafana**: 대시보드 (포트 3000)
- **Node Exporter**: 시스템 메트릭 (포트 9100)
- **Pushgateway**: 배치 작업 모니터링 (포트 9091)

---

## 데이터베이스 설정

### 🗄️ MySQL 설정

#### 데이터베이스 생성
```sql
CREATE DATABASE survive_stock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON survive_stock.* TO 'stock_user'@'%';
FLUSH PRIVILEGES;
```

#### 주요 테이블
- **users**: 사용자 정보
- **portfolios**: 포트폴리오 정보
- **trades**: 거래 내역
- **stocks**: 주식 정보
- **news**: 뉴스 데이터
- **keywords**: 키워드 분석 결과

### 🔄 Redis 설정

#### 기본 설정
```bash
# Redis 설정 파일 수정
nano /etc/redis/redis.conf

# 주요 설정
bind 0.0.0.0
port 6379
requirepass your_redis_password
maxmemory 2gb
maxmemory-policy allkeys-lru
```

#### 캐시 전략
- **세션 데이터**: 사용자 로그인 상태
- **주식 데이터**: 실시간 주가 정보
- **뉴스 데이터**: 키워드 분석 결과

---

## 모니터링 및 로깅

### 📈 Prometheus 메트릭

#### 주요 메트릭
- **애플리케이션 메트릭**: Spring Boot Actuator
- **시스템 메트릭**: Node Exporter
- **Spark 메트릭**: Spark Metrics Exporter
- **커스텀 메트릭**: 비즈니스 로직 메트릭

#### 설정 파일
- `news-keyword/spark/monitoring/prometheus.yml`

### 📊 Grafana 대시보드

#### 기본 대시보드
- **시스템 모니터링**: CPU, 메모리, 디스크 사용률
- **애플리케이션 모니터링**: 요청 수, 응답 시간, 에러율
- **Spark 모니터링**: 작업 실행 상태, 리소스 사용률
- **데이터베이스 모니터링**: 연결 수, 쿼리 성능

#### 접속 정보
- **URL**: http://localhost:3000
- **사용자명**: admin
- **비밀번호**: admin123

### 📝 로깅 설정

#### Spring Boot 로깅
```yaml
# application.yml
logging:
  level:
    com.stock: DEBUG
    org.springframework.security: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/application.log
```

#### 로그 파일 위치
- **애플리케이션 로그**: `logs/application.log`
- **Spark 로그**: `news-keyword/spark/logs/`
- **Nginx 로그**: `/var/log/nginx/`

---

## 문제 해결

### 🚨 일반적인 문제

#### 1. Docker 컨테이너 시작 실패
```bash
# 로그 확인
docker-compose logs [service_name]

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart [service_name]
```

#### 2. 데이터베이스 연결 실패
```bash
# MySQL 상태 확인
docker-compose exec mysql mysql -u root -p

# 연결 테스트
telnet localhost 3306
```

#### 3. Redis 연결 실패
```bash
# Redis 상태 확인
docker-compose exec redis redis-cli ping

# 연결 테스트
telnet localhost 6379
```

#### 4. Spark 클러스터 문제
```bash
# Spark 상태 확인
docker-compose exec spark-master /opt/spark/bin/spark-shell

# Worker 상태 확인
curl http://localhost:8000
```

#### 5. OAuth 인증 실패
- OAuth 클라이언트 ID/Secret 확인
- 리다이렉트 URI 설정 확인
- 도메인 설정 확인

### 🔧 성능 문제

#### 1. 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 컨테이너 메모리 제한 설정
# docker-compose.yml에서 mem_limit 설정
```

#### 2. 디스크 공간 부족
```bash
# 디스크 사용량 확인
df -h

# Docker 이미지 정리
docker system prune -a
```

#### 3. 네트워크 지연
```bash
# 네트워크 상태 확인
netstat -tulpn

# 포트 사용량 확인
ss -tulpn
```

---

## 성능 최적화

### ⚡ 애플리케이션 최적화

#### Spring Boot 최적화
```yaml
# application.yml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
```

#### Redis 최적화
```bash
# Redis 설정 최적화
maxmemory-policy allkeys-lru
tcp-keepalive 60
timeout 300
```

#### MySQL 최적화
```sql
-- 인덱스 최적화
CREATE INDEX idx_user_id ON portfolios(user_id);
CREATE INDEX idx_stock_code ON stocks(code);
CREATE INDEX idx_trade_date ON trades(created_at);
```

### 🚀 Spark 최적화

#### 메모리 설정
```bash
# Spark 설정
SPARK_WORKER_MEMORY=4g
SPARK_WORKER_CORES=4
SPARK_EXECUTOR_MEMORY=2g
SPARK_EXECUTOR_CORES=2
```

#### 데이터 처리 최적화
- **파티셔닝**: 데이터를 적절히 분할
- **캐싱**: 자주 사용되는 데이터 캐시
- **브로드캐스트**: 작은 데이터셋 브로드캐스트

### 📊 모니터링 최적화

#### 메트릭 수집 최적화
```yaml
# prometheus.yml
scrape_interval: 15s
evaluation_interval: 15s
```

#### 로그 레벨 조정
```yaml
# 운영 환경에서는 INFO 레벨 사용
logging:
  level:
    root: INFO
    com.stock: INFO
```

---

## 📞 지원 및 문의

### 🆘 문제 신고
- **이슈 트래커**: GitLab Issues
- **문서**: 프로젝트 README.md
- **로그**: 각 서비스별 로그 파일 확인

### 📚 추가 자료
- **Spring Boot 공식 문서**: https://spring.io/projects/spring-boot
- **React 공식 문서**: https://react.dev/
- **Apache Spark 공식 문서**: https://spark.apache.org/docs/
- **Docker 공식 문서**: https://docs.docker.com/

### 🔄 업데이트 및 유지보수
- **정기 업데이트**: 매월 첫째 주
- **보안 패치**: 즉시 적용
- **성능 모니터링**: 지속적 모니터링

---

**📝 문서 버전**: 1.0.0  
**📅 최종 업데이트**: 2025년 1월  
**👥 작성자**: S13P21A301 팀
