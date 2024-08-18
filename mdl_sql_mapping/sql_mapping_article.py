import json

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
        # FUNC ID : sqls_main_word_check      
        # 함수명 : 학습대상 워드 테이블 조회 (1차)
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_main_word_check":
            source_title  = request.GET.get("source_title")
            source_status = request.GET.get("source_status")
            source_type   = request.GET.get("source_type")

            try:
                query = "SELECT no, word, mean_en, mean_kr, DATE(create_date) as create_date "
                query += "  FROM processed_words "
                query += " WHERE  user_id = %s   "
                query += "   AND status = %s and src_title = %s  and group_code = %s "
                query += " ORDER BY DATE(create_date) DESC, no ASC "
                params = (current_username, source_status, source_title, source_type)
                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_main_word_check2      
        # 함수명 : URL, TITLE 조회 (1차)
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_main_word_check2":
            source_type   = request.GET.get("source_type")

            try:
                query  = "SELECT DISTINCT src_url, src_title  "
                query += "  FROM processed_words "
                query += " WHERE user_id = %s   "
                query += "   AND src_url is not null and group_code = %s and status = %s "
                query += " ORDER BY init_status DESC, create_date DESC "
                params = (
                    current_username,
                    source_type,
                    "C",
                )
                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed: ", e)

            existing_titles = cursor.fetchall()

            return existing_titles

        '''
        #############################################################
        # FUNC ID : sqls_main_word_table      
        # 함수명 : URL, TITLE 조회 (1차)
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqls_main_word_table":
            source_title = request.GET.get("source_title")
            source_status = request.GET.get("source_status")

            try:
                query  = "SELECT word, mean_en, mean_kr, DATE(create_date) as create_date "
                query += "  FROM processed_words   "
                query += " WHERE user_id = %s      "
                query += "   AND status  = %s and src_title = %s    "
                # query += " ORDER BY DATE(create_date) DESC, no ASC "
                params = (current_username, source_status, source_title)
                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_word_detail   
        # 함수명 : 해당 타이틀에 해당하는 모든 단어 조회 (daily_voca)
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqls_word_detail":
            word = request.GET.get("word")
            wrd_title = request.GET.get("wrd_title")

            try:
                query = "  SELECT ifnull(word,''), ifnull(word_guess,''), ifnull(tag,''), ifnull(mean,''), ifnull(group_code,''), ifnull(word_eng_example,''), ifnull(word_kor_example,''), ifnull(word_eng_example2,''), ifnull(word_kor_example2,'') "
                query += "   FROM daily_voca    "
                query += "  WHERE user_id = %s  "
                query += "    AND word    = %s  "
                params = (current_username, word,)
                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_word_detail2   
        # 함수명 : 상세 단어 조회 (daily_voca)
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_word_detail2":
            word = request.GET.get("word")
            wrd_title = request.GET.get("wrd_title")

            # word detail 화면에 title 별 전체 미완료 단어 보여주기
            try:
                words_query  = " SELECT ifnull(word,'') "
                words_query += "   FROM daily_voca      "
                words_query += "  WHERE user_id   = %s  "
                words_query += "    AND src_title = %s  "
                words_query += "    AND status   != 'D' "
                words_query += "  ORDER BY  word asc    "
                words_params = (current_username, wrd_title,)
                cursor.execute(words_query, words_params)

                all_words_by_title = cursor.fetchall()

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_uncomplete_chapter
        # 함수명 : tb_chapter_title 데이블 완료상태, 날짜 최기화
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_uncomplete_chapter":
            selectd_chapter = request.GET.get("selectd_chapter")

            try:
                uncomplete_query  = " UPDATE tb_chapter_title      "
                uncomplete_query += "    SET status         = 'C'  "
                uncomplete_query += "      , finish_date    = NULL "
                uncomplete_query += "  WHERE user_id        = %s   "
                uncomplete_query += "    AND src_chapter    = %s   "
                uncomplete_params = (current_username, selectd_chapter, )
                cursor.execute(uncomplete_query, uncomplete_params)


            except Exception as e:
                print("Chapter Uncomplete query failed:", e)
                selectd_chapter = "0"

            return selectd_chapter

        '''
        #############################################################
        # FUNC ID : sqls_call_process
        # 함수명 : 형태소 기반 단어 분류 진행 조회
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqls_call_process":
            undone_tot_cnt  = 0
            curr_undone_cnt = 0

            srcTitle = request.GET.get("src_title")

            try:
                call_proc_query  = " SELECT ifnull(undone_cnt,0), ifnull(undone_tot_cnt,0), ifnull(done_tot_cnt,0) "
                call_proc_query += "   FROM process_info   "
                call_proc_query += "  WHERE user_id   = %s "
                call_proc_query += "    AND src_title = %s "
                call_proc_params = (current_username, srcTitle,)
                cursor.execute(call_proc_query, call_proc_params)

                call_cnts = cursor.fetchone()

                undone_tot_cnt = call_cnts[1]

                if call_cnts:
                    curr_undone_cnt = call_cnts[0]
                else:
                    curr_undone_cnt = 0

            except Exception as e:
                print("Call Process Count failed:", e)

            return curr_undone_cnt, undone_tot_cnt

        '''
        #############################################################
        # FUNC ID : sqls_fetch_titles
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
        ##############
         INSERT BLOCK
        ############## '''
        '''
        #############################################################
        # FUNC ID : sqliu_save_topic
        # 함수명 : tb_chapter_title 데이블 완료상태, 날짜 최기화
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqliu_save_topic":
            try:
                # 요청의 본문을 JSON으로 파싱
                data = json.loads(request.body)
                topic_num = data.get("topic_num")
                audio_file_date = data.get("audio_file_date")  # 소스 Url 추가
                volume_size = data.get("volume_size")  # 소스 Title 추가
                topic_kr = data.get("topic_kr")  # 소스 Type 추가
                topic_en = data.get("topic_en")  # 소스 Type 추가
                topic_dur_start = data.get("topic_dur_start")  # 소스 Type 추가
                topic_dur_end = data.get("topic_dur_end")  # 소스 Type 추가

                # 접속 객체 생성
                conn = comn_func.fn_connector(request)
                cursor = conn.cursor()

                ins_topic_query = "  INSERT INTO tb_living_english_topic "
                ins_topic_query += " ( "
                ins_topic_query += "  user_id, topic_num, audio_file_date, volume_size, topic_kr, topic_en, topic_dur_start,  "
                ins_topic_query += "  topic_dur_end, native_dur_start, native_dur_end, etc_dur1_start, etc_dur1_end, "
                ins_topic_query += "  etc_dur2_start, etc_dur2_end, etc_dur3_start, etc_dur3_end, study_status, "
                ins_topic_query += "  topic_frequency, native_frequency, curr_point, create_date, start_date, finish_date "
                ins_topic_query += " ) "
                ins_topic_query += " values "
                ins_topic_query += " ( "
                ins_topic_query += "   %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0, 0, 0, 0, 'C', '0', '0', '', "
                ins_topic_query += "   date_format( now(), '%Y-%m-%d %H:%i:%S' ), '', '' "
                ins_topic_query += " ) "
                ins_topic_params = (current_username, topic_num, audio_file_date, volume_size, topic_kr, topic_en, topic_dur_start, topic_dur_end)

                cursor.execute(ins_topic_query, ins_topic_params)

                int_test_cnt = 1

            except Exception as e:
                upd_topic_query = " UPDATE tb_living_english_topic "
                upd_topic_query += "    SET topic_dur_start = %s "
                upd_topic_query += "      , topic_dur_end   = %s "
                upd_topic_query += "      , start_date      = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                upd_topic_query += " WHERE  user_id         = %s "
                upd_topic_query += "   AND  topic_num       = %s "

                upd_topic_params = (topic_dur_start, topic_dur_end, current_username, topic_num,)
                cursor.execute(upd_topic_query, upd_topic_params)

                int_test_cnt = 2

            return int_test_cnt

        '''
        #############################################################
        # FUNC ID : sqli_create_word
        # 함수명 : tb_chapter_title 데이블 완료상태, 날짜 최기화
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqli_create_word":

            # 요청의 본문을 JSON으로 파싱
            data = json.loads(request.body)
            wrd_word = data.get("wrd_word")
            wrd_title = data.get("wrd_title")
            wrd_group_code = data.get("wrd_group")

            try:
                ins_word_query = "  INSERT INTO processed_words   "
                ins_word_query += " ( no, user_id, word, src_title, group_code ) "
                ins_word_query += " values "
                ins_word_query += " ( 0, %s, %s, %s, %s ) "
                ins_word_params = (current_username, wrd_word, wrd_title, wrd_group_code)
                cursor.execute(ins_word_query, ins_word_params)

                ins_voca_query = "  INSERT INTO daily_voca   "
                ins_voca_query += " ( num, user_id, word, src_title, group_code ) "
                ins_voca_query += " values "
                ins_voca_query += " ( 0, %s, %s, %s, %s  ) "
                ins_voca_params = (current_username, wrd_word, wrd_title, wrd_group_code)
                cursor.execute(ins_voca_query, ins_voca_params)

                int_ins_cnt = 1

            except Exception as e:
                int_ins_cnt = 0

            return int_ins_cnt

        '''
        #############################################################
        # FUNC ID : sqli_confirm_word_check    
        # 함수명 : process_info 생성
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqli_confirm_word_check":
            selected_title = p_param

            # 2024.01.23 추가- process_info 데이터 생성
            proc_insert_query  = " INSERT INTO process_info "
            proc_insert_query += " (user_id, src_title, undone_cnt, undone_tot_cnt, done_tot_cnt) "
            proc_insert_query += " VALUES (%s, %s, 0, 0, 0) "
            proc_insert_params = (current_username, selected_title,)

            cursor.execute(proc_insert_query, proc_insert_params)

            return 1

        ''' 
        ##############
         UPDATE BLOCK
        ############## '''
        '''
        #############################################################
        # FUNC ID : sqlu_save_wordinfo    
        # 함수명 : processed_words 갱신
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqlu_save_wordinfo":
            saveWord = request.GET.get("txt_word")
            saveDefeng = request.GET.get("txt_defeng")
            saveDefkor = request.GET.get("txt_defkor")

            upd_word_query  = " UPDATE processed_words "
            upd_word_query += "    SET mean_en = %s    "
            upd_word_query += "      , mean_kr = %s    "
            upd_word_query += "  WHERE user_id = %s    "
            upd_word_query += "    AND word    = %s    "
            upd_word_params = (saveDefeng, saveDefkor, current_username, saveWord)
            cursor.execute(upd_word_query, upd_word_params)

            re_title_cnt = 1

            return re_title_cnt

        '''
        #############################################################
        # FUNC ID : sqlu_save_wordinfo2    
        # 함수명 : processed_words 갱신
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqlu_save_wordinfo2":
            saveWord = request.GET.get("txt_word")
            saveDefeng = request.GET.get("txt_defeng")
            saveDefkor = request.GET.get("txt_defkor")

            upd_mean_daily_word_params = p_param
            upd_mean_daily_word_params[7] = current_username

            # daily_voca의 meaning update
            upd_mean_daily_word_query = " UPDATE daily_voca       "
            upd_mean_daily_word_query += "    SET word_guess = %s "
            upd_mean_daily_word_query += "      , tag        = %s "
            upd_mean_daily_word_query += "      , mean       = %s "
            upd_mean_daily_word_query += "      , word_eng_example  = %s "
            upd_mean_daily_word_query += "      , word_kor_example  = %s "
            upd_mean_daily_word_query += "      , word_eng_example2 = %s "
            upd_mean_daily_word_query += "      , word_kor_example2 = %s "
            upd_mean_daily_word_query += "  WHERE user_id = %s "
            upd_mean_daily_word_query += "    AND word    = %s "
            cursor.execute(upd_mean_daily_word_query, upd_mean_daily_word_params)

            re_title_cnt = 1

            return re_title_cnt

        ''' 
        ##############
         DELETE BLOCK
        ############## '''
        '''
        #############################################################
        # FUNC ID : sqld_delete_content    
        # 함수명 : processed_words 타이틀 조건 삭제 
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqld_delete_content":
            source_title = request.GET.get("source_title")

            try:
                delete_query1  = " DELETE FROM processed_words "
                delete_query1 += "  WHERE user_id   = %s       "
                delete_query1 += "    AND src_title = %s       "
                delete_params1 = (current_username, source_title,)
                cursor.execute(delete_query1, delete_params1)

                delete_query2 = " DELETE FROM daily_voca       "
                delete_query2 += "  WHERE user_id   = %s       "
                delete_query2 += "    AND src_title = %s       "
                delete_params2 = (current_username, source_title,)
                cursor.execute(delete_query2, delete_params2)

                rows_cnt = 1

            except Exception as e:
                print("Renewal query failed:", e)

            return rows_cnt

        '''
        #############################################################
        # FUNC ID : sqld_confirm_word_check    
        # 함수명 : process_info 삭제 
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqld_confirm_word_check":
            selected_title = p_param

            # 2024.01.26 추가- process_info 데이터 삭제
            proc_delete_query  = " DELETE FROM process_info "
            proc_delete_query += " WHERE user_id   = %s     "
            proc_delete_query += "   AND src_title = %s     "
            proc_delete_params = (current_username, selected_title,)

            cursor.execute(proc_delete_query, proc_delete_params)

            return 1

    except Exception as e:
        return handle_sql_error(e, sql_name)

    finally:
        close_connection(conn, cursor)
'''            
# 쿼리 CALL 함수 끝            
'''