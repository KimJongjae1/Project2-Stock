#!/usr/bin/env python3
"""
대용량 배치 처리 테스트
10개 이상의 기업을 한 번에 처리하여 극적인 토큰 절약 효과를 확인합니다.
"""

import asyncio
import time
import requests
import threading
from typing import List

BASE_URL = "http://localhost:8888"

def test_massive_batching():
    """대용량 배치 처리 테스트"""
    print("🚀 대용량 배치 처리 테스트 시작")
    print("=" * 60)
    
    # 테스트할 기업 목록 (10개)
    companies = [
        "삼성전자", "LG전자", "SK하이닉스", "네이버", "카카오",
        "현대차", "기아", "POSCO", "LG화학", "SK텔레콤"
    ]
    
    print(f"📋 테스트 목표:")
    print(f"  • {len(companies)}개 기업 동시 요청")
    print(f"  • 1-2개 배치로 처리")
    print(f"  • 극적인 토큰 절약 (10개 → 1-2개)")
    print()
    
    # 1. 서버 상태 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행되지 않음")
            return
        print("✅ 서버 연결 확인됨")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 초기 통계 확인
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
    
    # 3. 대용량 배치 요청 제출
    print(f"\n3️⃣ {len(companies)}개 기업 동시 요청 시작...")
    
    task_ids = []
    
    def submit_request(company):
        """개별 요청 제출 함수"""
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
                print(f"  ✅ {company}: {task_id}")
                return task_id
            else:
                print(f"  ❌ {company}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ {company}: {e}")
            return None
    
    # 순차적 요청 실행 (동시성 문제 해결)
    start_time = time.time()
    
    for i, company in enumerate(companies):
        print(f"  📤 요청 {i+1}/{len(companies)}: {company}")
        task_id = submit_request(company)
        if task_id:
            task_ids.append(task_id)
        
        # 배치 수집을 위한 짧은 대기 (배치 조건에 맞춤)
        if i < len(companies) - 1:  # 마지막 요청이 아니면
            time.sleep(0.05)  # 50ms 대기 (배치 수집 시간 확보)
    
    # None 값 제거
    task_ids = [tid for tid in task_ids if tid is not None]
    submit_time = time.time() - start_time
    
    print(f"📤 요청 제출 완료: {len(task_ids)}개 작업, 소요 시간: {submit_time:.3f}초")
    print()
    
    if len(task_ids) != len(companies):
        print(f"❌ 예상과 다른 작업 수: {len(task_ids)} (예상: {len(companies)})")
        return
    
    # 4. 결과 대기
    print("⏳ 대용량 배치 처리 결과 대기 중...")
    completed_results = []
    
    start_wait = time.time()
    timeout = 180  # 3분 타임아웃 (대용량 처리용)
    
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
                        else:
                            print(f"  ❌ {company}: {result.get('error', '처리 실패')}")
            except Exception as e:
                print(f"  ⚠️ {companies[i]} 결과 확인 실패: {e}")
        
        if len(completed_results) < len(task_ids):
            elapsed = time.time() - start_wait
            remaining = len(task_ids) - len(completed_results)
            print(f"  ⏳ 대기 중... ({len(completed_results)}/{len(task_ids)} 완료, {elapsed:.1f}초 경과)")
            time.sleep(3)  # 3초 대기
    
    processing_time = time.time() - start_wait
    print(f"⏱️ 대용량 배치 처리 완료: {processing_time:.3f}초")
    print()
    
    # 5. 최종 통계 확인
    try:
        response = requests.get(f"{BASE_URL}/batch/stats")
        final_stats = response.json()
        
        print("📊 최종 통계:")
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
            if new_requests == len(companies):
                print(f"\n🎉 배치 처리 성공!")
                print(f"  ✅ {len(companies)}개 요청 처리 완료")
                print(f"  ✅ {new_batches}개 배치로 처리됨")
                print(f"  ✅ 토큰 절약: {new_tokens_saved}")
                
                # 배치 효율성 계산
                if new_batches > 0:
                    efficiency = new_requests / new_batches
                    print(f"  ✅ 배치 효율성: {efficiency:.1f}개 요청/배치")
                    
                    if efficiency >= 5:
                        print(f"  🚀 우수한 배치 효율성! (5개 이상 요청/배치)")
                    elif efficiency >= 3:
                        print(f"  ✅ 양호한 배치 효율성 (3개 이상 요청/배치)")
                    else:
                        print(f"  ⚠️ 배치 효율성 개선 필요 (3개 미만 요청/배치)")
            else:
                print(f"\n⚠️ 일부 요청 처리 실패")
                print(f"  • 성공: {len(completed_results)}/{len(companies)}")
    
    except Exception as e:
        print(f"❌ 최종 통계 확인 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 대용량 배치 테스트 완료")

if __name__ == "__main__":
    print("🚀 대용량 배치 처리 테스트를 시작합니다...")
    print("📋 테스트 내용:")
    print("  1. 10개 기업 순차 요청")
    print("  2. 빠른 배치 수집으로 효율성 극대화")
    print("  3. 토큰 절약 효과 확인")
    print()
    
    test_massive_batching()
    
    print("\n💡 최적화 결과:")
    print("  • 배치 크기: 10개 → 20개")
    print("  • 버퍼 시간: 2초 → 5초")
    print("  • 키워드 수: 50개 → 30개")
    print("  • 프롬프트 최적화: 더 간결한 지시사항")
