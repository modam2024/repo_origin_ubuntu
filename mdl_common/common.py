import re

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
# 작성일 : 2024.08.17
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

def filter_text(text):
    # 정규 표현식 패턴: 영어 대소문자, 공백, 특수문자, 한글 문자 포함
    pattern = re.compile(r'[a-zA-Z\s\W가-힣]')

    # 정규 표현식과 일치하는 문자만 남기고 합침
    filtered_text = ''.join(pattern.findall(text))

    return filtered_text

def filter_eng_text(text):
    # 정규 표현식 패턴: 영어 대소문자, 공백, 특수문자, 한글 문자 포함
    text = text.replace("A :", "")
    text = text.replace("B :", "")

    pattern = re.compile(r'[a-zA-Z\s\'\’]')
    # 정규 표현식과 일치하는 문자만 남기고 합침
    filter_eng_text = ''.join(pattern.findall(text))

    return filter_eng_text
