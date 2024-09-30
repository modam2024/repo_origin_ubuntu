import json

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from . import create_connection, close_connection, handle_sql_error
from proj_common import mdl_morph_words_proj as morph_new_words

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
        #############################################################
        # CALL ID : sqls_daily_voca_mean
        # 작업     : daily_voca 에서 한글 뜻을 읽어온다.
        # 작성일   : 2024.10.01
        # 작성자   : 이용학 
        ############################################################# '''
        if sql_name == "sqls_daily_voca_mean":
           lemma_word = p_param

           # 쿼리 정의
           voca_query  = " SELECT ifnull(mean,'X') as mean "
           voca_query += "   FROM daily_voca      "
           voca_query += "  WHERE user_id = %s    "
           voca_query += "    AND word    = %s    "
           voca_param = (current_username, lemma_word,)

           # 쿼리 실행
           cursor.execute(voca_query, voca_param)
           existing_mean = cursor.fetchone()

           str_existing_mean = existing_mean[0]

           return str_existing_mean

        '''
        #############################################################
        # CALL ID : sqls_processed_words
        # 작업     : processed_words 에 대상 단어의 정보가 존재하는지 확인        
        # 작성일   : 2024.09.16
        # 작성자   : 이용학 
        ############################################################# '''
        if sql_name == "sqls_processed_words":
           lemma_word = p_param

           # 쿼리 정의
           lemma_query  = " SELECT word, status, ifnull(mean_en,'X') as mean_en "
           lemma_query += "   FROM processed_words "
           lemma_query += "  WHERE user_id = %s    "
           lemma_query += "    AND word    = %s    "
           lemma_param = (current_username, lemma_word,)

           # 쿼리 실행
           cursor.execute(lemma_query, lemma_param)
           existing_word = cursor.fetchone()

           return existing_word

        '''
        #############################################################
        # CALL ID : sqls_group_code
        # 작업     : group_code 에서 구분코드를 조회한다.        
        # 작성일   : 2024.09.16
        # 작성자   : 이용학 
        ############################################################# '''
        if sql_name == "sqls_group_code":

            group_query  = " SELECT group_code         "
            group_query += "   FROM tb_group_code      "
            group_query += "  WHERE user_id = %s       "
            group_query += "  ORDER BY group_order ASC "
            group_params = (current_username,)
            cursor.execute(group_query, group_params)

            existing_group_code = cursor.fetchall()
            group_codes = [group_code[0] for group_code in existing_group_code]

            return group_codes

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
            p_menu_url = request.path
            p_main_menu_no = p_param

            click_query = " INSERT INTO tb_click_study_hist "
            click_query += " ( menu_url, main_menu_no, update_date ) "
            click_query += " VALUES "
            click_query += " ( %s, %s, date_format(now(), '%Y-%m-%d %H:%i:%S') ) "
            click_params = (p_menu_url, p_main_menu_no)
            cursor.execute(click_query, click_params)

        '''
        #############################################################
        # CALL ID : sqlii_processed_words
        # 작업     : 데이터베이스에 해당 단어가 없으면 INSERT 쿼리 실행        
        # 작성일   : 2024.09.16
        # 작성자   : 이용학  
        ############################################################# '''
        if sql_name == "sqlii_processed_words":

            dic_words_info = p_param

            word_insert_count = dic_words_info["word_insert_count"]
            lemma_word        = dic_words_info["lemma_word"]
            tag               = dic_words_info["tag"]
            tag_text          = dic_words_info["tag_text"]
            source_url        = dic_words_info["source_url"]
            source_type       = dic_words_info["source_type"]
            source_title      = dic_words_info["source_title"]
            mean_en_text      = dic_words_info["mean_en_text"]

            mean_en_text = morph_new_words.fn_word_syns_en(lemma_word)

            if mean_en_text == "":
               mean_en_text = "None"

            ins_query  = " INSERT INTO processed_words "
            ins_query += " (no, user_id, word, mean_en, mean_kr, tag, tag_text, src_url, group_code, src_title) "
            ins_query += (
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            )
            ins_params = (
                word_insert_count,
                current_username,
                lemma_word,
                mean_en_text,
                "-",
                tag,
                tag_text,
                source_url,
                source_type,
                source_title,
            )
            cursor.execute(ins_query, ins_params)

            voca_query  = " INSERT INTO daily_voca "
            voca_query += " (num, user_id, word, mean, tag, group_code, noun, verb, adjective, adverb, order_priority, frequency, status, src_url, src_title, create_date, start_date, finish_date) "
            voca_query += " SELECT no, user_id, word, mean_kr, mean_en, group_code, "
            voca_query += "        CASE WHEN SUBSTRING(tag, 1, 1) = 'N' THEN 1 ELSE 0 END, "
            voca_query += "        CASE WHEN SUBSTRING(tag, 1, 1) = 'V' THEN 1 ELSE 0 END, "
            voca_query += "        CASE WHEN SUBSTRING(tag, 1, 1) = 'J' THEN 1 ELSE 0 END, "
            voca_query += "        CASE WHEN SUBSTRING(tag, 1, 1) = 'R' THEN 1 ELSE 0 END, "
            voca_query += "        IFNULL(level, 'L'), frequency, status, src_url, src_title, create_date, start_date, finish_date "
            voca_query += " FROM  processed_words "
            voca_query += " WHERE user_id = %s "
            voca_query += "   AND word    = %s "
            voca_params = (current_username, lemma_word,)

            cursor.execute(voca_query, voca_params)

        '''
        ##############
         UPDATE BLOCK
        ############## '''
        '''
        #############################################################
        # CALL ID : sqluu_cond_processed_words
        # 작업     : processed_words 에 해당 단어의 정보를 업데이트 한다.   
        #           이미 데이터베이스에 해당 단어가 완료되지 않은 상태면 
        #           다시 url, title, 영문뜻, 날짜들을 갱신해 준다.
        # 작성일   : 2024.09.16
        # 작성자   : 이용학  
        ############################################################# '''
        if sql_name == "sqluu_cond_processed_words":

            dic_words_info = p_param

            # existing_word_2   = dic_words_info["existing_word_2"]
            lemma_word        = dic_words_info["lemma_word"]
            source_url        = dic_words_info["source_url"]
            source_type       = dic_words_info["source_type"]
            source_title      = dic_words_info["source_title"]
            # mean_en_text      = dic_words_info["mean_en_text"]

            try:
                mean_en_text = morph_new_words.fn_word_syns_en(lemma_word)
                mean_kr_text = sql_dao(request, "sqls_daily_voca_mean",  lemma_word)

                if mean_en_text == "":
                   mean_en_text = "None"
                
                renewal_query  = " UPDATE processed_words    "
                renewal_query += "    SET src_url      = %s  "
                renewal_query += "      , group_code   = %s  "
                renewal_query += "      , status       = 'C' "
                renewal_query += "      , init_status  = 'B' "
                renewal_query += "      , src_title    = %s  "
                renewal_query += "      , mean_kr      = %s  "
                renewal_query += "      , mean_en      = %s  "
                renewal_query += "      , start_date   = date_format(now(), '%Y-%m-%d %H:%i:%S') "
                renewal_query += "      , create_date  = now() "
                renewal_query += "      , finish_date  = NULL  "
                renewal_query += "  WHERE word    = %s "
                renewal_query += "    AND user_id = %s "
                renewal_params = (
                    source_url,
                    source_type,
                    source_title,
                    mean_kr_text,
                    mean_en_text,
                    lemma_word,
                    current_username,
                )
                cursor.execute(renewal_query, renewal_params)

                voca_query  = " UPDATE daily_voca "
                voca_query += "    SET src_url    = %s "
                voca_query += "      , group_code = %s "
                voca_query += "      , src_title  = %s "
                voca_query += "      , tag        = %s "
                voca_query += "      , status     = 'C' "
                voca_query += "      , create_date  = now() "
                voca_query += "      , finish_date  = NULL  "
                voca_query += " WHERE  word    = %s "
                voca_query += "   AND  user_id = %s "
                voca_params = (
                    source_url,
                    source_type,
                    source_title,
                    mean_en_text,
                    lemma_word,
                    current_username,
                )
                cursor.execute(voca_query, voca_params)

            except Exception as e:
                print("Renewal query failed:", e)

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
    page_url  = "/app_word_work/main-wordcheck/?source_url=&source_title=&source_type=ALL&source_status=C"

    if base_url in full_url:
        source_url = base_url + page_url
    else:
        source_url = local_url + page_url

    return HttpResponseRedirect(source_url)
