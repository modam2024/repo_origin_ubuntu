import json
import re

import pandas as pd

from proj_sql_mapping import create_connection, close_connection, handle_sql_error

'''
#######################################################
# CONNECTION 정보 함수
# 작성일 : 2024.06.20
####################################################### '''
def sql_dao(request, sql_name, p_param):
    conn, cursor, current_username = create_connection(request)

    try:
        ''' 
        ##############
         SELECT BLOCK
        ##############  '''
        '''
        ###################################################################################################
        LYH-2024.09.23 프로젝트 쿼리에서 어플리케이션 쿼리로 이동
        ###################################################################################################        
        '''
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
            sel_level     = request.GET.get("sel_level")

            try:
                if source_type == "ALL":
                    query  = "SELECT no, word, mean_en, mean_kr, DATE(create_date) as create_date "
                    query += "  FROM processed_words   "
                    query += " WHERE  user_id    = %s  "
                    query += "   AND status     != 'D' "
                    query += "   AND init_status = 'B' "
                    if sel_level == "E":
                       query += "   AND level    = %s  "
                    query += " ORDER BY DATE(create_date) DESC, no ASC "
                    query += " LIMIT 10 "

                    if sel_level == "E":
                       params = (current_username, sel_level)
                    else:
                       params = (current_username,)
                else:
                    query  = "SELECT no, word, mean_en, mean_kr, DATE(create_date) as create_date "
                    query += "  FROM processed_words   "
                    query += " WHERE  user_id    = %s  "
                    query += "   AND status      = %s  "
                    query += "   AND src_title   = %s  "
                    query += "   AND group_code  = %s  "
                    if sel_level == "E":
                       query += "   AND level    = %s  "
                    query += " ORDER BY DATE(create_date) DESC, no ASC "
                    if sel_level == "E":
                       params = (current_username, source_status, source_title, source_type, sel_level)
                    else:
                       params = (current_username, source_status, source_title, source_type,)

                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_main_word_check2      
        # 함수명 : URL, TITLE 조회 (2차)
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqls_main_word_check2":
            source_type   = request.GET.get("source_type")

            try:
                if source_type == "ALL":
                    query  = "SELECT DISTINCT src_url, src_title "
                    query += "  FROM processed_words   "
                    query += " WHERE  user_id    = %s  "
                    query += "   AND status     != 'D' "
                    query += "   AND init_status = 'B' "
                    query += " ORDER BY create_date DESC, src_title ASC  "
                    query += " LIMIT 10 "
                    params = (current_username,)
                else:
                    query  = "SELECT DISTINCT src_url, src_title  "
                    query += "  FROM processed_words     "
                    query += " WHERE user_id    = %s     "
                    query += "   AND src_url is not null "
                    query += "   AND group_code = %s     "
                    # query += "   AND status     = %s   "
                    query += " ORDER BY create_date DESC, src_title ASC "
                    params = (
                        current_username,
                        source_type,
                        # "C",
                    )

                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed: ", e)

            existing_titles = cursor.fetchall()

            return existing_titles

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
                query  = " SELECT ifnull(word,''), ifnull(word_guess,''), ifnull(tag,''), ifnull(mean,''), ifnull(group_code,''), ifnull(word_eng_example,''), ifnull(word_kor_example,''), ifnull(word_eng_example2,''), ifnull(word_kor_example2,'') "
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
        # FUNC ID : sqls_main_word_table      
        # 함수명 : URL, TITLE 조회 (1차)
        # 작성일 : 2024.07.20
        #############################################################  '''
        if sql_name == "sqls_main_word_table":
            source_title  = request.GET.get("source_title")
            source_status = request.GET.get("source_status")
            source_type   = request.GET.get("source_type")
            sel_level     = request.GET.get("sel_level")

            try:
                if source_type == "ALL":
                    query  = " SELECT word, mean_en, mean_kr, group_code as create_date "
                    query += "   FROM processed_words   "
                    query += "  WHERE  user_id    = %s  "
                    query += "    AND status     != 'D' "
                    query += "    AND init_status = 'B' "
                    query += "    AND group_code != 'TOPS' "
                    if sel_level == "E":
                       query += " AND level    = %s  "
                    query += " ORDER BY group_code, DATE(create_date) DESC, word ASC "
                    query += " LIMIT 10 "

                    if sel_level == "E":
                       params = (current_username, sel_level)
                    else:
                       params = (current_username,)

                else:
                    query  = " SELECT word, mean_en, mean_kr, DATE(create_date) as create_date "
                    query += "   FROM processed_words  "
                    query += "  WHERE user_id   = %s   "
                    query += "    AND status    = %s   "
                    query += "    AND src_title = %s   "
                    if sel_level == "E":
                       query += " AND level  = %s   "
                    query += " ORDER BY DATE(create_date) DESC, word ASC "

                    if sel_level == "E":
                       params = (current_username, source_status, source_title, sel_level)
                    else:
                       params = (current_username, source_status, source_title, )

                cursor.execute(query, params)

            except Exception as e:
                print("Database query failed:", e)

            existing_words = cursor.fetchall()

            return existing_words

        '''
        #############################################################
        # FUNC ID : sqls_process_info_step_status      
        # 함수명   : 1차 완료 처리 상태 조회
        # 작성일   : 2024.10.07
        #############################################################  '''
        if sql_name == "sqls_process_info_step_status":
            src_title = p_param

            try:
                status_query  = " SELECT ifnull(step,'X') "
                status_query += "   FROM process_info     "
                status_query += "  WHERE user_id   = %s   "
                status_query += "    AND src_title = %s   "
                status_params = (current_username, src_title,)
                cursor.execute(status_query, status_params)

            except Exception as e:
                print("Database query failed:", e)

            tmp_status = cursor.fetchone()
            res_status = tmp_status[0]

            return res_status

        ''' 
        ##############
         INSERT BLOCK
        ############## '''
        '''
        #############################################################
        # FUNC ID : sqli_confirm_word_check    
        # 함수명 : process_info 생성
        # 작성일 : 2024.07.20
        ############################################################# '''
        if sql_name == "sqli_confirm_word_check":

            data = json.loads(request.body)
            selected_title  = data.get("selected_title")
            selected_step   = data.get("selected_step")

            # 2024.01.23 추가- process_info 데이터 생성
            proc_insert_query  = " INSERT INTO process_info "
            proc_insert_query += " (user_id, src_title, undone_cnt, undone_tot_cnt, done_tot_cnt, step) "
            proc_insert_query += " VALUES (%s, %s, 0, 0, 0, %s) "
            proc_insert_params = (current_username, selected_title, selected_step)

            cursor.execute(proc_insert_query, proc_insert_params)

            return 1

        ''' 
        ##############
         UPDATE BLOCK
        ############## '''
        if sql_name == "sqlu_processed_words_status":
            completeWord = p_param

            complete_query1 = " UPDATE processed_words    "
            complete_query1 += "    SET status      = 'D' "
            complete_query1 += "      , init_status = 'B' "
            complete_query1 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
            complete_query1 += " WHERE  user_id = %s "
            complete_query1 += "   AND  word    = %s "
            complete_params1 = (current_username, completeWord,)
            cursor.execute(complete_query1, complete_params1)

        if sql_name == "sqlu_daily_voca_status":
            completeWord = p_param

            complete_query2  = " UPDATE daily_voca   "
            complete_query2 += "    SET status = 'D' "
            complete_query2 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
            complete_query2 += " WHERE  user_id = %s "
            complete_query2 += "   AND  word    = %s "
            complete_params2 = (current_username, completeWord,)

            cursor.execute(complete_query2, complete_params2)

        if sql_name == "sqlu_processed_words_status2":
            srcTitle = p_param

            init_query  = " UPDATE processed_words    "
            init_query += "    SET status      = 'C'  "
            init_query += "      , init_status = 'A'  "
            init_query += "      , start_date  = null "
            init_query += "      , finish_date = null "
            init_query += "  WHERE user_id     = %s   "
            init_query += "    AND src_title   = %s   "
            init_params = (current_username, srcTitle)
            cursor.execute(init_query, init_params)

        if sql_name == "sqlu_daily_voca_status2":
            srcTitle = p_param

            init_query  = " UPDATE daily_voca  "
            init_query += "    SET status         = 'C'  "
            init_query += "      , start_date     = null "
            init_query += "      , priority_date  = null "
            init_query += "      , finish_date    = null "
            init_query += "  WHERE user_id     = %s   "
            init_query += "    AND src_title   = %s   "
            init_query += "    AND word in ( SELECT word FROM processed_words WHERE user_id = %s AND src_title = %s ) "
            init_params = (current_username, srcTitle, current_username, srcTitle)
            cursor.execute(init_query, init_params)

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
        #############################################################
        # FUNC ID : sqlu_processed_words_init_status_for_a    
        # 함수명 : init_status 가 A 인 단어의 status 상태를 완료로 변경
        # 작성일 : 2024.10.06
        #############################################################  '''
        if sql_name == "sqlu_processed_words_init_status_for_a":
           upd_params1 = p_param

           upd_query1  = " UPDATE processed_words   "
           upd_query1 += "    SET no          = %s  "
           upd_query1 += "      , status      = 'D' "
           upd_query1 += "      , init_status = 'A' "
           upd_query1 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S')   "
           upd_query1 += " WHERE  user_id     = %s  "
           upd_query1 += "   AND  word        = %s  "
           upd_query1 += "   AND  init_status = 'A' "

           cursor.execute(upd_query1, upd_params1)

           return "sqlu_processed_words_init_status_for_a OK"

        '''
        #############################################################
        # FUNC ID : sqlu_processed_words_status_for_c    
        # 함수명 : init_status 가 A 인 단어의 status 상태를 완료로 변경
        # 작성일 : 2024.10.06
        #############################################################  '''
        if sql_name == "sqlu_processed_words_status_for_c":
           upd_params2 = p_param

           upd_query2 =  " UPDATE processed_words   "
           upd_query2 += "    SET no          = %s  "
           upd_query2 += "      , status      = 'D' "
           upd_query2 += "      , init_status = 'B' "
           upd_query2 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S')   "
           upd_query2 += " WHERE  user_id     = %s  "
           upd_query2 += "   AND  word        = %s  "
           upd_query2 += "   AND  status      = 'C' "

           cursor.execute(upd_query2, upd_params2)

           return "sqlu_processed_words_status_for_c OK"

        '''
        #############################################################
        # FUNC ID : sqlu_daily_voca_status_for_all    
        # 함수명   : 해당하는 단어의 daily_voca 상태 완료 처리
        # 작성일   : 2024.10.06
        #############################################################  '''
        if sql_name == "sqlu_daily_voca_status_for_all":
           upd_params3 = p_param

           upd_query3  = " UPDATE daily_voca        "
           upd_query3 += "    SET num         = %s  "
           upd_query3 += "      , status      = 'D' "
           upd_query3 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
           upd_query3 += " WHERE  user_id     = %s  "
           upd_query3 += "   AND  word        = %s  "

           cursor.execute(upd_query3, upd_params3)

           return "sqlu_daily_voca_status_for_all OK"

        '''
        #############################################################
        # FUNC ID : sqlu_processed_words_status_to_c_for_word    
        # 함수명 : processed_words 의 단어 상태를 진행으로 변경
        # 작성일 : 2024.10.06
        #############################################################  '''
        if sql_name == "sqlu_processed_words_status_to_c_for_word":
           upd_mean_params = p_param

           # processed_words의 meaning update
           upd_mean_query  = " UPDATE processed_words   "
           upd_mean_query += "    SET no      = %s      "
           upd_mean_query += "      , status  = 'C'     "
           upd_mean_query += "      , init_status = 'B' "
           upd_mean_query += "      , mean_kr = %s      "
           upd_mean_query += "      , start_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
           upd_mean_query += "      , finish_date = NULL "
           upd_mean_query += "  WHERE user_id     = %s   "
           upd_mean_query += "    AND word        = %s   "

           cursor.execute(upd_mean_query, upd_mean_params)

           return "sqlu_processed_words_status_to_c_for_word OK"

        '''
        #############################################################
        # FUNC ID : sqlu_process_info_counts_for_title    
        # 함수명 : process_info 의 타이틀별 건수 변경
        # 작성일 : 2024.10.06
        #############################################################  '''
        if sql_name == "sqlu_process_info_counts_for_title":
           proc_params = p_param

           # 2024.01.23 추가
           proc_query = " UPDATE process_info "
           proc_query += "    SET undone_cnt     = undone_cnt + 1 "
           proc_query += "      , undone_tot_cnt = %s "
           proc_query += "      , done_tot_cnt   = %s "
           proc_query += "      , create_date    = date_format(now(),'%Y-%m-%d %H:%i:%S') "
           proc_query += " WHERE  user_id   = %s   "
           proc_query += "   AND  src_title = %s   "

           cursor.execute(proc_query, proc_params)

           return "sqlu_process_info_counts_for_title OK"

        '''
        #############################################################
        # FUNC ID : sqluu_processed_words_daily_voca_level    
        # 함수명 : processed_words, daily_voca 의 중요도 변경
        # 작성일 : 2024.10.06
        #############################################################  '''
        if sql_name == "sqluu_processed_words_daily_voca_level":
           checked_words = p_param

           for each_word in checked_words:
               # processed_words level 변경
               upd_level_query  = " UPDATE processed_words    "
               upd_level_query += "    SET level   = 'E'      "
               upd_level_query += "      , finish_date = NULL "
               upd_level_query += "  WHERE user_id     = %s   "
               upd_level_query += "    AND word        = %s   "
               upd_level_param = ( current_username, each_word )
               cursor.execute(upd_level_query, upd_level_param)

               # daily_voca  order_priority 변경
               upd_priority_query  = " UPDATE daily_voca           "
               upd_priority_query += "    SET order_priority = 'H' "
               upd_priority_query += "      , priority_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
               upd_priority_query += "      , finish_date = NULL   "
               upd_priority_query += "  WHERE user_id     = %s     "
               upd_priority_query += "    AND word        = %s     "
               upd_priority_param = ( current_username, each_word )
               cursor.execute(upd_priority_query, upd_priority_param)

           return "sqluu_processed_words_daily_voca_level OK"

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
                delete_query1 = " DELETE FROM processed_words "
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
            proc_delete_query = " DELETE FROM process_info "
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
##################   
# 쿼리 CALL 함수 끝    
##################        
'''