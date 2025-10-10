#!/usr/bin/env python3
"""
배치 처리 매니저 모듈
OpenAI API 호출을 배치로 처리하여 토큰 소비를 최적화합니다.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BatchRequest:
    """배치 처리 요청"""
    task_id: str
    company_name: str
    keywords_dict: Dict[str, int]
    max_keywords: int
    start_date: str = ""
    end_date: str = ""
    total_news_count: int = 0
    original_keyword_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
@dataclass
class BatchResult:
    """배치 처리 결과"""
    task_id: str
    status: TaskStatus
    filtered_keywords: Optional[Dict[str, int]] = None
    top_keywords: Optional[List[str]] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    # 원본 요청 정보 저장
    original_request: Optional['BatchRequest'] = None

class BatchKeywordManager:
    """키워드 추출 배치 처리 매니저"""
    
    def __init__(self, 
                 buffer_time_ms: int = 2000,  # 2초 버퍼 (더 짧게)
                 max_batch_size: int = 10,    # 더 큰 배치 크기
                 max_tokens_per_batch: int = 4000):  # 배치당 최대 토큰
        """
        초기화
        
        Args:
            buffer_time_ms: 버퍼 대기 시간 (밀리초)
            max_batch_size: 최대 배치 크기
            max_tokens_per_batch: 배치당 최대 토큰 수
        """
        self.buffer_time_ms = buffer_time_ms
        self.max_batch_size = max_batch_size
        self.max_tokens_per_batch = max_tokens_per_batch
        
        # 첫 요청 시간 추적
        self.first_request_time: Optional[datetime] = None
        
        # 요청 버퍼
        self.pending_requests: List[BatchRequest] = []
        self.request_lock = asyncio.Lock()
        
        # 결과 저장소
        self.results: Dict[str, BatchResult] = {}
        self.result_lock = asyncio.Lock()
        
        # 배치 처리 태스크
        self.batch_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # 통계
        self.stats = {
            "total_requests": 0,
            "total_batches": 0,
            "total_tokens_saved": 0,
            "average_batch_size": 0.0
        }
    
    async def start(self):
        """배치 처리 매니저 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        self.batch_task = asyncio.create_task(self._batch_processor())
        logger.info(f"배치 처리 매니저 시작: 버퍼 시간 {self.buffer_time_ms}ms, 최대 배치 크기 {self.max_batch_size}")
    
    async def stop(self):
        """배치 처리 매니저 중지"""
        self.is_running = False
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
        logger.info("배치 처리 매니저 중지")
    
    async def submit_request(self, company_name: str, keywords_dict: Dict[str, int], max_keywords: int, 
                           start_date: str = "", end_date: str = "", total_news_count: int = 0) -> str:
        """
        키워드 필터링 요청 제출
        
        Args:
            company_name: 기업명
            keywords_dict: 키워드 딕셔너리
            max_keywords: 최대 키워드 개수
            start_date: 시작 날짜
            end_date: 종료 날짜
            total_news_count: 총 뉴스 개수
            
        Returns:
            str: 작업 ID
        """
        task_id = str(uuid.uuid4())
        
        request = BatchRequest(
            task_id=task_id,
            company_name=company_name,
            keywords_dict=keywords_dict,
            max_keywords=max_keywords,
            start_date=start_date,
            end_date=end_date,
            total_news_count=total_news_count,
            original_keyword_count=len(keywords_dict)
        )
        
        async with self.request_lock:
            # 첫 번째 요청이면 시간 기록
            if not self.pending_requests:
                self.first_request_time = datetime.now()
                logger.info(f"🕐 첫 번째 배치 요청 도착: {company_name}")
            
            self.pending_requests.append(request)
            self.stats["total_requests"] += 1
            
            logger.info(f"📥 배치 요청 추가: {company_name} (대기 중: {len(self.pending_requests)}개)")
        
        # 결과 저장소에 초기 상태 등록
        async with self.result_lock:
            self.results[task_id] = BatchResult(
                task_id=task_id,
                status=TaskStatus.PENDING,
                original_request=request
            )
        
        return task_id
    
    async def get_result(self, task_id: str) -> Optional[BatchResult]:
        """
        작업 결과 조회
        
        Args:
            task_id: 작업 ID
            
        Returns:
            BatchResult: 작업 결과 (없으면 None)
        """
        async with self.result_lock:
            return self.results.get(task_id)
    
    async def wait_for_result(self, task_id: str, timeout: float = 30.0) -> Optional[BatchResult]:
        """
        작업 완료까지 대기
        
        Args:
            task_id: 작업 ID
            timeout: 타임아웃 (초)
            
        Returns:
            BatchResult: 작업 결과
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.get_result(task_id)
            if result and result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return result
            
            await asyncio.sleep(0.1)  # 100ms 대기
        
        # 타임아웃
        async with self.result_lock:
            if task_id in self.results:
                existing_result = self.results[task_id]
                self.results[task_id] = BatchResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error_message="처리 시간 초과",
                    completed_at=datetime.now(),
                    original_request=existing_result.original_request
                )
                return self.results[task_id]
        
        return None
    
    async def _batch_processor(self):
        """배치 처리 메인 루프 (동시 요청 최적화)"""
        while self.is_running:
            try:
                # 0.5초마다 확인 (더 빠른 반응)
                await asyncio.sleep(3)
                
                # 대기 중인 요청들 수집
                batch_requests = await self._collect_batch_requests()
                
                if batch_requests:
                    logger.info(f"🚀 배치 처리 시작: {len(batch_requests)}개 요청을 하나의 API 호출로 처리")
                    
                    # 첫 요청 시간 초기화
                    async with self.request_lock:
                        self.first_request_time = None
                    
                    await self._process_batch(batch_requests)
                    self.stats["total_batches"] += 1
                    self.stats["average_batch_size"] = self.stats["total_requests"] / self.stats["total_batches"]
                    
                    # 토큰 절약 추정 (배치 크기 - 1) * 평균 토큰
                    if len(batch_requests) > 1:
                        estimated_tokens_saved = (len(batch_requests) - 1) * 500  # 평균 500 토큰으로 가정
                        self.stats["total_tokens_saved"] += estimated_tokens_saved
                        logger.info(f"💰 토큰 절약: +{estimated_tokens_saved} (총 절약: {self.stats['total_tokens_saved']})")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"배치 처리 중 오류: {e}")
                await asyncio.sleep(0.5)  # 오류 시 잠시 대기
    
    async def _collect_batch_requests(self) -> List[BatchRequest]:
        """배치 처리할 요청들 수집 (동시 요청 최적화)"""
        batch_requests = []
        
        async with self.request_lock:
            if not self.pending_requests:
                return batch_requests
            
            current_time = datetime.now()
            
            # 첫 요청 기준으로 경과 시간 계산
            if self.first_request_time:
                first_elapsed = (current_time - self.first_request_time).total_seconds() * 1000
            else:
                first_elapsed = 0
            
            # 배치 처리 조건 (더 적극적으로)
            should_process = (
                first_elapsed >= self.buffer_time_ms or  # 첫 요청부터 버퍼 시간 경과
                len(self.pending_requests) >= self.max_batch_size or  # 최대 크기 도달
                (len(self.pending_requests) >= 2 and first_elapsed >= 1000)  # 2개 이상이고 1초 경과
            )
            
            if should_process:
                # 모든 대기 중인 요청을 배치로 수집 (최대 크기까지)
                batch_requests = self.pending_requests[:self.max_batch_size]
                self.pending_requests = self.pending_requests[self.max_batch_size:]
                
                company_names = [req.company_name for req in batch_requests]
                logger.info(f"⚡ 배치 수집: {len(batch_requests)}개 요청 [{', '.join(company_names)}], 남은 요청: {len(self.pending_requests)}개")
                logger.info(f"⏱️ 첫 요청부터 경과 시간: {first_elapsed:.0f}ms")
        
        return batch_requests
    
    async def _process_batch(self, batch_requests: List[BatchRequest]):
        """배치 요청들 처리"""
        if not batch_requests:
            return
        
        # 모든 요청의 상태를 PROCESSING으로 변경
        async with self.result_lock:
            for request in batch_requests:
                if request.task_id in self.results:
                    self.results[request.task_id].status = TaskStatus.PROCESSING
        
        try:
            # SmartKeywordFilter를 동적으로 임포트 (순환 임포트 방지)
            from smart_keyword_filter import SmartKeywordFilter
            
            smart_filter = SmartKeywordFilter()
            
            if not smart_filter.is_available():
                # AI 사용 불가시 개별 처리로 폴백
                await self._process_batch_individually(batch_requests)
                return
            
            # 배치 프롬프트 생성 및 처리
            batch_response = await self._process_batch_with_ai(smart_filter, batch_requests)
            
            # 응답 파싱 및 결과 저장
            await self._parse_and_save_batch_results(batch_requests, batch_response)
            
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}")
            await self._mark_batch_as_failed(batch_requests, str(e))
    
    async def _process_batch_individually(self, batch_requests: List[BatchRequest]):
        """개별 처리로 폴백"""
        from smart_keyword_filter import SmartKeywordFilter
        
        smart_filter = SmartKeywordFilter()
        
        for request in batch_requests:
            try:
                filtered_keywords, top_keywords = smart_filter.filter_stock_related_keywords(
                    request.keywords_dict,
                    request.company_name,
                    request.max_keywords
                )
                
                async with self.result_lock:
                            self.results[request.task_id] = BatchResult(
                                task_id=request.task_id,
                                status=TaskStatus.COMPLETED,
                                filtered_keywords=filtered_keywords,
                                top_keywords=top_keywords,
                                completed_at=datetime.now(),
                                original_request=request
                            )
                
            except Exception as e:
                async with self.result_lock:
                    self.results[request.task_id] = BatchResult(
                        task_id=request.task_id,
                        status=TaskStatus.FAILED,
                        error_message=str(e),
                        completed_at=datetime.now(),
                        original_request=request
                    )
    
    async def _process_batch_with_ai(self, smart_filter, batch_requests: List[BatchRequest]) -> str:
        """AI를 사용한 배치 처리"""
        # 배치 프롬프트 생성
        batch_prompt = self._create_batch_prompt(batch_requests)
        
        # OpenAI API 호출
        response = smart_filter.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 금융 및 주식 시장 전문가입니다. 여러 기업의 뉴스 키워드들을 동시에 분석하여 각 기업별로 주가에 영향을 미칠 수 있는 키워드만을 선별하는 역할을 합니다."},
                {"role": "user", "content": batch_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_batch_prompt(self, batch_requests: List[BatchRequest]) -> str:
        """배치 프롬프트 생성"""
        prompt_parts = ["다음 기업들의 뉴스 키워드를 각각 분석하여 주가에 영향을 미칠 수 있는 키워드만 선별해주세요.\n"]
        
        for i, request in enumerate(batch_requests, 1):
            # 상위 50개 키워드만 사용 (토큰 절약)
            top_keywords = list(request.keywords_dict.keys())[:50]
            keywords_str = ', '.join(top_keywords)
            
            prompt_parts.append(f"\n{i}. {request.company_name}:")
            prompt_parts.append(f"키워드: {keywords_str}")
        
        prompt_parts.append("""
