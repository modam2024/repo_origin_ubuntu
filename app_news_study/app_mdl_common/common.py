import datetime
import re
from typing import List, Dict

import pandas as pd
import pytz

from app_news_study.app_sql_statement import sql_statement as sql_statement
from proj_common import common as proj_comn_func


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
'''
########################################################
# tag_decompose 함수 선언
# - 본문 내용 중에 불필요한 태그의 텍스트 제외하는 함수
########################################################
'''
def tag_decompose(p_article, p_tag, p_class=None, p_id=None):
    # id나 class 기반으로 태그를 찾습니다
    if p_class:
        wps_divs = p_article.find_all(p_tag, class_=p_class)
    elif p_id:
        wps_divs = p_article.find_all(p_tag, id=p_id)
    else:
        wps_divs = p_article.find_all(p_tag)

    # 각 해당 div 태그를 순회하며 제거
    if (p_tag == "b"):
        for wps_div in wps_divs:
            wps_div_text = "#"+ wps_div.text + "#"  # 전체 Tag 객체를 문자열로 변환하여 사용
            wps_div.replace_with(wps_div_text)
    else:
        for wps_div in wps_divs:
            wps_div.decompose()

'''
#######################################################
# 중앙일보 문장학습 정보 사전분석 작업
# 작성일 : 2024.08.07
####################################################### '''
def get_url_keyitems(url):
    text_data: List[Dict[str, str]] = []

    html, soup = proj_comn_func.url_parsing_with_webdriver(url, "3")
    article = soup.find('div',    class_='article_body')
    tag_decompose(article, 'div', p_id='admaruPlayerWrapperContainer')
    tag_decompose(article, 'h1',  p_class='view-article-title')
    tag_decompose(article, 'div', p_class='topArea')
    tag_decompose(article, 'div', p_class='journalistArea')
    tag_decompose(article, 'div', p_class='ab_photo')
    tag_decompose(article, 'p',   p_class='caption')
    tag_decompose(article, 'br',  )
    tag_decompose(article, 'b',   )
    each_texts = article.text.split("#")

    for each_text in each_texts:
        if len(each_text.strip()) > 0:
            # \xa0가 3개 이상 연속되거나 'WRITTEN BY'가 포함된 경우로 문자열 분할
            pattern = r'(\xa0\s*){3,}| BY |WRITTEN BY| {5,}'
            each_sentences = re.split(pattern, each_text.strip())

            for sentence in each_sentences:
                if sentence is not None and len(sentence.strip()) > 0:
                    text_data.append({'Text': sentence.strip()})

    df_text = pd.DataFrame(text_data)

    records = df_text.to_dict(orient='records')

    return records

'''
#######################################################
# 중앙일보 문장학습 정보 사전분석 작업 (DB 저장을 위한 함수)
# 날짜 형식의 데이터 이후 부터 데이터베이스에 저장하기 위한 검색
# 작성일 : 2024.08.07
####################################################### '''
def is_date_string(text):
    try:
        # 텍스트를 쉼표로 분할
        parts = text.split(',')
        # 마지막 두 부분을 다시 조합하여 날짜 부분을 완성
        if len(parts) >= 2: # 적어도 세 부분으로 나눠져야 함 (요일, 월일, 년도)
            date_part = parts[-1].strip()  # 'July 23, 2024' 형태로 재구성

            # strptime을 사용하여 문자열을 datetime 객체로 파싱
            date_obj = datetime.datetime.strptime(date_part, '%Y')
            print(date_obj)
            return True
    except ValueError:
        # 'date_part'가 연도 형식이 아닌 경우
        return False
    except IndexError:
        # 'parts' 리스트가 너무 짧은 경우
        return False

    return False

