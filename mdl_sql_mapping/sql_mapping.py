import json
import re

import pandas as pd

from mdl_common import common as comn_func
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
        #############################################################
        # 테스트 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 테스트 데이터를 읽어오는 쿼리 수행
        ############################################################# '''
        if sql_name == "sqls_test_info_if_first":

            selectd_version = request.GET.get("check")
            temp_next_page_date = ""

            select_query = "  SELECT DISTINCT trgt_page_date, next_page_date, last_page_flag, prve_page_date "
            select_query += "   FROM tb_test_page_info "
            select_query += "  WHERE user_id = %s "
            select_query += "  ORDER BY trgt_page_date desc "
            select_param  = (current_username,)

            try:
                temp_trgt_page_date = ""
                # 쿼리 실행
                cursor.execute(select_query, select_param)
                existing_pagedates = cursor.fetchall()

                # 첫 번째 튜플을 리스트로 변환
                first_page_data_list = list(existing_pagedates[0])

                temp_trgt_page_date = first_page_data_list[0]
                temp_next_page_date = first_page_data_list[1]
                temp_last_page_flag = first_page_data_list[2]
                temp_prve_page_date = first_page_data_list[3]

                if temp_last_page_flag == "Y":  # last_page_flag는 튜플의 2번째 요소이므로 인덱스는 1
                   temp_next_page_date = call_sql_update_next_page_date(request, temp_trgt_page_date)

                if temp_next_page_date == "":
                   temp_next_page_date = temp_trgt_page_date

            except Exception as e:
                print(e)

            return temp_next_page_date

        '''
        #############################################################
        # 테스트 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 테스트 데이터를 읽어오는 쿼리 수행
        ############################################################# '''
        if sql_name == "sqls_test_info_by_date":
            v_trgt_page_date = request.GET.get("wdate")

            df_page_info = pd.DataFrame()

            select_query = "  SELECT DISTINCT trgt_order_no, trgt_page_date, prve_page_date, next_page_date, last_page_flag  "
            select_query += "   FROM tb_test_page_info   "
            select_query += "  WHERE user_id = %s        "
            select_query += "    AND trgt_page_date = %s "
            select_param = (current_username, v_trgt_page_date,)

            try:
                # 쿼리 실행
                cursor.execute(select_query, select_param, )
                existing_pagedates = cursor.fetchall()

                # df_content를 DataFrame으로 변환
                df_page_info = pd.DataFrame(existing_pagedates,
                                            columns=['trgt_order_no', 'trgt_page_date', 'prve_page_date', 'next_page_date', 'last_page_flag'])

            except Exception as e:
                df_page_info = pd.DataFrame()

            return df_page_info

        '''
        #########################################################
        # 테스트 질문 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 테스트 질문 데이터를 읽어온다.
        ######################################################### '''
        if sql_name == "sqls_test_question_info_by_date":

            v_trgt_page_date = request.GET.get("wdate")

            select_query = "  SELECT DISTINCT question_no, question_content, choice_a, choice_b, choice_c, choice_d  "
            select_query += "   FROM tb_test_page_info   "
            select_query += "  WHERE user_id = %s        "
            select_query += "    AND trgt_page_date = %s "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param, )
            existing_pagedates = cursor.fetchall()

            # df_content를 DataFrame으로 변환
            df_question = pd.DataFrame(existing_pagedates,
                                        columns=[ 'question_no', 'question_content', 'choice_a', 'choice_b', 'choice_c', 'choice_d' ])
            return df_question

        '''
        #######################################################
        # FeedBack 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 FeedBack 데이터를 읽어온다.
        ######################################################### '''
        if sql_name == "sqls_feedback_info_by_date":
            v_trgt_page_date = request.GET.get("test_page_date")

            select_query = "  SELECT DISTINCT trgt_order_no, trgt_page_date "
            select_query += "   FROM tb_feedback_page_info "
            select_query += "  WHERE user_id = %s          "
            select_query += "    AND trgt_page_date = %s   "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param, )
            existing_pagedates = cursor.fetchall()

            # df_content를 DataFrame으로 변환
            df_page_info = pd.DataFrame(existing_pagedates,
                                        columns=['trgt_order_no', 'trgt_page_date'])
            return df_page_info

        '''
        ############################################################
        # FeedBack 질문 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 FeedBack 질문 데이터를 읽어온다.
        ######################################################### '''
        if sql_name == "sqls_feedback_question_info_by_date":
            v_trgt_page_date = request.GET.get("test_page_date")

            select_query = "  SELECT DISTINCT question_no, question_content, choice_a, choice_b, choice_c, choice_d, "
            select_query += "        your_answer, correct_answer, result_value,  feedback "
            select_query += "   FROM tb_feedback_page_info "
            select_query += "  WHERE user_id = %s          "
            select_query += "    AND trgt_page_date = %s   "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param, )
            existing_pagedates = cursor.fetchall()

            # df_content를 DataFrame으로 변환
            df_question = pd.DataFrame(existing_pagedates,
                                        columns=[ 'question_no', 'question_content', 'choice_a', 'choice_b', 'choice_c', 'choice_d',
                                                  'your_answer', 'correct_answer', 'result_value',  'feedback' ])
            return df_question

        '''
        ############################################################
        # select 박스 입력값 조회 함수
        # 작성일 : 2024.06.20
        # 작업 : html 의 select 초기화를 위한 정보를 가져온다.  
        ######################################################### '''
        if sql_name == "sqls_test_page_result_info":

            pagedate_query  = "  SELECT DISTINCT trgt_order_no, trgt_page_date "
            pagedate_query += "    FROM tb_test_page_info     "
            pagedate_query += "  WHERE user_id = %s           "
            pagedate_query += "   ORDER BY trgt_order_no DESC "
            pagedate_param  = (current_username,)

            # 쿼리 실행
            cursor.execute(pagedate_query, pagedate_param, )
            existing_pagedates = cursor.fetchall()

            return existing_pagedates

        '''
        ############################################################
        # 최대 테스트 횟수 조회 함수
        # 작성일 : 2024.06.20
        # 작업 : 테스트 페이지별 최대 테스트 횟수를 가져온다.   
        ######################################################### '''
        if sql_name == "sqls_max_frq_test_page":
            v_trgt_page_date = p_param

            select_query = "  SELECT  ifnull(max(test_no) ,'0') as test_no FROM tb_test_result "
            select_query += "  WHERE user_id = %s         "
            select_query += "    AND  trgt_page_date = %s "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param)
            v_test_no = cursor.fetchone()
            int_test_no = int(v_test_no[0])
            return int_test_no

        '''
        ############################################################
        # CALL ID : sqls_test_page_content_cnt
        # 함수명   : 테스트 문제 입력 여부 판단 함수  
        # 작성일   : 2024.06.20
        # 작업     : 테스트 문제 존재 여부로 판단해서 INSERT 여부 결정 목적   
        ############################################################ '''
        if sql_name == "sqls_test_page_content_cnt":
            v_trgt_page_date = p_param

            select_query  = " SELECT  count(*) as cnt     "
            select_query += "   FROM  tb_test_page_info   "
            select_query += "  WHERE  user_id = %s        "
            select_query += "    AND  trgt_page_date = %s "

            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param)
            v_test_cnt   = cursor.fetchone()
            int_test_cnt = int(v_test_cnt[0])
            return int_test_cnt
        '''
        ############################################################
        # CALL ID : sqls_select_db_converted_sentn
        # 함수명   : 변환 문장을 조회한다.   
        # 작성일   : 2024.07.10
        # 작업     : db_converted_sentn 에 저장된 자료를 죄회한다.   
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
'''
#######################################################
# Test 문제별 다음 날짜 업데이트 함수 
# 작성일 : 2024.06.20
# 작업 : 마지막 일자가 생기면 엡데이트 해주어야 한다.
####################################################### '''
def call_sql_update_next_page_date(request, p_trgt_page_date):
    conn, cursor, current_username = create_connection(request)
    v_trgt_page_date = p_trgt_page_date
    v_next_page_date = ""

    url = "https://free.ybmclass.com/free/toeic/toeic_5min_view.asp?wdate={}&page=1".format(v_trgt_page_date)
    # 공통 함수의 webdriver를 사용해서 파싱한다.
    html, soup = comn_func.url_parsing_with_webdriver(url, "1")
    v_ttitle_view = soup.find(class_=["title-view"])
    if v_ttitle_view:
        # a 태그 모두 찾기
        a_tags = v_ttitle_view.find_all("a")
        # a 태그의 갯수 출력
        for v_prve_next_page_info_tag in v_ttitle_view.find_all("a"):
            a_href = v_prve_next_page_info_tag.get('href')
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            try:
                page_date = re.search(date_pattern, a_href).group()
                list_class = v_prve_next_page_info_tag.get('class')
                if list_class[1] == "btn-next":
                    v_next_page_date = page_date
            except Exception as e:
                v_next_page_date = ""

    update_query =  " UPDATE tb_test_page_info   "
    update_query += "    SET next_page_date = %s "
    if v_next_page_date != "":
        update_query += "  , last_page_flag = 'N'"
    else:
        update_query += "  , last_page_flag = 'Y'"
    update_query += "  WHERE user_id        = %s "
    update_query += "    AND trgt_page_date = %s "
    update_param = (v_next_page_date, current_username, v_trgt_page_date, )

    # 쿼리 실행
    cursor.execute(update_query, update_param, )
    conn.commit()

    return v_next_page_date