주가 관련 키워드 선별 기준:
✅ 포함할 키워드: 재무/실적, 사업/투자, 시장, 경영, 주식시장 관련
❌ 제외할 키워드: 기업명 자체, 일반용어, 단순 제품명, 지역명

응답 형식: 각 기업별로 번호를 매겨 선별된 키워드들을 쉼표로 구분하여 나열
예시:
1. 투자, 주식, 출시, 소송
2. 실적, 계약, 개발, 시장
""")
        
        return '\n'.join(prompt_parts)
    
    async def _parse_and_save_batch_results(self, batch_requests: List[BatchRequest], batch_response: str):
        """배치 응답 파싱 및 결과 저장"""
        try:
            lines = batch_response.strip().split('\n')
            results_by_index = {}
            
            # 응답 파싱
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # "1. keyword1, keyword2, ..." 형태 파싱
                if line[0].isdigit() and '.' in line:
                    parts = line.split('.', 1)
                    if len(parts) == 2:
                        index = int(parts[0]) - 1  # 0-based 인덱스
                        keywords_str = parts[1].strip()
                        
                        if keywords_str:
                            selected_keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
                            results_by_index[index] = selected_keywords
            
            # 각 요청에 대해 결과 처리
            async with self.result_lock:
                for i, request in enumerate(batch_requests):
                    try:
                        if i in results_by_index:
                            selected_keywords = results_by_index[i]
                            
                            # 원본 키워드와 매칭하여 빈도수 포함한 결과 생성
                            filtered_keywords = self._match_keywords_with_frequency(
                                selected_keywords, 
                                request.keywords_dict
                            )
                            
                            # 빈도수 순으로 정렬하여 상위 키워드 추출
                            sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
                            top_keywords = [k for k, v in sorted_keywords[:request.max_keywords]]
                            final_keywords = dict(sorted_keywords[:request.max_keywords])
                            
                            self.results[request.task_id] = BatchResult(
                                task_id=request.task_id,
                                status=TaskStatus.COMPLETED,
                                filtered_keywords=final_keywords,
                                top_keywords=top_keywords,
                                completed_at=datetime.now(),
                                original_request=request
                            )
                        else:
                            # 해당 인덱스의 결과가 없는 경우
                            self.results[request.task_id] = BatchResult(
                                task_id=request.task_id,
                                status=TaskStatus.FAILED,
                                error_message="AI 응답에서 해당 기업의 결과를 찾을 수 없습니다.",
                                completed_at=datetime.now(),
                                original_request=request
                            )
                    
                    except Exception as e:
                        self.results[request.task_id] = BatchResult(
                            task_id=request.task_id,
                            status=TaskStatus.FAILED,
                            error_message=f"결과 처리 중 오류: {str(e)}",
                            completed_at=datetime.now(),
                            original_request=request
                        )
        
        except Exception as e:
            logger.error(f"배치 응답 파싱 실패: {e}")
            await self._mark_batch_as_failed(batch_requests, f"응답 파싱 실패: {str(e)}")
    
    def _match_keywords_with_frequency(self, selected_keywords: List[str], original_keywords: Dict[str, int]) -> Dict[str, int]:
        """선택된 키워드를 원본 키워드와 매칭하여 빈도수 포함한 딕셔너리 생성"""
        filtered_dict = {}
        matched_original_keywords = set()
        
        for selected in selected_keywords:
            matched = False
            
            # 1단계: 정확히 일치하는 키워드 찾기
            if selected in original_keywords and selected not in matched_original_keywords:
                filtered_dict[selected] = original_keywords[selected]
                matched_original_keywords.add(selected)
                matched = True
            
            # 2단계: 부분 일치하는 키워드 찾기
            if not matched:
                for original_keyword in original_keywords:
                    if original_keyword not in matched_original_keywords:
                        if (selected in original_keyword or original_keyword in selected) and len(selected) >= 2:
                            filtered_dict[original_keyword] = original_keywords[original_keyword]
                            matched_original_keywords.add(original_keyword)
                            matched = True
                            break
        
        return filtered_dict
    
    async def _mark_batch_as_failed(self, batch_requests: List[BatchRequest], error_message: str):
        """배치 요청들을 실패로 표시"""
        async with self.result_lock:
            for request in batch_requests:
                self.results[request.task_id] = BatchResult(
                    task_id=request.task_id,
                    status=TaskStatus.FAILED,
                    error_message=error_message,
                    completed_at=datetime.now(),
                    original_request=request
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        return {
            **self.stats,
            "pending_requests": len(self.pending_requests),
            "stored_results": len(self.results),
            "is_running": self.is_running
        }
    
    async def cleanup_old_results(self, max_age_hours: int = 24):
        """오래된 결과 정리"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        async with self.result_lock:
            old_task_ids = [
                task_id for task_id, result in self.results.items()
                if result.completed_at and result.completed_at < cutoff_time
            ]
            
            for task_id in old_task_ids:
                del self.results[task_id]
            
            if old_task_ids:
                logger.info(f"오래된 결과 {len(old_task_ids)}개 정리 완료")

# 전역 배치 매니저 인스턴스
batch_manager = None

def get_batch_manager() -> BatchKeywordManager:
    """배치 매니저 인스턴스 반환"""
    global batch_manager
    if batch_manager is None:
        batch_manager = BatchKeywordManager()
    return batch_manager
