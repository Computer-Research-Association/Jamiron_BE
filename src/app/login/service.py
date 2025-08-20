from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class SyllabusCollector:
    """
    히즈넷에서 강의 계획서 정보를 수집하는 클래스.
    """

    def __init__(self, progress_callback=None):
        """
        SyllabusCollector 인스턴스를 초기화함.
        """
        self.driver = None
        self.base_url = "https://hisnet.handong.edu/"
        self.login_url = self.base_url + "login/login.php"
        
    def _initialize_webdriver(self):
        """WebDriver를 초기화함."""
        if self.driver:
            return

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            raise Exception(f"WebDriver 초기화 실패: {e}")

    def login(self, user_id: str, password: str) -> bool:
        """
        히즈넷 사이트에 로그인 수행.
        """
        self._initialize_webdriver()
        self.driver.get(self.login_url)

        try:
            id_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(1) > td:nth-child(2) > span > input[type=text]",
            )
            id_input.send_keys(user_id)

            password_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2) > input[type=password]",
            )
            password_input.send_keys(password)

            login_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > input[type=image]",
            )

            login_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#kang_yy"))
            )
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return True 
        
        except Exception:
            return False
        finally:
            self.close()


    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None