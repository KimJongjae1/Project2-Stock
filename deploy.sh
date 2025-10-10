#!/bin/bash

# 배포 스크립트
set -e

echo "🚀 Stock Trading System 배포 시작..."

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 환경 변수 로드 완료"
else
    echo "❌ .env 파일을 찾을 수 없습니다"
    exit 1
fi

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다"
    exit 1
fi

echo "✅ Docker 환경 확인 완료"

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down --remove-orphans || true

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build --no-cache

# 서비스 시작
echo "🚀 서비스 시작 중..."
docker-compose up -d

# 헬스체크
echo "🏥 헬스체크 실행 중..."
sleep 30

# 백엔드 헬스체크
echo "백엔드 헬스체크..."
for i in {1..30}; do
    if curl -f http://localhost:8080/actuator/health > /dev/null 2>&1; then
        echo "✅ 백엔드 헬스체크 성공"
        break
    fi
    echo "⏳ 백엔드 헬스체크 대기 중... ($i/30)"
    sleep 10
done

# 프론트엔드 헬스체크
echo "프론트엔드 헬스체크..."
for i in {1..30}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ 프론트엔드 헬스체크 성공"
        break
    fi
    echo "⏳ 프론트엔드 헬스체크 대기 중... ($i/30)"
    sleep 10
done

# Jenkins 헬스체크
echo "Jenkins 헬스체크..."
for i in {1..30}; do
    if curl -f http://localhost:8081/login > /dev/null 2>&1; then
        echo "✅ Jenkins 헬스체크 성공"
        break
    fi
    echo "⏳ Jenkins 헬스체크 대기 중... ($i/30)"
    sleep 10
done

echo "🎉 배포 완료!"
echo ""
echo "📋 서비스 접속 정보:"
echo "  - 프론트엔드: http://localhost"
echo "  - 백엔드 API: http://localhost:8080"
echo "  - Jenkins: http://localhost:8081"
echo "  - MySQL: localhost:3306"
echo ""
echo "🔑 Jenkins 초기 비밀번호:"
docker exec stock_jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Jenkins가 아직 시작 중입니다. 잠시 후 다시 확인해주세요."

