# Grafana를 이용한 Spark Job 모니터링 가이드

## 🚀 빠른 시작

### 1. 모니터링 스택 시작
```bash
# 전체 모니터링 스택 시작
docker-compose up -d prometheus grafana spark-metrics-exporter node-exporter

# 또는 전체 스택 시작
docker-compose up -d
```

### 2. Grafana 접속
- **URL**: http://localhost:3000
- **사용자명**: admin
- **비밀번호**: admin123

### 3. Spark Job 실행
```bash
# Spark Job 실행
docker exec -it spark-client python3 /opt/spark/jobs/spark_pageRank_docker.py
```

## 📊 대시보드 구성

### 기본 대시보드
Grafana에 접속하면 자동으로 "Spark Job Monitoring" 대시보드가 로드됩니다.

### 포함된 메트릭
1. **Job 상태별 개수**: 성공/실패/실행중인 Job 수
2. **Stage 상태별 개수**: 완료/실패/실행중인 Stage 수
3. **Executor 수**: 활성 Executor 개수
4. **메모리 사용량**: Executor별 메모리 사용량
5. **Job 진행률**: 각 Job의 완료 퍼센트
6. **Job 실행 시간**: Job별 실행 시간

## 🔧 고급 설정

### 1. 커스텀 대시보드 생성
```bash
# Grafana에서 새 대시보드 생성
# + → Dashboard → Add Panel
```

### 2. 추가 메트릭 쿼리
```promql
# 실행중인 Job 수
spark_jobs_total{status="running"}

# 완료된 Job 수
spark_jobs_total{status="succeeded"}

# 실패한 Job 수
spark_jobs_total{status="failed"}

# Executor 메모리 사용률
spark_executor_memory_used_bytes / spark_executor_memory_max_bytes * 100

# Job 진행률
spark_job_progress_percent

# Stage 진행률
spark_stage_progress_percent
```

### 3. 알림 설정
```bash
# Grafana에서 알림 규칙 생성
# Alerting → Alert Rules → New Rule
```

## 📈 시각화 옵션

### 1. 시간 시리즈 그래프
- Job/Stage 상태 변화 추이
- 메모리 사용량 변화
- 진행률 변화

### 2. 통계 패널
- 현재 Executor 수
- 완료된 Job 수
- 실패한 Job 수

### 3. 게이지 차트
- Job 진행률
- 메모리 사용률
- CPU 사용률

### 4. 히트맵
- 시간대별 Job 실행 패턴
- Executor별 작업 분포

## 🔍 문제 해결

### 1. 메트릭이 표시되지 않는 경우
```bash
# 메트릭 수집기 상태 확인
docker logs spark-metrics-exporter

# Prometheus 타겟 상태 확인
# http://localhost:9091/targets
```

### 2. Grafana 연결 문제
```bash
# Grafana 로그 확인
docker logs grafana

# Prometheus 데이터소스 설정 확인
# Grafana → Configuration → Data Sources
```

### 3. 메트릭 수집 지연
```bash
# 수집 간격 조정
docker exec -it spark-metrics-exporter python3 /opt/spark/monitoring/spark_metrics_exporter.py --interval 10
```

## 🎯 모니터링 전략

### 1. 실시간 모니터링
- Job 실행 상태 실시간 추적
- 리소스 사용량 모니터링
- 성능 지표 추적

### 2. 트렌드 분석
- 장기간 성능 변화 추이
- 리소스 사용 패턴 분석
- 병목 지점 식별

### 3. 알림 설정
- Job 실패 시 즉시 알림
- 리소스 사용량 임계값 초과 시 알림
- 성능 저하 감지 시 알림

## 📱 모바일 접근

Grafana는 모바일 친화적 인터페이스를 제공합니다:
- 반응형 디자인
- 터치 최적화
- 모바일 대시보드

## 🔐 보안 설정

### 1. 인증 설정
```bash
# 환경변수로 관리자 계정 설정
GF_SECURITY_ADMIN_USER=your_admin
GF_SECURITY_ADMIN_PASSWORD=your_password
```

### 2. HTTPS 설정
```bash
# SSL 인증서 설정
GF_SERVER_CERT_FILE=/path/to/cert.pem
GF_SERVER_CERT_KEY=/path/to/key.pem
```

## 📊 성능 최적화

### 1. 데이터 보존 정책
```yaml
# prometheus.yml에서 설정
--storage.tsdb.retention.time=30d
```

### 2. 샘플링 간격
```yaml
# 더 자주 수집 (5초)
scrape_interval: 5s
```

### 3. 대시보드 최적화
- 불필요한 패널 제거
- 쿼리 최적화
- 캐싱 활용

## 🚀 확장 가능성

### 1. 추가 메트릭
- 커스텀 비즈니스 메트릭
- 애플리케이션별 성능 지표
- 사용자 정의 KPI

### 2. 통합 모니터링
- 다른 시스템과 연동
- 중앙 집중식 모니터링
- 통합 알림 시스템

### 3. 자동화
- 자동 스케일링
- 자동 복구
- 예측적 모니터링
