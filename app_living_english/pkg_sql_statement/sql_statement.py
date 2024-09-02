import json
import re

import pandas as pd

import app_living_english.pkg_sql_statement as att
from proj_common import mdl_common_proj as proj_comn_func

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
        # CALL ID : sqls_living_english_topic
        # APPL ID : app_living_english
        # 생활회화 제목별 오디오 대화 시간을 조회하는 함수
        # 작성일 : 2024.09.01
        # 작업 : 생활회화 화면 오디오의 제목별 오디오 대화 시작시간과  
        #       완료시간을 조회한다.
        ############################################################# '''
        if sql_name == "sqls_living_english_topic":
            selectd_chapter = p_param

            try:
                # 쿼리 정의
                topic_query = " SELECT  topic_dur_start, topic_dur_end "
                topic_query += "   FROM tb_living_english_topic  "
                topic_query += "  WHERE user_id   = %s           "
                topic_query += "    AND topic_num = %s           "
                topic_param = (current_username, selectd_chapter,)

                # 쿼리 실행
                cursor.execute(topic_query, topic_param)
                topic_dur_time = cursor.fetchone()

                if topic_dur_time is not None:
                    v_topic_dur_start = topic_dur_time[0]
                    v_topic_dur_end = topic_dur_time[1]
                else:
                    v_topic_dur_start, v_topic_dur_end = 0, 0

            except Exception as e:
                print("topic_dur_time Error occurred:", e)
                v_topic_dur_start = 0
                v_topic_dur_end = 0

            return v_topic_dur_start, v_topic_dur_end

        '''
        #############################################################
        # CALL ID : sqls_existing_max_chapter_num
        # APPL ID : app_living_english        
        # 이미 데이터베이스에 해당 단어가 있는지 확인
        # 작성일 : 2024.09.01
        # 작업 : 이미 데이터베이스에 해당 단어가 있는지 확인 한다.
        ############################################################# '''
        if sql_name == "sqls_existing_max_chapter_num":

            try:
                # 쿼리 정의
                chapter_query = " SELECT  ifnull(max(src_chapter) ,'4450') as max_chapter_num "
                chapter_query += "   FROM tb_chapter_title  "
                chapter_query += "  WHERE user_id   = %s    "
                chapter_param = ( current_username, )

                # 쿼리 실행
                cursor.execute(chapter_query, chapter_param)

                existing_max_chapter_num = cursor.fetchone()
                res_max_chapter_num = existing_max_chapter_num[0]

                return res_max_chapter_num
            except Exception as e:
                print("retrieve max num query failed(sqls_existing_max_chapter_num): ", e)
                return "4450"

        '''
        ###################################################################################################
        LYH-2024.08.21 프로젝트 쿼리에서 어플리케이션 쿼리로 이동
        ###################################################################################################        
        '''
        '''
        #############################################################
        # FUNC ID : sqls_fetch_titles
        # APPL ID : app_living_english        
        # 함수명 : 상태별 영어회화 음성파일 재생 정보 조회
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_fetch_titles":
            selectd_status = p_param

            # 쿼리 정의
            chapter_query = " SELECT DISTINCT src_chapter, src_title, voice_date "
            chapter_query += "   FROM tb_chapter_title         "
            chapter_query += "  WHERE user_id   = %s           "
            chapter_query += "    AND src_chapter is not null  "
            chapter_query += "    AND status    = %s           "
            chapter_query += "  ORDER BY src_chapter DESC      "
            chapter_param = (current_username, selectd_status,)

            # 쿼리 실행
            cursor.execute(chapter_query, chapter_param)
            existing_titles = cursor.fetchall()

            return existing_titles

        '''
        #############################################################
        # FUNC ID : sqls_fetch_titles2
        # APPL ID : app_living_english        
        # 함수명 : 완료된 영어회화 정보 조회
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqls_fetch_titles2":
            # 완료된 chapter 쿼리 정의
            comp_chapter_query  = " SELECT DISTINCT src_chapter, src_title, voice_date "
            comp_chapter_query += "   FROM tb_chapter_title         "
            comp_chapter_query += "  WHERE user_id = %s             "
            comp_chapter_query += "    AND src_chapter is not null  "
            comp_chapter_query += "    AND status  = 'D'            "
            comp_chapter_query += "  ORDER BY finish_date  DESC     "
            comp_chapter_param = (current_username,)

            # 쿼리 실행
            cursor.execute(comp_chapter_query, comp_chapter_param)
            existing_comp_titles = cursor.fetchall()

            return existing_comp_titles

        '''
        ############################################################
        # CALL ID : sqls_batch_max_date
        # 함수명   : 배치 히스토리 테이블의 가장 최근 일자 조회  
        # 작성일   : 2024.08.31
        # 작업     : 배치 히스토리 테이블의 가장 최근 일자 확인   
        ############################################################ '''
        if sql_name == "sqls_batch_max_date":

            select_batch_query  = " SELECT  ifnull(max(trgt_page_date) ,'00000000') as trgt_page_date  "
            select_batch_query += "   FROM  tb_part5_batch_hist "

            # 쿼리 실행
            cursor.execute(select_batch_query,)
            v_batch_max_date = cursor.fetchone()
            batch_max_date   = v_batch_max_date[0]

            return batch_max_date

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
        #########################################################
        # CALL ID : sqls_living_english_content_english
        # APPL ID : app_living_english
        # first part - english
        # 작성일 : 2024.09.01
        # 작업 : first part - english
        ######################################################### '''
        if sql_name == "sqls_living_english_content_english":
           p_selectd_chapter = p_param

           try:
               query  = " SELECT each_stmt       "
               query += "   FROM tb_living_english_content "
               query += "  WHERE user_id = %s    "
               query += "    AND type = 'eng' AND chapter_num = %s  "
               query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC   "
               query_param = (current_username, p_selectd_chapter,)

               cursor.execute(query, query_param)
               existing_eng_content = cursor.fetchall()

               selectd_eng_content = [(each_stmt) for each_stmt in existing_eng_content]

               return selectd_eng_content

           except Exception as e:
               print("sqls_living_english_content_english failed: ", e)
               return []

        '''
        #########################################################
        # CALL ID : sqls_living_english_content_korean
        # APPL ID : app_living_english
        # second part - korean
        # 작성일 : 2024.09.01
        # 작업 : second part - korean
        ######################################################### '''
        if sql_name == "sqls_living_english_content_korean":
           p_selectd_chapter = p_param

           try:
               query  = " SELECT each_stmt       "
               query += "   FROM tb_living_english_content "
               query += "  WHERE user_id = %s    "
               query += "    AND type = 'kor' AND chapter_num = %s  "
               query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC   "
               query_param = (current_username, p_selectd_chapter,)

               cursor.execute(query, query_param)
               existing_kor_content = cursor.fetchall()

               selectd_kor_content = [(each_stmt) for each_stmt in existing_kor_content]

               return selectd_kor_content

           except Exception as e:
               print("sqls_living_english_content_korean failed: ", e)
               return []

        '''
        #########################################################
        # CALL ID : sqls_living_english_content_additional
        # APPL ID : app_living_english
        # third part - additional
        # 작성일 : 2024.09.01
        # 작업 : third part - additional
        ######################################################### '''
        if sql_name == "sqls_living_english_content_additional":
           p_selectd_chapter = p_param

           try:
               # third part - additional
               query = " SELECT each_stmt       "
               query += "   FROM tb_living_english_content "
               query += "  WHERE user_id = %s   "
               query += "    AND type = 'add' AND chapter_num = %s  "
               query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC   "
               query_param = (current_username, p_selectd_chapter,)

               cursor.execute(query, query_param)
               existing_add_content = cursor.fetchall()

               selectd_add_content = [(each_stmt) for each_stmt in existing_add_content]

               return selectd_add_content

           except Exception as e:
               print("sqls_living_english_content_additional failed: ", e)
               return []

        '''
        #########################################################
        # CALL ID : sqls_living_english_content_resultcnt
        # APPL ID : app_living_english
        # 함수     : total count
        # 작성일   : 2024.09.01
        # 작업     : total count
        ######################################################### '''
        if sql_name == "sqls_living_english_content_resultcnt":
           p_selectd_chapter = p_param

           try:
               # total count
               query  = " SELECT count(*) as cnt      "
               query += "   FROM tb_living_english_content "
               query += "  WHERE user_id = %s         "
               query += "    AND chapter_num = %s "
               query_param = (current_username, p_selectd_chapter,)

               cursor.execute(query, query_param)
               result_cnt = cursor.fetchone()

               return_cnt = result_cnt[0]

               if int(return_cnt) > 0:
                   upd_query  = " UPDATE tb_chapter_title "
                   upd_query += "    SET start_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                   upd_query += "  WHERE user_id     = %s "
                   upd_query += "    AND src_chapter = %s "
                   upd_param  = (current_username, p_selectd_chapter,)

                   cursor.execute(upd_query, upd_param)

               return return_cnt

           except Exception as e:
               print("sqls_living_english_content_resultcnt failed: ", e)
               return 0

        ''' 
        ##############
         INSERT BLOCK
        ############## '''
        '''
        ############################################################
        # CALL ID : sqli_page_info
        # APPL ID : app_living_english        
        # 함수명   : 생활회화 페이지의 정보 저장
        # 작성일   : 2024.09.01
        # 작업     : 페이지의 번호, 타이틀, 오디오 파일 이름 정보를 저장한다.
        ############################################################  '''
        if sql_name == "sqli_page_info":
            chapter_values = p_param

            p_chapter_num = chapter_values["chapter_num"]
            p_title_text  = chapter_values["title_text"]
            p_audio_name  = chapter_values["audio_name"]

            try:
                chapter_query = " INSERT INTO tb_chapter_title "
                chapter_query += " ( user_id, src_chapter, src_title, voice_date ) "
                chapter_query += " VALUES "
                chapter_query += " ( %s, %s, %s, %s ) "
                chapter_params = (current_username, p_chapter_num, p_title_text, p_audio_name)
                cursor.execute(chapter_query, chapter_params)

                return 1
            except Exception as e:
                print("do_insert_page_info insert failed:", e)

                return 0
            finally:
                print("sqli_page_info finish")

        '''
        ############################################################
        # CALL ID : sqli_living_english_content
        # APPL ID : app_living_english
        # 함수명   : process_info 데이터 생성
        # 작성일   : 2024.01.23
        # 작업     : process_info 데이터 생성
        ############################################################  '''

        if sql_name == "sqli_living_english_content":
            content_values = p_param

            p_type        = content_values["type"]
            p_seq_num     = content_values["seq_num"]
            p_chapter_num = content_values["chapter_num"]
            p_each_stmt   = content_values["each_stmt"]

            # 2024.01.23 추가- process_info 데이터 생성
            insert_query = " INSERT INTO tb_living_english_content "
            insert_query += " (user_id, type, seq_num, chapter_num, each_stmt) "
            insert_query += " VALUES (%s, %s, %s, %s, %s) "
            insert_params = (
                current_username,
                p_type,
                p_seq_num,
                p_chapter_num,
                p_each_stmt,
            )

            cursor.execute(insert_query, insert_params)

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
        ############################################################
        # CALL ID : sqli_batch_living_english_hist
        # 함수명   : 생활회화 신규 chapter 자동 생성 스크립트용
        # 작성일   : 2024.09.02
        # 작업     : 생활회화 신규 chapter 자동 생성 한다.           
        ############################################################  '''
        if sql_name == "sqli_batch_living_english_hist":

            chapter_values = p_param

            p_chapter_num = chapter_values["chapter_num"]
            p_title_text  = chapter_values["title_text"]
            p_audio_name  = chapter_values["audio_name"]

            try:
                chapter_query  = " INSERT INTO tb_batch_living_english_hist "
                chapter_query += " ( src_chapter, src_title, voice_date, update_date ) "
                chapter_query += " VALUES "
                chapter_query += " ( %s, %s, %s, date_format(now(), '%Y-%m-%d %H:%i:%S') ) "

                chapter_params = ( p_chapter_num, p_title_text, p_audio_name )
                cursor.execute(chapter_query, chapter_params)

            except Exception as e:
                upd_batch_query  = " UPDATE tb_batch_living_english_hist  "
                upd_batch_query += "    SET update_date = date_format(now(),'%Y-%m-%d %H:%i:%S')   "
                upd_batch_query += "  WHERE src_chapter  = %s  "

                upd_batch_params = (p_chapter_num,)
                cursor.execute(upd_batch_query, upd_batch_params)

            finally:
                del_batch_query  = " DELETE FROM tb_chapter_title     "
                del_batch_query += "  WHERE src_chapter = 'undefined' "
                cursor.execute(del_batch_query,)

                del_batch_query  = " DELETE FROM tb_living_english_content "
                del_batch_query += "  WHERE chapter_num = 'undefined'      "
                cursor.execute(del_batch_query,)

                del_batch_query  = " DELETE FROM tb_converted_sentn   "
                del_batch_query += "  WHERE topic_num = 'undefined' "
                cursor.execute(del_batch_query,)

                del_batch_query  = " DELETE FROM tb_batch_living_english_hist "
                del_batch_query += "  WHERE src_chapter = 'undefined' "
                cursor.execute(del_batch_query,)

                print("sqli_batch_living_english_hist finish")

            return "OK"

        ''' 
        ##############
         UPDATE BLOCK
        ############## '''

        ''' 
        ##############
         DELETE BLOCK
        ############## '''

    except Exception as e:
        return att.handle_sql_error(e, sql_name)

    finally:
        att.close_connection(conn, cursor)

'''         
##################   
# 쿼리 CALL 함수 끝    
################## '''
