import json
import re

import pandas as pd

import app_test_timer.app_sql_statement as att
from app_test_timer.app_mdl_common import common as app_comn_func
from mdl_common import common as comn_func

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
        # CALL ID : sqls_check_news_info
        # 작성일   : 2024.08.09
        # 작업     : 개별 뉴스 URL 데이터 DB에 존재 여부 확인  
        ############################################################# '''
        if sql_name == "sqls_check_news_info":
            news_info_keyno = p_param

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT  ifnull(max(num) ,'0') as detail_max_no "
            select_query += "   FROM tb_news_info_detail "
            select_query += "  WHERE user_id = %s        "
            select_query += "    AND keyno   = %s        "
            select_params = (current_username, news_info_keyno,)

            # 쿼리 실행
            cursor.execute(select_query, select_params)
            sel_max_num = cursor.fetchone()
            news_max_num = int(sel_max_num[0])

            return news_max_num > 0

        '''
        #############################################################
        # CALL ID : sqls_news_info_titles
        # 작성일   : 2024.08.09
        # 작업     : 뉴스 사이트 타이틀 조회  
        ############################################################# '''
        if sql_name == "sqls_news_info_titles":
            p_news_date = p_param["today_news_date"]
            p_max_date  = p_param["max_news_date"]

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT keyno, title      "
            select_query += "   FROM tb_news_info_main "
            select_query += "  WHERE user_id = %s      "
            select_query += "    AND DATE_FORMAT(create_date, '%Y-%m-%d') = %s "
            select_query += "  ORDER BY keyno          "
            select_params = (current_username, p_news_date,)

            # 쿼리 실행
            cursor.execute(select_query, select_params,)
            news_titles = cursor.fetchall()
            list_news_titles = list(news_titles)

            if len(list_news_titles) == 0:
                # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
                select_query2 =  " SELECT keyno, title      "
                select_query2 += "   FROM tb_news_info_main "
                select_query2 += "  WHERE user_id = %s      "
                select_query2 += "    AND DATE_FORMAT(create_date, '%Y-%m-%d') = %s "
                select_query2 += "  ORDER BY keyno          "
                select_params2 = (current_username, p_max_date,)

                # 쿼리 실행
                cursor.execute(select_query2, select_params2,)
                news_titles = cursor.fetchall()
                list_news_titles = list(news_titles)

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query  = " SELECT DISTINCT DATE_FORMAT(create_date, '%Y-%m-%d') AS news_date "
            select_query += "   FROM tb_news_info_main   "
            select_query += "  WHERE user_id = %s        "
            select_query += "  ORDER BY create_date DESC "
            select_params = (current_username,)

            # 쿼리 실행
            cursor.execute(select_query,select_params,)
            news_dates = cursor.fetchall()
            list_news_dates = [date[0] for date in news_dates]

            return list_news_titles, list_news_dates

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
        #############################################################
        # SQL ID : sqls_recent_news_date
        # 작성일  : 2024.08.10
        # 작  업 : 뉴스 사이트 최대 생성일자 조회  
        ############################################################# '''
        if sql_name == "sqls_recent_news_date":
            today_news_date = p_param

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT ifnull(date_format(max(create_date), '%Y-%m-%d'), '0000-00-00') AS recent_date "
            select_query += "   FROM tb_news_info_main  "
            select_query += "  WHERE user_id = %s       "
            select_params = (current_username,)

            # 쿼리 실행
            cursor.execute(select_query, select_params,)
            recent_date = cursor.fetchone()
            result_recent_date = recent_date[0]

            return today_news_date == result_recent_date, result_recent_date

        '''
        #############################################################
        # SQL ID : sqls_selected_news_info_eng
        # 작성일  : 2024.08.10
        # 작  업 : 뉴스 사이트 최대 생성일자 조회  
        ############################################################# '''
        if sql_name == "sqls_selected_news_info_eng":
            keyno_eng = p_param

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT keyitem, groupno, newstype, keyno "
            select_query += "   FROM tb_news_info_detail  "
            select_query += "  WHERE user_id  = %s     "
            select_query += "    AND keyno    = %s     "
            select_query += "    AND (newstype = 'ENG' or newstype = 'KOR')  "
            select_query += "  ORDER BY num "
            select_params = (current_username, keyno_eng,)

            # 쿼리 실행
            cursor.execute( select_query, select_params, )
            news_info_engs = cursor.fetchall()

            # 튜플의 리스트를 사전의 리스트로 변환
            news_info_engs_dicts = [{'keyitem': row[0], 'groupno': row[1], 'newstype': row[2], 'keyno': row[3]} for row in news_info_engs]

            return news_info_engs_dicts

        '''
        #############################################################
        # SQL ID : sqls_news_info_inf
        # 작성일  : 2024.08.12
        # 작  업 : 뉴스 사이트 문장별 이디엄 조회
        ############################################################# '''
        if sql_name == "sqls_news_info_inf":
            p_keyno   = p_param["keyno"]
            p_groupno = p_param["groupno"]

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT keyitem "
            select_query += "   FROM tb_news_info_detail  "
            select_query += "  WHERE user_id  = %s     "
            select_query += "    AND keyno    = %s     "
            select_query += "    AND groupno  = %s     "
            select_query += "    AND newstype = 'INF'  "
            select_query += "  ORDER BY num "
            select_params = (current_username, p_keyno, p_groupno,)

            # 쿼리 실행
            cursor.execute( select_query, select_params, )
            news_info_infs = cursor.fetchall()

            # 튜플의 리스트를 사전의 리스트로 변환
            news_info_infs_dicts = [{'keyitem': row[0]} for row in news_info_infs]

            return news_info_infs_dicts

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
        ##############
         INSERT BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqli_news_info
        # 함수명   : 뉴스 사이트 상세 정보 저장
        # 작성일   : 2024.08.07
        dic_news_info['URL'],  dic_news_info['TITLE'],   dic_news_info['DATE']
        dic_news_info['DEPT'], dic_news_info['SECTION'], dic_news_info['KEYNO']
        dic_news_info['KEYITEM']   
        ############################################################  '''
        if sql_name == "sqli_news_info":
            dic_news_info_detail = p_param

            news_info_keyno    = dic_news_info_detail['KEYNO']
            news_info_keyitem  = dic_news_info_detail['KEYITEM']

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT  ifnull(max(num) ,'0') as detail_max_no "
            select_query += "   FROM tb_news_info_detail "
            select_query += "  WHERE user_id = %s        "
            select_query += "    AND keyno   = %s        "
            select_params = ( current_username, news_info_keyno, )

            # 쿼리 실행
            cursor.execute(select_query, select_params)
            sel_max_num = cursor.fetchone()
            news_max_num = int(sel_max_num[0])+1

            news_info_type = ""
            if app_comn_func.check_subscript(news_info_keyitem):
                news_info_type = "INF"
            elif app_comn_func.check_length_of_english(news_info_keyitem):
               news_info_type = "ENG"
            elif app_comn_func.check_length_of_korean(news_info_keyitem):
               news_info_type = "KOR"
            else:
               news_info_type = "NOT"

            # tb_news_info_detail 테이블에 개발 news_info 저장
            ins_query = " INSERT INTO tb_news_info_detail "
            ins_query += " ( "
            ins_query += "   user_id, keyno, num, keyitem, groupno, newstype, create_date, start_date, finish_date "
            ins_query += " ) "
            ins_query += " values "
            ins_query += " ( "
            ins_query += "   %s, %s, %s, %s, 0, %s, "
            ins_query += "   date_format( now(), '%Y-%m-%d %H:%i:%S' ), '', '' "
            ins_query += " ) "
            ins_params = (
                current_username,
                news_info_keyno,
                news_max_num,
                news_info_keyitem,
                news_info_type,
            )

            cursor.execute(ins_query, ins_params)

            # tb_news_info_detail 테이블에 @joongang.co.kr 찾아서 삭제함
            delete_query  = " DELETE FROM tb_news_info_detail "
            delete_query += " WHERE keyitem LIKE '%@joongang.co.kr%' "
            cursor.execute( delete_query, )

            return str(news_max_num)

        '''
        ############################################################
        # CALL ID : sqli_main_news_info
        # 함수명   : 뉴스 사이트 일반 정보 저장
        # 작성일   : 2024.08.09
        # 작업     : 뉴스 사이트의 간략 정보 정보 저장한다. 
        ############################################################  '''
        if sql_name == "sqli_main_news_info":

            dic_news_info_detail = p_param

            news_info_url   = dic_news_info_detail['URL']
            news_info_title = dic_news_info_detail['TITLE']
            news_info_date  = dic_news_info_detail['DATE']
            news_info_dept  = dic_news_info_detail['DEPT']
            news_info_section  = dic_news_info_detail['SECTION']
            news_info_keyno    = dic_news_info_detail['KEYNO']

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT  ifnull(count(*) ,'0') as detail_max_no "
            select_query += "   FROM tb_news_info_detail "
            select_query += "  WHERE user_id = %s        "
            select_query += "    AND keyno   = %s        "
            select_params = ( current_username, news_info_keyno, )

            # 쿼리 실행
            cursor.execute(select_query, select_params)
            sel_count_num = cursor.fetchone()
            news_count_num = int(sel_count_num[0])

            # tb_news_info_detail 테이블에 개발 news_info 저장
            ins_query = " INSERT INTO tb_news_info_main "
            ins_query += " ( "
            ins_query += "   user_id, keyno, dept, section, url, title, news_info_date, tot_count, create_date, start_date, finish_date "
            ins_query += " ) "
            ins_query += " values "
            ins_query += " ( "
            ins_query += "   %s, %s, %s, %s, %s, %s, %s, %s, "
            ins_query += "   date_format( now(), '%Y-%m-%d %H:%i:%S' ), '', '' "
            ins_query += " ) "
            ins_params = (
                current_username,
                news_info_keyno,
                news_info_dept,
                news_info_section,
                news_info_url,
                news_info_title,
                news_info_date,
                news_count_num,
            )
            cursor.execute(ins_query, ins_params)

            return str(news_count_num)

        ''' 
        ##############
         UPDATE BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqlu_non_eng_type_groupno
        # 함수명   : 뉴스 사이트별 문장별 그룹 생성
        # 작성일   : 2024.08.11
        # 작업     : 뉴스 사이트 정보를 문장 단락별로 그룹화 한다.
        ############################################################  '''
        if sql_name == "sqlu_non_eng_type_groupno":
            eng_keyno   = p_param['news_keyno']
            non_eng_num = p_param['news_num']
            eng_groupno = p_param['news_groupno']

            # 영어 문장별 단락을 만들기 위한 정보 생성
            upd_query  = " UPDATE tb_news_info_detail "
            upd_query += "    SET groupno  = %s       "
            upd_query += "  WHERE user_id  = %s       "
            upd_query += "    AND keyno    = %s       "
            upd_query += "    AND num      = %s       "
            upd_params = (eng_groupno, current_username, eng_keyno, non_eng_num,)
            cursor.execute(upd_query, upd_params,)

            return "OK"

        ''' 
        ##############
         DELETE BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqld_invalid_news_info
        # 함수명   : 뉴스 사이트 일반 정보 저장
        # 작성일   : 2024.08.09
        # 작업     : 뉴스 사이트의 간략 정보 정보 저장한다.
        ############################################################  '''
        if sql_name == "sqld_invalid_news_info":

            sel_query =  " SELECT a.keyno AS keyno  "
            sel_query += "   FROM (                 "
            sel_query += "  		SELECT keyno ,  "
            sel_query += "   		       SUM( case when newstype = 'ENG'              "
            sel_query += "   		                 then 1 else 0 END )   AS news_eng, "
            sel_query += "   		       SUM( case when newstype = 'INF'              "
            sel_query += "   		                 then 1 else 0 END )   AS news_inf, "
            sel_query += "   		       SUM( case when newstype = 'KOR'              "
            sel_query += "   		                 then 1 else 0 END )   AS news_kor  "
            sel_query += "   		  FROM tb_news_info_detail "
            sel_query += "           WHERE user_id = %s        "
            sel_query += "   		 GROUP BY keyno            "
            sel_query += "   	  ) a               "
            sel_query += "  WHERE a.news_inf < 5    "
            sel_params = ( current_username, )

            cursor.execute(sel_query, sel_params,)
            keynos = cursor.fetchall()

            if keynos:
                for keyno in keynos:
                    str_keyno = keyno[0]

                    # tb_news_info_detail 테이블에 @joongang.co.kr 찾아서 삭제함
                    delete_query1  = " DELETE FROM tb_news_info_main "
                    delete_query1 += "  WHERE user_id = %s  "
                    delete_query1 += "    AND keyno   = %s  "
                    delete_params1 = ( current_username, str_keyno,)
                    cursor.execute(delete_query1, delete_params1,)

                    # tb_news_info_detail 테이블에 @joongang.co.kr 찾아서 삭제함
                    delete_query2  = " DELETE FROM tb_news_info_detail "
                    delete_query2 += "  WHERE user_id = %s  "
                    delete_query2 += "    AND keyno   = %s  "
                    delete_params2 = ( current_username, str_keyno,)
                    cursor.execute(delete_query2, delete_params2,)

                # tb_news_info_detail 테이블에 @joongang.co.kr 찾아서 삭제함
                delete_query3  = " DELETE FROM tb_news_info_detail "
                delete_query3 += "  WHERE user_id   = %s    "
                delete_query3 += "    AND newstype  = 'NOT' "
                delete_params3 = ( current_username, )
                cursor.execute(delete_query3, delete_params3,)
            conn.commit()

            # 영어 문장별 단락을 만들기 위한 정보 생성
            upd_query  = " UPDATE tb_news_info_detail "
            upd_query += "    SET groupno  = num      "
            upd_query += "  WHERE user_id  = %s       "
            upd_query += "    AND newstype = 'ENG'    "
            upd_params = (current_username,)
            cursor.execute(upd_query, upd_params,)
            conn.commit()

            sel_query  = " SELECT keyno, num, newstype, groupno  "
            sel_query += "   FROM tb_news_info_detail            "
            sel_query += "  WHERE user_id  = %s                  "
            sel_query += "  ORDER BY keyno, num                  "
            sel_params = (current_username,)
            cursor.execute(sel_query, sel_params,)
            detail_info = cursor.fetchall()

            if detail_info:
                app_comn_func.update_non_eng_type_groupno(request, detail_info)

            return "OK"

        '''
        ############################################################
        # CALL ID : sqld_less_couple_groupno
        # 함수명   : 마지막으로 뉴스 사이트 데이터 정리
        # 작성일   : 2024.08.09
        # 작업     : 문장 단락 갯수가 3개 미만인 경우 삭제한다.
        ############################################################  '''
        if sql_name == "sqld_less_couple_groupno":
            # 문장 단락 갯수가 3개 미만인 대상 조회
            sel_query  = " SELECT keyno, groupno      "
            sel_query += "   FROM tb_news_info_detail "
            sel_query += "  WHERE user_id  = %s       "
            sel_query += "  GROUP BY keyno, groupno   "
            sel_query += "  HAVING count(*) < 2       "
            sel_params = (current_username,)
            cursor.execute(sel_query,sel_params,)
            keynos = cursor.fetchall()

            if keynos:
                for keyno in keynos:
                    str_keyno   = keyno[0]
                    str_groupno = keyno[1]
                    # 문장 단락 갯수가 3개 미만인 경우 삭제한다.
                    delete_query = " DELETE FROM tb_news_info_detail "
                    delete_query += "  WHERE user_id = %s "
                    delete_query += "    AND keyno   = %s "
                    delete_query += "    AND num     = %s "
                    delete_params = (current_username, str_keyno, str_groupno,)
                    cursor.execute(delete_query, delete_params, )

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