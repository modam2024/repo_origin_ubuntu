import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def fn_connector(request):
    sub_conn = mysql.connector.connect(
        host="modamtech.com",
        port=3306,
        user="aeit",
        password="susx2020",
        database="aeit",
    )
    return sub_conn

'''
#######################################################
# 동적으로 코드가 더이상 수행되지 않을 때 까지 기다리는 함수
# 작성일 : 2024.07.15
####################################################### '''
def url_parsing_with_webdriver(url, p_type):
    service = Service(
        executable_path="C:\\pyDjangoDEV\\mdmproj1\\chromedriver-win64\\chromedriver.exe"
    )

    # Headless 모드를 위한 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    # ChromeDriver를 headless 모드로 시작합니다.
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    if p_type == "1":
        WebDriverWait(driver, 20).until(
            lambda driver: driver.execute_script("return jQuery.active == 0")
        )
    elif p_type == "2":
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "component_example"))
        )
    elif p_type == "3":
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "comment-top"))
    )

    # 페이지의 소스를 가져옵니다.
    html = driver.page_source

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(html, "lxml")

    # 브라우저 종료
    driver.quit()

    return html, soup