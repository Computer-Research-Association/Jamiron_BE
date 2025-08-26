from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import re
import os
import threading
import math
import json
from sqlalchemy.orm import Session
from src.app.model import Syllabus  # models.py에서 import
from ..config.database import SessionLocal  # 데이터베이스 세션


# process_and_save_syllabus 함수는 preprocessor.py에서 import하여 사용


def clean_text(text: str) -> str:
    """텍스트에서 공백을 정리하고 앞뒤 공백을 제거함."""
    text = re.sub(r"\s+", " ", text).strip()
    return text

class SyllabusCollector:
    """
    히즈넷에서 강의 계획서 정보를 수집하고 데이터베이스에 저장하는 클래스.
    """

    def __init__(self, progress_callback=None):
        """
        SyllabusCollector 인스턴스를 초기화함.

        Args:
            progress_callback (callable, optional): 진행 상황을 업데이트할 콜백 함수.
                                                   메시지와 진행률(0-100)을 인자로 받음.
        """
        self.driver = None
        self.base_url = "https://hisnet.handong.edu/"
        self.login_url = self.base_url + "login/login.php"
        self.progress_callback = progress_callback
        self.current_user_year = None
        self.current_user_semester = None
        self.saved_syllabuses_count = 0  # JSON 리스트 대신 저장 카운트 사용
        self.collected_class_codes = []

    def _update_progress(self, message: str, percent: int):
        """진행 상황을 콜백 함수를 통해 업데이트함."""
        if self.progress_callback:
            self.progress_callback(message, percent)

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
            self._update_progress(f"WebDriver 초기화 실패: {e}", 0)
            raise

    def login(self, user_id: str, password: str) -> bool:
        """
        히즈넷 사이트에 로그인 수행.
        """
        self._initialize_webdriver()
        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return False

        self._update_progress("로그인 시도 중...", 50)
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
            self._update_progress("로그인 성공!", 100)
            return True
        except Exception as e:
            self._update_progress(
                f"로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요. ({e})", 0
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    def navigate_to_planner_page(self, year: str, semester: str) -> bool:
        self.current_user_year = year
        self.current_user_semester = semester

        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return False

        try:
            my_year_select = Select(
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#kang_yy"))
                )
            )
            if year not in [
                option.get_attribute("value") for option in my_year_select.options
            ]:
                self._update_progress(
                    f"해당 학년도({year})에 대한 강의를 찾을 수 없습니다.", 0
                )
                return False
            my_year_select.select_by_value(year)

            my_semester_select = Select(
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#kang_hakgi"))
                )
            )
            my_semester_select.select_by_value(semester)

            load_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#tr_box_1 > table > tbody > tr:nth-child(1) > td > div > div > form > a",
                    )
                )
            )
            load_btn.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#div_box_1"))
            )
            return True
        except (NoSuchElementException, TimeoutException) as e:
            self._update_progress(
                f"강의 계획서 페이지 이동 중 오류 발생 (요소 찾기 실패 또는 타임아웃): {e}",
                0,
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False
        except Exception as e:
            self._update_progress(
                f"강의 계획서 페이지 이동 중 예상치 못한 오류 발생: {e}", 0
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    def download_planners(self):
        self.collected_syllabuses = []
        """강의 계획서를 다운로드하고 데이터베이스에 저장"""
        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return

        classes_list = self._get_class_list()
        total_classes = len(classes_list)

        if total_classes == 0:
            self._update_progress("해당 학기 강의가 없습니다.", 100)
            return

        self._update_progress("데이터베이스 연결 확인 중...", 5)

        # 데이터베이스 연결 테스트
        if not self.test_database_connection():
            self._update_progress("데이터베이스 연결 실패! 설정을 확인하세요.", 0)
            return

        # 강의 코드 리스트 초기화 (혹시 모를 재호출 대비)
        self.collected_class_codes = []  # ✨ 이 줄을 추가하여 호출 시마다 초기화합니다. ✨

        for idx, class_info in enumerate(classes_list, 1):
            url = class_info["href"]
            title = class_info["title"]

            print(f"처리 중인 URL: {url}")
            temp = url[-16:]
            syllabus_detail_url = f"{self.base_url}SMART/lp_view_4student_1.php?kang_yy={temp[:4]}&kang_hakgi={temp[5]}&kang_code={temp[-8:]}&kang_ban={temp[6:8]}"

            try:
                data = self._parse_syllabus_page(
                    syllabus_detail_url,
                    title,
                    self.current_user_year,
                    self.current_user_semester,
                )

                if data:
                    raw_success = self._save_syllabus_to_db(data)
                    if raw_success:
                        self.saved_syllabuses_count += 1

                        syllabus_info = {
                            "class_code": data.get('class_code'),
                            "class_name": data.get('class_name'),
                            "professor_name": data.get('professor_name')
                        }
                        if syllabus_info not in self.collected_syllabuses:
                            self.collected_syllabuses.append(syllabus_info)

                    try:
                        from ..utils.file_process.preprocessor import (
                            process_and_save_syllabus,
                        )

                        processed_data = process_and_save_syllabus(
                            data, self.current_user_year, self.current_user_semester, title
                        )

                        if processed_data:
                            processed_success = self._save_syllabus_to_db(processed_data)
                            # 만약 전처리된 데이터 저장이 성공했고, raw 데이터 저장 시 코드를 추가하지 않았다면 여기에서 추가할 수 있습니다.
                            # 하지만 일반적으로 raw 데이터 저장 시 한 번만 추가하는 것이 목적에 부합합니다.
                            # if processed_success and not raw_success: # 이 조건은 raw_success가 False일 때만 추가하므로, 이미 추가된 코드를 다시 추가하지 않을 때 유용합니다.
                            #     class_code = processed_data.get('class_code')
                            #     if class_code and class_code not in self.collected_class_codes:
                            #         self.collected_class_codes.append(class_code)
                            if processed_success and raw_success is None:  # raw_success가 실패했을 때 processed_data가 저장되었다면
                                class_code = processed_data.get('class_code')
                                if class_code and class_code not in self.collected_class_codes:
                                    self.collected_class_codes.append(class_code)

                    except Exception as preprocessor_error:
                        print(f"전처리 과정에서 오류 발생 (원본은 저장됨): {preprocessor_error}")

                progress_percent = 5 + int((idx / total_classes) * 90)
                self._update_progress(
                    f"[{idx}/{total_classes}] {title} 처리 완료",
                    progress_percent,
                )
            except Exception as e:
                progress_percent = 5 + int((idx / total_classes) * 90)
                self._update_progress(
                    f"[{idx}/{total_classes}] {title} 처리 중 오류 발생: {str(e)[:50]}...",
                    progress_percent,
                )
                print(f"ERROR: Exception during processing {title}: {e}")
                continue

        self._update_progress(
            f"크롤링 완료! 총 {self.saved_syllabuses_count}개 강의 계획서가 데이터베이스에 저장되었습니다.",
            100
        )

    def get_collected_syllabuses(self) -> list:
        """수집된 강의 코드, 강의명, 교수명 리스트를 반환"""
        return self.collected_syllabuses

    def _save_syllabus_to_db(self, syllabus_data: dict) -> bool:
        """강의 계획서 데이터를 데이터베이스에 저장"""
        db = SessionLocal()
        try:
            # 데이터베이스 연결 테스트
            #db.execute("SELECT 1")

            # 기존 데이터 확인 (중복 방지)
            existing_syllabus = db.query(Syllabus).filter(
                Syllabus.class_code == syllabus_data.get('class_code'),
                Syllabus.year == syllabus_data.get('year'),
                Syllabus.semester == syllabus_data.get('semester')
            ).first()

            if existing_syllabus:
                # 기존 데이터 업데이트
                existing_syllabus.class_name = syllabus_data.get('class_name', '')
                existing_syllabus.professor_name = syllabus_data.get('professor_name', '')
                existing_syllabus.prof_email = syllabus_data.get('prof_email', '')
                existing_syllabus.objectives = syllabus_data.get('objectives', '')
                existing_syllabus.description = syllabus_data.get('description', '')
                existing_syllabus.schedule = syllabus_data.get('schedule', '')
                print(f"기존 강의 계획서 업데이트: {syllabus_data.get('class_name')}")
            else:
                # 새로운 데이터 생성
                new_syllabus = Syllabus(
                    class_name=syllabus_data.get('class_name', ''),
                    class_code=syllabus_data.get('class_code', ''),
                    professor_name=syllabus_data.get('professor_name', ''),
                    prof_email=syllabus_data.get('prof_email', ''),
                    year=syllabus_data.get('year', ''),
                    semester=syllabus_data.get('semester', ''),
                    objectives=syllabus_data.get('objectives', ''),
                    description=syllabus_data.get('description', ''),
                    schedule=syllabus_data.get('schedule', '')
                )
                db.add(new_syllabus)
                print(f"새 강의 계획서 저장: {syllabus_data.get('class_name')}")

            db.commit()
            print(f"✅ DB 저장 성공: {syllabus_data.get('class_name')}")
            return True

        except Exception as e:
            db.rollback()
            print(f"❌ 데이터베이스 저장 오류: {e}")
            print(f"실패한 데이터: {syllabus_data}")
            return False
        finally:
            db.close()

    def _get_class_list(self) -> list:
        classes_list = []
        try:
            print(f"현재 페이지 URL: {self.driver.current_url}")
            print("강의 목록 요소 대기 중...")

            # old/crawler.py 방식: 2초 대기 후 div 요소들을 순차적으로 확인
            time.sleep(2)

            div_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "#div_box_1 > div"
            )
            print(f"div_box_1 내부의 div 요소 개수: {len(div_elements)}")

            for i in range(1, len(div_elements) + 1):
                try:
                    my_class = self.driver.find_element(
                        By.CSS_SELECTOR,
                        f"#div_box_1 > div:nth-child({i}) > a:nth-child(2)",
                    )
                    href = my_class.get_attribute("href")
                    text = my_class.text.strip()

                    if href and text:
                        classes_list.append({"href": href, "title": text})
                        print(f"강의 추가: {text} - {href}")

                except Exception as e:
                    print(f"div {i} 처리 중 오류: {e}")
                    continue

        except Exception as e:
            print(f"강의 목록 파싱 중 예상치 못한 오류 발생: {e}")
            # 오류 발생 시에만 프로그래스바에 메시지 표시
            self._update_progress(f"강의 목록 파싱 중 예상치 못한 오류 발생: {e}", 0)

        print(f"총 {len(classes_list)}개의 강의를 찾았습니다.")
        return classes_list

    def _parse_syllabus_page(
        self, url: str, class_title: str, year: str, semester: str
    ) -> dict:
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        prof_name = ""
        try:
            prof_name_element = soup.select_one(
                "#div1 > div > table:nth-child(3) > tbody > tr:nth-child(5) > td:nth-child(1) > div"
            )
            if prof_name_element:
                prof_name = prof_name_element.get_text(strip=True)
        except Exception:
            pass

        prof_email = ""
        try:
            prof_email_element = soup.select_one(
                "#div1 > div > table:nth-child(3) > tbody > tr:nth-child(5) > td:nth-child(2)"
            )
            if prof_email_element:
                prof_email = prof_email_element.get_text(strip=True)
        except Exception:
            pass

        tds_description = soup.select(
            "#div1 > div > table:nth-child(13) > tbody > tr > td"
        )
        description_text = "\n".join(
            [clean_text(td.get_text()) for td in tds_description]
        )

        objectives_text = "Course Objectives\n"
        tds_objectives = soup.select("#tbl_Obj > tbody > tr")[1:]
        for tr in tds_objectives:
            td_element = tr.select_one("td.cls_AlignLeft")
            if td_element:
                objectives_text += clean_text(td_element.get_text()) + "\n"

        schedule_text = ""
        i = 2
        while True:
            selector = f"#tblN16 > tbody > tr:nth-child({i}) > td:nth-child(3)"
            td = soup.select_one(selector)
            if not td:
                break
            text = clean_text(td.get_text())
            if text:
                schedule_text += text + "\n"
            i += 1

        match = re.search(r"kang_code=([^&]+)", url)
        kang_code = match.group(1)
        temp = url[-16:]

        return {
            "class_name": class_title,
            "class_code": kang_code,
            "professor_name": prof_name,
            "prof_email": prof_email,
            "year": year,
            "semester": semester,
            "objectives": objectives_text.strip(),
            "description": description_text.strip(),
            "schedule": schedule_text.strip(),
        }

    def get_saved_syllabuses_count(self) -> int:
        """저장된 강의 계획서 개수 반환"""
        return self.saved_syllabuses_count

    def get_all_syllabuses_from_db(self, year: str = None, semester: str = None) -> list:
        """데이터베이스에서 강의 계획서 조회"""
        db = SessionLocal()
        try:
            query = db.query(Syllabus)

            if year:
                query = query.filter(Syllabus.year == year)
            if semester:
                query = query.filter(Syllabus.semester == semester)

            syllabuses = query.all()

            # 딕셔너리 형태로 변환
            result = []
            for syllabus in syllabuses:
                result.append({
                    "id": syllabus.id,
                    "class_name": syllabus.class_name,
                    "class_code": syllabus.class_code,
                    "professor_name": syllabus.professor_name,
                    "prof_email": syllabus.prof_email,
                    "year": syllabus.year,
                    "semester": syllabus.semester,
                    "objectives": syllabus.objectives,
                    "description": syllabus.description,
                    "schedule": syllabus.schedule,
                })
            
            return result
            
        except Exception as e:
            print(f"데이터베이스 조회 오류: {e}")
            return []
        finally:
            db.close()

    def test_database_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            db = SessionLocal()
            #db.execute("SELECT 1")
            db.close()
            print("✅ 데이터베이스 연결 성공!")
            return True
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None




syllabusCollector = SyllabusCollector()
def get_syllabus_collector():
    return syllabusCollector
