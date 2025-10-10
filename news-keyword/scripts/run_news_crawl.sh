#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# 스크립트 절대 경로 기준으로 프로젝트 루트 계산
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NEWS_CRAWL_DIR="${PROJECT_ROOT}/news_crawl"

# 모니터링 설정
PUSHGATEWAY_ADDR="${PUSHGATEWAY_ADDR:-http://localhost:9092}"
JOB_NAME="news_crawl"
INSTANCE="${INSTANCE:-$(hostname)}"

cd "${NEWS_CRAWL_DIR}" || exit 1

# docker compose 명령(v1/v2 호환)
if command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  DC="docker compose"
fi

# 혹시 떠 있는 동일 스택이 있으면 종료 (선택)
$DC down --remove-orphans || true

# 이미지 업데이트(선택)
$DC pull || true

# 시작 시간 기록 및 메트릭 푸시
start_ts=$(date +%s)
echo "[DEBUG] Pushing start metrics to ${PUSHGATEWAY_ADDR}"
cat <<EOF | curl -v --data-binary @- "${PUSHGATEWAY_ADDR}/metrics/job/${JOB_NAME}/instance/${INSTANCE}"
batch_last_start_timestamp_seconds ${start_ts}
EOF

# docker-compose.yml 기준 서비스명: bigkinds-automation (container_name은 bigkinds-news-crawler)
# 배치 1회 실행 후 종료
$DC run --rm bigkinds-automation
status=$?

# 종료 시간 및 결과 메트릭 푸시
end_ts=$(date +%s)
duration=$((end_ts - start_ts))
if [ $status -eq 0 ]; then
  success=1
else
  success=0
fi

echo "[DEBUG] Pushing end metrics to ${PUSHGATEWAY_ADDR}"
cat <<EOF | curl -v --data-binary @- "${PUSHGATEWAY_ADDR}/metrics/job/${JOB_NAME}/instance/${INSTANCE}"
batch_last_end_timestamp_seconds ${end_ts}
batch_last_run_duration_seconds ${duration}
batch_last_run_success ${success}
batch_runs_total 1
EOF

# 실행 후 downloads 디렉토리 정리
if [[ -d "${NEWS_CRAWL_DIR}/downloads" ]]; then
  # 내부 파일/폴더만 삭제하고 디렉토리는 유지
  rm -rf "${NEWS_CRAWL_DIR}/downloads"/* || true
fi

exit $status