#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
"""

import uvicorn
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("뉴스 키워드 추출 FastAPI 서버를 시작합니다...")
    print("API 문서: http://localhost:8888/docs")
    print("헬스체크: http://localhost:8888/health")
    print("Ctrl+C를 눌러 서버를 종료할 수 있습니다.")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,  # 개발 모드에서 파일 변경 시 자동 재시작
        log_level="info"
    )



