#!/usr/bin/env python3
"""
뉴스 키워드 추출 FastAPI 애플리케이션
기간별 기업 키워드 추출 서비스를 제공합니다.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging
import os
import time
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
from keyword_extractor import KeywordExtractor
from cache_manager import CacheManager
import glob
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordRequest(BaseModel):
    """키워드 추출 요청 모델"""
    company_name: str  # 기업명 (예: "삼성전자")
    start_date: str    # 시작 날짜 (YYYYMMDD 형식, 예: "20200901")
    end_date: str      # 종료 날짜 (YYYYMMDD 형식, 예: "20200903")
    top_keywords: Optional[int] = 20  # 상위 키워드 개수 (기본값: 20)
    use_ai_filter: Optional[bool] = True  # AI 필터링 사용 여부 (기본값: True)

class NewsArticle(BaseModel):
    """뉴스 기사 정보 모델"""
    title: str
    date: str
    url: str
    matched_keywords_count: int
    matched_keywords: List[str]

class KeywordResponse(BaseModel):
    """키워드 추출 응답 모델"""
    company_name: str
    period: str
    total_news_count: int
    daily_news_count: Optional[Dict[str, int]] = {}  # 날짜별 뉴스 개수 {"20210811": 15, "20210812": 23, ...}
    keywords: Dict[str, int]  # {"키워드": 빈도수, ...}
    top_news_articles: Optional[List[NewsArticle]] = []  # 상위 키워드가 많이 포함된 뉴스 기사들
    message: str
    ai_filtered: Optional[bool] = False  # AI 필터링 적용 여부
    ai_analysis: Optional[str] = ""  # AI 분석 결과
    original_keyword_count: Optional[int] = 0  # 원본 키워드 개수
    filtered_keyword_count: Optional[int] = 0  # 필터링된 키워드 개수

# 키워드 추출기 및 캐시 매니저 인스턴스
keyword_extractor = KeywordExtractor()
cache_manager = CacheManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    # 시작 시
    logger.info("FastAPI 애플리케이션이 시작되었습니다.")
    yield
    # 종료 시
    keyword_extractor.cleanup()
    cache_manager.cleanup()
    logger.info("FastAPI 애플리케이션이 종료되었습니다.")

app = FastAPI(
    title="뉴스 키워드 추출 API",
    description="기간별 기업의 키워드 추출을 위한 FastAPI 서비스",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "뉴스 키워드 추출 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "endpoints": {
            "키워드 추출 (AI 필터링 포함)": "/extract-keywords/ticker",
            "캐시 통계": "/cache/stats",
            "캐시 삭제": "/cache/clear",
            "API 문서": "/docs",
            "헬스체크": "/health"
        },
        "features": {
            "빈도수 기반 키워드 추출": "기존 키워드 추출 방식",
            "AI 스마트 필터링": "OpenAI를 활용한 주가 관련 키워드 필터링",
            "키워드 분석": "AI 기반 키워드 트렌드 분석",
            "SQLite 캐싱": "동일한 요청에 대한 빠른 응답 제공",
            "자동 캐시 관리": "오래된 캐시 자동 삭제 및 통계 제공"
        }
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/cache/stats")
async def get_cache_stats():
    """캐시 통계 조회 엔드포인트"""
    try:
        stats = cache_manager.get_cache_stats()
        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"캐시 통계 조회 중 오류가 발생했습니다: {str(e)}")

@app.delete("/cache/clear")
async def clear_old_cache(days: int = 30):
    """오래된 캐시 삭제 엔드포인트"""
    try:
        deleted_count = cache_manager.clear_old_cache(days)
        return {
            "status": "success",
            "message": f"{deleted_count}개의 오래된 캐시가 삭제되었습니다.",
            "deleted_count": deleted_count,
            "days_threshold": days,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"캐시 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"캐시 삭제 중 오류가 발생했습니다: {str(e)}")

@app.post("/extract-keywords/ticker", response_model=KeywordResponse)
async def extract_keywords(request: KeywordRequest):
    """
    기업의 키워드를 추출하는 메인 엔드포인트 (AI 필터링 지원)
    
    Args:
        request: 키워드 추출 요청 (회사명, 시작일자, 종료일자, 상위 키워드 개수, AI 필터링 사용 여부)
    
    Returns:
        KeywordResponse: 추출된 키워드와 빈도수, AI 분석 결과
    
    Features:
        - 빈도수 기반 키워드 추출
        - OpenAI를 활용한 주가 관련 키워드 필터링
        - AI 기반 키워드 트렌드 분석
    
    Example:
        POST /extract-keywords
        {
            "company_name": "삼성전자",
            "start_date": "20200901", 
            "end_date": "20200903",
            "top_keywords": 20,
            "use_ai_filter": true
        }
    """
    start_time = time.time()
    
    try:
        logger.info(f"🚀 키워드 추출 요청: {request.company_name}, {request.start_date}-{request.end_date}")
        
        # 날짜 형식 검증
        try:
            datetime.strptime(request.start_date, "%Y%m%d")
            datetime.strptime(request.end_date, "%Y%m%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. YYYYMMDD 형식을 사용해주세요.")
        
        # 캐시에서 결과 조회
        cached_result = cache_manager.get_cached_result(
            company_name=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            top_keywords=request.top_keywords,
            use_ai_filter=request.use_ai_filter
        )
        
        if cached_result:
            logger.info(f"🎯 캐시에서 결과 반환: {request.company_name}")
            result = cached_result
        else:
            logger.info(f"🔍 캐시 미스 - 키워드 추출 실행: {request.company_name}")
            
            # 키워드 추출 실행 (AI 필터링 옵션 포함)
            if request.use_ai_filter:
                result = keyword_extractor.extract_smart_keywords_from_csv(
                    company_name=request.company_name,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    top_keywords=request.top_keywords,
                    use_ai_filter=request.use_ai_filter
                )
            else:
                result = keyword_extractor.extract_keywords_from_csv(
                    company_name=request.company_name,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    top_keywords=request.top_keywords
                )
            
            # 결과를 캐시에 저장
            cache_saved = cache_manager.save_result(
                company_name=request.company_name,
                start_date=request.start_date,
                end_date=request.end_date,
                top_keywords=request.top_keywords,
                use_ai_filter=request.use_ai_filter,
                result_data=result
            )
            
            if cache_saved:
                logger.info(f"💾 결과 캐시 저장 완료: {request.company_name}")
            else:
                logger.info(f"⚠️ 캐시 저장 실패 또는 이미 존재: {request.company_name}")
        
        # 응답 형식에 맞게 변환 (상위 키워드만)
        top_keywords_dict = dict(list(result["keywords"].items())[:request.top_keywords])
        
        # 뉴스 기사 정보 변환
        top_news_articles = []
        if "top_news_articles" in result and result["top_news_articles"]:
            for article in result["top_news_articles"]:
                # nan 값 처리
                url = article.get("url", "URL 없음")
                if url is None or (isinstance(url, float) and str(url).lower() == 'nan'):
                    url = "URL 없음"
                
                title = article.get("title", "제목 없음")
                if title is None or (isinstance(title, float) and str(title).lower() == 'nan'):
                    title = "제목 없음"
                
                date = article.get("date", "날짜 없음")
                if date is None or (isinstance(date, float) and str(date).lower() == 'nan'):
                    date = "날짜 없음"
                
                top_news_articles.append(NewsArticle(
                    title=str(title),
                    date=str(date),
                    url=str(url),
                    matched_keywords_count=article.get("matched_keywords_count", 0),
                    matched_keywords=article.get("matched_keywords", [])
                ))
        
        response = KeywordResponse(
            company_name=result["company_name"],
            period=result["period"],
            total_news_count=result["total_news_count"],
            daily_news_count=result.get("daily_news_count", {}),
            keywords=top_keywords_dict,
            top_news_articles=top_news_articles,
            message=result["message"],
            ai_filtered=result.get("ai_filtered", False),
            ai_analysis=result.get("ai_analysis", ""),
            original_keyword_count=result.get("original_keyword_count", 0),
            filtered_keyword_count=result.get("filtered_keyword_count", 0)
        )
        
        # 총 소요 시간 계산
        total_time = time.time() - start_time
        
        # 날짜별 뉴스 개수 로그 출력
        daily_count = result.get("daily_news_count", {})
        if daily_count:
            daily_summary = ", ".join([f"{date}: {count}개" for date, count in daily_count.items()])
            logger.info(f"키워드 추출 완료: '{request.company_name}' 관련 뉴스 {result['total_news_count']}개에서 {len(result['keywords'])}개 키워드 추출")
            logger.info(f"날짜별 뉴스 개수: {daily_summary}")
        else:
            logger.info(f"키워드 추출 완료: '{request.company_name}' 관련 뉴스 {result['total_news_count']}개에서 {len(result['keywords'])}개 키워드 추출")
        
        # 총 API 응답 시간 출력
        logger.info(f"🎯 총 API 응답 시간: {total_time:.2f}초")
        
        return response
        
    except FileNotFoundError as e:
        total_time = time.time() - start_time
        logger.error(f"파일을 찾을 수 없습니다: {str(e)}")
        logger.error(f"❌ API 실패 응답 시간: {total_time:.2f}초")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        total_time = time.time() - start_time
        logger.error(f"잘못된 요청: {str(e)}")
        logger.error(f"❌ API 실패 응답 시간: {total_time:.2f}초")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"내부 서버 오류: {str(e)}")
        logger.error(f"❌ API 실패 응답 시간: {total_time:.2f}초")
        raise HTTPException(status_code=500, detail=f"키워드 추출 중 오류가 발생했습니다: {str(e)}")


# ------------------------------
# 기업 영향력 API (Parquet → pyarrow)
# ------------------------------

class InfluenceItem(BaseModel):
    rank: int
    company: str
    score: float
    relative: float
    score_type: str  # "pagerank" | "degree"


def _resolve_parquet_glob(base_path: str) -> str:
    # S3 경로는 그대로 사용. 디렉터리로 끝나면 *.parquet 자동 부여
    if isinstance(base_path, str) and base_path.lower().startswith("s3://"):
        if base_path.endswith("/"):
            return base_path + "*.parquet"
        return base_path
    if os.path.isdir(base_path):
        return os.path.join(base_path, "*.parquet")
    return base_path


def _load_influence_with_pyarrow(path_glob: str, top_n: int, target_company: Optional[str] = None):
    try:
        import pyarrow.parquet as pq
        import pyarrow as pa
        import pandas as pd
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"pyarrow/pandas 로드 실패: {e}")

    # 로컬 vs S3 구분 및 파일 리스트 수집
    file_list: List[str] = []
    is_s3 = isinstance(path_glob, str) and path_glob.lower().startswith("s3://")
    has_wildcard = isinstance(path_glob, str) and ("*" in path_glob or "?" in path_glob or "[" in path_glob)

    if is_s3:
        try:
            import fsspec
            fs = fsspec.filesystem("s3")
            if has_wildcard:
                file_list = fs.glob(path_glob)
            else:
                file_list = [path_glob]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 접근 실패: {e}")
    else:
        file_list = glob.glob(path_glob)

    if not file_list:
        raise HTTPException(status_code=404, detail=f"Parquet 파일을 찾을 수 없습니다: {path_glob}")

    try:
        if is_s3:
            s3fs = pa.fs.S3FileSystem()
            tables = [pq.read_table(fp, filesystem=s3fs) for fp in file_list]
        else:
            tables = [pq.read_table(fp) for fp in file_list]
        table = pa.concat_tables(tables, promote=True)
        pdf = table.to_pandas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parquet 로드 실패: {e}")

    cols = set(pdf.columns)

    # Case 1: PageRank 결과
    if {"company", "pagerank_score"}.issubset(cols):
        df = pdf[["company", "pagerank_score"]].copy()
        if target_company:
            # 부분 일치로 필터링
            df = df[df["company"].astype(str).str.contains(target_company)]
        if df.empty:
            return [], "pagerank"
        df = df.sort_values("pagerank_score", ascending=False)
        max_score = float(df.iloc[0]["pagerank_score"]) if not df.empty else 0.0
        top_df = df.head(top_n)
        items = []
        for idx, row in enumerate(top_df.itertuples(index=False), 1):
            score = float(getattr(row, "pagerank_score") or 0.0)
            rel = (score / max_score * 100.0) if max_score > 0 else 0.0
            items.append({
                "rank": idx,
                "company": str(getattr(row, "company")),
                "score": round(score, 10),
                "relative": round(rel, 2),
                "score_type": "pagerank"
            })
        return items, "pagerank"

    # Case 2: 연결 그래프 결과 → 임시 영향력 (가중 in/out-degree 합)
    if {"src", "dst", "weight"}.issubset(cols):
        df = pdf[["src", "dst", "weight"]].copy()
        if target_company:
            mask = df["src"].astype(str).str.contains(target_company) | df["dst"].astype(str).str.contains(target_company)
            df = df[mask]
        if df.empty:
            return [], "degree"
        out_w = df.groupby("src")["weight"].sum()
        in_w = df.groupby("dst")["weight"].sum()
        companies = sorted(set(out_w.index).union(in_w.index))
        influence = []
        for c in companies:
            influence.append((c, float(out_w.get(c, 0.0)) + float(in_w.get(c, 0.0))))
        influence.sort(key=lambda x: x[1], reverse=True)
        topk = influence[: top_n]
        if not topk:
            return [], "degree"
        max_score = topk[0][1]
        items = []
        for idx, (company, score) in enumerate(topk, 1):
            rel = (score / max_score * 100.0) if max_score > 0 else 0.0
            items.append({
                "rank": idx,
                "company": str(company),
                "score": float(round(score, 6)),
                "relative": float(round(rel, 2)),
                "score_type": "degree"
            })
        return items, "degree"

    # Unknown schema
    raise HTTPException(status_code=422, detail="지원하지 않는 Parquet 스키마입니다. 'company,pagerank_score' 또는 'src,dst,weight'를 기대합니다.")


@app.get("/influence", response_model=List[InfluenceItem])
async def get_influence(path: str = "s3://cheesecrust-spark-data-bucket/outputs/pagerank/pagerank/", top: int = 20, company: Optional[str] = None):
    """
    Parquet 결과에서 기업 영향력 순위를 반환합니다.
    - 기본 경로: /output
    - 기본 top: 20
    - company 지정 시 해당 이름이 포함된 기업만 필터링하여 순위 반환
    """
    if top <= 0:
        raise HTTPException(status_code=400, detail="top 은 1 이상이어야 합니다.")

    path_glob = _resolve_parquet_glob(path)
    items, score_type = _load_influence_with_pyarrow(path_glob, top, company)
    return items

if __name__ == "__main__":
    import uvicorn
    print("🚀 뉴스 키워드 추출 API 서버를 시작합니다...")
    print("📊 API 문서: http://localhost:8888/docs")
    print("💓 헬스체크: http://localhost:8888/health") 
    print("🤖 AI 스마트 필터링 지원")
    print("⏹️  Ctrl+C를 눌러 서버를 종료할 수 있습니다.")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8888,
        log_level="info"
    )