#!/usr/bin/env python3
"""
AI 기반 스마트 키워드 필터링 모듈
OpenAI API를 사용하여 주가와 관련된 키워드만 추출합니다.
"""

import os
import logging
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import json
import time

# 환경 변수 로드 (.env 파일 경로 명시적 지정)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

logger = logging.getLogger(__name__)

class SmartKeywordFilter:
    """OpenAI API를 사용한 스마트 키워드 필터링 클래스"""
    
    def __init__(self):
        """초기화"""
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key or self.api_key == 'your_openai_api_key_here':
            logger.warning("OpenAI API 키가 설정되지 않았습니다. .env 파일에서 OPENAI_API_KEY를 설정해주세요.")
            return
            
        try:
            # OpenAI 클라이언트 초기화 (버전 호환성 고려)
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=30.0,  # 타임아웃 설정
            )
            logger.info("OpenAI 클라이언트 초기화 완료")
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """OpenAI API 사용 가능 여부 확인"""
        return self.client is not None
    
    def _rule_based_filter(self, keywords_dict: Dict[str, int], company_name: str, max_keywords: int = 20) -> Tuple[Dict[str, int], List[str]]:
        """규칙 기반 주가 관련 키워드 필터링 (OpenAI API 사용 불가시 대안)"""
        
        # 주가 관련 키워드 패턴
        stock_related_patterns = {
            '재무/실적': ['실적', '매출', '이익', '손실', '영업이익', '순이익', '수익', '적자', '흑자'],
            '투자/사업': ['투자', '계약', '출시', '개발', '특허', '기술', '혁신', '프로젝트'],
            '시장': ['시장', '점유율', '경쟁', '성장', '확장', '진출'],
            '경영': ['인수', '합병', '전략', '조직', '구조조정', '임원'],
            '주식시장': ['주식', '주가', '상장', '증자', '배당', '공시', '소송', '규제']
        }
        
        # 제외할 키워드 패턴
        exclude_patterns = [
            company_name, '삼성', '기업', '회사', '업체', '기자', '뉴스', '보도', '발표',
            'TV', '냉장고', '스마트폰', '제품', '취업', '소비자', '미국', '해외', '적용'
        ]
        
        filtered_keywords = {}
        
        # 키워드별 점수 계산
        for keyword, frequency in keywords_dict.items():
            score = 0
            
            # 주가 관련 패턴 매칭
            for category, patterns in stock_related_patterns.items():
                for pattern in patterns:
                    if pattern in keyword:
                        score += 3  # 높은 점수
                        break
            
            # 키워드가 주가 관련 단어를 포함하는지 확인
            stock_keywords = ['주식', '투자', '매출', '이익', '실적', '시장', '출시', '개발', '소송', '계약']
            for stock_word in stock_keywords:
                if stock_word in keyword:
                    score += 2
            
            # 제외할 키워드 확인
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if exclude_pattern in keyword or keyword in exclude_pattern:
                    should_exclude = True
                    break
            
            # 점수가 있고 제외되지 않은 키워드만 포함
            if score > 0 and not should_exclude and len(keyword) >= 2:
                filtered_keywords[keyword] = frequency
        
        # 빈도수 순으로 정렬
        sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
        final_keywords = dict(sorted_keywords[:max_keywords])
        top_keywords_list = list(final_keywords.keys())
        
        logger.info(f"규칙 기반 필터링 완료: {len(keywords_dict)}개 → {len(final_keywords)}개 키워드")
        return final_keywords, top_keywords_list

    def filter_stock_related_keywords(self, keywords_dict: Dict[str, int], company_name: str, max_keywords: int = 20) -> Tuple[Dict[str, int], List[str]]:
        """
        주가와 관련된 키워드만 필터링합니다.
        
        Args:
            keywords_dict: {"키워드": 빈도수} 형태의 딕셔너리
            company_name: 기업명
            max_keywords: 최대 키워드 개수
            
        Returns:
            Tuple[Dict[str, int], List[str]]: (필터링된 키워드 딕셔너리, 상위 키워드 리스트)
        """
        if not self.is_available():
            logger.warning("OpenAI API를 사용할 수 없습니다. 원본 키워드를 반환합니다.")
            top_keywords = list(keywords_dict.keys())[:max_keywords]
            filtered_dict = {k: keywords_dict[k] for k in top_keywords}
            return filtered_dict, top_keywords
        
        try:
            # 키워드를 빈도수 순으로 정렬하여 상위 키워드만 선택 (API 비용 절약)
            sorted_keywords = sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)
            top_keywords_for_analysis = sorted_keywords[:min(50, len(sorted_keywords))]  # 최대 50개까지만 분석
            
            keywords_list = [keyword for keyword, _ in top_keywords_for_analysis]
            
            # OpenAI API 호출을 위한 프롬프트 생성
            prompt = self._create_filtering_prompt(keywords_list, company_name)
            
            logger.info(f"{company_name}의 {len(keywords_list)}개 키워드를 AI로 분석 중...")
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 금융 및 주식 시장 전문가입니다. 당신이 아는 한국 기업들의 배경 지식을 활용하여 기업의 뉴스 키워드 중에서 주가에 영향을 미칠 수 있는 키워드만을 선별하는 역할을 합니다. 이때 키워드 간의 조합도 고려하여 선별해주세요. 조합한 키워드가 강력한 경우 합쳐서 보여줘"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 일관된 결과를 위해 낮은 temperature 사용
                max_tokens=1500
            )
            
            # 응답 파싱
            ai_response = response.choices[0].message.content.strip()
            filtered_keywords = self._parse_ai_response(ai_response, keywords_dict)
            
            # 결과 정리
            if filtered_keywords:
                # 빈도수 순으로 정렬
                sorted_filtered = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
                final_keywords = sorted_filtered[:max_keywords]
                
                result_dict = dict(final_keywords)
                result_list = [keyword for keyword, _ in final_keywords]
                
                logger.info(f"AI 필터링 완료: {len(keywords_dict)}개 → {len(result_dict)}개 키워드")
                return result_dict, result_list
            else:
                logger.warning("AI 필터링에서 유효한 키워드를 찾지 못했습니다. 원본 키워드를 반환합니다.")
                top_keywords = list(keywords_dict.keys())[:max_keywords]
                filtered_dict = {k: keywords_dict[k] for k in top_keywords}
                return filtered_dict, top_keywords
                
        except Exception as e:
            logger.error(f"AI 키워드 필터링 중 오류 발생: {e}")
            logger.info("규칙 기반 필터링으로 대체합니다.")
            return self._rule_based_filter(keywords_dict, company_name, max_keywords)
    
    def _create_filtering_prompt(self, keywords_list: List[str], company_name: str) -> str:
        """OpenAI API 호출을 위한 프롬프트 생성"""
        keywords_str = ', '.join(keywords_list)
        
        prompt = f"""
다음은 {company_name}의 뉴스에서 추출된 키워드 목록입니다. 이 중에서 주가에 직접적으로 영향을 미칠 수 있는 키워드만 선별해주세요.

키워드 목록:
{keywords_str}

주가 관련 키워드 선별 기준:
✅ 포함할 키워드:
- 재무/실적: 매출, 이익, 손실, 실적, 영업이익, 순이익, 수익성
- 사업/투자: 투자, 계약, 신제품, 출시, 기술개발, 특허, R&D
- 시장: 시장점유율, 경쟁, 점유율, 성장, 확장
- 경영: 인수합병, 전략, 조직개편, 구조조정
- 주식시장: 주식, 상장, 증자, 배당, 공시, 소송

❌ 제외할 키워드:
- 기업명: {company_name}, 삼성 (기업명 자체)
- 일반용어: 기업, 회사, 업체, 기자, 뉴스, 보도, 발표
- 제품명: TV, 냉장고, 스마트폰 (단순 제품명)
- 지역명: 미국, 해외 (지역만 언급)
- 기타: 취업, 소비자, 적용 (주가와 무관)

중요: 주가에 실질적 영향을 미치는 키워드만 선택하세요.

응답 형식: 선별된 키워드들을 정확히 쉼표로 구분하여 나열 (설명 불필요)
예시: 투자, 주식, 출시, 소송, 시장
"""
        return prompt
    
    def _parse_ai_response(self, ai_response: str, original_keywords: Dict[str, int]) -> Dict[str, int]:
        """AI 응답을 파싱하여 필터링된 키워드 딕셔너리 생성"""
        try:
            # AI가 선택한 키워드들을 파싱
            selected_keywords = [keyword.strip() for keyword in ai_response.split(',')]
            selected_keywords = [k for k in selected_keywords if k]  # 빈 문자열 제거
            
            logger.info(f"AI가 선택한 키워드 개수: {len(selected_keywords)}개")
            logger.info(f"원본 키워드 개수: {len(original_keywords)}개")
            
            # 원본 키워드 딕셔너리에서 선택된 키워드들의 빈도수를 가져옴
            filtered_dict = {}
            matched_original_keywords = set()  # 이미 매칭된 원본 키워드 추적
            
            for selected in selected_keywords:
                matched = False
                
                # 1단계: 정확히 일치하는 키워드 찾기
                if selected in original_keywords and selected not in matched_original_keywords:
                    filtered_dict[selected] = original_keywords[selected]
                    matched_original_keywords.add(selected)
                    matched = True
                    logger.debug(f"정확 매칭: '{selected}'")
                
                # 2단계: 부분 일치하는 키워드 찾기 (정확 매칭이 없는 경우)
                if not matched:
                    for original_keyword in original_keywords:
                        if original_keyword not in matched_original_keywords:
                            # 양방향 부분 매칭
                            if (selected in original_keyword or original_keyword in selected) and len(selected) >= 2:
                                filtered_dict[original_keyword] = original_keywords[original_keyword]
                                matched_original_keywords.add(original_keyword)
                                matched = True
                                logger.debug(f"부분 매칭: '{selected}' → '{original_keyword}'")
                                break
                
                if not matched:
                    logger.debug(f"매칭 실패: '{selected}'")
            
            logger.info(f"AI 응답 파싱 완료: {len(selected_keywords)}개 선택 → {len(filtered_dict)}개 매칭")
            
            # 매칭된 키워드들 로그 출력 (간소화)
            if filtered_dict:
                logger.info(f"매칭된 키워드 개수: {len(filtered_dict)}개")
            
            return filtered_dict
            
        except Exception as e:
            logger.error(f"AI 응답 파싱 중 오류: {e}")
            return {}
    
    def get_keyword_analysis(self, keywords_dict: Dict[str, int], company_name: str) -> str:
        """
        키워드에 대한 간단한 분석 제공
        
        Args:
            keywords_dict: 필터링된 키워드 딕셔너리
            company_name: 기업명
            
        Returns:
            str: 키워드 분석 결과
        """
        if not self.is_available() or not keywords_dict:
            return "키워드 분석을 위한 AI 서비스를 사용할 수 없습니다."
        
        try:
            top_keywords = list(keywords_dict.keys())[:10]
            keywords_str = ', '.join(top_keywords)
            
            prompt = f"""
{company_name}의 주요 뉴스 키워드를 분석해주세요.

키워드: {keywords_str}

이 키워드들을 바탕으로 다음 관점에서 간단히 분석해주세요:
1. 주요 이슈나 트렌드
2. 긍정적/부정적 요소
3. 주가에 미칠 수 있는 영향

200자 이내로 요약해주세요.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 금융 분석 전문가입니다. 키워드를 바탕으로 간단하고 명확한 분석을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"키워드 분석 중 오류: {e}")
            return "키워드 분석 중 오류가 발생했습니다."
