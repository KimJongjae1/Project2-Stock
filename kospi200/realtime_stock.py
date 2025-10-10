import asyncio
import json
import logging
import websockets
import pymysql
import time
import requests
from stock_items_data import TICKER_TO_ITEM_NO

# ===================== 설정 =====================
APP_KEY = "PSgXaH8s5e6LjYFuJcx6XIEt7fk4idpDKiOU"
SECRET_KEY = "rI+GejeP/8lysdn0ooKkuSNLTlXERdY6UtJHLNjaHwwRtd+cQ+70RKZyoDiU9SHjWMchZn0odqt+bitxZ47EnkSq3LPy/EvOrwZPmHJxCTfdKdlqPNy5oS6OE22xsS99whjbjuU4zGOL0AnwWRUo="
CUSTTYPE = "P"
TR_TYPE = "1"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ssafy",
    "database": "survive_stock",
    "charset": "utf8mb4"
}

prev_data = {}       # {ticker: price} 이전 가격 저장
BUFFER = {}          # 현재 배치에서 수신된 가격
SUBSCRIBED_CODES = set()
WS_CLIENTS = set()

# ===================== DB =====================
def create_table_if_not_exists():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_realtime (
            realtime_no INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(255) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            price VARCHAR(255) DEFAULT '0',
            rate VARCHAR(255) DEFAULT '0',
            item_no TINYINT UNSIGNED,
            UNIQUE KEY unique_ticker (ticker)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def initialize_realtime_table():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT ticker, company_name, item_no FROM stock_items")
    rows = cursor.fetchall()
    
    for row in rows:
        ticker = row["ticker"].strip()  # ✅ 공백 제거
        company_name = row["company_name"]
        item_no = row["item_no"]
        
        cursor.execute("""
            INSERT INTO stock_realtime (ticker, company_name, price, rate, item_no)
            VALUES (%s, %s, '0', '0', %s)
            ON DUPLICATE KEY UPDATE
                company_name = VALUES(company_name),
                item_no = VALUES(item_no)
        """, (ticker, company_name, item_no))
        
        prev_data[ticker] = 0.0
    
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("✅ stock_realtime 초기화 완료")

def save_realtime_stocks(buffer, name_map):
    if not buffer:
        return
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    ws_payload = []

    for ticker, price_str in buffer.items():
        ticker = ticker.strip()  # ✅ 항상 공백 제거
        price = float(price_str.replace(',', ''))
        prev_price = prev_data.get(ticker)
        rate = ((price - prev_price) / prev_price * 100) if prev_price else 0
        company_name = name_map[ticker]["company_name"]
        item_no = name_map[ticker]["item_no"]

        sql = """
            INSERT INTO stock_realtime (ticker, company_name, price, rate, item_no)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                price = VALUES(price),
                rate = VALUES(rate)
        """
        cursor.execute(sql, (ticker, company_name, price_str, rate, item_no))
        
        if cursor.rowcount == 1:
            logging.info(f"➕ 신규 INSERT: {ticker} | price={price_str}, rate={rate:.2f}%")
        elif cursor.rowcount == 2:
            logging.info(f"♻️ UPDATE: {ticker} | price={price_str}, rate={rate:.2f}%")
        else:
            logging.info(f"❗ 영향 없음: {ticker} | price={price_str}, rate={rate:.2f}%")

        prev_data[ticker] = price

        ws_payload.append({
            "ticker": ticker,
            "companyName": company_name,
            "price": price,
            "rate": round(rate, 2)
        })

    conn.commit()
    cursor.close()
    conn.close()

    asyncio.create_task(broadcast_ws(ws_payload))

# ===================== 종목 정보 맵 생성 =====================
def create_name_map():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT item_no, company_name, ticker FROM stock_items")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    name_map = {}
    for row in rows:
        name_map[row["ticker"].strip()] = {  # ✅ 공백 제거
            "company_name": row["company_name"],
            "item_no": row["item_no"]
        }
    return name_map

# ===================== WebSocket 브로드캐스트 =====================
async def broadcast_ws(payload):
    if WS_CLIENTS:
        message = json.dumps(payload)
        await asyncio.gather(*(client.send(message) for client in WS_CLIENTS))

async def ws_handler(websocket, path):
    WS_CLIENTS.add(websocket)
    logging.info(f"✅ WS 클라이언트 연결: {websocket.remote_address}")
    
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, company_name, price, rate, item_no FROM stock_realtime")
        rows = cursor.fetchall()
        await websocket.send(json.dumps(rows))
        cursor.close()
        conn.close()

        await websocket.wait_closed()
    finally:
        WS_CLIENTS.remove(websocket)
        logging.info(f"❌ WS 클라이언트 종료: {websocket.remote_address}")

# ===================== approval_key 발급 =====================
def get_approval_key():
    url = "https://openapi.koreainvestment.com:9443/oauth2/Approval"
    headers = {"Content-Type": "application/json"}
    data = {"appkey": APP_KEY, "secretkey": SECRET_KEY, "grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        logging.info(f"✅ approval_key 발급 성공")
        return result["approval_key"]
    else:
        logging.error(f"❌ approval_key 발급 실패: {response.text}")
        return None

# ===================== 배치 구독 =====================
async def subscribe_realtime_batch(batch_codes, name_map, approval_key, batch_idx):
    uri = "ws://ops.koreainvestment.com:31000"
    try:
        async with websockets.connect(uri, ping_interval=30, ping_timeout=20, close_timeout=10) as ws:
            header = {
                "approval_key": approval_key,
                "custtype": CUSTTYPE,
                "tr_type": TR_TYPE,
                "content-type": "utf-8"
            }
            
            # 구독 요청
            for code in batch_codes:
                body = {"input": {"tr_id": "H0STCNT0", "tr_key": code.strip()}}  # ✅ 공백 제거
                await ws.send(json.dumps({"header": header, "body": body}))
                await asyncio.sleep(0.1)
            SUBSCRIBED_CODES.update(batch_codes)
            
            batch_start_time = time.time()
            while time.time() - batch_start_time < 60:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1)
                    if "PINGPONG" in message or message.startswith("{"):
                        continue

                    parts = message.split("|")
                    if len(parts) < 4:
                        continue
                    data = parts[3].split("^")
                    if len(data) < 3:
                        continue
                    stock_code, price = data[0].strip(), data[2]  # ✅ 공백 제거
                    if stock_code in batch_codes and price and price != "0":
                        BUFFER[stock_code] = price
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logging.error(f"메시지 처리 오류: {e}")
            
            save_realtime_stocks(BUFFER, name_map)
            BUFFER.clear()
            
            # 구독 해제
            unsubscribe_header = {**header, "tr_type": "2"}
            for code in batch_codes:
                body = {"input": {"tr_id": "H0STCNT0", "tr_key": code.strip()}}  # ✅ 공백 제거
                await ws.send(json.dumps({"header": unsubscribe_header, "body": body}))
                await asyncio.sleep(0.05)
            SUBSCRIBED_CODES.difference_update(batch_codes)
            logging.info(f"✅ 배치 {batch_idx} 완료 후 구독 해제")
    except Exception as e:
        logging.error(f"❌ 웹소켓 오류: {e}")

# ===================== 메인 =====================
async def main():
    logging.info("🚀 주식 실시간 데이터 수집기 + WS 시작")
    create_table_if_not_exists()
    initialize_realtime_table()
    
    approval_key = get_approval_key()
    if not approval_key:
        logging.error("❌ approval_key 없으면 진행 불가")
        return
    
    name_map = create_name_map()
    batches = sorted(TICKER_TO_ITEM_NO.items(), key=lambda x: x[1])
    batch_size = 40
    batches = [[ticker.strip() for ticker,_ in batches[i:i+batch_size]] 
               for i in range(0,len(batches),batch_size)]
    
    ws_server = await websockets.serve(ws_handler, "localhost", 8765)
    
    while True:
        for batch_idx, batch_codes in enumerate(batches, 1):
            logging.info(f"🚀 배치 {batch_idx}/{len(batches)} 시작 ({len(batch_codes)}개)")
            await subscribe_realtime_batch(batch_codes, name_map, approval_key, batch_idx)
            await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("stock_collector_ws.log", encoding="utf-8")]
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 사용자 종료")
    except Exception as e:
        logging.error(f"❌ 예상치 못한 오류: {e}")
