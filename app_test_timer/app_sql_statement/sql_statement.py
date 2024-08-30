import json
import re

import pandas as pd

import app_test_timer.app_sql_statement as att
from proj_common import proj_common_mdl as proj_comn_func

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def sql_dao(request, sql_name, p_param):
    conn, cursor, current_username = att.create_connection(request)

    try:
        ''' 
        ##############
         SELECT BLOCK
        ##############  '''
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

            select_query  = "  SELECT count(*)       "
            select_query += "   FROM processed_words "
            select_query += "  WHERE user_id    = %s "
            select_query += "    AND src_url    = %s "
            select_query += "    AND group_code = %s "
            select_query += "    AND src_title  = %s "
            select_params = ( current_username, source_url, source_type, source_title, )

            # 쿼리 실행
            cursor.execute(select_query, select_params, )
            src_title_cnt = cursor.fetchone()
            re_title_cnt = str(src_title_cnt[0])

            return re_title_cnt

        '''
        ###################################################################################################
        LYH-2024.08.21 프로젝트 쿼리에서 어플리케이션 쿼리로 이동
        ###################################################################################################        
        '''
        '''
        ############################################################
        # 최대 테스트 횟수 조회 함수
        # 작성일 : 2024.06.20
        # 작업 : 테스트 페이지별 최대 테스트 횟수를 가져온다.   
        ######################################################### '''
        if sql_name == "sqls_max_frq_test_page":
            v_trgt_page_date = p_param

            select_query  = "  SELECT ifnull(max(test_no) ,'0') as test_no "
            select_query += "   FROM  tb_part5_result_hist "
            select_query += "  WHERE  user_id = %s         "
            select_query += "    AND  trgt_page_date = %s  "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param)
            v_test_no = cursor.fetchone()
            int_test_no = int(v_test_no[0])
            return int_test_no

        '''
        ############################################################
        # 문항별 테스트 시간 & 통계 조회 (feedback 테이블)
        # 작성일 : 2024.08.27
        # 작업 : feedback 테이블에서 문항별 테스트 시간과 통계을 읽어온다.   
        ######################################################### '''
        if sql_name == "sqls_test_times":
            v_trgt_page_date = p_param

            res_test_times  = []
            sum_test_time   = 0
            remaining_time  = 0
            crrct_res_ratio = 0

            try:
                select_query = "  SELECT question_no, test_time "
                select_query += "   FROM tb_part5_feedback_page  "
                select_query += "  WHERE user_id = %s           "
                select_query += "    AND  trgt_page_date = %s   "
                select_param = (current_username, v_trgt_page_date,)

                # 쿼리 실행
                cursor.execute(select_query, select_param)
                res_test_times = cursor.fetchall()

                if len(res_test_times) == 0:
                    res_test_times = []

                select_sttc_query  = "  SELECT sum_test_time, remaining_time, crrct_res_ratio "
                select_sttc_query += "   FROM tb_part5_feedback_page_statistic               "
                select_sttc_query += "  WHERE user_id = %s           "
                select_sttc_query += "    AND  trgt_page_date = %s   "
                select_sttc_param  = (current_username, v_trgt_page_date,)

                # 쿼리 실행
                cursor.execute(select_sttc_query, select_sttc_param)
                statistic_results = cursor.fetchone()

                if statistic_results is None:
                    sum_test_time   = 0
                    remaining_time  = 0
                    crrct_res_ratio = 0
                else:
                    sum_test_time   = statistic_results[0]
                    remaining_time  = statistic_results[1]
                    crrct_res_ratio = statistic_results[2]

            except ValueError:
                # 적절한 오류 처리
                print("Error: Non-integer data found.")

            return res_test_times, sum_test_time, remaining_time, crrct_res_ratio

        '''
        #######################################################
        # FeedBack 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 FeedBack 데이터를 읽어온다.
        ######################################################### '''
        if sql_name == "sqls_feedback_info_by_date":
            v_trgt_page_date = request.GET.get("test_page_date")

            select_query = "  SELECT DISTINCT trgt_order_no, trgt_page_date "
            select_query += "   FROM tb_part5_feedback_page "
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
        # select 박스 입력값 조회 함수
        # 작성일 : 2024.06.20
        # 작업 : html 의 select 초기화를 위한 정보를 가져온다.  
        ######################################################### '''
        if sql_name == "sqls_test_page_result_info":

            pagedate_query  = " SELECT DISTINCT trgt_order_no, trgt_page_date "
            pagedate_query += "   FROM tb_part5_test_page       "
            pagedate_query += "  WHERE user_id = %s            "
            pagedate_query += "   ORDER BY trgt_page_date DESC "
            pagedate_param  = (current_username,)

            # 쿼리 실행
            cursor.execute(pagedate_query, pagedate_param, )
            existing_pagedates = cursor.fetchall()

            return existing_pagedates

        '''
        ############################################################
        # FeedBack 질문 정보 쿼리 함수
        # 작성일 : 2024.06.20
        # 작업 : 특정 일자에 해당하는 저장된 FeedBack 질문 데이터를 읽어온다.
        ######################################################### '''
        if sql_name == "sqls_feedback_question_info_by_date":
            v_trgt_page_date = request.GET.get("test_page_date")

            select_query = "  SELECT DISTINCT question_no, question_content, choice_a, choice_b, choice_c, choice_d, "
            select_query += "        your_answer, correct_answer, result_value, test_time, feedback "
            select_query += "   FROM tb_part5_feedback_page "
            select_query += "  WHERE user_id = %s          "
            select_query += "    AND trgt_page_date = %s   "
            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param,)
            existing_pagedates = cursor.fetchall()

            # df_content를 DataFrame으로 변환
            df_question = pd.DataFrame(existing_pagedates,
                                        columns=[ 'question_no', 'question_content', 'choice_a', 'choice_b', 'choice_c', 'choice_d',
                                                  'your_answer', 'correct_answer', 'result_value', 'test_time', 'feedback' ])

            return df_question

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
            select_query += "   FROM tb_part5_test_page "
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
        ############################################################
        # CALL ID : sqls_test_page_content_cnt
        # 함수명   : 테스트 문제 입력 여부 판단 함수  
        # 작성일   : 2024.06.20
        # 작업     : 테스트 문제 존재 여부로 판단해서 INSERT 여부 결정 목적   
        ############################################################ '''
        if sql_name == "sqls_test_page_content_cnt":
            v_trgt_page_date = p_param

            select_query  = " SELECT  count(*) as cnt     "
            select_query += "   FROM  tb_part5_test_page   "
            select_query += "  WHERE  user_id = %s        "
            select_query += "    AND  trgt_page_date = %s "

            select_param = (current_username, v_trgt_page_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_param)
            v_test_cnt   = cursor.fetchone()
            int_test_cnt = int(v_test_cnt[0])
            return int_test_cnt

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
            select_query += "   FROM tb_part5_test_page   "
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
            select_query += "   FROM tb_part5_test_page   "
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
        #########################################################
        # CALL ID : sqls_classified_words
        # 단어 학습 진행 상황 조회
        # 작성일 : 2024.08.26
        # 작업 : daily_voca 데이블의 타이틀에 대한 미완료, 완료 건수 조회
        ######################################################### '''
        if sql_name == "sqls_classified_words":
           v_trgt_page_date = p_param

           select_query  = " SELECT "
           select_query += "     SUM(CASE WHEN status = 'C' THEN 1 ELSE 0 END) as undone_tot_cnt, "
           select_query += "     SUM(CASE WHEN status = 'D' THEN 1 ELSE 0 END) as done_tot_cnt    "
           select_query += "   FROM  daily_voca            "
           select_query += "  WHERE  user_id   =  %s       "
           select_query += "    AND  src_title like %s     "
           select_param = (current_username, '%' + v_trgt_page_date + '%',)

           # 쿼리 실행
           cursor.execute(select_query, select_param)
           v_words_cnt    = cursor.fetchone()

           if v_words_cnt:
              v_undone_tot_cnt = v_words_cnt[0]
              v_done_tot_cnt   = v_words_cnt[1]
           else:
               v_undone_tot_cnt = 0
               v_done_tot_cnt   = 0

           rtn_value = {
               "undone_tot_cnt" : v_undone_tot_cnt,
               "done_tot_cnt"   : v_done_tot_cnt,
           }

           return rtn_value

        ''' 
        ##############
         INSERT BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqli_feedback_page_content
        # 함수명   : 토익 PART 5 피드백 화면 정보 저장
        # 작성일   : 2024.08.23
        # 작업     : tb_part5_feedback_page 테이블과 tb_part5_result_hist
        #            테이블에 데이터 생성한다.         
        ############################################################  '''
        if sql_name == "sqli_feedback_page_content":
            each_feedback_page_content = p_param
            int_test_no        = each_feedback_page_content['test_no']
            v_trgt_order_no    = each_feedback_page_content['trgt_order_no']
            v_trgt_page_date   = each_feedback_page_content['trgt_page_date']
            v_question_no      = each_feedback_page_content['question_no']
            v_question_content = each_feedback_page_content['question_content']
            v_choice_a         = each_feedback_page_content['choice_a']
            v_choice_b         = each_feedback_page_content['choice_b']
            v_choice_c         = each_feedback_page_content['choice_c']
            v_choice_d         = each_feedback_page_content['choice_d']
            v_your_answer      = each_feedback_page_content['your_answer']
            v_correct_answer   = each_feedback_page_content['correct_answer']
            v_result_value     = each_feedback_page_content['result_value']
            v_test_time        = each_feedback_page_content['test_time']
            v_feedback         = each_feedback_page_content['feedback']

            insert_query  = " INSERT INTO tb_part5_feedback_page "
            insert_query += " (user_id, trgt_order_no, trgt_page_date, question_no, question_content, choice_a, choice_b, choice_c, choice_d, "
            insert_query += "  your_answer, correct_answer, result_value, test_time, feedback ) "
            insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            insert_params = ( current_username, v_trgt_order_no, v_trgt_page_date, v_question_no, v_question_content, v_choice_a, v_choice_b,
                              v_choice_c, v_choice_d, v_your_answer, v_correct_answer, v_result_value, v_test_time, v_feedback)

            cursor.execute(insert_query, insert_params)

            # tb_part5_result_hist 테이블은 여러번의 파트 5 테스트를 히스토리성으로 관리하는 목적이다.
            insert_query  = " INSERT INTO tb_part5_result_hist "
            insert_query += " (user_id, test_no, trgt_order_no, trgt_page_date, question_no, your_answer, correct_answer, result_value, test_time ) "
            insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
            insert_params = ( current_username, int_test_no, v_trgt_order_no, v_trgt_page_date, v_question_no, v_your_answer, v_correct_answer, v_result_value, v_test_time)

            cursor.execute(insert_query, insert_params)

            return str(int_test_no)

        '''
        ############################################################
        # CALL ID : sqli_test_page_content_create
        # 함수명   : 토익 PART 5 테스트 정보 저장
        # 작성일   : 2024.08.23
        # 작업     : tb_part5_test_page 테이블에 데이터 생성한다.         
        ############################################################  '''
        if sql_name == "sqli_test_page_content_create":

            v_trgt_order_no  = p_param['trgt_order_no']
            v_trgt_page_date = p_param['trgt_page_date']
            v_prve_page_date = p_param['prve_page_date']
            v_next_page_date = p_param['next_page_date']
            v_last_page_flag = p_param['last_page_flag']

            v_question_no      = p_param['question_no']
            v_question_content = p_param['question_content']
            v_choice_a = p_param['choice_a']
            v_choice_b = p_param['choice_b']
            v_choice_c = p_param['choice_c']
            v_choice_d = p_param['choice_d']

            v_test_page_content_cnt = sql_dao(request, "sqls_test_page_content_cnt", v_trgt_page_date)

            if v_test_page_content_cnt < 3:
                insert_query = " INSERT INTO tb_part5_test_page "
                insert_query += " (user_id, trgt_order_no, trgt_page_date, prve_page_date, next_page_date, last_page_flag,  "
                insert_query += " question_no, question_content, choice_a, choice_b, choice_c, choice_d ) "
                insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                insert_params = (
                current_username, v_trgt_order_no, v_trgt_page_date, v_prve_page_date, v_next_page_date, v_last_page_flag,
                v_question_no, v_question_content, v_choice_a, v_choice_b, v_choice_c, v_choice_d,)

                cursor.execute(insert_query, insert_params)
            return "OK"

        '''
        ############################################################
        # CALL ID : sqli_feedback_page_statistic
        # 함수명   : 토익 PART 5 피드백 화면 정보 저장
        # 작성일   : 2024.08.23
        # 작업     : tb_part5_feedback_page 테이블과 tb_part5_result_hist
        #            테이블에 데이터 생성한다.         
        ############################################################  '''
        if sql_name == "sqli_feedback_page_statistic":
            each_feedback_page_content = p_param
            v_trgt_order_no = each_feedback_page_content['trgt_order_no']
            v_trgt_page_date = each_feedback_page_content['trgt_page_date']

            insert_sttc_query = " INSERT INTO tb_part5_feedback_page_statistic "
            insert_sttc_query += " (user_id, trgt_order_no, trgt_page_date, sum_test_time, remaining_time, crrct_res_ratio ) "
            insert_sttc_query += " SELECT user_id, trgt_order_no, trgt_page_date, SUM(test_time), 90-SUM(test_time), ROUND(SUM(test_time) / 90 * 100, 1) "
            insert_sttc_query += "   FROM  tb_part5_feedback_page  "
            insert_sttc_query += "  WHERE  user_id        = %s     "
            insert_sttc_query += "    AND  trgt_order_no  = %s     "
            insert_sttc_query += "    AND  trgt_page_date = %s     "
            insert_sttc_query += "  GROUP BY user_id, trgt_order_no, trgt_page_date "
            insert_sttc_params = ( current_username, v_trgt_order_no, v_trgt_page_date )

            cursor.execute(insert_sttc_query, insert_sttc_params)

        '''    
        ############################################################
        # CALL ID : sqli_insert_tb_converted_sentn
        # 함수명   : 변환된 문장을 저장한다.   
        # 작성일   : 2024.07.02
        # 작업     : 변환된 문장을 저장한다.   
        ############################################################  '''
        if sql_name == "sqli_insert_tb_converted_sentn":
            question_no      = p_param["question_no"]
            source_url       = p_param["source_url"]
            source_title     = p_param["source_title"]
            source_type      = p_param["source_type"]
            topic_num        = p_param["topic_num"]
            list_rslt_sentns = p_param["list_rslt_sentns"]

            int_test_cnt = 0

            for converted_sentn, original_sentn in list_rslt_sentns:
                str_converted_sentn      = converted_sentn
                str_original_sentn       = original_sentn
                str_whitespace_converted = ""
                str_translated_sentn     = ""

                topic_num = topic_num + "-" + question_no

                int_test_cnt += 1

                ins_query = " INSERT INTO tb_converted_sentn "
                ins_query += " (no, user_id, topic_num, whitespace_converted, converted_sentn, original_sentn, translated_sentn, src_url, group_code, src_title) "
                ins_query += (
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                )
                ins_params = (
                    question_no,
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

        ''' 
        ##############
         DELETE BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqld_feedback_page_content
        # 함수명   : 토익 파트 5 피트백 삭제 
        # 작성일   : 2024.08.09
        # 작업     : 토익 파트 5 피트백 삭제한다.
        ############################################################  '''
        if sql_name == "sqld_feedback_page_content":

            p_trgt_order_no  = p_param['trgt_order_no']
            p_trgt_page_date = p_param['trgt_page_date']

            delete_query  = " DELETE FROM tb_part5_feedback_page "
            delete_query += "  WHERE  user_id        = %s "
            delete_query += "    AND  trgt_order_no  = %s "
            delete_query += "    AND  trgt_page_date = %s "
            delete_param = (current_username, p_trgt_order_no, p_trgt_page_date,)
            cursor.execute(delete_query, delete_param)

            delete_query  = " DELETE FROM tb_part5_feedback_page_statistic "
            delete_query += "  WHERE  user_id        = %s "
            delete_query += "    AND  trgt_order_no  = %s "
            delete_query += "    AND  trgt_page_date = %s "
            delete_param = (current_username, p_trgt_order_no, p_trgt_page_date,)
            cursor.execute(delete_query, delete_param)

            return "OK"

    except Exception as e:
        return att.handle_sql_error(e, sql_name)

    finally:
        att.close_connection(conn, cursor)
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
    conn, cursor, current_username = att.create_connection(request)
    v_trgt_page_date = p_trgt_page_date
    v_next_page_date = ""

    url = "https://free.ybmclass.com/free/toeic/toeic_5min_view.asp?wdate={}&page=1".format(v_trgt_page_date)
    # 공통 함수의 webdriver를 사용해서 파싱한다.
    html, soup = proj_comn_func.url_parsing_with_webdriver(url, "1")
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

    update_query =  " UPDATE tb_part5_test_page   "
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