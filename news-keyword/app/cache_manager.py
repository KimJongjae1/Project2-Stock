#!/usr/bin/env python3
"""
SQLite 기반 키워드 추출 결과 캐시 매니저
시작일자, 끝일자, 기관명을 복합 키로 사용하여 결과를 캐시합니다.
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib

logger = logging.getLogger(__name__)

class CacheManager:
    """SQLite 기반 캐시 매니저"""
    
    def __init__(self, db_path: str = "keyword_cache.db"):
        """
        캐시 매니저 초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 키워드 캐시 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS keyword_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE NOT NULL,
                        company_name TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        top_keywords INTEGER NOT NULL,
                        use_ai_filter BOOLEAN NOT NULL,
                        result_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 1
                    )
                """)
                
                # 인덱스 생성 (조회 성능 향상)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_key ON keyword_cache(cache_key)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_company_date ON keyword_cache(company_name, start_date, end_date)
                """)
                
                conn.commit()
                logger.info(f"✅ 캐시 데이터베이스 초기화 완료: {self.db_path}")
                
        except Exception as e:
            logger.error(f"❌ 캐시 데이터베이스 초기화 실패: {e}")
            raise
    
    def _generate_cache_key(self, company_name: str, start_date: str, end_date: str, 
                           top_keywords: int, use_ai_filter: bool) -> str:
        """
        캐시 키 생성 (복합 키의 해시값)
        
        Args:
            company_name: 기업명
            start_date: 시작일자
            end_date: 끝일자
            top_keywords: 상위 키워드 개수
            use_ai_filter: AI 필터링 사용 여부
            
        Returns:
            캐시 키 (해시값)
        """
        key_string = f"{company_name}|{start_date}|{end_date}|{top_keywords}|{use_ai_filter}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get_cached_result(self, company_name: str, start_date: str, end_date: str, 
                         top_keywords: int, use_ai_filter: bool) -> Optional[Dict[str, Any]]:
        """
        캐시된 결과 조회
        
        Args:
            company_name: 기업명
            start_date: 시작일자
            end_date: 끝일자
            top_keywords: 상위 키워드 개수
            use_ai_filter: AI 필터링 사용 여부
            
        Returns:
            캐시된 결과 데이터 또는 None
        """
        try:
            cache_key = self._generate_cache_key(company_name, start_date, end_date, 
                                               top_keywords, use_ai_filter)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 캐시 조회
                cursor.execute("""
                    SELECT result_data, access_count FROM keyword_cache 
                    WHERE cache_key = ?
                """, (cache_key,))
                
                result = cursor.fetchone()
                
                if result:
                    # 접근 시간 및 횟수 업데이트
                    cursor.execute("""
                        UPDATE keyword_cache 
                        SET accessed_at = CURRENT_TIMESTAMP, access_count = access_count + 1
                        WHERE cache_key = ?
                    """, (cache_key,))
                    
                    conn.commit()
                    
                    # JSON 데이터 파싱
                    cached_data = json.loads(result[0])
                    access_count = result[1] + 1
                    
                    logger.info(f"🎯 캐시 히트: {company_name} ({start_date}-{end_date}) - 접근횟수: {access_count}")
                    return cached_data
                else:
                    logger.info(f"❌ 캐시 미스: {company_name} ({start_date}-{end_date})")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 캐시 조회 실패: {e}")
            return None
    
    def save_result(self, company_name: str, start_date: str, end_date: str, 
                   top_keywords: int, use_ai_filter: bool, result_data: Dict[str, Any]) -> bool:
        """
        결과를 캐시에 저장
        
        Args:
            company_name: 기업명
            start_date: 시작일자
            end_date: 끝일자
            top_keywords: 상위 키워드 개수
            use_ai_filter: AI 필터링 사용 여부
            result_data: 저장할 결과 데이터
            
        Returns:
            저장 성공 여부
        """
        try:
            cache_key = self._generate_cache_key(company_name, start_date, end_date, 
                                               top_keywords, use_ai_filter)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # JSON 데이터 직렬화
                json_data = json.dumps(result_data, ensure_ascii=False, indent=2)
                
                # 캐시 저장 (중복 시 무시)
                cursor.execute("""
                    INSERT OR IGNORE INTO keyword_cache 
                    (cache_key, company_name, start_date, end_date, top_keywords, 
                     use_ai_filter, result_data, created_at, accessed_at, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                """, (cache_key, company_name, start_date, end_date, top_keywords, 
                      use_ai_filter, json_data))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"💾 캐시 저장 완료: {company_name} ({start_date}-{end_date})")
                    return True
                else:
                    logger.info(f"⚠️ 캐시 이미 존재: {company_name} ({start_date}-{end_date})")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 캐시 저장 실패: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 정보 조회
        
        Returns:
            캐시 통계 데이터
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전체 캐시 개수
                cursor.execute("SELECT COUNT(*) FROM keyword_cache")
                total_caches = cursor.fetchone()[0]
                
                # 총 접근 횟수
                cursor.execute("SELECT SUM(access_count) FROM keyword_cache")
                total_accesses = cursor.fetchone()[0] or 0
                
                # 최근 생성된 캐시 (7일 이내)
                cursor.execute("""
                    SELECT COUNT(*) FROM keyword_cache 
                    WHERE created_at >= datetime('now', '-7 days')
                """)
                recent_caches = cursor.fetchone()[0]
                
                # 가장 많이 접근된 캐시 Top 5
                cursor.execute("""
                    SELECT company_name, start_date, end_date, access_count 
                    FROM keyword_cache 
                    ORDER BY access_count DESC 
                    LIMIT 5
                """)
                top_caches = cursor.fetchall()
                
                return {
                    "total_caches": total_caches,
                    "total_accesses": total_accesses,
                    "recent_caches_7days": recent_caches,
                    "top_accessed_caches": [
                        {
                            "company": row[0],
                            "period": f"{row[1]}-{row[2]}",
                            "access_count": row[3]
                        }
                        for row in top_caches
                    ]
                }
                
        except Exception as e:
            logger.error(f"❌ 캐시 통계 조회 실패: {e}")
            return {}
    
    def clear_old_cache(self, days: int = 30) -> int:
        """
        오래된 캐시 삭제
        
        Args:
            days: 삭제할 캐시의 일수 (기본값: 30일)
            
        Returns:
            삭제된 캐시 개수
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 삭제 전 개수 확인
                cursor.execute("""
                    SELECT COUNT(*) FROM keyword_cache 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days))
                
                delete_count = cursor.fetchone()[0]
                
                # 오래된 캐시 삭제
                cursor.execute("""
                    DELETE FROM keyword_cache 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days))
                
                conn.commit()
                
                logger.info(f"🗑️ 오래된 캐시 삭제 완료: {delete_count}개 (>{days}일)")
                return delete_count
                
        except Exception as e:
            logger.error(f"❌ 캐시 삭제 실패: {e}")
            return 0
    
    def cleanup(self):
        """캐시 매니저 정리"""
        try:
            # 데이터베이스 연결 정리
            if os.path.exists(self.db_path):
                logger.info(f"✅ 캐시 매니저 정리 완료: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 캐시 매니저 정리 실패: {e}")
