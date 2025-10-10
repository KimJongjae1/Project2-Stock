#!/usr/bin/env python3
"""
개선된 배치 처리 테스트
동시 요청이 하나의 배치로 처리되는지 확인합니다.
"""

import time
import threading

BASE_URL = "http://localhost:8000"

def test_optimized_batching():
    """개선된 배치 처리 테스트"""
    print("🚀 개선된 배치 처리 테스트 시작")
    print("=" * 60)
    
    # 기대값: 3개 동시 요청 → 1개 배치 → 1번 토큰 사용
    print("📋 테스트 목표:")
    print("  • 3개 기업 동시 요청")
    print("  • 1개 배치로 처리")
    print("  • 1번 토큰 사용 (개별 처리 시 3번)")
    print()
    
    # 1. 서버 상태 확인
    try:
        import requests
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행되지 않음. docker compose up 실행 필요")
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
        print(f"  • 총 요청: {initial_stats['total_requests']}")
        print(f"  • 총 배치: {initial_stats['total_batches']}")
        print(f"  • 토큰 절약: {initial_stats['total_tokens_saved']}")
        print()
    except Exception as e:
        print(f"⚠️ 초기 통계 확인 실패: {e}")
        initial_stats = {}
    
    # 3. 동시 요청 테스트
    print("🔄 3개 기업 동시 요청 시작...")
    
    companies = ["삼성전자", "LG전자", "SK하이닉스"]
    task_ids = []
    
    def submit_request(company):
        """개별 요청 제출 함수"""
        try:
            payload = {
                "company_name": company,
                "start_date": "20200901",
                "end_date": "20200903"
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
    
    # 동시 요청 실행 (매우 빠른 연속 요청)
    start_time = time.time()
    threads = []
    
    for company in companies:
        thread = threading.Thread(target=lambda c=company: task_ids.append(submit_request(c)))
        threads.append(thread)
        thread.start()
        # 거의 동시에 실행 (10ms 간격)
        time.sleep(0.01)
    
    # 모든 스레드 완료 대기
    for thread in threads:
        thread.join()
    
    # None 값 제거
    task_ids = [tid for tid in task_ids if tid is not None]
    submit_time = time.time() - start_time
    
    print(f"📤 요청 제출 완료: {len(task_ids)}개 작업, 소요 시간: {submit_time:.3f}초")
    print()
    
    if len(task_ids) != 3:
        print(f"❌ 예상과 다른 작업 수: {len(task_ids)} (예상: 3)")
        return
    
    # 4. 결과 대기
    print("⏳ 배치 처리 결과 대기 중...")
    completed_results = []
    
    start_wait = time.time()
    timeout = 15  # 15초 타임아웃
    
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
                            keyword_count = len(result["data"]["filtered_keywords"])
                            print(f"  ✅ {company}: {keyword_count}개 키워드 추출 완료")
                        else:
                            print(f"  ❌ {company}: {result.get('error', '처리 실패')}")
            except Exception as e:
                print(f"  ⚠️ {companies[i]} 결과 확인 실패: {e}")
        
        if len(completed_results) < len(task_ids):
            time.sleep(0.5)
    
    processing_time = time.time() - start_wait
    print(f"⏱️ 배치 처리 완료: {processing_time:.3f}초")
    print()
    
    # 5. 최종 통계 확인
    try:
        response = requests.get(f"{BASE_URL}/batch/stats")
        final_stats = response.json()
        
        print("📊 최종 통계:")
        print(f"  • 총 요청: {final_stats['total_requests']}")
        print(f"  • 총 배치: {final_stats['total_batches']}")
        print(f"  • 토큰 절약: {final_stats['total_tokens_saved']}")
        print(f"  • 평균 배치 크기: {final_stats['average_batch_size']:.1f}")
        print(f"  • 대기 중 요청: {final_stats['pending_requests']}")
        print()
        
        # 증가량 계산
        if initial_stats:
            new_requests = final_stats['total_requests'] - initial_stats.get('total_requests', 0)
            new_batches = final_stats['total_batches'] - initial_stats.get('total_batches', 0)
            new_tokens_saved = final_stats['total_tokens_saved'] - initial_stats.get('total_tokens_saved', 0)
            
            print("📈 이번 테스트 증가량:")
            print(f"  • 새 요청: +{new_requests}")
            print(f"  • 새 배치: +{new_batches}")
            print(f"  • 추가 토큰 절약: +{new_tokens_saved}")
            print()
            
            # 성공 여부 판단
            if new_requests == 3 and new_batches == 1:
                print("🎉 배치 처리 성공!")
                print("  ✅ 3개 요청이 1개 배치로 처리됨")
                print(f"  ✅ 토큰 절약: {new_tokens_saved} (예상: 1000)")
                efficiency = ((3 - new_batches) / 3) * 100
                print(f"  ✅ 효율성: {efficiency:.1f}% 토큰 절약")
            else:
                print("⚠️ 배치 처리 부분 성공")
                print(f"  • 3개 요청 → {new_batches}개 배치")
                if new_batches > 1:
                    print("  • 개선 필요: 모든 요청이 하나의 배치로 처리되지 않음")
                else:
                    print("  • 예상대로 작동함")
        
    except Exception as e:
        print(f"❌ 최종 통계 확인 실패: {e}")
    
    print("=" * 60)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_optimized_batching()
