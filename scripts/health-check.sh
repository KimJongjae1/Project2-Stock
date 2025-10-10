#!/bin/bash

# 헬스체크 스크립트
set -e

echo "🏥 서비스 헬스체크 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 헬스체크 함수
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "🔍 $service_name 체크 중... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✅ 정상${NC}"
            return 0
        else
            echo -e "${RED}❌ 오류 (HTTP $response)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 연결 실패${NC}"
        return 1
    fi
}

# 서비스별 헬스체크
echo "📊 서비스 상태 확인:"
echo "===================="

# 프론트엔드 체크
check_service "프론트엔드 (Nginx)" "http://localhost/health"

# 백엔드 체크
check_service "백엔드 (Spring Boot)" "http://localhost:8080/actuator/health"

# Jenkins 체크
check_service "Jenkins" "http://localhost:8081/login"

# MySQL 체크
echo -n "🔍 MySQL 체크 중... "
if docker exec stock_mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo -e "${GREEN}✅ 정상${NC}"
else
    echo -e "${RED}❌ 연결 실패${NC}"
fi

echo ""
echo "📋 컨테이너 상태:"
echo "=================="
docker-compose ps

echo ""
echo "📊 리소스 사용량:"
echo "=================="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

