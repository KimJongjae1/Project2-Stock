# stock_data_system.py
import time
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
import pymysql
from sqlalchemy import create_engine, text
import warnings
import logging
import sys
import argparse
import os   #얜 임포트를 왜 안했는가

from stock_items_data import TICKER_TO_ITEM_NO  # item_no 매핑

warnings.filterwarnings('ignore')

# MySQL 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),     # <- 이거 로컬 호스트 기준으로 일단 바꿔놓음
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'ssafy'),
    'database': os.getenv('DB_NAME', 'survive_stock'),
    'charset': 'utf8mb4'
}

class StockDataSystem:
    def __init__(self):
        self.setup_logging()
        self.engine = None

    def setup_logging(self):
        log_file = f"stock_system_{datetime.now().strftime('%Y%m')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def create_connection(self):
        try:
            self.engine = create_engine(
                f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
            )
            return True
        except Exception as e:
            logging.error(f"MySQL 연결 실패: {e}")
            return False

    def check_data_exists(self, date_str):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM stock_infos WHERE date = :date"),
                    {'date': date_str}
                )
                return result.scalar_one() > 0
        except Exception as e:
            logging.error(f"데이터 존재 확인 실패: {e}")
            return False

    def add_market_cap_data(self, ticker, df, start_date_str, end_date_str):
        try:
            market_cap_df = stock.get_market_cap(start_date_str, end_date_str, ticker)
            df_copy = df.copy()
            if not market_cap_df.empty:
                df_copy['market_cap'] = (market_cap_df['시가총액'] / 100000000).astype(int)
            else:
                df_copy['market_cap'] = None
            return df_copy
        except Exception as e:
            logging.debug(f"시총 데이터 추가 실패 {ticker}: {e}")
            df_copy = df.copy()
            df_copy['market_cap'] = None
            return df_copy

    def save_stock_infos(self, ticker, company_name, df):
        try:
            df_copy = df.copy()
            df_copy['ticker'] = ticker
            df_copy['company_name'] = company_name
            df_copy['created_at'] = datetime.now()

            # 하드코딩 매핑으로 item_no 지정
            item_no = TICKER_TO_ITEM_NO.get(ticker)
            if item_no is None:
                logging.warning(f"{ticker}에 대한 item_no 없음")
                return False
            df_copy['item_no'] = item_no

            df_copy.reset_index(inplace=True)
            df_copy.rename(columns={
                '날짜': 'date',
                '시가': 'start_price',
                '고가': 'high_price',
                '저가': 'low_price',
                '종가': 'end_price',
                '거래량': 'volume'
            }, inplace=True)

            # 모든 컬럼 BIGINT/정수형으로 변환
            for col in ['start_price','end_price','high_price','low_price','volume','market_cap']:
                df_copy[col] = df_copy[col].fillna(0).astype(int)

            columns_order = [
                'item_no', 'date',
                'start_price', 'high_price', 'low_price', 'end_price', 'volume',
                'market_cap', 'created_at'
            ]
            df_copy = df_copy[columns_order]

            df_copy.to_sql(
                name='stock_infos',
                con=self.engine,
                if_exists='append',
                index=False,
                chunksize=1000
            )
            return True
        except Exception as e:
            if "Duplicate entry" in str(e):
                logging.warning(f"데이터 저장 경고 (중복) {ticker}: {df.index[0].strftime('%Y-%m-%d')}")
                return True
            logging.error(f"데이터 저장 실패 {ticker}: {e}")
            return False

    def collect_historical_data(self, years=5):
        logging.info(f"🏗️ {years}년치 히스토리컬 데이터 수집 시작")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")
        logging.info(f"수집 기간: {start_date_str} ~ {end_date_str}")

        tickers = list(TICKER_TO_ITEM_NO.keys())
        logging.info(f"총 {len(tickers)}개 종목")

        success_count = 0
        fail_count = 0

        for i, ticker in enumerate(tickers):
            try:
                df = stock.get_market_ohlcv(start_date_str, end_date_str, ticker)
                if df.empty:
                    fail_count += 1
                    continue
                company_name = stock.get_market_ticker_name(ticker)
                df_with_market_cap = self.add_market_cap_data(ticker, df, start_date_str, end_date_str)
                if self.save_stock_infos(ticker, company_name, df_with_market_cap):
                    success_count += 1
                    logging.info(f"✅ [{i+1:3d}/{len(tickers)}] {ticker} ({company_name}) - {len(df)}건")
                else:
                    fail_count += 1
                time.sleep(1.5)
            except Exception as e:
                fail_count += 1
                logging.error(f"❌ [{i+1:3d}/{len(tickers)}] {ticker} - {str(e)}")
                continue
            if (i + 1) % 20 == 0:
                progress = (i + 1) / len(tickers) * 100
                logging.info(f"📊 진행률: {progress:.1f}% (성공: {success_count}, 실패: {fail_count})")

        logging.info(f"🎉 히스토리컬 데이터 수집 완료! 성공: {success_count}, 실패: {fail_count}")
        return True

    def update_daily_data(self):
        logging.info("📅 일일 데이터 업데이트 시작")
        target_date = datetime.now() - timedelta(days=1)
        target_date_str = target_date.strftime("%Y%m%d")
        target_date_sql = target_date.strftime("%Y-%m-%d")

        logging.info(f"수집 대상: {target_date_str} ({target_date.strftime('%A')})")
        if self.check_data_exists(target_date_sql):
            logging.info(f"{target_date_sql} 데이터가 이미 존재합니다.")
            return True

        tickers = list(TICKER_TO_ITEM_NO.keys())
        logging.info(f"총 {len(tickers)}개 종목 처리")

        success_count = 0
        fail_count = 0

        for i, ticker in enumerate(tickers):
            try:
                df = stock.get_market_ohlcv(target_date_str, target_date_str, ticker)
                if df.empty:
                    fail_count += 1
                    continue
                company_name = stock.get_market_ticker_name(ticker)
                market_cap_df = stock.get_market_cap(target_date_str, target_date_str, ticker)
                if not market_cap_df.empty:
                    market_cap = int(market_cap_df.iloc[0]['시가총액'] / 100000000)
                    df['market_cap'] = market_cap
                else:
                    df['market_cap'] = 0
                if self.save_stock_infos(ticker, company_name, df):
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.5)
            except Exception as e:
                fail_count += 1
                logging.warning(f"{ticker} 실패: {str(e)}")
                continue
            if (i + 1) % 50 == 0:
                progress = (i + 1) / len(tickers) * 100
                logging.info(f"진행률: {progress:.1f}% ({i+1}/{len(tickers)})")

        logging.info(f"✅ 일일 업데이트 완료! 성공: {success_count}, 실패: {fail_count}")
        return True

    def show_status(self):
        if not self.engine:
            print("❌ 데이터베이스 연결이 필요합니다.")
            return
        try:
            with self.engine.connect() as conn:
                total_records = conn.execute(text("SELECT COUNT(*) FROM stock_infos")).scalar_one()
                unique_items = conn.execute(text("SELECT COUNT(DISTINCT item_no) FROM stock_infos")).scalar_one()
                date_range = conn.execute(text("SELECT MIN(date), MAX(date) FROM stock_infos")).fetchone()
                print("📊 데이터베이스 현황")
                print("=" * 60)
                print(f"총 레코드: {total_records:,}건")
                print(f"기업 수: {unique_items}개")
                if date_range and date_range[0]:
                    print(f"기간: {date_range[0]} ~ {date_range[1]}")
        except Exception as e:
            print(f"❌ 상태 확인 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description='통합 주식 데이터 시스템')
    parser.add_argument('command', nargs='?', choices=['init', 'update', 'status'], 
                        default='update', help='실행할 명령')
    parser.add_argument('--years', type=int, default=5, help='초기 데이터 수집 연수 (기본: 5년)')
    args = parser.parse_args()

    system = StockDataSystem()

    if not system.create_connection():
        sys.exit(1)

    if args.command == 'init':
        system.collect_historical_data(args.years)
    elif args.command == 'update':
        system.update_daily_data()
    elif args.command == 'status':
        system.show_status()

if __name__ == "__main__":
    main()

# 사용 예제:
# python stock_data_system.py init       # 5년치 초기 데이터 수집
# python stock_data_system.py update     # 일일 업데이트 (기본값)
# python stock_data_system.py status     # 현재 상태 확인
# python stock_data_system.py scheduler  # 24시간 스케줄러 실행