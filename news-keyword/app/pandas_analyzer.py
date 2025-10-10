"""
Pandas를 사용한 키워드 추출 엔진
중소용량 데이터 처리에 최적화
"""

import os
import re
from typing import Dict, List
from collections import Counter
import logging
import pandas as pd
import time
from csv_cache_manager import CSVCacheManager

logger = logging.getLogger(__name__)

class PandasAnalyzer:
    """Pandas를 사용한 키워드 추출 분석기"""
    
    def __init__(self):
        # CSV 캐시 매니저 초기화
        self.csv_cache = CSVCacheManager()
    
    def extract_keywords_with_pandas(self, company_name: str, start_date: str, end_date: str, top_keywords: int, csv_files: List[str]) -> Dict:
        """
        pandas를 사용한 키워드 추출 (백업 방법)
        여러 CSV 파일을 읽어서 통합 처리
        """
        logger.info("🐼 Pandas 엔진으로 키워드 추출을 시작합니다.")
        
        all_dataframes = []
        total_loaded_rows = 0
        
        # 모든 CSV 파일 읽기 (캐시 우선 사용)
        for csv_path in csv_files:
            try:
                filename = os.path.basename(csv_path)
                logger.info(f"CSV 파일 처리 중: {filename}")
                
                file_start_time = time.time()
                
                # 1. 캐시에서 먼저 확인
                df = self.csv_cache.load_from_cache(csv_path)
                
                if df is not None:
                    # 캐시에서 로드 성공
                    file_read_time = time.time() - file_start_time
                    logger.info(f"🚀 {filename} 캐시 로드: {len(df):,}행, {file_read_time:.3f}초")
                else:
                    # 2. 캐시에 없으면 S3에서 읽고 캐시에 저장
                    logger.info(f"📥 {filename} S3에서 읽는 중...")
                    read_start_time = time.time()
                    df = pd.read_csv(csv_path, encoding='utf-8')
                    read_time = time.time() - read_start_time
                    
                    # 캐시에 저장
                    cache_saved = self.csv_cache.save_to_cache(csv_path, df)
                    
                    file_read_time = time.time() - file_start_time
                    cache_status = "✅ 캐시됨" if cache_saved else "❌ 캐시 실패"
                    logger.info(f"📁 {filename} S3 읽기: {len(df):,}행, {read_time:.2f}초 ({cache_status})")
                
                all_dataframes.append(df)
                total_loaded_rows += len(df)
                
            except Exception as e:
                logger.warning(f"CSV 파일 처리 실패: {csv_path}, 오류: {e}")
                continue
        
        if not all_dataframes:
            raise FileNotFoundError("읽을 수 있는 CSV 파일이 없습니다.")
        
        # 모든 데이터프레임 병합
        df = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"총 {len(csv_files)}개 파일에서 {total_loaded_rows}개 행 로드 완료")
        logger.info(f"병합 후 총 {len(df)}개 행")
        logger.info(f"컬럼명: {list(df.columns)}")
        
        # 기업 필터링 (기관 컬럼에서 해당 기업이 포함된 행들을 가져옴)
        if '기관' in df.columns:
            # 기관 컬럼에 NaN이 아니고 회사명이 포함된 행 필터링
            mask = df['기관'].notna() & df['기관'].str.contains(company_name, na=False, regex=False)
            company_filtered_df = df[mask]
            company_count = len(company_filtered_df)
            
            logger.info(f"'{company_name}' 관련 뉴스: {company_count}개 (기관 필터링 후)")
            
            # 날짜 필터링 적용
            date_filtered_df = self.apply_date_filter(company_filtered_df, start_date, end_date)
            total_count = len(date_filtered_df)
            
            logger.info(f"날짜 필터링 후 뉴스: {total_count}개 ({start_date}-{end_date})")
            
            # 최종 필터링된 데이터프레임 사용
            filtered_df = date_filtered_df
            
            if total_count == 0:
                return {
                    "company_name": company_name,
                    "period": f"{start_date}-{end_date}",
                    "total_news_count": 0,
                    "daily_news_count": {},
                    "keywords": {},
                    "message": f"'{company_name}'와 관련된 뉴스를 찾을 수 없습니다."
                }
            
            # 날짜별 뉴스 개수 계산
            daily_news_count = self.calculate_daily_news_count(filtered_df, start_date, end_date)
            
            # 키워드 추출 (기존 키워드 컬럼 사용)
            if '키워드' in df.columns:
                # 키워드 컬럼에서 키워드 분리 및 정리
                all_keywords = []
                for keywords_str in filtered_df['키워드'].dropna():
                    keywords = [re.sub(r'[^가-힣a-zA-Z0-9\s]', '', k.strip()) for k in keywords_str.split(',') if k.strip()]
                    all_keywords.extend([k for k in keywords if len(k) >= 2])
                
                # 기업명 자체는 키워드에서 제외
                all_keywords = [k for k in all_keywords if company_name not in k]
                
                # 키워드 빈도 계산
                keyword_counter = Counter(all_keywords)
                
                # 빈도순으로 정렬하여 딕셔너리 생성
                keywords_dict = dict(keyword_counter.most_common())
                
                # 상위 키워드가 많이 포함된 뉴스 기사들 추출
                top_keywords_list = list(keywords_dict.keys())[:top_keywords]
                top_news_articles = self.extract_top_news_articles(filtered_df, top_keywords_list)
                
                # 캐시 통계 출력
                self.csv_cache.print_cache_stats()
                
                return {
                    "company_name": company_name,
                    "period": f"{start_date}-{end_date}",
                    "total_news_count": total_count,
                    "daily_news_count": daily_news_count,
                    "keywords": keywords_dict,
                    "top_news_articles": top_news_articles,
                    "message": f"🐼 Pandas 엔진으로 성공적으로 키워드를 추출했습니다. 총 {len(keywords_dict)}개 키워드 발견 (파일 {len(csv_files)}개 처리)"
                }
            else:
                return {
                    "company_name": company_name,
                    "period": f"{start_date}-{end_date}",
                    "total_news_count": total_count,
                    "daily_news_count": daily_news_count,
                    "keywords": {},
                    "message": "키워드 컬럼을 찾을 수 없습니다."
                }
        else:
            raise ValueError("기관 컬럼을 찾을 수 없습니다.")
    
    def apply_date_filter(self, df, start_date: str, end_date: str) -> pd.DataFrame:
        """
        날짜 컬럼을 사용하여 설정된 기간 내의 데이터만 필터링합니다.
        
        Args:
            df: 필터링할 데이터프레임
            start_date: 시작 날짜 (YYYYMMDD)
            end_date: 종료 날짜 (YYYYMMDD)
            
        Returns:
            pd.DataFrame: 날짜 필터링된 데이터프레임
        """
        try:
            from datetime import datetime
            
            # 날짜 관련 컬럼 찾기
            date_column = None
            for col in ['일자', '날짜', 'date', 'Date', 'DATE']:
                if col in df.columns:
                    date_column = col
                    break
            
            if date_column is None:
                logger.warning("날짜 관련 컬럼을 찾을 수 없습니다. 날짜 필터링을 건너뜁니다.")
                return df
            
            logger.info(f"날짜 필터링에 사용할 컬럼: {date_column}")
            
            # 날짜 범위를 datetime 객체로 변환
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            
            # 날짜 컬럼의 값들을 파싱하여 필터링
            def parse_date(date_str):
                """다양한 날짜 형식을 파싱합니다."""
                if pd.isna(date_str):
                    return None
                
                date_str = str(date_str).strip()
                
                # 다양한 날짜 형식 시도
                date_formats = [
                    "%Y%m%d",      # 20210811
                    "%Y-%m-%d",   # 2021-08-11
                    "%Y/%m/%d",   # 2021/08/11
                    "%Y.%m.%d",   # 2021.08.11
                    "%Y-%m-%d %H:%M:%S",  # 2021-08-11 10:30:00
                    "%Y/%m/%d %H:%M:%S",  # 2021/08/11 10:30:00
                ]
                
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                
                # 파싱 실패 시 None 반환
                return None
            
            # 날짜 파싱 및 필터링
            df_copy = df.copy()
            df_copy['parsed_date'] = df_copy[date_column].apply(parse_date)
            
            # 유효한 날짜만 필터링
            valid_dates_mask = df_copy['parsed_date'].notna()
            df_with_dates = df_copy[valid_dates_mask]
            
            logger.info(f"유효한 날짜가 있는 뉴스: {len(df_with_dates)}개")
            
            if len(df_with_dates) == 0:
                logger.warning("유효한 날짜가 있는 뉴스가 없습니다.")
                return df.iloc[0:0]  # 빈 데이터프레임 반환
            
            # 날짜 범위 필터링
            date_range_mask = (
                (df_with_dates['parsed_date'] >= start_dt) & 
                (df_with_dates['parsed_date'] <= end_dt)
            )
            
            filtered_df = df_with_dates[date_range_mask]
            
            # 원본 컬럼만 유지 (parsed_date 컬럼 제거)
            result_df = filtered_df.drop('parsed_date', axis=1)
            
            logger.info(f"날짜 범위 필터링 완료: {len(result_df)}개 뉴스")
            
            # 샘플 날짜 값 로그 출력
            if len(result_df) > 0:
                sample_dates = result_df[date_column].head(3).tolist()
                logger.info(f"필터링된 샘플 날짜: {sample_dates}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"날짜 필터링 중 오류 발생: {e}")
            logger.info("날짜 필터링을 건너뛰고 원본 데이터를 반환합니다.")
            return df
    
    def calculate_daily_news_count(self, filtered_df, start_date: str, end_date: str) -> Dict[str, int]:
        """
        날짜별 뉴스 개수를 계산합니다.
        
        Args:
            filtered_df: 필터링된 데이터프레임
            start_date: 시작 날짜 (YYYYMMDD)
            end_date: 종료 날짜 (YYYYMMDD)
            
        Returns:
            Dict[str, int]: 날짜별 뉴스 개수 {"20210811": 15, "20210812": 23, ...}
        """
        try:
            from datetime import datetime, timedelta
            
            # 사용 가능한 컬럼 확인
            logger.info(f"사용 가능한 컬럼: {list(filtered_df.columns)}")
            
            # 날짜 관련 컬럼 찾기
            date_column = None
            for col in ['일자', '날짜', 'date', 'Date', 'DATE']:
                if col in filtered_df.columns:
                    date_column = col
                    break
            
            if date_column is None:
                logger.warning("날짜 관련 컬럼을 찾을 수 없습니다. 빈 딕셔너리를 반환합니다.")
                return {}
            
            logger.info(f"날짜 컬럼 사용: {date_column}")
            
            # 날짜 범위 생성
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            
            daily_count = {}
            current_date = start_dt
            
            # 각 날짜별로 뉴스 개수 계산
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y%m%d")
                
                # 해당 날짜의 뉴스 개수 계산
                try:
                    # 다양한 날짜 형식 지원
                    date_patterns = [
                        date_str,  # 20210811
                        f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",  # 2021-08-11
                        f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}",  # 2021/08/11
                        f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}",  # 2021.08.11
                    ]
                    
                    # 각 패턴에 대해 매칭 시도
                    count = 0
                    for pattern in date_patterns:
                        date_mask = filtered_df[date_column].astype(str).str.contains(pattern, na=False)
                        pattern_count = date_mask.sum()
                        if pattern_count > 0:
                            count = pattern_count
                            logger.debug(f"{date_str} ({pattern}): {count}개 뉴스 발견")
                            break
                    
                    # 디버깅을 위한 로그
                    if count == 0:
                        # 샘플 날짜 값 확인
                        sample_dates = filtered_df[date_column].dropna().head(3).tolist()
                        logger.debug(f"{date_str} 매칭 실패. 샘플 날짜 값: {sample_dates}")
                    
                except Exception as e:
                    logger.warning(f"날짜 {date_str} 계산 중 오류: {e}")
                    count = 0
                
                daily_count[date_str] = int(count)
                current_date += timedelta(days=1)
            
            # 총합 검증
            total_daily_count = sum(daily_count.values())
            logger.info(f"날짜별 뉴스 개수 계산 완료: {len(daily_count)}일, 총합: {total_daily_count}개")
            logger.info(f"daily_news_count 합계: {total_daily_count}, total_news_count: {len(filtered_df)}")
            
            return daily_count
            
        except Exception as e:
            logger.warning(f"날짜별 뉴스 개수 계산 중 오류: {e}")
            return {}
    
    def extract_top_news_articles(self, filtered_df, top_keywords_list, max_articles=10):
        """
        상위 키워드가 많이 포함된 뉴스 기사들을 추출합니다.
        
        Args:
            filtered_df: 필터링된 데이터프레임
            top_keywords_list: 상위 키워드 리스트
            max_articles: 최대 기사 수
            
        Returns:
            List[Dict]: 뉴스 기사 정보 리스트
        """
        try:
            if not top_keywords_list:
                return []
            
            # 각 기사에서 상위 키워드 매칭 개수 계산
            articles_with_score = []
            
            for idx, row in filtered_df.iterrows():
                article_keywords = []
                if pd.notna(row.get('키워드', '')):
                    # 기사 키워드 분리
                    article_keywords = [k.strip() for k in str(row['키워드']).split(',') if k.strip()]
                
                # 상위 키워드와 매칭되는 개수 계산
                matched_count = 0
                matched_keywords = []
                for keyword in top_keywords_list:
                    for article_keyword in article_keywords:
                        if keyword in article_keyword or article_keyword in keyword:
                            matched_count += 1
                            matched_keywords.append(keyword)
                            break  # 중복 카운트 방지
                
                if matched_count > 0:
                    # nan 값 처리
                    title = row.get('제목', '제목 없음')
                    if pd.isna(title):
                        title = '제목 없음'
                    
                    date = row.get('일자', '일자 없음')
                    if pd.isna(date):
                        date = '일자 없음'
                    
                    url = row.get('URL', 'URL 없음')
                    if pd.isna(url):
                        url = 'URL 없음'
                    
                    articles_with_score.append({
                        'title': str(title),
                        'date': str(date),
                        'url': str(url),
                        'matched_keywords_count': matched_count,
                        'matched_keywords': list(set(matched_keywords)),
                        'all_keywords': article_keywords
                    })
            
            # 매칭된 키워드 개수 순으로 정렬
            articles_with_score.sort(key=lambda x: x['matched_keywords_count'], reverse=True)
            
            # 상위 기사들만 반환
            top_articles = articles_with_score[:max_articles]
            
            logger.info(f"상위 키워드가 포함된 뉴스 기사 {len(top_articles)}개 추출 완료")
            
            return top_articles
            
        except Exception as e:
            logger.warning(f"뉴스 기사 추출 중 오류: {e}")
            return []
