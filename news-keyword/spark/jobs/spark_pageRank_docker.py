#!/usr/bin/env python3
"""
단순화된 KOSPI 200 기업 대상 Docker Spark 클러스터용 PageRank 분석기
- 직렬화 문제 완전 해결
- 사용법: docker exec -it spark-client python /opt/spark/jobs/spark_pageRank_kospi200_simple.py
"""

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
import pandas as pd
import numpy as np
import networkx as nx
import os
import glob
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 글로벌 KOSPI 200 기업 리스트 (클래스 외부에 정의)
KOSPI200_COMPANIES = [
    "BGF리테일","BNK금융지주","CJ","CJ대한통운","CJ제일제당",
    "DB손해보험","DL","DL이앤씨","DN오토모티브","F&F",
    "GKL","GS","GS건설","GS리테일","HDC",
    "HD한국조선해양","HD현대","HD현대마린솔루션","HD현대미포","HD현대인프라코어",
    "HD현대일렉트릭","HD현대중공업","HL만도","HMM","HS효성첨단소재",
    "JB금융지주","KB금융","KCC","KG모빌리티","KT",
    "KT&G",
    "LG","LG디스플레이","LG생활건강","LG에너지솔루션","LG유플러스",
    "LG이노텍","LG전자","LG화학","LIG넥스원","LS",
    "LS ELECTRIC","NAVER","NH투자증권","OCI","OCI홀딩스",
    "POSCO홀딩스","S-Oil","SK","SKC","SK바이오사이언스",
    "SK바이오팜","SK스퀘어","SK아이이테크놀로지","SK이노베이션","SK케미칼",
    "SK텔레콤","SK하이닉스","TCC스틸","TKG휴켐스","iM금융지주",
    "강원랜드","고려아연","금호석유화학","금호타이어","기아",
    "기업은행","넷마블","녹십자","녹십자홀딩스","농심",
    "대상","대우건설","대웅","대웅제약","대한유화",
    "대한전선","대한항공","더블유게임즈","덴티움","동서",
    "동원산업","동원시스템즈","두산","두산로보틱스","두산밥캣",
    "두산에너빌리티","롯데쇼핑","롯데웰푸드","롯데정밀화학","롯데지주",
    "롯데칠성","롯데케미칼","메리츠금융지주","미래에셋증권","미스토홀딩스",
    "미원상사","미원에스씨","삼성E&A","삼성SDI","삼성물산",
    "삼성바이오로직스","삼성생명","삼성에스디에스","삼성전기","삼성전자",
    "삼성중공업","삼성증권","삼성카드","삼성화재","삼양식품",
    "세방전지","세아베스틸지주","세아제강지주","셀트리온","신세계",
    "신한지주","씨에스윈드","아모레퍼시픽","아모레퍼시픽홀딩스","에스디바이오센서",
    "에스엘","에스원","에이피알","에코프로머티","엔씨소프트",
    "엘앤에프","영원무역","영원무역홀딩스","영풍","오뚜기",
    "오리온","오리온홀딩스","우리금융지주","유한양행","율촌화학",
    "이마트","이수스페셜티케미컬","제일기획","종근당","지역난방공사",
    "카카오","카카오뱅크","카카오페이","코스맥스","코스모화학",
    "코오롱인더","코웨이","크래프톤","키움증권","태광산업",
    "팬오션","포스코DX","포스코인터내셔널","포스코퓨처엠","풍산",
    "하나금융지주","하나투어","하이브","하이트진로","한국가스공사",
    "한국금융지주","한국앤컴퍼니","한국전력","한국카본","한국콜마",
    "한국타이어앤테크놀로지","한국항공우주","한미반도체","한미사이언스","한미약품",
    "한샘","한솔케미칼","한온시스템","한올바이오파마","한일시멘트",
    "한전KPS","한전기술","한진칼","한화","한화비전",
    "한화생명","한화솔루션","한화시스템","한화에어로스페이스","한화오션",
    "현대건설","현대글로비스","현대로템","현대모비스","현대백화점",
    "현대엘리베이터","현대위아","현대제철","현대차","현대해상",
    "호텔신라","효성중공업","효성티앤씨","후성"
]

