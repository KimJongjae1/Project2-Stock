import time
import os
import glob
import pandas as pd
import boto3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import logging

class BigKindsAutomation:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        self.wait = None
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        # Docker 환경에서는 logs 디렉토리 사용
        log_dir = os.environ.get('LOG_DIR', '.')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'bigkinds_automation.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Chrome/Chromium 드라이버 설정"""
        try:
            chrome_options = Options()
            
            # Docker 환경에서 필요한 옵션들
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Docker 환경에서 헤드리스 모드 활성화
            if os.environ.get('DOCKER_ENV') == 'true' or not os.environ.get('DISPLAY'):
                chrome_options.add_argument("--headless")
                self.logger.info("Docker 환경에서 헤드리스 모드로 실행")
            
            # 다운로드 경로 설정
            download_dir = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
            os.makedirs(download_dir, exist_ok=True)
            self.download_dir = download_dir
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Docker 환경에서 Chromium 사용
            if os.environ.get('DOCKER_ENV') == 'true':
                # Chromium 바이너리 경로 설정
                chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
                if os.path.exists(chrome_bin):
                    chrome_options.binary_location = chrome_bin
                    self.logger.info(f"Chromium 바이너리 사용: {chrome_bin}")
                else:
                    self.logger.warning(f"Chromium 바이너리를 찾을 수 없습니다: {chrome_bin}")
                
                # Chromium 드라이버 경로 설정
                chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
                if os.path.exists(chromedriver_path):
                    service = Service(chromedriver_path)
                    self.logger.info(f"Chromium 드라이버 사용: {chromedriver_path}")
                else:
                    self.logger.warning(f"Chromium 드라이버를 찾을 수 없습니다: {chromedriver_path}")
                    # 기본 ChromeDriver 사용
                    service = Service(ChromeDriverManager().install())
            else:
                # 로컬 환경에서는 기본 ChromeDriver 사용
                service = Service(ChromeDriverManager().install())
            
            # 드라이버 생성
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            # User-Agent 설정
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Headless 다운로드 허용 (CDP)
            try:
                self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                    'behavior': 'allow',
                    'downloadPath': download_dir
                })
                self.logger.info(f"다운로드 경로 활성화: {download_dir}")
            except Exception as e:
                self.logger.warning(f"CDP 다운로드 허용 설정 실패(무시 가능): {e}")

            self.logger.info("Chrome/Chromium 드라이버 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"드라이버 설정 실패: {e}")
            return False
    
    def login(self):
        """BIG KINDS 로그인 - 여러 방법으로 시도"""
        try:
            self.logger.info("BIG KINDS 로그인 시작")
            
            # 페이지가 완전히 로드될 때까지 대기
            time.sleep(5)
            
            # 여러 가지 방법으로 로그인 버튼 찾기 시도
            login_methods = [
                self._try_direct_login_button,
                self._try_user_icon_hover,
                self._try_navigation_menu
            ]
            
            for method in login_methods:
                try:
                    self.logger.info(f"로그인 방법 시도: {method.__name__}")
                    if method():
                        self.logger.info("로그인 성공")
                        return True
                except Exception as e:
                    self.logger.warning(f"로그인 방법 {method.__name__} 실패: {e}")
                    continue
            
            self.logger.error("모든 로그인 방법 실패")
            return False
            
        except Exception as e:
            self.logger.error(f"로그인 실패: {e}")
            return False
    
    def _try_direct_login_button(self):
        """직접 로그인 버튼 찾기"""
        try:
            # 페이지에서 직접 로그인 버튼 찾기
            login_selectors = [
                "//a[contains(text(), '로그인')]",
                "//button[contains(text(), '로그인')]",
                "//span[contains(text(), '로그인')]",
                "//div[contains(text(), '로그인')]",
                "//*[contains(@class, 'login')]",
                "//*[contains(@id, 'login')]"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = self.driver.find_element(By.XPATH, selector)
                    if login_btn.is_displayed() and login_btn.is_enabled():
                        self.logger.info(f"직접 로그인 버튼 찾음: {selector}")
                        login_btn.click()
                        time.sleep(3)
                        return self._complete_login_form()
                except:
                    continue
            
            return False
        except Exception as e:
            self.logger.warning(f"직접 로그인 버튼 방법 실패: {e}")
            return False
    
    def _try_user_icon_hover(self):
        """사용자 아이콘 호버 방법"""
        try:
            # 사용자 아이콘 찾기
            user_icon_selectors = [
                "//i[contains(@class, 'user')]",
                "//i[contains(@class, 'person')]",
                "//i[contains(@class, 'account')]",
                "//span[contains(@class, 'user')]",
                "//div[contains(@class, 'user')]",
                "//a[contains(@class, 'user')]",
                "//button[contains(@class, 'user')]",
                "//*[contains(@class, 'user')]"
            ]
            
            user_icon = None
            for selector in user_icon_selectors:
                try:
                    user_icon = self.driver.find_element(By.XPATH, selector)
                    if user_icon.is_displayed():
                        self.logger.info(f"사용자 아이콘 찾음: {selector}")
                        break
                except:
                    continue
            
            if not user_icon:
                return False
            
            # JavaScript로 호버 이벤트 발생
            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", user_icon)
            time.sleep(2)
            
            # 호버 후 나타나는 로그인 버튼 찾기
            hover_login_selectors = [
                "//a[contains(text(), '로그인')]",
                "//button[contains(text(), '로그인')]",
                "//span[contains(text(), '로그인')]",
                "//div[contains(text(), '로그인')]"
            ]
            
            for selector in hover_login_selectors:
                try:
                    login_btn = self.driver.find_element(By.XPATH, selector)
                    if login_btn.is_displayed() and login_btn.is_enabled():
                        self.logger.info(f"호버 후 로그인 버튼 찾음: {selector}")
                        login_btn.click()
                        time.sleep(3)
                        return self._complete_login_form()
                except:
                    continue
            
            return False
        except Exception as e:
            self.logger.warning(f"사용자 아이콘 호버 방법 실패: {e}")
            return False
    
    def _try_navigation_menu(self):
        """네비게이션 메뉴에서 로그인 찾기"""
        try:
            # 메뉴나 네비게이션에서 로그인 찾기
            nav_login_selectors = [
                "//nav//a[contains(text(), '로그인')]",
                "//header//a[contains(text(), '로그인')]",
                "//ul//a[contains(text(), '로그인')]",
                "//menu//a[contains(text(), '로그인')]"
            ]
            
            for selector in nav_login_selectors:
                try:
                    login_btn = self.driver.find_element(By.XPATH, selector)
                    if login_btn.is_displayed() and login_btn.is_enabled():
                        self.logger.info(f"네비게이션에서 로그인 버튼 찾음: {selector}")
                        login_btn.click()
                        time.sleep(3)
                        return self._complete_login_form()
                except:
                    continue
            
            return False
        except Exception as e:
            self.logger.warning(f"네비게이션 메뉴 방법 실패: {e}")
            return False
    
    def _complete_login_form(self):
        """로그인 폼 완성"""
        try:
            self.logger.info("로그인 폼 완성 시작")
            
            # 로그인 폼이 나타날 때까지 대기
            time.sleep(3)
            
            # ID로 직접 이메일 입력 필드 찾기
            try:
                email_input = self.driver.find_element(By.ID, "login-user-id")
                self.logger.info("이메일 입력 필드 찾음: login-user-id")
            except:
                self.logger.error("이메일 입력 필드(login-user-id)를 찾을 수 없습니다")
                return False
            
            # ID로 직접 비밀번호 입력 필드 찾기
            try:
                password_input = self.driver.find_element(By.ID, "login-user-password")
                self.logger.info("비밀번호 입력 필드 찾음: login-user-password")
            except:
                self.logger.error("비밀번호 입력 필드(login-user-password)를 찾을 수 없습니다")
                return False
            
            # 이메일 입력
            try:
                self.driver.execute_script("arguments[0].value = arguments[1];", email_input, self.email)
                self.logger.info("JavaScript로 이메일 입력 성공")
            except Exception as e:
                self.logger.error(f"이메일 입력 실패: {e}")
                return False
            
            time.sleep(1)
            
            # 비밀번호 입력
            try:
                self.driver.execute_script("arguments[0].value = arguments[1];", password_input, self.password)
                self.logger.info("JavaScript로 비밀번호 입력 성공")
            except Exception as e:
                self.logger.error(f"비밀번호 입력 실패: {e}")
                return False
            
            time.sleep(1)
            
            # 로그인 제출 버튼 찾기 및 클릭
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                self.logger.info("제출 버튼 찾음")
            except:
                self.logger.error("제출 버튼을 찾을 수 없습니다")
                return False
            
            # 제출 버튼 클릭
            try:
                self.driver.execute_script("arguments[0].click();", submit_btn)
                self.logger.info("JavaScript로 제출 버튼 클릭 성공")
            except Exception as e:
                self.logger.error(f"제출 버튼 클릭 실패: {e}")
                return False
            
            time.sleep(5)
            
            # 로그인 성공 여부 확인
            return self._verify_login_success()
            
        except Exception as e:
            self.logger.error(f"로그인 폼 완성 실패: {e}")
            return False
    
    def _verify_login_success(self):
        """로그인 성공 여부 확인"""
        try:
            # 로그인 후 나타나는 요소들 확인
            success_indicators = [
                "//a[contains(text(), '로그아웃')]",
                "//a[contains(text(), '마이페이지')]",
                "//span[contains(text(), '님')]",
                "//div[contains(@class, 'user-info')]",
                "//*[contains(@class, 'logout')]",
                "//*[contains(@class, 'user')]"
            ]
            
            login_success = False
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        login_success = True
                        self.logger.info(f"로그인 성공 확인: {indicator}")
                        break
                except:
                    continue
            
            if login_success:
                self.logger.info("로그인 성공 확인됨")
                return True
            else:
                self.logger.warning("로그인 성공 여부를 확인할 수 없습니다")
                # URL 변경이나 다른 지표로 확인
                current_url = self.driver.current_url
                if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                    self.logger.info("URL 변경으로 로그인 성공 추정")
                    return True
                return True  # 일단 성공으로 간주
                
        except Exception as e:
            self.logger.warning(f"로그인 성공 확인 중 오류: {e}")
            return True  # 일단 성공으로 간주
    
    def navigate_to_news_analysis(self):
        """뉴스 검색 분석 탭으로 이동"""
        try:
            self.logger.info("뉴스 검색 분석 탭으로 이동")
            
            # 로그인 후 페이지 로딩 대기
            time.sleep(3)
            
            # 직접 뉴스검색·분석 페이지 URL로 이동
            news_analysis_url = "https://www.bigkinds.or.kr/v2/news/index.do"
            self.logger.info(f"직접 URL로 이동: {news_analysis_url}")
            
            self.driver.get(news_analysis_url)
            time.sleep(5)
            
            # 페이지 이동 확인
            current_url = self.driver.current_url
            self.logger.info(f"현재 URL: {current_url}")
            
            # 페이지 제목 확인
            page_title = self.driver.title
            self.logger.info(f"페이지 제목: {page_title}")
            
            # 뉴스 검색 페이지의 특징적인 요소 확인
            search_page_indicators = [
                "//input[@placeholder*='검색어']",
                "//input[@placeholder*='키워드']",
                "//button[contains(text(), '검색')]",
                "//div[contains(@class, 'search')]",
                "//form[contains(@class, 'search')]",
                "//input[@id='total-search-key']",
                "//input[@name='interestKeyword']"
            ]
            
            page_loaded = False
            for indicator in search_page_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        page_loaded = True
                        self.logger.info(f"뉴스 검색 페이지 로드 확인: {indicator}")
                        break
                except:
                    continue
            
            if page_loaded:
                self.logger.info("뉴스 검색 분석 페이지 도달 성공")
                return True
            else:
                self.logger.warning("뉴스 검색 페이지의 특징적인 요소를 찾을 수 없습니다")
                # URL이나 제목으로 판단
                if any(keyword in current_url.lower() for keyword in ['news', 'search', 'analysis', '뉴스', '검색', '분석', 'v2']):
                    self.logger.info("URL 기반으로 뉴스 검색 페이지 도달 추정")
                    return True
                elif any(keyword in page_title.lower() for keyword in ['news', 'search', 'analysis', '뉴스', '검색', '분석']):
                    self.logger.info("제목 기반으로 뉴스 검색 페이지 도달 추정")
                    return True
                else:
                    self.logger.error("뉴스 검색 페이지 도달 실패")
                    return False
            
        except Exception as e:
            self.logger.error(f"뉴스 검색 분석 페이지 이동 실패: {e}")
            # 현재 페이지 정보 로깅
            try:
                self.logger.info(f"현재 URL: {self.driver.current_url}")
                self.logger.info(f"현재 제목: {self.driver.title}")
                page_source = self.driver.page_source[:1000]
                self.logger.info(f"페이지 소스 일부: {page_source}")
            except:
                pass
            return False
    
    def set_custom_period(self, start_date, end_date):
        """분석 페이지에서 사용자 지정 기간 설정"""
        try:
            self.logger.info(f"사용자 지정 기간 설정: {start_date} ~ {end_date}")
            time.sleep(1)

            # 기간 탭/버튼 클릭 (텍스트 포함 다양한 경우 대응)
            period_triggers = [
                "//button[contains(text(), '기간')]",
                "//a[contains(text(), '기간')]",
                "//*[contains(@class, 'date') and (self::button or self::a)]",
                "//div[contains(@class, 'date')]//button",
            ]
            period_btn = None
            for xp in period_triggers:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        period_btn = el
                        break
                except:
                    continue
            if not period_btn:
                self.logger.warning("기간 버튼을 못찾음. 직접 날짜 입력 시도")
            else:
                try:
                    self.driver.execute_script("arguments[0].click();", period_btn)
                except:
                    try:
                        period_btn.click()
                    except Exception as e:
                        self.logger.warning(f"기간 버튼 클릭 실패: {e}")
            time.sleep(1)

            # 시작 날짜 입력
            start_date_input = None
            start_date_selectors = [
                "//input[@id='search-begin-date']",
                "//input[contains(@class, 'input-dateFrom')]",
                "//input[contains(@placeholder, 'YYYY-MM-DD')]",
                "//input[contains(@title, '달력보기')]",
                "//input[@type='text' and contains(@class, 'date')]"
            ]
            
            for xp in start_date_selectors:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        start_date_input = el
                        break
                except:
                    continue
                    
            if not start_date_input:
                self.logger.error("시작 날짜 입력 필드를 찾을 수 없습니다")
                return False

            # 시작 날짜 입력
            try:
                self.driver.execute_script("arguments[0].value = '';", start_date_input)
                start_date_input.clear()
                start_date_input.send_keys(start_date)
                self.logger.info(f"시작 날짜 입력: {start_date}")
            except Exception as e:
                self.logger.error(f"시작 날짜 입력 실패: {e}")
                return False

            time.sleep(0.5)

            # 종료 날짜 입력
            end_date_input = None
            end_date_selectors = [
                "//input[@id='search-end-date']",
                "//input[contains(@class, 'input-dateTo')]",
                "//input[contains(@placeholder, 'YYYY-MM-DD') and not(contains(@class, 'input-dateFrom'))]",
                "//input[@type='text' and contains(@class, 'date') and not(contains(@class, 'input-dateFrom'))]"
            ]
            
            for xp in end_date_selectors:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        end_date_input = el
                        break
                except:
                    continue
                    
            if not end_date_input:
                self.logger.error("종료 날짜 입력 필드를 찾을 수 없습니다")
                return False

            # 종료 날짜 입력
            try:
                self.driver.execute_script("arguments[0].value = '';", end_date_input)
                end_date_input.clear()
                end_date_input.send_keys(end_date)
                self.logger.info(f"종료 날짜 입력: {end_date}")
            except Exception as e:
                self.logger.error(f"종료 날짜 입력 실패: {e}")
                return False

            time.sleep(0.5)

            # 적용/확인 버튼이 따로 있는 UI 대응
            apply_candidates = [
                "//button[contains(text(),'적용')]",
                "//button[contains(text(),'확인')]",
                "//a[contains(text(),'적용')]",
                "//a[contains(text(),'확인')]",
                "//button[contains(text(),'검색')]",
                "//a[contains(text(),'검색')]",
            ]
            for xp in apply_candidates:
                try:
                    btn = self.driver.find_element(By.XPATH, xp)
                    if btn.is_displayed() and btn.is_enabled():
                        try:
                            self.driver.execute_script("arguments[0].click();", btn)
                        except:
                            btn.click()
                        self.logger.info("기간 적용 버튼 클릭 완료")
                        break
                except:
                    continue

            time.sleep(1)
            self.logger.info("사용자 지정 기간 설정 완료")
            return True
        except Exception as e:
            self.logger.error(f"사용자 지정 기간 설정 실패: {e}")
            return False

    def set_period_one_day(self):
        """분석 페이지에서 기간 → 1일 선택"""
        try:
            self.logger.info("기간 탭 클릭 후 1일 선택")
            time.sleep(1)

            # 기간 탭/버튼 클릭 (텍스트 포함 다양한 경우 대응)
            period_triggers = [
                "//button[contains(text(), '기간')]",
                "//a[contains(text(), '기간')]",
                "//*[contains(@class, 'date') and (self::button or self::a)]",
                "//div[contains(@class, 'date')]//button",
            ]
            period_btn = None
            for xp in period_triggers:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        period_btn = el
                        break
                except:
                    continue
            if not period_btn:
                # 페이지 내 '1일' 라디오가 보이면 기간 버튼 없이 직접 진행
                self.logger.warning("기간 버튼을 못찾음. '1일' 직접 선택 시도")
            else:
                try:
                    self.driver.execute_script("arguments[0].click();", period_btn)
                except:
                    try:
                        period_btn.click()
                    except Exception as e:
                        self.logger.warning(f"기간 버튼 클릭 실패: {e}")
            time.sleep(1)

            # '1일' 옵션 선택 (라디오/버튼 모두 대응)
            one_day_selectors = [
                "//label[contains(., '1일')]",
                "//button[contains(text(), '1일')]",
                "//span[contains(text(), '1일')]/ancestor::label",
                "//input[@type='radio' and (contains(@id,'date') or contains(@name,'date'))]/following-sibling::label[contains(., '1일')]",
                "//*[contains(@class,'date') and contains(.,'1일')]",
            ]
            one_day = None
            for xp in one_day_selectors:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        one_day = el
                        break
                except:
                    continue
            if not one_day:
                self.logger.error("'1일' 옵션을 찾을 수 없습니다")
                return False

            try:
                self.driver.execute_script("arguments[0].click();", one_day)
            except:
                try:
                    one_day.click()
                except Exception as e:
                    self.logger.error(f"'1일' 클릭 실패: {e}")
                    return False

            time.sleep(1)

            # 적용/확인 버튼이 따로 있는 UI 대응
            apply_candidates = [
                "//button[contains(text(),'적용')]",
                "//button[contains(text(),'확인')]",
                "//a[contains(text(),'적용')]",
                "//a[contains(text(),'확인')]",
            ]
            for xp in apply_candidates:
                try:
                    btn = self.driver.find_element(By.XPATH, xp)
                    if btn.is_displayed() and btn.is_enabled():
                        try:
                            self.driver.execute_script("arguments[0].click();", btn)
                        except:
                            btn.click()
                        break
                except:
                    continue

            self.logger.info("기간 1일 선택 완료")
            return True
        except Exception as e:
            self.logger.error(f"기간 1일 선택 실패: {e}")
            return False

    def select_economy_and_apply(self):
        """통합 분류 탭 클릭 → '경제' 체크 → 적용하기"""
        try:
            self.logger.info("통합 분류에서 '경제' 선택 후 적용")
            time.sleep(1)

            # 0) 필터/상세검색 열기(있다면)
            try:
                self.driver.execute_script(
                    """
                    const selectors = [
                      'button', 'a', '[role="button"]', '[data-role="toggle"]'
                    ];
                    const keys = ['상세검색','상세 검색','필터','검색옵션','검색 옵션','조건설정','조건 설정'];
                    const all = Array.from(document.querySelectorAll(selectors.join(',')));
                    for (const el of all){
                      const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                      if (!t) continue;
                      for (const k of keys){
                        if (t.includes(k.replace(/\s+/g,''))){
                          try { el.click(); return true; } catch(e){}
                        }
                      }
                    }
                    return false;
                    """
                )
            except:
                pass
            time.sleep(0.8)

            # 1) 통합 분류 탭/버튼 열기 (공백 제거 텍스트 매칭 포함)
            opened = self.driver.execute_script(
                """
                function clickByTextLike(keys){
                  const nodes = Array.from(document.querySelectorAll('button, a, [role="tab"], [role="button"], .tab button, .tab a'));
                  for (const el of nodes){
                    const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                    if (!t) continue;
                    for (const k of keys){
                      if (t.includes(k)){
                        try { el.scrollIntoView({block:'center'}); el.click(); return true; } catch(e){}
                      }
                    }
                  }
                  return false;
                }
                const keys = ['통합분류','분류','카테고리','분야'];
                if (clickByTextLike(keys)) return true;
                // 탭 패널 헤더 형태(aria-controls 등)
                const headers = Array.from(document.querySelectorAll('[aria-controls]'));
                for (const h of headers){
                  const t = (h.innerText||h.textContent||'').replace(/\s+/g,'');
                  if (!t) continue;
                  if (keys.some(k => t.includes(k))){ try { h.click(); return true; } catch(e){} }
                }
                return false;
                """
            )
            if not opened:
                self.logger.warning("통합 분류 탭 텍스트 매칭 실패. 대체 XPath 시도")
                category_triggers = [
                    "//button[contains(normalize-space(.),'통합 분류')]",
                    "//a[contains(normalize-space(.),'통합 분류')]",
                    "//button[contains(normalize-space(.),'분류')]",
                    "//a[contains(normalize-space(.),'분류')]",
                    "//*[@role='tab' and contains(normalize-space(.),'분류')]",
                    "//*[contains(@class,'filter') or contains(@class,'accordion') or contains(@class,'tab')]//*[contains(normalize-space(.),'통합 분류') or contains(normalize-space(.),'분류')]",
                ]
                for xp in category_triggers:
                    try:
                        el = self.driver.find_element(By.XPATH, xp)
                        if el.is_displayed() and el.is_enabled():
                            try:
                                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el)
                            except:
                                el.click()
                            break
                    except:
                        continue
            time.sleep(1)

            # 패널 열림 재확인: 체크박스 컨테이너나 '적용' 영역이 보여야 함
            panel_open = False
            for xp in [
                "//button[contains(text(),'적용하기')]",
                "//a[contains(text(),'적용하기')]",
                "//div[contains(@class,'category') or contains(@class,'filter') or contains(@class,'panel')]//input[@type='checkbox']",
                "//*[contains(text(),'경제')]"
            ]:
                try:
                    if self.driver.find_element(By.XPATH, xp).is_displayed():
                        panel_open = True
                        break
                except:
                    continue
            if not panel_open:
                self.logger.warning("통합 분류 패널 열림 감지 실패. 한번 더 탭 클릭 시도")
                self.driver.execute_script(
                    """
                    const keys = ['통합분류','분류','카테고리','분야'];
                    const nodes = Array.from(document.querySelectorAll('button, a, [role="tab"], [role="button"], .tab button, .tab a'));
                    for (const el of nodes){
                      const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                      if (t && keys.some(k => t.includes(k))){ try { el.click(); return true; } catch(e){} }
                    }
                    return false;
                    """
                )
                time.sleep(0.8)

            # 열림 상태에서 스크롤을 중앙으로 이동(고정 헤더에 가려지는 문제 방지)
            try:
                self.driver.execute_script("window.scrollBy(0, -100);")
            except:
                pass

            # 2) '경제' 체크박스 탐색 (JS 근접 텍스트 매칭 우선)
            js_find = """
            function getTextAround(el){
              const getText = n => (n?.innerText || n?.textContent || '').replace(/\s+/g,'');
              const label = el.closest('label');
              if (label) return getText(label);
              if (el.nextElementSibling) {
                const sib = getText(el.nextElementSibling);
                if (sib) return sib;
              }
              const parent = el.parentElement;
              if (parent){
                const ptxt = getText(parent);
                if (ptxt) return ptxt;
              }
              let node = el;
              for (let i=0;i<3;i++){
                node = node?.parentElement;
                if (!node) break;
                const txt = getText(node);
                if (txt) return txt;
              }
              return '';
            }
            const allCandidates = Array.from(document.querySelectorAll('[data-checkbox="true"]'));
            // 일부 사이트는 input이 숨겨져 있고 label/div가 클릭 타겟인 경우가 있어 input 외 요소도 수집
            const inputs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            const candidates = Array.from(new Set([...allCandidates, ...inputs]));
            for (const el of candidates){
              const text = getTextAround(el);
              if (text.includes('경제')){
                let target = el;
                // 숨겨진 input이면 label/부모로 타겟 변경
                const style = window.getComputedStyle(el);
                const hidden = style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
                if ((el.tagName.toLowerCase()==='input' && el.type==='checkbox') && hidden){
                  const label = el.closest('label');
                  if (label) target = label;
                  else if (el.parentElement) target = el.parentElement;
                }
                target.scrollIntoView({block:'center'});
                return [el, target];
              }
            }
            return null;
            """
            economy_el = None
            click_target = None
            try:
                result = self.driver.execute_script(js_find)
                if result:
                    try:
                        # Expect a list [checkbox, clickTarget]
                        if isinstance(result, list) and len(result) >= 2:
                            economy_el = result[0]
                            click_target = result[1]
                        else:
                            economy_el = result
                            click_target = result
                    except Exception:
                        economy_el = result
                        click_target = result
            except Exception as e:
                self.logger.warning(f"JS 탐색 실패: {e}")

            # 3) XPath 대체
            if economy_el is None:
                for xp in [
                    "//label[contains(normalize-space(.), '경제')]//input[@type='checkbox']",
                    "//span[contains(normalize-space(text()),'경제')]/ancestor::label//input[@type='checkbox']",
                    "//input[@type='checkbox' and following-sibling::*[contains(normalize-space(.), '경제')]]",
                    "//*[contains(normalize-space(.),'경제')]/ancestor::*[self::label or self::li or self::div][1]//input[@type='checkbox']",
                ]:
                    try:
                        el = self.driver.find_element(By.XPATH, xp)
                        if el.is_displayed() and el.is_enabled():
                            economy_el = el
                            try:
                                # 클릭 타겟은 label 또는 부모일 수 있음
                                lbl = el.find_element(By.XPATH, "ancestor::label[1]")
                                click_target = lbl if lbl else el
                            except:
                                click_target = el
                            break
                    except:
                        continue

            if not economy_el:
                self.logger.error("'경제' 항목을 찾을 수 없습니다")
                return False

            # 체크
            try:
                if click_target is None:
                    click_target = economy_el
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", click_target)
                # 먼저 클릭 타겟 클릭
                try:
                    self.driver.execute_script("arguments[0].click();", click_target)
                except Exception:
                    pass
                # 체크 상태 확인, 아니면 input 강제 체크
                try:
                    is_checked = economy_el.is_selected()
                except Exception:
                    is_checked = False
                if not is_checked:
                    self.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", economy_el)
            except Exception:
                try:
                    if click_target is not None:
                        click_target.click()
                    else:
                        economy_el.click()
                except Exception as e:
                    self.logger.warning(f"일반 클릭 실패, checked 강제: {e}")
                    try:
                        self.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", economy_el)
                    except Exception as e2:
                        self.logger.error(f"'경제' 선택 실패: {e2}")
                        return False
            time.sleep(0.5)

            # 적용하기 클릭
            apply_btn = None
            # 0) 명시 클래스 우선 타겟
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-search.news-search-btn.news-report-search-btn")
                if btn.is_displayed() and btn.is_enabled():
                    apply_btn = btn
            except:
                pass

            # 1) XPath로 클래스/텍스트 정밀 매칭
            if not apply_btn:
                apply_xpaths = [
                    "//button[contains(@class,'news-report-search-btn') and contains(normalize-space(.),'적용하기')]",
                    "//button[contains(@class,'news-report-search-btn')]",
                    "//button[contains(normalize-space(.),'적용하기')]",
                    "//a[contains(normalize-space(.),'적용하기')]",
                    "//button[contains(normalize-space(.),'적용')]",
                    "//a[contains(normalize-space(.),'적용')]",
                    "//*[contains(@class,'btn') and contains(normalize-space(.),'적용')]",
                    "//div[contains(@class,'filter') or contains(@class,'panel')]//button[contains(normalize-space(.),'적용')]",
                ]
                for xp in apply_xpaths:
                    try:
                        el = self.driver.find_element(By.XPATH, xp)
                        if el.is_displayed() and el.is_enabled():
                            apply_btn = el
                            break
                    except:
                        continue

            if not apply_btn:
                # 스크롤로 하단 고정바 노출 시도 후 재검색
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.4)
                except:
                    pass
                for xp in apply_xpaths:
                    try:
                        el = self.driver.find_element(By.XPATH, xp)
                        if el.is_displayed() and el.is_enabled():
                            apply_btn = el
                            break
                    except:
                        continue

            if not apply_btn:
                # JS로 명시 클래스 또는 텍스트 매칭 우선 클릭
                clicked = False
                try:
                    clicked = self.driver.execute_script(
                        """
                        const prefer = document.querySelector('button.btn.btn-search.news-search-btn.news-report-search-btn');
                        if (prefer){ try { prefer.scrollIntoView({block:'center'}); prefer.click(); return true; } catch(e){} }
                        const keys = ['적용하기'];
                        const nodes = Array.from(document.querySelectorAll('button, a, [role="button"], .btn, .button'));
                        for (const el of nodes){
                          const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                          if (!t) continue;
                          if (keys.some(k => t.includes(k))){
                            try { el.scrollIntoView({block:'center'}); el.click(); return true; } catch(e){}
                          }
                        }
                        return false;
                        """
                    )
                except Exception as e:
                    self.logger.warning(f"JS 적용버튼 클릭 시도 실패: {e}")

                if not clicked:
                    # 후보 로깅 후 실패 처리
                    try:
                        candidates = self.driver.find_elements(By.XPATH, "//*[contains(normalize-space(.),'적용')]")
                        self.logger.error(f"'적용하기' 버튼을 찾을 수 없습니다. 후보 개수: {len(candidates)}")
                    except:
                        pass
                    return False
            else:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", apply_btn)
                except:
                    try:
                        apply_btn.click()
                    except Exception as e:
                        self.logger.error(f"'적용하기' 클릭 실패: {e}")
                        return False

            time.sleep(1.5)
            self.logger.info("'경제' 적용 완료")
            return True
        except Exception as e:
            self.logger.error(f"통합 분류 경제 적용 실패: {e}")
            return False

    def open_analysis_and_download_excel(self):
        """'분석 결과 및 시각화' 탭을 열고 '엑셀 다운로드'를 클릭하여 저장"""
        try:
            self.logger.info("분석 결과 및 시각화 탭 열기 및 엑셀 다운로드 시도")
            # 적용 후 결과 로딩 대기
            time.sleep(2.0)

            # 1) 탭 클릭 (텍스트 정규화 매칭)
            opened = False
            tab_xpaths = [
                "//a[contains(normalize-space(.),'분석 결과 및 시각화')]",
                "//button[contains(normalize-space(.),'분석 결과 및 시각화')]",
                "//*[@role='tab' and contains(normalize-space(.),'분석 결과 및 시각화')]",
                "//*[contains(@class,'tab')]//*[contains(normalize-space(.),'분석 결과 및 시각화')]",
            ]
            for xp in tab_xpaths:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el)
                        except Exception:
                            el.click()
                        opened = True
                        break
                except Exception:
                    continue

            if not opened:
                # JS fallback by text includes (whitespace-agnostic)
                try:
                    opened = self.driver.execute_script(
                        """
                        const keys = ['분석결과및시각화','분석결과','시각화'];
                        const nodes = Array.from(document.querySelectorAll('a, button, [role=\"tab\"], .tab a, .tab button'));
                        for (const el of nodes){
                          const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                          if (!t) continue;
                          if (keys.some(k => t.includes(k))){
                            try { el.scrollIntoView({block:'center'}); el.click(); return true; } catch(e){}
                          }
                        }
                        return false;
                        """
                    )
                except Exception as e:
                    self.logger.warning(f"JS 탭 열기 실패: {e}")

            if not opened:
                self.logger.error("'분석 결과 및 시각화' 탭을 찾을 수 없습니다")
                return False

            # 탭 콘텐츠 로딩 대기
            time.sleep(1.2)

            # 2) 엑셀 다운로드 버튼 클릭
            dl_btn = None
            dl_xpaths = [
                "//button[contains(normalize-space(.),'엑셀') and contains(normalize-space(.),'다운')]",
                "//a[contains(normalize-space(.),'엑셀') and contains(normalize-space(.),'다운')]",
                "//*[contains(@class,'btn') and contains(normalize-space(.),'엑셀')]",
                "//*[contains(@class,'excel') and (self::a or self::button)]",
            ]
            for xp in dl_xpaths:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el.is_displayed() and el.is_enabled():
                        dl_btn = el
                        break
                except Exception:
                    continue

            if not dl_btn:
                # JS fallback: prefer any button-like with text including '엑셀' and '다운'
                clicked = False
                try:
                    clicked = self.driver.execute_script(
                        """
                        const nodes = Array.from(document.querySelectorAll('button, a, [role=\"button\"], .btn'));
                        for (const el of nodes){
                          const t = (el.innerText||el.textContent||'').replace(/\s+/g,'');
                          if (!t) continue;
                          if (t.includes('엑셀') && (t.includes('다운') || t.includes('다운로드'))){
                            try { el.scrollIntoView({block:'center'}); el.click(); return true; } catch(e){}
                          }
                        }
                        return false;
                        """
                    )
                except Exception as e:
                    self.logger.warning(f"JS 엑셀 다운로드 클릭 실패: {e}")

                if not clicked:
                    self.logger.error("'엑셀 다운로드' 버튼을 찾을 수 없습니다")
                    return False
            else:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", dl_btn)
                except Exception:
                    dl_btn.click()

            self.logger.info("엑셀 다운로드 클릭 완료")
            # 다운로드 완료 대기 (시간 증가)
            try:
                self.logger.info("다운로드 완료 대기 시작...")
                self._wait_for_download(timeout=60)  # 30초 → 60초로 증가
                self.logger.info("다운로드 완료 확인됨")
            except Exception as e:
                self.logger.warning(f"다운로드 완료 대기 중 경고: {e}")
                # 다운로드 실패해도 파일이 있을 수 있으므로 확인
                try:
                    files = [f for f in os.listdir(self.download_dir) if f.endswith('.xlsx')]
                    if files:
                        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(self.download_dir, x)))
                        self.logger.info(f"다운로드된 파일 발견: {latest_file}")
                    else:
                        self.logger.error("다운로드된 파일을 찾을 수 없습니다")
                except Exception as check_e:
                    self.logger.error(f"파일 확인 중 오류: {check_e}")
            return True
        except Exception as e:
            self.logger.error(f"분석 탭/엑셀 다운로드 실패: {e}")
            return False

    def _wait_for_download(self, timeout=60):
        """다운로드 디렉토리에 파일 생성/완료를 기다림"""
        start = time.time()
        last_size = -1
        stable_count = 0
        self.logger.info(f"다운로드 대기 시작 (타임아웃: {timeout}초)")
        
        while time.time() - start < timeout:
            try:
                files = [f for f in os.listdir(self.download_dir) if not f.endswith('.crdownload')]
                # 진행중인 파일도 추적
                partials = [f for f in os.listdir(self.download_dir) if f.endswith('.crdownload')]
                
                if files:
                    # 파일 크기 안정화 체크
                    latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(self.download_dir, x)), reverse=True)[0]
                    path = os.path.join(self.download_dir, latest_file)
                    size = os.path.getsize(path)
                    
                    self.logger.info(f"파일 발견: {latest_file} (크기: {size} bytes)")
                    
                    if size == last_size:
                        stable_count += 1
                        self.logger.info(f"파일 크기 안정화 중... ({stable_count}/3)")
                        if stable_count >= 3 and not partials:
                            self.logger.info(f"다운로드 완료 확인: {path}")
                            return True
                    else:
                        last_size = size
                        stable_count = 0
                        self.logger.info(f"파일 크기 변경: {size} bytes")
                elif partials:
                    self.logger.info(f"다운로드 진행 중: {len(partials)}개 파일")
                else:
                    self.logger.info("다운로드 파일 대기 중...")
                    
            except Exception as e:
                self.logger.warning(f"파일 확인 중 오류: {e}")
                
            time.sleep(2)  # 1초 → 2초로 증가
            
        self.logger.error(f"다운로드 타임아웃 ({timeout}초 초과)")
        raise TimeoutError("다운로드 완료를 확인하지 못했습니다")
    
    def run_automation(self, start_date, end_date):
        """전체 자동화 플로우 실행"""
        try:
            self.logger.info(f"자동화 시작: {start_date} ~ {end_date}")
            
            # 1. 드라이버 설정
            if not self.setup_driver():
                self.logger.error("드라이버 설정 실패")
                return False
            
            # 2. BIG KINDS 접속
            self.driver.get("https://www.bigkinds.or.kr/")
            time.sleep(3)
            
            # 3. 로그인
            if not self.login():
                self.logger.error("로그인 실패")
                return False
            
            # 4. 뉴스 검색 분석 탭으로 이동
            if not self.navigate_to_news_analysis():
                self.logger.error("뉴스 검색 분석 탭 이동 실패")
                return False
            
            # 5. 사용자 지정 기간 설정
            if not self.set_custom_period(start_date, end_date):
                self.logger.error("사용자 지정 기간 설정 실패")
                return False
            
            # 6. 통합 분류에서 '경제' 선택 및 적용
            if not self.select_economy_and_apply():
                self.logger.error("통합 분류에서 '경제' 선택 및 적용 실패")
                return False
            
            # 7. 분석 결과 및 시각화 → 엑셀 다운로드
            if not self.open_analysis_and_download_excel():
                self.logger.error("분석 결과 및 엑셀 다운로드 실패")
                return False
            
            # 8. 엑셀 파일을 CSV로 변환
            self.logger.info("엑셀 파일을 CSV로 변환 중...")
            csv_files = self.convert_excel_to_csv()
            if csv_files:
                self.logger.info(f"CSV 변환 완료: {len(csv_files)}개 파일 생성")
                for csv_file in csv_files:
                    self.logger.info(f"  - {csv_file}")
                
                # 9. CSV 파일을 S3에 업로드
                self.logger.info("CSV 파일을 S3에 업로드 중...")
                s3_url = self.upload_csv_to_s3()
                if s3_url:
                    self.logger.info(f"S3 업로드 완료: {s3_url}")
                else:
                    self.logger.warning("S3 업로드 실패")
            else:
                self.logger.warning("CSV 변환 실패")
            
            self.logger.info("자동화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"자동화 실행 중 오류: {e}")
            return False
        finally:
            try:
                self.close()
            except:
                pass

    def convert_excel_to_csv(self, download_dir="./downloads"):
        """다운로드된 엑셀 파일을 CSV로 변환"""
        try:
            # 다운로드 디렉토리 생성
            os.makedirs(download_dir, exist_ok=True)
            
            # 엑셀 파일 찾기
            excel_files = glob.glob(os.path.join(download_dir, "*.xlsx"))
            if not excel_files:
                self.logger.warning("다운로드된 엑셀 파일을 찾을 수 없습니다.")
                return None
            
            # 가장 최근 파일 선택
            latest_excel = max(excel_files, key=os.path.getctime)
            self.logger.info(f"엑셀 파일 발견: {latest_excel}")
            
            # 엑셀 파일 읽기
            try:
                # 모든 시트 읽기
                excel_data = pd.read_excel(latest_excel, sheet_name=None)
                
                csv_files = []
                
                # CSV 파일명 생성
                base_name = os.path.splitext(os.path.basename(latest_excel))[0]
                
                # 단일 시트인 경우
                if len(excel_data) == 1:
                    sheet_name = list(excel_data.keys())[0]
                    df = excel_data[sheet_name]
                    csv_filename = f"{base_name}.csv"
                    csv_path = os.path.join(download_dir, csv_filename)
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    csv_files.append(csv_path)
                    self.logger.info(f"CSV 파일 생성: {csv_path}")
                else:
                    # 다중 시트인 경우 각 시트별로 저장
                    for sheet_name, df in excel_data.items():
                        csv_filename = f"{base_name}_{sheet_name}.csv"
                        csv_path = os.path.join(download_dir, csv_filename)
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        csv_files.append(csv_path)
                        self.logger.info(f"CSV 파일 생성: {csv_path}")
                
                return csv_files
                
            except Exception as e:
                self.logger.error(f"엑셀 파일 읽기 실패: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"CSV 변환 중 오류: {e}")
            return None

    def get_latest_downloaded_file(self, download_dir="./downloads", file_extension=".xlsx"):
        """다운로드 디렉토리에서 가장 최근 파일 반환"""
        try:
            os.makedirs(download_dir, exist_ok=True)
            
            # 지정된 확장자의 파일들 찾기
            pattern = os.path.join(download_dir, f"*{file_extension}")
            files = glob.glob(pattern)
            
            if not files:
                return None
            
            # 가장 최근 파일 반환
            latest_file = max(files, key=os.path.getctime)
            return latest_file
            
        except Exception as e:
            self.logger.error(f"최근 파일 찾기 실패: {e}")
            return None

    def convert_filename_format(self, original_filename):
        """파일명을 새로운 형식으로 변환"""
        try:
            # NewsResult_15600305-2025091720250917.xlsx -> NewsResult_20250917-20250917.csv
            if original_filename.startswith('NewsResult_'):
                # 파일 확장자 제거
                name_without_ext = os.path.splitext(original_filename)[0]
                
                # NewsResult_15600305-2025091720250917에서 날짜 부분 추출
                # 2025091720250917에서 20250917 부분만 추출
                parts = name_without_ext.split('-')
                if len(parts) >= 2:
                    date_part = parts[1]  # 2025091720250917
                    if len(date_part) >= 8:
                        date_only = date_part[:8]  # 20250917
                        new_filename = f"NewsResult_{date_only}-{date_only}.csv"
                        return new_filename
            
            # 변환 실패시 원본 파일명 사용
            return original_filename
            
        except Exception as e:
            self.logger.warning(f"파일명 변환 실패: {e}, 원본 파일명 사용")
            return original_filename

    def upload_to_s3(self, file_path, s3_key=None):
        """파일을 S3에 업로드"""
        try:
            from config import S3_BUCKET_NAME, S3_REGION, S3_PREFIX
            
            # S3 클라이언트 생성
            s3_client = boto3.client(
                's3',
                region_name=S3_REGION,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                aws_session_token=os.environ.get('AWS_SESSION_TOKEN')  # 임시 자격 증명 사용시
            )
            
            # S3 키 생성
            if s3_key is None:
                original_filename = os.path.basename(file_path)
                new_filename = self.convert_filename_format(original_filename)
                s3_key = f"{S3_PREFIX}{new_filename}"
            
            # 파일 업로드
            self.logger.info(f"S3 업로드 시작: {file_path} -> s3://{S3_BUCKET_NAME}/{s3_key}")
            
            s3_client.upload_file(
                file_path,
                S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'ContentType': 'text/csv' if file_path.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
            )
            
            s3_url = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            self.logger.info(f"S3 업로드 완료: {s3_url}")
            
            return s3_url
            
        except Exception as e:
            self.logger.error(f"S3 업로드 실패: {e}")
            return None

    def upload_csv_to_s3(self, download_dir="./downloads"):
        """CSV 파일을 S3에 업로드"""
        try:
            # CSV 파일 찾기
            csv_files = glob.glob(os.path.join(download_dir, "*.csv"))
            if not csv_files:
                self.logger.warning("업로드할 CSV 파일을 찾을 수 없습니다.")
                return None
            
            # 가장 최근 CSV 파일 선택
            latest_csv = max(csv_files, key=os.path.getctime)
            self.logger.info(f"CSV 파일 발견: {latest_csv}")
            
            # S3에 업로드
            s3_url = self.upload_to_s3(latest_csv)
            
            if s3_url:
                self.logger.info(f"CSV 파일 S3 업로드 성공: {s3_url}")
                return s3_url
            else:
                self.logger.error("CSV 파일 S3 업로드 실패")
                return None
                
        except Exception as e:
            self.logger.error(f"CSV S3 업로드 중 오류: {e}")
            return None

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