'''
#######################################################
# 중앙일보 문장학습 정보 사전분석 작업 (DB 저장 함수)
# 작성일 : 2024.08.07
# 파라미터 news_info 의 구조
news_info = {
    'URL': link,
    'TITLE': each_items[-2].replace("-", " "),
    'DATE': each_items[4],
    'DEPT': each_items[5],
    'SECTION': each_items[6],
    'KEYNO': each_items[-1],
    'KEYITEM': list_keyitems
}
####################################################### '''
def save_to_news_info_database(request, news_info):
    res_sql_insert = ""

    dic_news_info = {}
    dic_news_info['NEWSORDER'] = news_info['NEWSORDER']
    dic_news_info['URL']       = news_info['URL']
    dic_news_info['TITLE']     = news_info['TITLE']
    dic_news_info['DATE']      = news_info['DATE']
    dic_news_info['DEPT']      = news_info['DEPT']
    dic_news_info['SECTION']   = news_info['SECTION']
    dic_news_info['KEYNO']     = news_info['KEYNO']
    dic_news_info['KEYITEM']   = ""

    bl_insert_flag = False
    for item in news_info['KEYITEM']:
       try:
           if bl_insert_flag:
              dic_news_info['KEYITEM'] = item['Text']
              if except_rules(item['Text']):
                 res_sql_insert = sql_statement.sql_dao(request, "sqli_news_info", dic_news_info)

           is_date_item = is_date_string(item['Text'])
           if is_date_item:
              bl_insert_flag = True

       except Exception as e:
           print(f"Error inserting data into database: {e}")
           res_sql_insert = ""

    item_cnt:int = 0
    if bl_insert_flag == False and len(news_info['KEYITEM']) > 10:
        for item in news_info['KEYITEM']:
            item_cnt += 1
            if item_cnt > 3:
               dic_news_info['KEYITEM'] = item['Text']
               if except_rules(item['Text']):
                  res_sql_insert = sql_statement.sql_dao(request, "sqli_news_info", dic_news_info)

    return res_sql_insert

def extract_english(text):
    # 영어 문자만 추출하는 정규식 패턴
    pattern = r'[a-zA-Z]+'
    # re.findall()을 사용하여 모든 영어 문자를 추출
    english_chars = re.findall(pattern, text)
    # 추출된 영어 문자를 하나의 문자열로 합침
    return ''.join(english_chars)

def check_length_of_english(text):
    # 영어 문자 추출
    english_text = extract_english(text)
    # 영어 문자의 길이 확인
    return len(english_text) > 10

def extract_korean(text):
    # 한글 문자만 추출하는 정규식 패턴
    pattern = r'[가-힣]+'
    # re.findall()을 사용하여 모든 한글 문자를 추출
    korean_chars = re.findall(pattern, text)
    # 추출된 한글 문자를 하나의 문자열로 합침
    return ''.join(korean_chars)

# news type 이 INF 인 경우
def check_subscript(text):
    subscript = ""
    subscript = re.findall(r'[a-zA-Z]:|[a-zA-Z] :', text)
    korean_text = extract_korean(text)

    if len(subscript) > 0 and len(korean_text) > 0:
        return True
    else:
        return False

def check_length_of_korean(text):
    # 한글 문자 추출
    korean_text = extract_korean(text)
    # 한글 문자의 길이 확인
    return len(korean_text) > 10

def except_rules(text):
    # item 딕셔너리에서 'Text' 키에 해당하는 값이 '기사'로 끝나는지 확인
    if text.endswith('기사'):
       return False
    else:
        return True

def get_recent_news_date(request):

    # 서울 시간대를 설정합니다.
    seoul_timezone = pytz.timezone('Asia/Seoul')

    # 현재 날짜와 시간을 서울 시간대로 가져옵니다.
    now = datetime.datetime.now(seoul_timezone)

    # 날짜를 'YYYY-MM-DD' 형식으로 포맷합니다
    today_news_date = now.strftime('%Y-%m-%d')

    is_recent_news, max_news_date = sql_statement.sql_dao(request, "sqls_recent_news_date", today_news_date)

    return is_recent_news, today_news_date, max_news_date

def update_non_eng_type_groupno(request, param):
    detail_info = param

    tmp_news_groupno = 0
    for news_data in detail_info:
        news_keyno, news_num, news_newstype, news_groupno = news_data
        if news_newstype == "ENG":
            tmp_news_groupno = news_groupno
        else:
            if tmp_news_groupno != 0:
               trgt_news_data = {
                   "news_keyno"    : news_keyno,
                   "news_num"      : news_num,
                   "news_newstype" : news_newstype,
                   "news_groupno"  : tmp_news_groupno,
               }
               # 뉴스 사이트 정보를 문장 단락별로 그룹화 한다.
               result_value = sql_statement.sql_dao(request, "sqlu_non_eng_type_groupno", trgt_news_data)

    # 뉴스 사이트 정보를 문장 단락별로 그룹화 한다.
    result_value = sql_statement.sql_dao(request, "sqld_less_couple_groupno", "")

    return "OK"