def init_spark_session():
    """Spark 클러스터 세션 초기화 (Docker/EC2 자동 감지)"""
    try:
        # 실행 환경 감지
        is_docker = os.path.exists('/opt/spark/data')
        is_ec2 = os.path.exists('/opt/spark')
        
        if is_docker:
            print("🐳 Docker Spark 클러스터 연결 중...")
            master_url = "spark://spark-master:7077"
        elif is_ec2:
            print("☁️ EC2 Spark 클러스터 연결 중...")
            master_url = "spark://localhost:7077"
        else:
            print("💻 로컬 Spark 세션 시작...")
            master_url = "local[*]"
        
        spark = SparkSession.builder \
            .appName("SimpleKOSPI200PageRank") \
            .master(master_url) \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.shuffle.partitions", "400") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
            .config("spark.executor.memory", "3g") \
            .config("spark.executor.memoryOverhead", "1g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.network.timeout", "800s") \
            .config("spark.sql.broadcastTimeout", "600") \
            .getOrCreate()
        
        print(f"✅ Docker Spark 클러스터 연결 완료!")
        print(f"   Spark 버전: {spark.version}")
        
        # S3 설정 (환경변수 기반)
        try:
            hconf = spark._jsc.hadoopConfiguration()
            hconf.set("fs.s3a.aws.credentials.provider", "com.amazonaws.auth.EnvironmentVariableCredentialsProvider")
            region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
            if region:
                hconf.set("fs.s3a.endpoint", f"s3.{region}.amazonaws.com")
            if os.getenv("S3_PATH_STYLE", "false").lower() in ("1","true","yes"):
                hconf.set("fs.s3a.path.style.access", "true")
        except Exception:
            pass
        
        return spark
        
    except Exception as e:
        print(f"❌ Docker Spark 클러스터 연결 실패: {e}")
        sys.exit(1)

