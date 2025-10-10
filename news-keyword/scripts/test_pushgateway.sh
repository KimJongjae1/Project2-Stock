#!/usr/bin/env bash

# Pushgateway 테스트 스크립트
PUSHGATEWAY_ADDR="http://localhost:9092"
JOB_NAME="test_job"
INSTANCE="test_instance"

echo "=== Pushgateway 테스트 ==="
echo "주소: ${PUSHGATEWAY_ADDR}"

# 테스트 메트릭 푸시
echo "1. 테스트 메트릭 푸시 중..."
cat <<EOF | curl -v --data-binary @- "${PUSHGATEWAY_ADDR}/metrics/job/${JOB_NAME}/instance/${INSTANCE}"
test_metric 123
test_timestamp $(date +%s)
EOF

echo ""
echo "2. Pushgateway 메트릭 확인..."
curl -s "${PUSHGATEWAY_ADDR}/metrics" | grep test_

echo ""
echo "3. 완료!"

