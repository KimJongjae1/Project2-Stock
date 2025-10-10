# Spark Job 모니터링 가이드

이 디렉토리는 Spark Job의 성공/실패를 Grafana로 모니터링하는 도구들을 포함합니다.

## 📋 모니터링 방법들

### 1. Spark Web UI (기본)
- **Master Web UI**: http://localhost:8080
- **Worker Web UI**: http://localhost:8081, http://localhost:8082
- 실시간으로 Job 상태, Stage 진행률, 리소스 사용량 확인 가능

### 2. Grafana 모니터링 (권장)
- **Grafana URL**: http://localhost:3000
- **사용자명**: admin
- **비밀번호**: admin123
- 실시간 대시보드로 Job 상태, 진행률, 리소스 사용량 시각화

## 🔧 환경 설정

### Grafana 모니터링 스택 시작
```bash
# 모니터링 스택 시작
docker-compose up -d prometheus grafana spark-metrics-exporter node-exporter

# 또는 전체 스택 시작
docker-compose up -d
```

## 📊 모니터링 정보

### Job 상태
- **RUNNING**: Job이 실행 중
- **COMPLETED**: Job이 성공적으로 완료
- **FAILED**: Job이 실패
- **UNKNOWN**: 상태를 확인할 수 없음

### Stage 상태
- **ACTIVE**: Stage가 실행 중
- **COMPLETE**: Stage가 완료
- **FAILED**: Stage가 실패

## 🚀 사용 예시

### 1. Grafana 모니터링 시작
```bash
# 1. 모니터링 스택 시작
docker-compose up -d prometheus grafana spark-metrics-exporter node-exporter

# 2. Grafana 접속
# URL: http://localhost:3000
# 사용자명: admin, 비밀번호: admin123
```

### 2. Spark Job 실행 및 모니터링
```bash
# 1. Spark Job 실행
docker exec -it spark-client python3 /opt/spark/jobs/spark_pageRank_docker.py

# 2. Grafana에서 실시간 모니터링
# "Spark Job Monitoring" 대시보드에서 진행 상황 확인
```

### 3. 로그 확인
```bash
# 메트릭 수집기 로그 확인
docker logs spark-metrics-exporter -f

# Prometheus 로그 확인
docker logs prometheus -f

# Grafana 로그 확인
docker logs grafana -f
```

## 📈 성능 지표

Grafana 대시보드에서 다음 지표들을 시각화합니다:
- **Job 상태별 개수**: 성공/실패/실행중인 Job 수
- **Stage 진행률**: 각 Stage의 완료 퍼센트
- **Executor 메모리**: 메모리 사용량 및 한계
- **Job 진행률**: 실시간 진행 상황
- **실행 시간**: Job별 소요 시간
- **시스템 리소스**: CPU, 메모리, 디스크 사용량

## 🔔 알림 설정

### Grafana 알림
- Job 실패 시 자동 알림
- 리소스 사용량 임계값 초과 시 알림
- 성능 저하 감지 시 알림

### Prometheus 메트릭
- 모든 상태 변화가 Prometheus에 기록
- 실시간 메트릭 수집

## 🛠️ 문제 해결

### 일반적인 문제들

1. **Spark Master 연결 실패**
   ```bash
   # Spark 클러스터 상태 확인
   docker-compose ps
   
   # Master 로그 확인
   docker logs spark-master
   ```

2. **Grafana 접속 불가**
   ```bash
   # Grafana 컨테이너 상태 확인
   docker logs grafana
   
   # 포트 확인
   netstat -tlnp | grep 3000
   ```

3. **메트릭이 표시되지 않음**
   ```bash
   # 메트릭 수집기 상태 확인
   docker logs spark-metrics-exporter
   
   # Prometheus 타겟 상태 확인
   # http://localhost:9091/targets
   ```

## 📝 로그 파일

- `monitoring/`: Grafana 모니터링 설정 및 대시보드
- `logs/`: Spark 클러스터 로그
- Docker 로그: 각 컨테이너별 로그

## 🔄 자동화

### Docker Compose 자동 시작
```bash
# 시스템 부팅 시 자동 시작
docker-compose up -d
```

### Grafana 알림 규칙
- Grafana에서 알림 규칙 설정
- 이메일, 슬랙 등 다양한 알림 채널 지원
