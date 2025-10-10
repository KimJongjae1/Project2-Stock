#!/usr/bin/env python3
"""
SQLite 캐싱 기능 테스트 스크립트
"""

import requests
import time
import json

BASE_URL = "http://localhost:8888"

def test_cache_functionality():
    """캐싱 기능 테스트"""
    print("🧪 SQLite 캐싱 기능 테스트 시작")
    print("=" * 50)
    
    # 테스트 요청 데이터
    test_request = {
        "company_name": "삼성전자",
        "start_date": "20240101",
        "end_date": "20240103",
        "top_keywords": 10,
        "use_ai_filter": True
    }
    
    print(f"📋 테스트 요청: {test_request['company_name']} ({test_request['start_date']}-{test_request['end_date']})")
    print()
    
    # 1. 첫 번째 요청 (캐시 미스 예상)
    print("1️⃣ 첫 번째 요청 (캐시 미스 예상)")
    start_time = time.time()
    
    try:
        response1 = requests.post(
            f"{BASE_URL}/extract-keywords/ticker",
            json=test_request,
            timeout=60
        )
        
        first_request_time = time.time() - start_time
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"   ✅ 첫 번째 요청 성공: {first_request_time:.3f}초")
            print(f"   📊 키워드 개수: {len(result1['keywords'])}개")
            print(f"   📰 뉴스 개수: {result1['total_news_count']}개")
        else:
            print(f"   ❌ 첫 번째 요청 실패: {response1.status_code}")
            print(f"   오류: {response1.text}")
            return
            
    except Exception as e:
        print(f"   ❌ 첫 번째 요청 오류: {e}")
        return
    
    print()
    
    # 2. 두 번째 요청 (캐시 히트 예상)
    print("2️⃣ 두 번째 요청 (캐시 히트 예상)")
    start_time = time.time()
    
    try:
        response2 = requests.post(
            f"{BASE_URL}/extract-keywords/ticker",
            json=test_request,
            timeout=30
        )
        
        second_request_time = time.time() - start_time
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"   ✅ 두 번째 요청 성공: {second_request_time:.3f}초")
            print(f"   📊 키워드 개수: {len(result2['keywords'])}개")
            print(f"   📰 뉴스 개수: {result2['total_news_count']}개")
        else:
            print(f"   ❌ 두 번째 요청 실패: {response2.status_code}")
            print(f"   오류: {response2.text}")
            return
            
    except Exception as e:
        print(f"   ❌ 두 번째 요청 오류: {e}")
        return
    
    print()
    
    # 3. 성능 비교
    print("3️⃣ 성능 비교")
    speedup = first_request_time / second_request_time if second_request_time > 0 else 0
    print(f"   🐌 첫 번째 요청 시간: {first_request_time:.3f}초")
    print(f"   ⚡ 두 번째 요청 시간: {second_request_time:.3f}초")
    print(f"   🚀 속도 향상: {speedup:.1f}배")
    
    if speedup > 1.5:
        print("   ✅ 캐싱 효과 확인됨!")
    else:
        print("   ⚠️ 캐싱 효과가 미미함 (데이터가 작거나 네트워크 지연)")
    
    print()
    
    # 4. 캐시 통계 확인
    print("4️⃣ 캐시 통계 확인")
    try:
        stats_response = requests.get(f"{BASE_URL}/cache/stats", timeout=10)
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            cache_stats = stats.get("cache_stats", {})
            
            print(f"   📊 총 캐시 개수: {cache_stats.get('total_caches', 0)}개")
            print(f"   🔄 총 접근 횟수: {cache_stats.get('total_accesses', 0)}회")
            print(f"   📅 최근 7일 캐시: {cache_stats.get('recent_caches_7days', 0)}개")
            
            top_caches = cache_stats.get('top_accessed_caches', [])
            if top_caches:
                print("   🏆 가장 많이 접근된 캐시:")
                for i, cache in enumerate(top_caches[:3], 1):
                    print(f"      {i}. {cache['company']} ({cache['period']}) - {cache['access_count']}회")
        else:
            print(f"   ❌ 캐시 통계 조회 실패: {stats_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 캐시 통계 조회 오류: {e}")
    
    print()
    print("🎉 캐싱 기능 테스트 완료!")

def test_different_parameters():
    """다른 파라미터로 캐싱 테스트"""
    print("\n🔬 다른 파라미터로 캐싱 테스트")
    print("=" * 50)
    
    # 다른 기업으로 테스트
    test_requests = [
        {
            "company_name": "LG전자",
            "start_date": "20240101",
            "end_date": "20240103",
            "top_keywords": 5,
            "use_ai_filter": False
        },
        {
            "company_name": "삼성전자",
            "start_date": "20240101",
            "end_date": "20240103",
            "top_keywords": 15,  # 다른 키워드 개수
            "use_ai_filter": True
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"{i}️⃣ 테스트 요청: {request['company_name']} (키워드 {request['top_keywords']}개, AI필터: {request['use_ai_filter']})")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/extract-keywords/ticker",
                json=request,
                timeout=60
            )
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 요청 성공: {request_time:.3f}초")
                print(f"   📊 키워드 개수: {len(result['keywords'])}개")
            else:
                print(f"   ❌ 요청 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 요청 오류: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 SQLite 캐싱 기능 테스트 시작")
    print("서버가 실행 중인지 확인하세요: http://localhost:8888/health")
    print()
    
    try:
        # 서버 상태 확인
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 서버 연결 확인됨")
        else:
            print("❌ 서버 연결 실패")
            exit(1)
    except Exception as e:
        print(f"❌ 서버 연결 오류: {e}")
        print("서버를 먼저 실행해주세요: python main.py")
        exit(1)
    
    # 기본 캐싱 테스트
    test_cache_functionality()
    
    # 다른 파라미터 테스트
    test_different_parameters()
    
    print("\n📝 테스트 요약:")
    print("- 첫 번째 요청은 캐시 미스로 실제 처리가 필요합니다")
    print("- 두 번째 요청은 캐시 히트로 빠른 응답을 제공합니다")
    print("- 다른 파라미터는 별도의 캐시로 저장됩니다")
    print("- /cache/stats 엔드포인트로 캐시 통계를 확인할 수 있습니다")