def load_data(spark, file_path):
    """CSV 또는 Excel 파일을 Spark DataFrame으로 로드 (로컬/S3 지원)"""
    
    print("📁 파일 로드 중...")
    print("=" * 50)
    
    try:
        # S3 경로 확인
        is_s3_path = file_path.startswith('s3a://') or file_path.startswith('s3://')
        
        if is_s3_path:
            print(f"☁️ S3 파일 감지: {file_path}")
        else:
            print(f"📄 로컬 파일 감지: {file_path}")
        
        # 파일 확장자 확인
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            print("📊 Excel 파일 감지 - Pandas로 읽기")
            
            if is_s3_path:
                print("⚠️ S3의 Excel 파일은 직접 읽을 수 없습니다. CSV로 변환 후 사용하세요.")
                return None
            
            # Pandas로 엑셀 읽기
            import pandas as pd
            pandas_df = pd.read_excel(file_path)
            
            # Spark DataFrame으로 변환
            news_df = spark.createDataFrame(pandas_df)
            
            print(f"✅ Excel 파일 로드 성공!")
            print(f"   원본 행 수: {len(pandas_df):,}건")
            
        else:
            print("📄 CSV 파일 감지 - Spark로 읽기")
            
            # CSV 파일 읽기 (다양한 옵션 시도)
            news_df = spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .option("encoding", "UTF-8") \
                .option("sep", ",") \
                .option("quote", '"') \
                .option("escape", '"') \
                .option("multiLine", "true") \
                .option("ignoreLeadingWhiteSpace", "true") \
                .option("ignoreTrailingWhiteSpace", "true") \
                .csv(file_path)
        
        news_df.cache()
        
        total_count = news_df.count()
        column_count = len(news_df.columns)
        
        print(f"✅ 파일 로드 성공!")
        print(f"   전체 뉴스: {total_count:,}건")
        print(f"   컬럼 수: {column_count}개")
        
        # 컬럼 정보 출력
        print(f"\n📋 컬럼 정보:")
        print("-" * 60)
        for i, col in enumerate(news_df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 샘플 데이터 확인
        print("\n🔍 데이터 샘플 확인:")
        print("-" * 80)
        sample_data = news_df.limit(3).collect()
        for i, row in enumerate(sample_data, 1):
            print(f"\n📄 샘플 {i}:")
            row_dict = dict(row.asDict())
            for key, value in row_dict.items():
                # 값이 너무 길면 잘라서 표시
                if isinstance(value, str) and len(value) > 100:
                    display_value = value[:100] + "..."
                else:
                    display_value = value
                print(f"   {key}: {display_value}")
            print("-" * 40)
        
        return news_df
        
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_kospi200_connections(spark, news_df):
    """KOSPI 200 기업 간 연결 관계 추출 (완전 함수형)"""
    
    print(f"\n🔗 KOSPI 200 기업 간 연결 관계 추출")
    print("=" * 50)
    
    # '기관' 컬럼 찾기
    org_column = None
    columns = news_df.columns
    print(columns)
    for column_name in columns:
        if '기관' in column_name:
            org_column = column_name
            break
    
    if org_column is None:
        print("❌ '기관' 컬럼을 찾을 수 없습니다!")
        return None
    
    print(f"✅ 기관 컬럼 발견: '{org_column}'")
    
    try:
        # 1단계: 기본 필터링
        print("🔄 1단계: 기본 데이터 필터링...")
        valid_news = news_df.filter(
            F.col(org_column).isNotNull() & 
            (F.col(org_column) != "") &
            (F.length(F.col(org_column)) > 1)
        )
        
        valid_count = valid_news.count()
        print(f"   유효한 뉴스: {valid_count:,}건")
        
        if valid_count == 0:
            print("❌ 유효한 기관 정보가 없습니다!")
            return None
        
        # 2단계: 뉴스별 ID 추가하여 같은 뉴스 내 기업들 그룹핑
        print("🔄 2단계: 뉴스별 ID 추가...")
        news_with_id = valid_news.select(
            F.monotonically_increasing_id().alias("news_id"),
            F.col(org_column).alias("companies")
        )
        
        # 3단계: 기업명 분리
        print("🔄 3단계: 기업명 분리...")
        companies_exploded = news_with_id.select(
            "news_id",
            F.explode(F.split(F.col("companies"), ",")).alias("company")
        ).select(
            "news_id",
            F.trim(F.col("company")).alias("company")
        ).filter(
            (F.col("company") != "") & 
            (F.length(F.col("company")) > 1)
        )
        
        # 4단계: KOSPI 200 기업만 필터링 (IN 연산자 사용)
        print("🔄 4단계: KOSPI 200 기업 필터링...")
        kospi200_companies_filtered = companies_exploded.filter(
            F.col("company").isin(KOSPI200_COMPANIES)
        )
        
        kospi_count = kospi200_companies_filtered.select("company").distinct().count()
        print(f"   발견된 KOSPI 200 기업: {kospi_count}개")
        
        if kospi_count == 0:
            print("❌ 데이터에서 KOSPI 200 기업을 찾을 수 없습니다!")
            return None
        
        # 5단계: 같은 뉴스 내에서 기업 간 연결 생성 (뉴스 내 동일 기업 중복 제거 후 쌍 생성)
        print("🔄 5단계: 기업 간 연결 관계 생성...")
        # 뉴스 내 중복 기업 제거
        dedup_companies = kospi200_companies_filtered.select("news_id", "company").distinct()

        # Self-join으로 같은 뉴스 내 기업 쌍 생성 (사전순 정렬로 중복 제거)
        connections = dedup_companies.alias("c1").join(
            dedup_companies.alias("c2"),
            (F.col("c1.news_id") == F.col("c2.news_id")) & 
            (F.col("c1.company") < F.col("c2.company"))  # 중복 제거 및 순서 정렬
        ).select(
            F.col("c1.company").alias("company1"),
            F.col("c2.company").alias("company2")
        )
        
        # 6단계: 연결 강도 계산
        print("🔄 6단계: 연결 강도 계산...")
        connections_df = connections.groupBy("company1", "company2") \
            .count() \
            .withColumnRenamed("count", "weight") \
            .filter(F.col("weight") > 0)
        
        connections_df.cache()
        
        # 통계
        connection_count = connections_df.count()
        
        if connection_count == 0:
            print("❌ KOSPI 200 기업 간 연결 관계를 찾을 수 없습니다!")
            return None
        
        avg_weight = connections_df.agg(F.avg("weight")).collect()[0][0]
        max_weight = connections_df.agg(F.max("weight")).collect()[0][0]
        
        participating_companies = connections_df.select("company1").union(
            connections_df.select("company2")
        ).distinct().count()
        
        print(f"📊 KOSPI 200 추출 결과:")
        print(f"   참여 기업 수: {participating_companies}개")
        print(f"   총 연결 관계: {connection_count:,}개")
        print(f"   평균 연결 강도: {avg_weight:.1f}회")
        print(f"   최대 연결 강도: {max_weight}회")
        
        # 상위 연결 관계 출력
        print(f"\n🔗 강한 연결 관계 TOP 5:")
        top_connections = connections_df.orderBy(F.desc("weight")).limit(5).collect()
        for i, row in enumerate(top_connections, 1):
            print(f"   {i}. {row['company1']} ↔ {row['company2']}: {row['weight']}회")
        
        return connections_df
        
    except Exception as e:
        print(f"❌ 연결 관계 추출 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_pagerank(spark, connections_df):
    """KOSPI 200 PageRank 계산 (함수형)"""
    
    print(f"\n🏆 KOSPI 200 PageRank 계산")
    print("=" * 40)
    
    try:
        # 정점 준비
        vertices = connections_df.select(F.col("company1").alias("company")).union(
            connections_df.select(F.col("company2").alias("company"))
        ).distinct()
        
        num_vertices = vertices.count()
        print(f"   분석 대상 기업 수: {num_vertices}개")
        
        edges = connections_df.select(
            F.col("company1").alias("src"),
            F.col("company2").alias("dst"),
            F.col("weight").cast("double")
        ).repartition(400, "src")

        # 무방향 등가: 엣지 대칭화 후 합치기 (가중치 합산)
        edges_sym = edges.unionByName(
            edges.select(
                F.col("dst").alias("src"),
                F.col("src").alias("dst"),
                F.col("weight").alias("weight")
            )
        )
        edges = edges_sym.groupBy("src", "dst").agg(F.sum("weight").alias("weight"))
        
        # PageRank 파라미터
        damping = 0.85
        base_val = (1.0 - damping) / float(num_vertices)
        
        # 초기 rank
        ranks = vertices.withColumn("rank", F.lit(1.0 / float(num_vertices)))
        
        # out-degree 계산
        out_weight = edges.groupBy("src").agg(F.sum("weight").alias("out_w"))
        edges_norm = edges.join(out_weight, on="src", how="left").withColumn(
            "norm_w", F.when(F.col("out_w") > 0, F.col("weight") / F.col("out_w")).otherwise(F.lit(0.0))
        ).select("src", "dst", "norm_w")
        
        # 반복 계산 (수렴 조건 추가)
        iterations = 30  # 25 → 30으로 증가
        convergence_threshold = 1e-6  # 수렴 임계값
        print(f"🔄 PageRank 반복 계산 (최대 {iterations}회, 수렴 임계값: {convergence_threshold})...")
        
        for i in range(iterations):
            # 이전 rank 저장 (수렴 체크용)
            prev_ranks = ranks
            
            # contribution 계산
            contribs = edges_norm.join(
                ranks.withColumnRenamed("company", "src"), on="src", how="left"
            ).withColumn(
                "contrib", F.col("rank") * F.col("norm_w")
            ).groupBy("dst").agg(F.sum("contrib").alias("sum_contrib"))
            
            # 새로운 rank 계산
            ranks = vertices.join(
                contribs.withColumnRenamed("dst", "company"), on="company", how="left"
            ).withColumn(
                "sum_contrib", F.coalesce(F.col("sum_contrib"), F.lit(0.0))
            ).withColumn(
                "rank", F.lit(base_val) + F.lit(damping) * F.col("sum_contrib")
            ).select("company", "rank")
            
            # 수렴 체크 (매 5회마다)
            if (i + 1) % 5 == 0:
                # rank 변화량 계산
                rank_diff = ranks.join(
                    prev_ranks.withColumnRenamed("rank", "prev_rank"), 
                    on="company", how="inner"
                ).withColumn(
                    "diff", F.abs(F.col("rank") - F.col("prev_rank"))
                ).agg(F.max("diff")).collect()[0][0]
                
                print(f"   반복 {i + 1}/{iterations} 완료 (최대 변화량: {rank_diff:.8f})")
                
                # 수렴 확인
                if rank_diff < convergence_threshold:
                    print(f"   ✅ {i + 1}회 반복에서 수렴 완료!")
                    break
        
        pagerank_results = ranks.select(
            F.col("company"), F.col("rank").alias("pagerank_score")
        ).orderBy(F.desc("pagerank_score"))
        
        print(f"✅ PageRank 계산 완료!")
        
        # 결과 출력
        print(f"\n🏆 KOSPI 200 영향력 순위:")
        print(f"{'순위':>4} {'기업명':>20} {'PageRank 점수':>15} {'상대 점수':>10}")
        print("-" * 60)
        
        top_results = pagerank_results.limit(15).collect()
        max_score = top_results[0]['pagerank_score'] if top_results else 0
        
        for i, row in enumerate(top_results, 1):
            company = row['company']
            score = row['pagerank_score']
            relative = (score / max_score) * 100 if max_score > 0 else 0
            print(f"{i:>4} {company:>20} {score:>15.6f} {relative:>9.1f}%")
        
        return pagerank_results
        
    except Exception as e:
        print(f"❌ PageRank 계산 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_company_from_s3(spark, company_name, s3_bucket, s3_prefix):
    """S3에 저장된 PageRank 결과를 기반으로 특정 기업 분석"""
    
    print(f"\n🔍 '{company_name}' 기업 상세 분석 (S3 기반)")
    print("=" * 60)
    
    try:
        # S3에서 PageRank 결과 로드
        pagerank_path = f"s3a://{s3_bucket}/{s3_prefix}/pagerank/"
        connections_path = f"s3a://{s3_bucket}/{s3_prefix}/connections/"
        
        print(f"📁 S3에서 데이터 로드 중...")
        print(f"   PageRank: {pagerank_path}")
        print(f"   Connections: {connections_path}")
        
        # PageRank 결과 로드
        try:
            pagerank_results = spark.read.parquet(pagerank_path)
            print(f"✅ PageRank 결과 로드 완료: {pagerank_results.count()}개 기업")
        except Exception as e:
            print(f"❌ PageRank 결과 로드 실패: {e}")
            print("💡 먼저 PageRank 분석을 실행하여 S3에 결과를 저장하세요.")
            return
        
        # 연결 관계 로드
        try:
            connections_df = spark.read.parquet(connections_path)
            print(f"✅ 연결 관계 로드 완료: {connections_df.count()}개 연결")
        except Exception as e:
            print(f"❌ 연결 관계 로드 실패: {e}")
            print("💡 연결 관계 데이터가 없습니다.")
            connections_df = None
        
        # 1. PageRank 점수 확인
        company_pagerank = pagerank_results.filter(
            F.col("company").contains(company_name)
        ).collect()
        
        if not company_pagerank:
            print(f"❌ '{company_name}' 기업을 찾을 수 없습니다!")
            print("💡 기업명을 정확히 입력해주세요. (예: 삼성전자, 현대차)")
            
            # 유사한 기업명 제안
            print(f"\n🔍 유사한 기업명 제안:")
            similar_companies = pagerank_results.filter(
                F.col("company").rlike(f".*{company_name}.*")
            ).limit(5).collect()
            
            if similar_companies:
                for i, row in enumerate(similar_companies, 1):
                    print(f"   {i}. {row['company']}")
            else:
                print("   유사한 기업명을 찾을 수 없습니다.")
            return
        
        # 2. PageRank 정보
        company_score = company_pagerank[0]['pagerank_score']
        total_companies = pagerank_results.count()
        
        # 전체 순위 계산
        rank_position = pagerank_results.filter(
            F.col("pagerank_score") > company_score
        ).count() + 1
        
        print(f"📊 기본 정보:")
        print(f"   기업명: {company_pagerank[0]['company']}")
        print(f"   PageRank 점수: {company_score:.6f}")
        print(f"   전체 순위: {rank_position}위 / {total_companies}개 기업")
        print(f"   상위 {rank_position/total_companies*100:.1f}%")
        
        # 3. 연결 관계 분석 (연결 데이터가 있는 경우)
        if connections_df is not None:
            company_connections = connections_df.filter(
                (F.col("company1").contains(company_name)) | 
                (F.col("company2").contains(company_name))
            )
            
            total_connections = company_connections.count()
            
            if total_connections > 0:
                avg_weight = company_connections.agg(F.avg("weight")).collect()[0][0]
                max_weight = company_connections.agg(F.max("weight")).collect()[0][0]
                
                print(f"\n🔗 연결 관계 분석:")
                print(f"   총 연결 수: {total_connections}개")
                print(f"   평균 연결 강도: {avg_weight:.1f}회")
                print(f"   최대 연결 강도: {max_weight}회")
                
                # 4. 주요 연결 기업들
                print(f"\n🤝 주요 연결 기업 TOP 10:")
                print("-" * 50)
                
                # company1이 대상 기업인 경우
                connections_as_source = company_connections.filter(
                    F.col("company1").contains(company_name)
                ).select(
                    F.col("company2").alias("partner"),
                    F.col("weight")
                )
                
                # company2가 대상 기업인 경우
                connections_as_target = company_connections.filter(
                    F.col("company2").contains(company_name)
                ).select(
                    F.col("company1").alias("partner"),
                    F.col("weight")
                )
                
                # 모든 연결 통합
                all_connections = connections_as_source.union(connections_as_target)
                
                # 파트너별 총 연결 강도 계산
                partner_connections = all_connections.groupBy("partner").agg(
                    F.sum("weight").alias("total_weight")
                ).orderBy(F.desc("total_weight")).limit(10)
                
                top_partners = partner_connections.collect()
                for i, row in enumerate(top_partners, 1):
                    print(f"   {i:2d}. {row['partner']}: {row['total_weight']}회")
                
                # 5. 연결 패턴 분석
                print(f"\n📈 연결 패턴 분석:")
                
                # 연결 강도 분포
                weight_distribution = company_connections.groupBy("weight").count().orderBy("weight").collect()
                print(f"   연결 강도 분포:")
                for row in weight_distribution:
                    print(f"     {row['weight']}회: {row['count']}개 연결")
                
                # 6. 영향력 분석
                print(f"\n💡 영향력 분석:")
                
                # 높은 연결 강도를 가진 관계들
                strong_connections = company_connections.filter(F.col("weight") >= 5).count()
                print(f"   강한 연결 (5회 이상): {strong_connections}개")
                
                # 연결 다양성
                unique_partners = all_connections.select("partner").distinct().count()
                print(f"   연결된 기업 수: {unique_partners}개")
                print(f"   연결 다양성: {unique_partners/total_connections*100:.1f}%")
                
            else:
                print(f"\n❌ '{company_name}'과 연결된 기업이 없습니다.")
                print("   이 기업은 뉴스에서 다른 KOSPI 200 기업과 함께 언급되지 않았습니다.")
        else:
            print(f"\n⚠️  연결 관계 데이터가 없어 연결 분석을 건너뜁니다.")
        
        # 7. 상대적 위치 분석
        print(f"\n📊 상대적 위치 분석:")
        
        # 상위 10% 기업들과 비교
        top_10_percent = int(total_companies * 0.1)
        top_companies = pagerank_results.limit(top_10_percent).collect()
        top_scores = [row['pagerank_score'] for row in top_companies]
        
        if company_score >= top_scores[-1]:
            print(f"   🏆 상위 10% 기업에 속합니다!")
        elif rank_position <= total_companies * 0.3:
            print(f"   🥈 상위 30% 기업에 속합니다.")
        elif rank_position <= total_companies * 0.5:
            print(f"   🥉 상위 50% 기업에 속합니다.")
        else:
            print(f"   📉 하위 50% 기업에 속합니다.")
        
        # 8. 권장사항
        print(f"\n💭 분석 결과:")
        if company_score > 0.01:
            print(f"   ✅ '{company_name}'은 높은 영향력을 가진 기업입니다.")
            print(f"   📈 뉴스에서 자주 언급되며 다른 기업들과 강한 연결을 가지고 있습니다.")
        elif company_score > 0.005:
            print(f"   ⚖️  '{company_name}'은 중간 수준의 영향력을 가진 기업입니다.")
            print(f"   📊 적당한 연결 관계를 가지고 있습니다.")
        else:
            print(f"   ⚠️  '{company_name}'은 상대적으로 낮은 영향력을 가진 기업입니다.")
            print(f"   📉 뉴스에서의 언급 빈도나 연결 관계가 제한적입니다.")
        
        # 9. S3 저장 (선택사항)
        save_analysis = input(f"\n💾 이 분석 결과를 S3에 저장하시겠습니까? (y/n): ").strip().lower()
        if save_analysis == 'y':
            analysis_path = f"s3a://{s3_bucket}/{s3_prefix}/company_analysis/{company_name.replace(' ', '_')}/"
            
            # 분석 결과를 DataFrame으로 변환하여 저장
            analysis_data = [
                ("company_name", company_name),
                ("pagerank_score", company_score),
                ("rank_position", rank_position),
                ("total_companies", total_companies),
                ("analysis_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ]
            
            analysis_df = spark.createDataFrame(analysis_data, ["metric", "value"])
            analysis_df.write.mode("overwrite").parquet(analysis_path)
            print(f"✅ 분석 결과 저장 완료: {analysis_path}")
        
    except Exception as e:
        print(f"❌ 기업 분석 실패: {e}")
        import traceback
        traceback.print_exc()

def analyze_company(spark, company_name, pagerank_results, connections_df):
    """특정 기업에 대한 상세 분석 (로컬 데이터 기반)"""
    
    print(f"\n🔍 '{company_name}' 기업 상세 분석")
    print("=" * 60)
    
    try:
        # 1. PageRank 점수 확인
        company_pagerank = pagerank_results.filter(
            F.col("company").contains(company_name)
        ).collect()
        
        if not company_pagerank:
            print(f"❌ '{company_name}' 기업을 찾을 수 없습니다!")
            print("💡 기업명을 정확히 입력해주세요. (예: 삼성전자, 현대차)")
            return
        
        # 2. PageRank 정보
        company_score = company_pagerank[0]['pagerank_score']
        total_companies = pagerank_results.count()
        
        # 전체 순위 계산
        rank_position = pagerank_results.filter(
            F.col("pagerank_score") > company_score
        ).count() + 1
        
        print(f"📊 기본 정보:")
        print(f"   기업명: {company_pagerank[0]['company']}")
        print(f"   PageRank 점수: {company_score:.6f}")
        print(f"   전체 순위: {rank_position}위 / {total_companies}개 기업")
        print(f"   상위 {rank_position/total_companies*100:.1f}%")
        
        # 3. 연결 관계 분석
        company_connections = connections_df.filter(
            (F.col("company1").contains(company_name)) | 
            (F.col("company2").contains(company_name))
        )
        
        total_connections = company_connections.count()
        
        if total_connections > 0:
            avg_weight = company_connections.agg(F.avg("weight")).collect()[0][0]
            max_weight = company_connections.agg(F.max("weight")).collect()[0][0]
            
            print(f"\n🔗 연결 관계 분석:")
            print(f"   총 연결 수: {total_connections}개")
            print(f"   평균 연결 강도: {avg_weight:.1f}회")
            print(f"   최대 연결 강도: {max_weight}회")
            
            # 4. 주요 연결 기업들
            print(f"\n🤝 주요 연결 기업 TOP 10:")
            print("-" * 50)
            
            # company1이 대상 기업인 경우
            connections_as_source = company_connections.filter(
                F.col("company1").contains(company_name)
            ).select(
                F.col("company2").alias("partner"),
                F.col("weight")
            )
            
            # company2가 대상 기업인 경우
            connections_as_target = company_connections.filter(
                F.col("company2").contains(company_name)
            ).select(
                F.col("company1").alias("partner"),
                F.col("weight")
            )
            
            # 모든 연결 통합
            all_connections = connections_as_source.union(connections_as_target)
            
            # 파트너별 총 연결 강도 계산
            partner_connections = all_connections.groupBy("partner").agg(
                F.sum("weight").alias("total_weight")
            ).orderBy(F.desc("total_weight")).limit(10)
            
            top_partners = partner_connections.collect()
            for i, row in enumerate(top_partners, 1):
                print(f"   {i:2d}. {row['partner']}: {row['total_weight']}회")
            
            # 5. 연결 패턴 분석
            print(f"\n📈 연결 패턴 분석:")
            
            # 연결 강도 분포
            weight_distribution = company_connections.groupBy("weight").count().orderBy("weight").collect()
            print(f"   연결 강도 분포:")
            for row in weight_distribution:
                print(f"     {row['weight']}회: {row['count']}개 연결")
            
            # 6. 영향력 분석
            print(f"\n💡 영향력 분석:")
            
            # 높은 연결 강도를 가진 관계들
            strong_connections = company_connections.filter(F.col("weight") >= 5).count()
            print(f"   강한 연결 (5회 이상): {strong_connections}개")
            
            # 연결 다양성
            unique_partners = all_connections.select("partner").distinct().count()
            print(f"   연결된 기업 수: {unique_partners}개")
            print(f"   연결 다양성: {unique_partners/total_connections*100:.1f}%")
            
        else:
            print(f"\n❌ '{company_name}'과 연결된 기업이 없습니다.")
            print("   이 기업은 뉴스에서 다른 KOSPI 200 기업과 함께 언급되지 않았습니다.")
        
        # 7. 권장사항
        print(f"\n💭 분석 결과:")
        if company_score > 0.01:
            print(f"   ✅ '{company_name}'은 높은 영향력을 가진 기업입니다.")
            print(f"   📈 뉴스에서 자주 언급되며 다른 기업들과 강한 연결을 가지고 있습니다.")
        elif company_score > 0.005:
            print(f"   ⚖️  '{company_name}'은 중간 수준의 영향력을 가진 기업입니다.")
            print(f"   📊 적당한 연결 관계를 가지고 있습니다.")
        else:
            print(f"   ⚠️  '{company_name}'은 상대적으로 낮은 영향력을 가진 기업입니다.")
            print(f"   📉 뉴스에서의 언급 빈도나 연결 관계가 제한적입니다.")
        
    except Exception as e:
        print(f"❌ 기업 분석 실패: {e}")
        import traceback
        traceback.print_exc()


def main():
    """메인 실행 함수 (완전 함수형)"""
    
    print("🚀 단순화된 KOSPI 200 PageRank 분석기")
    print("=" * 50)
    
    # 데이터 소스 확인 (S3 또는 로컬)
    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX", "data")
    
    if s3_bucket:
        # S3에서 데이터 읽기
        s3_data_path = f"s3a://{s3_bucket}/{s3_prefix}/data/*.csv"
        print(f"☁️ S3 데이터 소스: {s3_data_path}")
        csv_file = s3_data_path
    else:
        # 로컬 데이터 읽기
        csv_files = ["/opt/spark/data/*.csv"]
        
        print("📁 로컬 CSV 파일 검색 중...")
        csv_file = None
        for file in csv_files:
            if any(ch in file for ch in ['*', '?', '[']):
                matched = glob.glob(file)
                if matched:
                    csv_file = file
                    print(f"✅ 매칭된 파일 {len(matched)}개: {file}")
                    break
        
        if csv_file is None:
            print("❌ 로컬 CSV 파일을 찾을 수 없습니다!")
            print("💡 S3 사용: docker-compose.yml에 S3_BUCKET 환경변수 설정")
            return
    
    # Spark 세션 초기화
    spark = init_spark_session()
    
    try:
        # 1. 데이터 로드 (CSV 또는 Excel)
        news_df = load_data(spark, csv_file)
        if news_df is None:
            return
        
        # 2. 연결 관계 추출
        connections_df = extract_kospi200_connections(spark, news_df)
        if connections_df is None:
            return
        
        # 3. PageRank 계산
        pagerank_results = calculate_pagerank(spark, connections_df)
        if pagerank_results is None:
            return
        
        print(f"\n🎉 KOSPI 200 분석 완료!")
        
        # S3 저장 (환경변수 S3_BUCKET/S3_PREFIX 설정 시)
        bucket = os.getenv("S3_BUCKET")
        prefix = os.getenv("S3_PREFIX", "outputs/pagerank").rstrip("/")
        if bucket:
            base = f"s3a://{bucket}/{prefix}"
            try:
                print(f"\n☁️  S3 저장 중: {base}")
                pagerank_results.write.mode("overwrite").parquet(f"{base}/pagerank/")
                connections_df.write.mode("overwrite").parquet(f"{base}/connections/")
                print("✅ S3 Parquet 저장 완료")
                if os.getenv("EXPORT_CSV", "false").lower() in ("1","true","yes"):
                    pagerank_results.coalesce(1).write.mode("overwrite").option("header","true").csv(f"{base}/pagerank_csv/")
                    print("✅ S3 CSV 내보내기 완료")
            except Exception as e:
                print(f"❌ S3 저장 실패: {e}")
        
        total_companies = pagerank_results.count()
        print(f"\n📈 분석 요약:")
        print(f"   분석된 기업 수: {total_companies}개")
        
        top_3 = pagerank_results.limit(3).collect()
        print(f"   TOP 3 영향력 기업:")
        for i, row in enumerate(top_3, 1):
            print(f"     {i}. {row['company']} (점수: {row['pagerank_score']:.6f})")
        
        # # 기업 상세 분석 (S3 기반)
        # print(f"\n" + "="*60)
        # print("🔍 기업 상세 분석 모드 (S3 기반)")
        # print("="*60)
        
        # # S3 설정 확인
        # s3_bucket = os.getenv("S3_BUCKET")
        # s3_prefix = os.getenv("S3_PREFIX", "outputs/pagerank")
        
        # if s3_bucket:
        #     print(f"☁️ S3 기반 분석 모드")
        #     print(f"   버킷: {s3_bucket}")
        #     print(f"   경로: {s3_prefix}")
            
        #     while True:
        #         try:
        #             company_input = input("\n📝 분석할 기업명을 입력하세요 (종료: 'quit'): ").strip()
                    
        #             if company_input.lower() in ['quit', 'exit', 'q']:
        #                 print("👋 분석을 종료합니다.")
        #                 break
                    
        #             if not company_input:
        #                 print("⚠️  기업명을 입력해주세요.")
        #                 continue
                    
        #             # S3 기반 기업 분석 실행
        #             analyze_company_from_s3(spark, company_input, s3_bucket, s3_prefix)
                    
        #         except KeyboardInterrupt:
        #             print("\n👋 분석을 종료합니다.")
        #             break
        #         except Exception as e:
        #             print(f"❌ 입력 처리 오류: {e}")
        #             continue
        # else:
        #     print(f"⚠️  S3_BUCKET 환경변수가 설정되지 않아 S3 기반 분석을 사용할 수 없습니다.")
        #     print(f"💡 환경변수를 설정하거나 로컬 분석을 사용하세요.")
            
        #     # 로컬 분석 모드 (기존 방식)
        #     print(f"\n🔍 로컬 분석 모드")
        #     while True:
        #         try:
        #             company_input = input("\n📝 분석할 기업명을 입력하세요 (종료: 'quit'): ").strip()
                    
        #             if company_input.lower() in ['quit', 'exit', 'q']:
        #                 print("👋 분석을 종료합니다.")
        #                 break
                    
        #             if not company_input:
        #                 print("⚠️  기업명을 입력해주세요.")
        #                 continue
                    
        #             # 로컬 기업 분석 실행 (기존 함수 사용)
        #             analyze_company(spark, company_input, pagerank_results, connections_df)
                    
        #         except KeyboardInterrupt:
        #             print("\n👋 분석을 종료합니다.")
        #             break
        #         except Exception as e:
        #             print(f"❌ 입력 처리 오류: {e}")
        #             continue
    
    finally:
        print("🔄 Spark 세션 종료 중...")
        spark.stop()
        print("✅ 완료")

if __name__ == "__main__":
    main()