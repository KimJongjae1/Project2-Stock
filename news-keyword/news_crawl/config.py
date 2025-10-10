# BIG KINDS 자동화 설정 파일

# 로그인 정보
LOGIN_EMAIL = "jack0810@kookmin.ac.kr"
LOGIN_PASSWORD = "0810jack!"

# 검색 설정
DEFAULT_SEARCH_PERIOD_DAYS = 0  # 기본 검색 기간 (일)

# 웹 요소 대기 시간 (초)
WAIT_TIMEOUT = 20
PAGE_LOAD_WAIT = 3
ELEMENT_WAIT = 2

# Chrome 브라우저 설정
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    # "--headless",  # 헤드리스 모드 (필요시 주석 해제)
]

# 다운로드 설정
DOWNLOAD_WAIT_TIME = 10  # 엑셀 다운로드 완료 대기 시간 (초)

# S3 설정
S3_BUCKET_NAME = "cheesecrust-spark-data-bucket"  # S3 버킷 이름
S3_REGION = "ap-northeast-2"  # 서울 리전
S3_PREFIX = "outputs/pagerank/data/"  # S3 키 접두사

# AWS 자격 증명 (환경 변수에서 가져옴)
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN

# 로그 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "bigkinds_automation.log"

