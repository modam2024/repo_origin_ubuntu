import json
import re

import pandas as pd

from app_common import app_common_mdl as comn_func
from mdl_sql_mapping import create_connection, close_connection, handle_sql_error

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
        # CALL ID : sqls_select_db_converted_sentn
        # 함수명   : 변환 문장을 조회한다.   
        # 작성일   : 2024.07.10
        # 작업     : db_converted_sentn 에 저장된 자료를 조회한다.   
        ############################################################ '''
        if sql_name == "sqls_select_tb_converted_sentn":
            topic_param = ""

            if p_param == "submit_topic":
               data = json.loads(request.body)
               topic_param = data.get("sourceUrl")  # 소스 Url 추가
            elif p_param == "main_cnvrt_tpc_exec":
               topic_param = request.GET.get("topic_num")

            query = "  SELECT no, ifnull(topic_num,''), ifnull(src_title,''), ifnull(whitespace_converted,''), ifnull(converted_sentn,''), ifnull(original_sentn,'') "
            query += "   FROM tb_converted_sentn "
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
        if sql_name == "sqls_submit_article_pre_check":
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
        ##############
         INSERT BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqli_insert_tb_converted_sentn
        # 함수명   : 변환된 문장을 저장한다.   
        # 작성일   : 2024.07.02
        # 작업     : 변환된 문장을 저장한다.   
        ############################################################  '''
        if sql_name == "sqli_insert_tb_converted_sentn":
            data = json.loads(request.body)
            source_url = data.get("sourceUrl")  # 소스 Url 추가
            source_title = data.get("sourceTitle")  # 소스 Title 추가
            source_type = data.get("sourceType")  # 소스 Type 추가
            list_rslt_sentns = p_param

            int_test_cnt = 0

            # base_url 부분을 제거
            base_url = "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx="
            topic_num = source_url.replace(base_url, "")

            for whitespace_converted, converted_sentn, original_sentn, translated_sentn in list_rslt_sentns:
                str_whitespace_converted = whitespace_converted
                str_converted_sentn      = converted_sentn
                str_original_sentn       = original_sentn
                str_translated_sentn     = translated_sentn

                int_test_cnt += 1

                ins_query = " INSERT INTO tb_converted_sentn "
                ins_query += " (no, user_id, topic_num, whitespace_converted, converted_sentn, original_sentn, translated_sentn, src_url, group_code, src_title) "
                ins_query += (
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                )
                ins_params = (
                    int_test_cnt,
                    current_username,
                    topic_num,
                    str_whitespace_converted,
                    str_converted_sentn,
                    str_original_sentn,
                    str_translated_sentn,
                    source_url,
                    source_type,
                    source_title,
                )

                cursor.execute(ins_query, ins_params)

            return int_test_cnt
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
##################        
'''