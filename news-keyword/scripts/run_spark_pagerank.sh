#!/usr/bin/env bash

# Spark PageRank 잡 실행 스크립트
# 사용: bash scripts/run_spark_pagerank.sh
# 환경변수로 조정 가능:
#   CONTAINER_NAME (기본: spark-client)
#   JOB_PATH (기본: /opt/spark/jobs/spark_pageRank_docker.py)
#   RUN_TIMES (기본: 1)  # 필요 시 같은 잡을 연속 실행

set -Eeuo pipefail
IFS=$'\n\t'

CONTAINER_NAME="${CONTAINER_NAME:-spark-client}"
JOB_PATH="${JOB_PATH:-//opt/spark/jobs/spark_pageRank_docker.py}"
RUN_TIMES=${RUN_TIMES:-1}

# docker cli 확인
if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] docker 명령을 찾을 수 없습니다." >&2
  exit 1
fi

# 컨테이너가 존재하는지 확인
if ! docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  echo "[ERROR] 컨테이너가 존재하지 않습니다: ${CONTAINER_NAME}" >&2
  docker ps -a
  exit 1
fi

# 컨테이너 실행 상태 확인 (실행 중이 아니면 시작 시도는 하지 않음 — docker-compose에서 관리 권장)
if ! docker ps --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  echo "[ERROR] 컨테이너가 실행 중이 아닙니다: ${CONTAINER_NAME}" >&2
  exit 1
fi

echo "[INFO] 컨테이너: ${CONTAINER_NAME}"
echo "[INFO] 잡 경로: ${JOB_PATH}"
echo "[INFO] 실행 횟수: ${RUN_TIMES}"

for ((i=1; i<=RUN_TIMES; i++)); do
  echo "[INFO] (${i}/${RUN_TIMES}) docker exec 실행"
  docker exec -it "${CONTAINER_NAME}" python3 "${JOB_PATH}"
done

echo "[INFO] 완료"

exit 0


