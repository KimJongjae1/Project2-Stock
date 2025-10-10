#!/usr/bin/env python3
"""
통합된 배치 시스템 테스트
S3에서 CSV 파일을 읽어 키워드를 추출하고 배치 처리하는 전체 시스템을 테스트합니다.
"""

import asyncio
import time
import requests
import json
from typing import List, Dict

BASE_URL = "http://localhost:8888"

async def test_integrated_system():
    """통합된 시스템 테스트"""
    print("🚀 통합된 배치 시스템 테스트 시작")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행되지 않음. main.py를 실행해주세요.")
            return
        print("✅ 서버 연결 확인됨")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 배치 통계 초기 확인
    print("\n2️⃣ 초기 배치 통계 확인...")
    try:
        response = requests.get(f"{BASE_URL}/batch/stats")
        initial_stats = response.json()
        print(f"📊 초기 통계:")
        print(f"  • 총 요청: {initial_stats['stats']['total_requests']}")
        print(f"  • 총 배치: {initial_stats['stats']['total_batches']}")
        print(f"  • 토큰 절약: {initial_stats['stats']['total_tokens_saved']}")
    except Exception as e:
        print(f"⚠️ 초기 통계 확인 실패: {e}")
        initial_stats = {}
    
    # 3. 배치 요청 제출
    print("\n3️⃣ 배치 요청 제출...")
    companies = ["삼성전자", "LG전자", "SK하이닉스"]
    task_ids = []
    
    for company in companies:
        try:
            payload = {
                "company_name": company,
                "start_date": "20200901",
                "end_date": "20200903",
                "top_keywords": 10
            }
            
            response = requests.post(
                f"{BASE_URL}/extract-keywords-batch",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result["task_id"]
                task_ids.append(task_id)
                print(f"  ✅ {company}: {task_id}")
            else:
                print(f"  ❌ {company}: HTTP {response.status_code}")
                print(f"      응답: {response.text}")
                
        except Exception as e:
            print(f"  ❌ {company}: {e}")
    
    if not task_ids:
        print("❌ 모든 요청이 실패했습니다.")
        return
    
    print(f"\n📤 총 {len(task_ids)}개 작업 제출 완료")
    
    # 4. 결과 대기 및 확인
    print("\n4️⃣ 배치 처리 결과 대기...")
    completed_results = []
    timeout = 30  # 30초 타임아웃
    start_wait = time.time()
    
    while len(completed_results) < len(task_ids) and (time.time() - start_wait) < timeout:
        for i, task_id in enumerate(task_ids):
            if i < len(completed_results):
                continue  # 이미 완료된 작업
                
            try:
                response = requests.get(f"{BASE_URL}/task/{task_id}/result")
                if response.status_code == 200:
                    result = response.json()
                    
                    if result["status"] in ["completed", "failed"]:
                        completed_results.append(result)
                        company = companies[i]
                        
                        if result["status"] == "completed":
                            keyword_count = len(result["data"]["keywords"])
                            print(f"  ✅ {company}: {keyword_count}개 키워드 추출 완료")
                            print(f"      원본: {result['data']['original_keyword_count']}개 → 필터링: {result['data']['filtered_keyword_count']}개")
                        else:
                            print(f"  ❌ {company}: {result.get('error', '처리 실패')}")
            except Exception as e:
                print(f"  ⚠️ {companies[i]} 결과 확인 실패: {e}")
        
        if len(completed_results) < len(task_ids):
            await asyncio.sleep(1)  # 1초 대기
    
    processing_time = time.time() - start_wait
    print(f"\n⏱️ 배치 처리 완료: {processing_time:.3f}초")
    
    # 5. 최종 통계 확인
    print("\n5️⃣ 최종 배치 통계 확인...")
    try:
        response = requests.get(f"{BASE_URL}/batch/stats")
        final_stats = response.json()
        
        print(f"📊 최종 통계:")
        print(f"  • 총 요청: {final_stats['stats']['total_requests']}")
        print(f"  • 총 배치: {final_stats['stats']['total_batches']}")
        print(f"  • 토큰 절약: {final_stats['stats']['total_tokens_saved']}")
        print(f"  • 평균 배치 크기: {final_stats['stats']['average_batch_size']:.1f}")
        print(f"  • 대기 중 요청: {final_stats['stats']['pending_requests']}")
        
        # 증가량 계산
        if initial_stats:
            new_requests = final_stats['stats']['total_requests'] - initial_stats['stats'].get('total_requests', 0)
            new_batches = final_stats['stats']['total_batches'] - initial_stats['stats'].get('total_batches', 0)
            new_tokens_saved = final_stats['stats']['total_tokens_saved'] - initial_stats['stats'].get('total_tokens_saved', 0)
            
            print(f"\n📈 이번 테스트 증가량:")
            print(f"  • 새 요청: +{new_requests}")
            print(f"  • 새 배치: +{new_batches}")
            print(f"  • 추가 토큰 절약: +{new_tokens_saved}")
            
            # 성공 여부 판단
            if new_requests == len(task_ids) and new_batches >= 1:
                print(f"\n🎉 배치 처리 성공!")
                print(f"  ✅ {len(task_ids)}개 요청이 {new_batches}개 배치로 처리됨")
                print(f"  ✅ 토큰 절약: {new_tokens_saved}")
                if new_batches == 1:
                    efficiency = ((len(task_ids) - new_batches) / len(task_ids)) * 100
                    print(f"  ✅ 효율성: {efficiency:.1f}% 토큰 절약")
            else:
                print(f"\n⚠️ 배치 처리 부분 성공")
                print(f"  • {len(task_ids)}개 요청 → {new_batches}개 배치")
    
    except Exception as e:
        print(f"❌ 최종 통계 확인 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 통합 시스템 테스트 완료")

def test_individual_extraction():
    """개별 키워드 추출 테스트 (비교용)"""
    print("\n🔍 개별 키워드 추출 테스트 (비교용)")
    print("-" * 40)
    
    try:
        payload = {
            "company_name": "삼성전자",
            "start_date": "20200901",
            "end_date": "20200903",
            "top_keywords": 10,
            "use_ai_filter": True
        }
        
        response = requests.post(
            f"{BASE_URL}/extract-keywords",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 개별 추출 성공:")
            print(f"  • 회사: {result['company_name']}")
            print(f"  • 총 뉴스: {result['total_news_count']}개")
            print(f"  • 키워드: {len(result['keywords'])}개")
            print(f"  • AI 필터링: {result['ai_filtered']}")
            if result['ai_filtered']:
                print(f"  • 원본 → 필터링: {result['original_keyword_count']}개 → {result['filtered_keyword_count']}개")
        else:
            print(f"❌ 개별 추출 실패: HTTP {response.status_code}")
            print(f"    응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 개별 추출 테스트 실패: {e}")

if __name__ == "__main__":
    print("🚀 통합된 배치 시스템 테스트를 시작합니다...")
    print("📋 테스트 내용:")
    print("  1. 서버 상태 확인")
    print("  2. 배치 통계 확인")
    print("  3. 여러 기업 동시 배치 요청")
    print("  4. 배치 처리 결과 대기")
    print("  5. 토큰 절약 효과 확인")
    print("  6. 개별 추출과 비교")
    print()
    
    # 통합 시스템 테스트
    asyncio.run(test_integrated_system())
    
    # 개별 추출 테스트 (비교용)
    test_individual_extraction()
    
    print("\n💡 사용법:")
    print("  1. 환경 변수 설정 (.env 파일 생성):")
    print("     - OPENAI_API_KEY: OpenAI API 키")
    print("     - AWS_ACCESS_KEY_ID: AWS 액세스 키")
    print("     - AWS_SECRET_ACCESS_KEY: AWS 시크릿 키")
    print("     - AWS_SESSION_TOKEN: AWS 세션 토큰 (선택사항)")
    print("  2. main.py 실행: python main.py")
    print("  3. 이 테스트 실행: python integration_test.py")
