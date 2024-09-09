import json

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from mdmproj1 import settings
from . import create_connection, close_connection, handle_sql_error

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def sql_dao(request, sql_name, p_param):
    conn, cursor, current_username = create_connection(request)
    df_page_info = pd.DataFrame()
    df_questions = pd.DataFrame()

    try:
        ''' 
        ##############
         SELECT BLOCK
        ##############  '''
        '''
        ############################################################
        # CALL ID : sqls_proj_converted_sentn
        # 함수명   : 변환 문장을 조회한다.   
        # 작성일   : 2024.07.10
        # 작업     : db_converted_sentn 에 저장된 자료를 조회한다.   
        ############################################################ '''
        if sql_name == "sqls_proj_converted_sentn":
            topic_param = ""

            if p_param == "submit_topic":
               data = json.loads(request.body)
               topic_param = data.get("sourceUrl")  # 소스 Url 추가
            elif p_param == "main_cnvrt_tpc_exec":
               topic_param = request.GET.get("topic_num")

            query = "  SELECT no, ifnull(topic_num,''), ifnull(src_title,''), ifnull(whitespace_converted,''), ifnull(converted_sentn,''), ifnull(original_sentn,'') "
            query += "   FROM tb_convert_living_english "
            if p_param == "submit_topic":
                query += "  WHERE user_id   = %s "
                query += "    AND src_url   = %s "
            elif p_param == "main_cnvrt_tpc_exec":
                query += "  WHERE user_id   = %s "
                query += "    AND topic_num = %s "
            query += "  ORDER BY no ASC "
            params = (current_username, topic_param,)
            cursor.execute(query, params)
            existing_topic = cursor.fetchall()

            return existing_topic

        '''
        #############################################################
        # 문장 분석 submition 완료확인 함수
        # 작성일 : 2024.07.10
        # 작업 : 모든 페이지에서 문장 분석 프로시져 처리 여부 확인용도 
        ############################################################# '''
        if sql_name == "sqls_proj_submit_article_pre_check":
            re_title_cnt = ""

            data = json.loads(request.body)
            source_url   = data.get("sourceUrl")    # 소스 Url 추가
            source_title = data.get("sourceTitle")  # 소스 Title 추가
            source_type  = data.get("sourceType")   # 소스 Type 추가

            select_query  = "  SELECT count(*)   "
            select_query += "   FROM processed_words "
            select_query += "  WHERE user_id    = %s "
            select_query += "    AND src_url    = %s "
            select_query += "    AND group_code = %s "
            select_query += "    AND src_title  = %s "
            select_param = ( current_username, source_url, source_type, source_title, )

            # 쿼리 실행
            cursor.execute(select_query, select_param, )
            src_title_cnt = cursor.fetchone()
            re_title_cnt = str(src_title_cnt[0])

            return re_title_cnt

        '''
        #############################################################
        # CALL ID : sqls_retrieve_ing_chapter_num
        # 함수명   : 완료된  capther  번호 다음 번호 조회
        # 작업     : 완료된  capther  번호 다음 번호 조회        
        # 작성일   : 2024.09.10
        # 작성자   : 이용학 
        ############################################################# '''
        if sql_name == "sqls_retrieve_ing_chapter_num":

            selectd_chapter = p_param

            try:
                # 이미 데이터베이스에 해당 단어가 있는지 확인
                select_query  = "  SELECT ifnull(max(src_chapter), 0) as max_chapter_num "
                select_query += "   FROM tb_chapter_title  "
                select_query += "  WHERE user_id     = %s  "
                select_query += "    AND src_chapter < %s  "
                select_query += "    AND status      = 'C' "
                select_param = (current_username, selectd_chapter)

                # 쿼리 실행
                cursor.execute(select_query, select_param, )
                existing_max_chapter_num = cursor.fetchone()
                return existing_max_chapter_num[0]
            except Exception as e:
                print("retrieve max num query failed: ", e)
                return "0"

        ''' 
        ##############
         INSERT BLOCK
        ############## '''
        '''
        #############################################################
        # 함수명 : 날짜별 학습 이력 저장
        # 작성일 : 2024.09.07
        # 작업 : 메인 메뉴 또는 서브 메뉴 클릭할 때마다 이력을 남긴다. 
        ############################################################# '''
        if sql_name == "sqli_click_study_hist":
            p_menu_url = p_menu_url = request.path
            p_main_menu_no = p_param

            click_query = " INSERT INTO tb_click_study_hist "
            click_query += " ( menu_url, main_menu_no, update_date ) "
            click_query += " VALUES "
            click_query += " ( %s, %s, date_format(now(), '%Y-%m-%d %H:%i:%S') ) "
            click_params = (p_menu_url, p_main_menu_no)
            cursor.execute(click_query, click_params)

        '''
        ##############
         UPDATE BLOCK
        ############## '''

    except Exception as e:
        return handle_sql_error(e, sql_name)

    finally:
        close_connection(conn, cursor)
'''         
##################   
# 쿼리 CALL 함수 끝    
################## '''
'''
############################################################
# CALL ID : check_login_status
# 함수명   : request 객체의 url 값을 추출한다.   
# 작성일   : 2024.09.08
# 작업     : request 객체의 url 값을 추출한다.   
############################################################ '''
@login_required(login_url='/login/')
def check_login_status(request):
    full_url  = request.build_absolute_uri()
    base_url  = "http://modameng.com:8000"
    local_url = "http://localhost:8001"
    page_url  = "/article/main-wordcheck/?source_url=&source_title=&source_type=NEWS&source_status=C"

    if base_url in full_url:
        source_url = base_url + page_url
    else:
        source_url = local_url + page_url

    return HttpResponseRedirect(source_url)
