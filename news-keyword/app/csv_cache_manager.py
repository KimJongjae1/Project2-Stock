#!/usr/bin/env python3
"""
CSV 파일 디스크 캐시 매니저
S3에서 읽은 CSV 파일을 로컬 디스크에 저장하고 재사용
"""

import os
import hashlib
import logging
import pandas as pd
import time
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CSVCacheManager:
    """CSV 파일 디스크 캐시 관리"""
    
    def __init__(self, cache_dir: str = "./csv_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 캐시 통계
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"CSV 캐시 디렉토리 초기화: {self.cache_dir.absolute()}")
    
    def _get_cache_key(self, s3_path: str) -> str:
        """S3 경로를 기반으로 캐시 키 생성"""
        # S3 경로를 해시화하여 안전한 파일명 생성
        hash_key = hashlib.md5(s3_path.encode()).hexdigest()
        filename = os.path.basename(s3_path)
        return f"{hash_key}_{filename}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """캐시 파일 경로 반환"""
        return self.cache_dir / cache_key
    
    def is_cached(self, s3_path: str) -> bool:
        """파일이 캐시되어 있는지 확인"""
        cache_key = self._get_cache_key(s3_path)
        cache_path = self._get_cache_path(cache_key)
        return cache_path.exists()
    
    def save_to_cache(self, s3_path: str, df: pd.DataFrame) -> bool:
        """DataFrame을 캐시에 저장"""
        try:
            cache_key = self._get_cache_key(s3_path)
            cache_path = self._get_cache_path(cache_key)
            
            start_time = time.time()
            
            # Parquet 형식으로 저장 (압축률과 속도 최적화)
            parquet_path = cache_path.with_suffix('.parquet')
            df.to_parquet(
                parquet_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            
            save_time = time.time() - start_time
            file_size = parquet_path.stat().st_size / (1024*1024)  # MB
            
            logger.info(f"💾 캐시 저장 완료: {os.path.basename(s3_path)}")
            logger.info(f"   📁 크기: {file_size:.2f}MB, 시간: {save_time:.3f}초")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 실패 ({s3_path}): {e}")
            return False
    
    def load_from_cache(self, s3_path: str) -> Optional[pd.DataFrame]:
        """캐시에서 DataFrame 로드"""
        try:
            cache_key = self._get_cache_key(s3_path)
            cache_path = self._get_cache_path(cache_key)
            parquet_path = cache_path.with_suffix('.parquet')
            
            if not parquet_path.exists():
                self.cache_misses += 1
                return None
            
            start_time = time.time()
            df = pd.read_parquet(parquet_path, engine='pyarrow')
            load_time = time.time() - start_time
            
            self.cache_hits += 1
            
            logger.info(f"📂 캐시에서 로드: {os.path.basename(s3_path)}")
            logger.info(f"   📊 행 수: {len(df):,}개, 시간: {load_time:.3f}초")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 캐시 로드 실패 ({s3_path}): {e}")
            self.cache_misses += 1
            return None
    
    def get_cache_stats(self) -> dict:
        """캐시 통계 반환"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # 캐시 디렉토리 크기 계산
        total_size = 0
        file_count = 0
        for file_path in self.cache_dir.glob('*.parquet'):
            total_size += file_path.stat().st_size
            file_count += 1
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cached_files": file_count,
            "total_size_mb": f"{total_size / (1024*1024):.2f}MB"
        }
    
    def clear_cache(self) -> bool:
        """캐시 디렉토리 정리"""
        try:
            deleted_count = 0
            for file_path in self.cache_dir.glob('*.parquet'):
                file_path.unlink()
                deleted_count += 1
            
            logger.info(f"🗑️ 캐시 정리 완료: {deleted_count}개 파일 삭제")
            return True
            
        except Exception as e:
            logger.error(f"❌ 캐시 정리 실패: {e}")
            return False
    
    def cleanup_old_cache(self, max_age_days: int = 7) -> int:
        """오래된 캐시 파일 정리"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            deleted_count = 0
            
            for file_path in self.cache_dir.glob('*.parquet'):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🗑️ 오래된 캐시 정리: {deleted_count}개 파일 삭제 ({max_age_days}일 이상)")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 오래된 캐시 정리 실패: {e}")
            return 0
    
    def print_cache_stats(self):
        """캐시 통계 출력"""
        stats = self.get_cache_stats()
        logger.info("📊 === CSV 캐시 통계 ===")
        logger.info(f"   🎯 캐시 적중률: {stats['hit_rate']}")
        logger.info(f"   ✅ 캐시 히트: {stats['cache_hits']}회")
        logger.info(f"   ❌ 캐시 미스: {stats['cache_misses']}회")
        logger.info(f"   📁 캐시된 파일: {stats['cached_files']}개")
        logger.info(f"   💾 총 크기: {stats['total_size_mb']}")
