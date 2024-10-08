import re

import spacy

from app_common import mdl_common_app as comn_func
from app_news_study.pkg_mdl_common import mdl_common_news as app_comn_func
from app_news_study.pkg_sql_statement import create_connection, close_connection, handle_sql_error

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
            # p_news_date = p_param["today_news_date"]
            # p_max_date  = p_param["max_news_date"]
            p_max_date = p_param

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query =  " SELECT keyno, title      "
            select_query += "   FROM tb_news_info_main "
            select_query += "  WHERE user_id = %s      "
            select_query += "    AND DATE_FORMAT(create_date, '%Y-%m-%d') = %s "
            select_query += "  ORDER BY keyno          "
            select_params = (current_username, p_max_date,)

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
            news_info_engs_dicts = []

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

            for news_info_eng in news_info_engs:
                tmp_orderno  = news_info_eng[1]
                tmp_newstype = news_info_eng[2]

                tmp_whitespace_converted = ""
                tmp_converted_sentn = ""
                tmp_original_sentn = ""

                if tmp_newstype == "ENG":
                   # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
                   study_query =  " SELECT whitespace_converted, converted_sentn, original_sentn "
                   study_query += "   FROM tb_convert_news_study  "
                   study_query += "  WHERE user_id   = %s    "
                   study_query += "    AND key_no    = %s    "
                   study_query += "    AND group_no  = %s    "
                   study_query += "  ORDER BY order_no ASC   "
                   study_params = (current_username, keyno_eng, tmp_orderno)
                   # 쿼리 실행
                   cursor.execute( study_query, study_params, )
                   cnvrt_engs_info = cursor.fetchall()

                   if cnvrt_engs_info:
                      for cnvrt_eng in cnvrt_engs_info:
                          tmp_whitespace_converted += cnvrt_eng[0]
                          tmp_converted_sentn      += cnvrt_eng[1]
                          tmp_original_sentn       += cnvrt_eng[2]

                news_study_eng = {
                   'keyitem'  : news_info_eng[0],
                   'groupno'  : news_info_eng[1],
                   'newstype' : news_info_eng[2],
                   'keyno'    : news_info_eng[3],
                   'whitespace_converted' : tmp_whitespace_converted.strip(),
                   'converted_sentn'      : tmp_converted_sentn.strip(),
                   'original_sentn'       : tmp_original_sentn.strip(),
                }

                # 튜플의 리스트를 사전의 리스트로 변환
                news_info_engs_dicts.append(news_study_eng)

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
        #############################################################
        # SQL ID : sqls_uncompleted_words
        # 작성일  : 2024.09.18
        # 작  업 : 선택된 뉴스 기사의 미완료된 단어의 건수를 조회한다.   
        ############################################################# '''
        if sql_name == "sqls_uncompleted_words":
            p_param = p_param.strip()
            selected_title = "%" + p_param + "%"

            # tb_news_info_detail 테이블에 keyno 대상 최대 num 을 가져온다.
            select_query  = " SELECT COUNT(*)          "
            select_query += "   FROM processed_words   "
            select_query += "  WHERE user_id   = %s    "
            select_query += "    AND src_title LIKE %s "
            select_query += "    AND status     != 'D' "
            select_query += "    AND init_status = 'B' "
            select_params = (current_username, selected_title)

            # 쿼리 실행
            cursor.execute(select_query, select_params,)
            ing_count = cursor.fetchone()
            ing_cnt   = ing_count[0]

            return ing_cnt

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

            try:
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
                conn.commit()

                # tb_news_info_detail 테이블에 @joongang.co.kr 찾아서 삭제함
                delete_query  = " DELETE FROM tb_news_info_detail "
                delete_query += " WHERE keyitem LIKE '%@joongang.co.kr%' "
                cursor.execute( delete_query, )
                conn.commit()

                if news_info_type == "ENG":
                   sql_news_convert_sentence(request, news_info_keyitem, news_max_num, dic_news_info_detail)

            except Exception as e:
                print("sqli_news_info exception =", e)

            return str(news_max_num), ins_params

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
        ############################################################
        # CALL ID : sqli_batch_news_study_hist
        # 함수명   : 뉴스 배치 자동 생성 스크립트용
        # 작성일   : 2024.09.04
        # 작업     : 뉴스 배치 자동 생성 스크립트용  
        ############################################################  '''
        if sql_name == "sqli_batch_news_study_hist":

            v_title = p_param['TITLE']

            try:
                batch_query = " INSERT INTO tb_batch_news_study_hist "
                batch_query += " ( new_title, update_date ) "
                batch_query += " VALUES ( %s, date_format(now(), '%Y-%m-%d %H:%i:%S') ) "
                batch_params = (v_title,)

                cursor.execute(batch_query, batch_params)
                conn.commit()

            except Exception as e:
                #  3일전 배치 작업은 전체 삭제 한다.
                sql_dao(request, "sqld_batch_news_study_hist", p_param)

            finally:
                #  3일전 배치 작업은 전체 삭제 한다.
                sql_dao(request, "sqld_batch_news_study_hist", p_param)
                print("sqli_batch_news_study_hist finished")

            return "OK"

        '''    
        ############################################################
        # CALL ID : sqli_convert_news_study
        # 함수명   : NEWS 문장을 변환된 문장을 저장한다.   
        # 작성일   : 2024.09.13
        # 작업     : NEWS 문장을 변환된 문장을 저장한다.  
        ############################################################  '''
        if sql_name == "sqli_convert_news_study":
            key_no           = p_param["key_no"]
            group_no         = p_param["group_no"]
            source_url       = p_param["source_url"]
            source_title     = p_param["source_title"]
            source_type      = p_param["source_type"]
            list_rslt_sentns = p_param["list_rslt_sentns"]

            int_test_cnt = 0

            for whitespace_converted, converted_sentn, original_sentn, translated_sentn in list_rslt_sentns:

                # “ 와 ” 문자를 제거합니다.
                clean_converted_sentn = re.sub(r'[“”]', '', converted_sentn)
                clean_original_sentn  = re.sub(r'[“”]', '', original_sentn)


                str_whitespace_converted = whitespace_converted
                str_converted_sentn      = clean_converted_sentn
                str_original_sentn       = clean_original_sentn
                str_translated_sentn     = translated_sentn

                int_test_cnt += 1

                try:
                    ins_query = " INSERT INTO tb_convert_news_study "
                    ins_query += " (user_id, key_no, group_no, order_no, whitespace_converted, converted_sentn, original_sentn, translated_sentn, src_url, group_code, src_title) "
                    ins_query += " VALUES "
                    ins_query += " (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "

                    ins_params = (
                        current_username,
                        key_no,
                        group_no,
                        int_test_cnt,
                        str_whitespace_converted,
                        str_converted_sentn,
                        str_original_sentn,
                        str_translated_sentn,
                        source_url,
                        source_type,
                        source_title,
                    )
                    cursor.execute(ins_query, ins_params)
                    conn.commit()

                    delete_query = " DELETE FROM tb_convert_news_study "
                    delete_query += " WHERE original_sentn LIKE '%@joongang.co.kr%' "
                    cursor.execute(delete_query, )
                    conn.commit()

                except Exception as e:
                    int_test_cnt -= 1

            return int_test_cnt

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
        # CALL ID : sqld_batch_news_study_hist
        # 함수명   : 배치 히스토리 테이블의 7일 이전의 데이터 삭제
        # 작성일   : 2024.08.31
        # 작업     : 배치 히스토리 테이블의 7일 이전의 데이터 삭제
        ############################################################ '''
        if sql_name == "sqld_batch_news_study_hist":
            print(" INTERVAL 4  sqld_batch_news_study_hist ")
            del_batch_query = " DELETE FROM tb_batch_news_study_hist "
            del_batch_query += "  WHERE create_date <= DATE_SUB(now(), INTERVAL 2 DAY) "
            cursor.execute(del_batch_query, )

        '''
        ############################################################
        # CALL ID : sqld_invalid_news_info
        # 함수명   : 뉴스 사이트 예외 article 삭제  
        # 작성일   : 2024.08.09
        # 작업     : 뉴스 사이트 예외 article 삭제한다.
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
# 배치작업시 중앙일보 문장변환 후 저장하는 함수
# 작성일 : 2024.09.16
####################################################### '''
def sql_news_convert_sentence(request, article_content, p_group_no, news_info):
    # 변환된 텍스트 저장용 리스트
    convert_values = {
        "key_no"           : news_info['KEYNO'],
        "group_no"         : p_group_no,
        "source_url"       : news_info['URL'],
        "source_title"     : news_info['TITLE'],
        "source_type"      : "ENG",
        "list_rslt_sentns" : [],
    }

    # 변환된 텍스트 저장용 리스트
    converted_sentences = []
    list_rslt_sentns = []

    nlp = spacy.load('en_core_web_sm')

    # 뉴스 기사 텍스트를 SpaCy의 nlp 객체로 분석
    doc = nlp(article_content)

    # 문장 단위로 분리된 리스트 생성
    sentences = list(doc.sents)

    # 문장에서 각 품사를 변환
    for sent in sentences:
        original_sentence = sent.text
        # 어플 공통 : 대상 영문장을 변환문장시 전처리한다.
        original_sentence, converted_sentence = comn_func.fn_preparation_process_of_convert(sent, original_sentence)
        converted_sentences.append((original_sentence, converted_sentence))

    # 결과 출력
    for original_sentence, converted_sentence in converted_sentences:
        # 어플 공통 : 변환문장에서 특수문자 전처리한다.
        result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn = comn_func.fn_comma_process_of_convert(
            original_sentence, converted_sentence)
        list_rslt_sentns.append(
            (result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn))

    convert_values["list_rslt_sentns"] = list_rslt_sentns

    v_test_no = sql_dao(request, "sqli_convert_news_study", convert_values)

    # 처리 성공 응답
    return "OK"