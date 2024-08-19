import json

import mysql.connector
import nltk
from django.contrib.auth.decorators import login_required
# 2024.04.28 : spacy 포함
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from googletrans import Translator
from nltk.corpus import wordnet

from mdl_common import common_morph_process as comn_mph_process, common as comn_func
from mdl_sql_mapping import sql_mapping_article as sql_statement_article
from mdl_sql_mapping import create_connection, close_connection

# nltk 리소스 다운로드 (서버 시작 시 한 번만 수행하면 됩니다)
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")

def fn_word_syns_kr(p_word):
    translator = Translator()
    syns = wordnet.synsets(p_word)
    def_list_kr = ""
    for syn in syns:
        english_definition = syn.definition()
        # Korean
        korean_definition = translator.translate(
            english_definition, src="en", dest="ko"
        )

        if def_list_kr:
            def_list_kr += " , " + korean_definition.text
        else:
            def_list_kr = korean_definition.text
    return def_list_kr


# GROUP CODE 생성함수, 2024-02-13
def get_group_codes(request):
    conn, cursor, current_username = create_connection(request)

    try:
        cursor.execute(
            "SELECT  group_code FROM tb_group_code WHERE user_id = %s ORDER BY group_order ASC",
            (current_username,),
        )
        existing_group_code = cursor.fetchall()
        group_codes = [group_code[0] for group_code in existing_group_code]
        return group_codes
    except Exception as e:
        print("group_code query failed: ", e)
        return []
    finally:
        close_connection(conn, cursor)

# MAX CHAPTER NUM 조회함수, 2024-02-21
def retrieve_max_chapter_num(request):
    conn, cursor, current_username = create_connection(request)

    try:
        # 이미 데이터베이스에 해당 단어가 있는지 확인
        cursor.execute(
            "SELECT ifnull(max(src_chapter) ,'4450') as max_chapter_num FROM tb_chapter_title WHERE user_id = %s ",
            (current_username,),
        )
        existing_max_chapter_num = cursor.fetchone()
        return existing_max_chapter_num[0]
    except Exception as e:
        print("retrieve max num query failed: ", e)
        return "4450"
    finally:
        close_connection(conn, cursor)

def retrieve_ing_chapter_num(request):
    conn, cursor, current_username = create_connection(request)

    try:
        # 이미 데이터베이스에 해당 단어가 있는지 확인
        cursor.execute(
            "SELECT ifnull(max(src_chapter), 0) as max_chapter_num FROM tb_chapter_title WHERE user_id = %s and status = 'C' ",
            (current_username,),
        )
        existing_max_chapter_num = cursor.fetchone()
        return existing_max_chapter_num[0]
    except Exception as e:
        print("retrieve max num query failed: ", e)
        return "0"
    finally:
        close_connection(conn, cursor)

# PAGE INFO 생성함수, 2024-02-21
def make_page_info(request):
    # 변수 초기화
    err_cnt = 0
    new_chapter_cnt = 0
    number = 1
    max_chapter_num = int(retrieve_max_chapter_num(request))

    while True:  # 무한 루프
        if number > 1:
            max_chapter_num += 1

        if number > 4000:
            break
        else:
            number += 1

        try:
            url = "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx={}".format(
                max_chapter_num
            )

            # 공통 함수의 webdriver를 사용해서 파싱한다.
            html, soup = comn_func.url_parsing_with_webdriver(url, "1")

            # <audio> 태그 찾기
            audio_tag = soup.find("audio")

            # 존재하지 않는 페이지 처리
            if not audio_tag:
                print(
                    f"Page for chapter {max_chapter_num} does not exist or has no audio."
                )
                break

            # 'src' 속성 추출
            src_value = audio_tag["src"]

            # 파일명 추출 (마지막 '/' 이후의 내용)
            file_name = src_value.split("/")[-1]

            # 확장자 제거 및 출력
            audio_name = file_name.split(".")[0]

            # YBM 생활영어 제목 찾기
            title_view = soup.find(class_=["title-view"])
            if title_view:
                for title in title_view.find_all("strong"):
                    title_text = title.get_text(strip=True)

            # CHAPTER 3가지 정보 테이블 저장
            incr_cnt = do_insert_page_info(
                request, max_chapter_num, title_text, audio_name
            )
            new_chapter_cnt += int(incr_cnt)

            # 신규 회차의 CONTENT 생성
            # <dl> 태그의 내용을 추출합니다.
            text = ""
            dl_tags = soup.find_all("dl")

            for dl in dl_tags:
                text += dl.get_text(separator="\n", strip=True) + "\n"

            # A와 B 기준으로 텍스트를 그룹화
            txt_eng_map = []
            txt_kor_map = []
            txt_additional_map = []
            prv_ab_text = "A"
            tmp_ab_text = ""
            tmp_ab_text2 = ""
            grouped_text = "A"
            lines = text.split("\n")
            loop = 0
            for line in lines:
                line = line.replace("A ", " A ")
                line = line.replace("B ", " B ")

                if line.startswith("A"):
                    tmp_ab_text = "A"
                elif line.startswith("B"):
                    tmp_ab_text = "B"
                elif line.startswith("2"):
                    tmp_ab_text2 = "B2"
                elif line.startswith("[A"):
                    tmp_ab_text = "C"
                elif line.startswith("해설"):
                    tmp_ab_text = "D"
                else:
                    if tmp_ab_text == "A" or tmp_ab_text == "B" or tmp_ab_text == "C":
                        if prv_ab_text != tmp_ab_text:
                            prv_ab_text = tmp_ab_text
                            if tmp_ab_text == "C":
                                if loop == 1:
                                    txt_kor_map.append(grouped_text)
                                grouped_text = line
                                txt_additional_map.append(grouped_text)
                            elif tmp_ab_text2 == "B2":
                                if loop == 0:
                                    txt_eng_map.append(grouped_text)
                                    grouped_text = tmp_ab_text + " " + line
                                    loop = loop + 1
                                else:
                                    txt_kor_map.append(grouped_text)
                                    grouped_text = tmp_ab_text + " " + line
                            elif tmp_ab_text2 != "B2":
                                txt_eng_map.append(grouped_text)
                                grouped_text = tmp_ab_text + " " + line
                            else:
                                txt_eng_map.append(grouped_text)
                                grouped_text = tmp_ab_text + " " + line
                        elif tmp_ab_text == "C":
                            grouped_text = ""
                            grouped_text += line
                            txt_additional_map.append(grouped_text)
                        else:
                            if (
                                line.startswith("2")
                                or line.startswith("3")
                                or line.startswith("오디오")
                                or line.startswith("해석")
                            ):
                                grouped_text = grouped_text + ""
                            else:
                                grouped_text += " " + line
                    elif tmp_ab_text == "D":
                        txt_engs = ""
            if new_chapter_cnt > 0:
                txt_engs = "\n\n"
                eng_num = 1
                for each_eng in txt_eng_map:
                    txt_engs += each_eng + "\n\n"
                    do_saving_each_content(
                        request, "eng", eng_num, max_chapter_num, each_eng
                    )
                    eng_num += 1

                txt_kors = "\n\n"
                kor_num = 1
                for each_kor in txt_kor_map:
                    txt_kors += each_kor + "\n\n"
                    do_saving_each_content(
                        request, "kor", kor_num, max_chapter_num, each_kor
                    )
                    kor_num += 1

                txt_additionals = "\n\n"
                additional_num = 1
                for each_additional in txt_additional_map:
                    txt_additionals += each_additional + "\n\n"
                    do_saving_each_content(
                        request, "add", additional_num, max_chapter_num, each_additional
                    )
                    additional_num += 1

        except Exception as e:
            print("Finding web-page failed: ", e)
            if int(err_cnt > 0) and int(max_chapter_num) > 4730:
                break
            else:
                err_cnt += 1
    return new_chapter_cnt  # while 수행 완료 후 return 함


# 단어 추출 첫화면 조회, group_code 셋팅
@login_required(login_url='/login/')
def main_view(request):
    group_codes = get_group_codes(request)

    values = {
        "group_codes": group_codes,
    }
    return render(request, "article.html", values)
def get_mean_kr_from_naver_dic(en_word):
    try:
        # Chrome 드라이버 경로 지정
        # driver_path = r'C:\pyDjangoDEV\mdmproj1\chromedriver-win64\chromedriver.exe'

        url = "http://en.dict.naver.com/#/search?&query={}".format(en_word)

        # 공통 함수의 webdriver를 사용해서 파싱한다.
        html, soup = comn_func.url_parsing_with_webdriver(url, "1")

        # 단어의 의미 추출
        meanings = []
        mean_list = soup.find(class_=["mean_list", "mean_list_multi", "mean_list multi", "word_class"])
        # mean_list가 None이 아니면 실행될 코드
        if mean_list is not None:
            print("meaning of {} is completed(1)".format(en_word))
        else:
            html, soup = comn_func.url_parsing_with_webdriver(url, "2")
            meanings = []
            mean_list = soup.find(class_=["mean_list", "mean_list_multi", "mean_list multi", "word_class"])
            # mean_list가 None이 아니면 실행될 코드
            if mean_list is not None:
               print("meaning of {} is completed(2)".format(en_word))
            else:
               print("No elements found with the specified class(3).")
        if mean_list:
            for li in mean_list.find_all("li"):
                meaning = li.find("p", class_="mean")
                if meaning:
                    # <span> 태그 내의 텍스트를 제외한 나머지 텍스트 추출
                    for span in meaning.find_all("span"):
                        span.decompose()  # <span> 태그와 그 내용을 제거
                    extracted_text = meaning.get_text(strip=True)
                    if extracted_text:
                        meanings.append(extracted_text)

        meaning_kr = ""

        for meaning in meanings:
            meaning_kr += meaning + "\n"

    except Exception as e:
        meaning_kr = ""
        print("Finding meaning_kr failed - ( {} ): ".format(en_word), e)

    return meaning_kr
def fetch_titles(request, selectd_chapter, selectd_status):

    rtn_selectd_chapter    = ""
    rtn_title_text         = ""
    rtn_selectd_voice_date = ""

    # 상태별 영어회화 음성파일 재생 정보 조회
    existing_titles = sql_statement_article.sql_dao(request, "sqls_fetch_titles", selectd_status)

    # 결과를 리스트로 변환
    titles = [
        (chapter, title, voice_date)
        for chapter, title, voice_date in existing_titles
    ]

    for title in titles:
        if title[0] == selectd_chapter:
            rtn_selectd_chapter = title[0]
            rtn_title_text = title[1]
            rtn_selectd_voice_date = title[2]
            break
    else:
        # for 루프가 break 없이 정상 종료되면, 첫 번째 항목으로 기본값을 설정
        rtn_selectd_chapter = titles[0][0] if titles else ""
        rtn_title_text = titles[0][1] if titles else ""
        rtn_selectd_voice_date = titles[0][2] if titles else ""

    # 완료된 영어회화 정보 조회
    existing_comp_titles = sql_statement_article.sql_dao(request, "sqls_fetch_titles2", "")

    # 결과를 리스트로 변환
    comp_titles = [
        (chapter, title, voice_date)
        for chapter, title, voice_date in existing_comp_titles
    ]

    return (
        titles,
        comp_titles,
        rtn_selectd_chapter,
        rtn_title_text,
        rtn_selectd_voice_date,
    )

def show_current_living_english(request, selectd_chapter, selectd_status):

    # 데이터베이스 연결 초기화
    conn, cursor, current_username = create_connection(request)

    v_topic_dur_start = 0
    v_topic_dur_end   = 0

    # 전체 titles 정보와 선택된 chapter 정보를 조회한다.
    titles, comp_titles, selectd_chapter, title_text, audio_name = fetch_titles(
        request, selectd_chapter, selectd_status
    )

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
        v_topic_dur_end   = 0

    try:
        txt_eng_data, txt_kor_data, txt_additional_data, content_cnt = (
            retrieve_content_info(request, selectd_chapter)
        )
        if int(content_cnt) > 0:
            txt_engs = "\n\n"
            eng_num = 1
            for each_eng in txt_eng_data:
                each_eng = each_eng[0]
                txt_engs += each_eng + "\n\n"
                eng_num += 1

            txt_kors = "\n\n"
            kor_num = 1
            for each_kor in txt_kor_data:
                each_kor = each_kor[0]
                txt_kors += each_kor + "\n\n"
                kor_num += 1

            txt_additionals = "\n\n"
            additional_num = 1
            for each_additional in txt_additional_data:
                each_additional = each_additional[0]
                txt_additionals += each_additional + "\n\n"
                additional_num += 1

            return (
                titles,
                comp_titles,
                title_text,
                audio_name,
                txt_engs,
                txt_kors,
                txt_additionals,
                v_topic_dur_start,
                v_topic_dur_end,
            )

    except Exception as e:
        print("Error occurred:", e)
        return ""

    finally:
        close_connection(conn, cursor)

@csrf_exempt
def do_saving_each_content(request, p_type, p_seq_num, p_chapter_num, p_each_stmt):
    conn, cursor, current_username = create_connection(request)

    try:

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

        conn.commit()
    except Exception as e:
        print("do_saving_each_content failed:", e)
    finally:
        close_connection(conn, cursor)

def retrieve_content_info(request, p_selectd_chapter):
    conn, cursor, current_username = create_connection(request)

    try:
        # first part - english
        query = " SELECT each_stmt       "
        query += "   FROM tb_living_english_content "
        query += "  WHERE user_id = %s   "
        query += "    AND type = 'eng' AND chapter_num = %s  "
        query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC   "
        query_param = (current_username, p_selectd_chapter,)
        cursor.execute(query, query_param)
        existing_eng_content = cursor.fetchall()
        selectd_eng_content = [(each_stmt) for each_stmt in existing_eng_content]

        # second part - korean
        query = " SELECT each_stmt       "
        query += "   FROM tb_living_english_content "
        query += "  WHERE user_id = %s   "
        query += "    AND type = 'kor' AND chapter_num = %s  "
        query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC  "
        query_param = (current_username, p_selectd_chapter,)
        cursor.execute(query, query_param)
        existing_kor_content = cursor.fetchall()
        selectd_kor_content = [(each_stmt) for each_stmt in existing_kor_content]

        # third part - additional
        query = " SELECT each_stmt       "
        query += "   FROM tb_living_english_content "
        query += "  WHERE user_id = %s   "
        query += "    AND type = 'add' AND chapter_num = %s  "
        query += "  ORDER BY CAST(seq_num AS UNSIGNED) ASC  "
        query_param = (current_username, p_selectd_chapter,)
        cursor.execute(query, query_param)
        existing_add_content = cursor.fetchall()
        selectd_add_content = [(each_stmt) for each_stmt in existing_add_content]

        # total count
        cursor.execute(
            "SELECT  count(*) as cnt FROM tb_living_english_content WHERE user_id = %s AND chapter_num = %s",
            (current_username, p_selectd_chapter,),
        )
        result_cnt = cursor.fetchone()
        return_cnt = result_cnt[0]

        if int(return_cnt) > 0:
            query  = " UPDATE tb_chapter_title "
            query += "    SET start_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
            query += "  WHERE user_id     = %s "
            query += "    AND src_chapter = %s "
            query_param = (current_username, p_selectd_chapter,)
            cursor.execute(query, query_param)
            conn.commit()

        return selectd_eng_content, selectd_kor_content, selectd_add_content, return_cnt

    except Exception as e:
        print("retrieve_content_info failed: ", e)
        return [], [], [], 0
    finally:
        close_connection(conn, cursor)
@login_required(login_url='/login/')
def main_word_check(request):
    source_url = request.GET.get("source_url")
    source_title = request.GET.get("source_title")
    source_status = request.GET.get("source_status")
    source_type = request.GET.get("source_type")

    existing_words = sql_statement_article.sql_dao(request, "sqls_main_word_check", "")

    rows = []
    rows_cnt = 0

    for record in existing_words:
        cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date = record
        rows.append([cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date])
        rows_cnt += 1

    existing_titles = sql_statement_article.sql_dao(request, "sqls_main_word_check2", "")

    titles = [(url, title) for url, title in existing_titles]
    group_codes = get_group_codes(request)

    values = {
        "rows": rows,
        "titles": titles,
        "rows_cnt": rows_cnt,
        "source_url": source_url,
        "source_title": source_title,
        "source_status": source_status,
        "source_type": source_type,
        "group_codes": group_codes,
    }

    return render(request, "word_check.html", values)

@login_required(login_url='/login/')
def main_word_table(request):
    source_title = request.GET.get("source_title")
    source_status = request.GET.get("source_status")

    existing_words = sql_statement_article.sql_dao(request, "sqls_main_word_table", "")

    rows = []
    rows_cnt = 0

    cur_no = 0
    for record in existing_words:
        cur_word, cur_mean_en, cur_tag_text, cur_create_date = record
        cur_no = cur_no + 1
        rows.append([cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date])
        rows_cnt += 1

    # 처리 성공 응답
    return JsonResponse({"rows": rows, "rows_cnt": rows_cnt})
@login_required(login_url='/login/')
def delete_content(request):

    rows_cnt = sql_statement_article.sql_dao(request, "sqld_delete_content", "")

    # 처리 성공 응답
    return JsonResponse({"rows_cnt": rows_cnt})

@csrf_exempt
@login_required(login_url='/login/')
def submit_article(request):
    # POST 요청일 때만 처리
    if request.method == "POST":
        # 기존의 submit-article 함수를 모듈화 시켰다.
        rtn_result = comn_mph_process.submit_topic(request)
        # if rtn_result["status"] == "success":
        #    comn_morph.submit_sentence(request)
        return JsonResponse(rtn_result)
    else:
        # POST 요청이 아닐 때의 처리
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )

@csrf_exempt
@login_required(login_url='/login/')
def confirm_word_check(request):
    conn, cursor, current_username = create_connection(request)
    proc_conn, proc_cursor, current_username = create_connection(request)

    # POST 요청일 때만 처리
    if request.method == "POST":
        done_row_num = 0
        undone_row_num = 0
        update_word_count = 0

        try:
            data = json.loads(request.body)
            checked_words = data.get("words")
            unchecked_words = data.get("unchckd_words")
            selected_status = data.get("selected_status")
            selected_title = data.get("selected_title")

            # process_info 삭제
            rtn_code = sql_statement_article.sql_dao(request, "sqld_confirm_word_check", selected_title)

            # process_info 생성
            rtn_code = sql_statement_article.sql_dao(request, "sqli_confirm_word_check", selected_title)

            # 2024.01.23 추가- process_info 개별 count 데이터 초기화
            if checked_words is not None:
                checked_words_count = len(checked_words)
            else:
                checked_words_count = 0

            if unchecked_words is not None:
                unchecked_words_count = len(unchecked_words)
            else:
                unchecked_words_count = 0

            if selected_status == "D":
                # Checked 된 경우
                for checked_word in checked_words:
                    try:
                        done_row_num = done_row_num + 1

                        upd_query1  = " UPDATE processed_words   "
                        upd_query1 += "    SET no          = %s  "
                        upd_query1 += "      , status      = 'D' "
                        upd_query1 += "      , init_status = 'A' "
                        upd_query1 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S')   "
                        upd_query1 += " WHERE  user_id     = %s  "
                        upd_query1 += "   AND  word        = %s  "
                        upd_query1 += "   AND  init_status = 'A' "
                        upd_params1 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )
                        cursor.execute(upd_query1, upd_params1)

                        upd_query1 = " UPDATE processed_words   "
                        upd_query1 += "    SET no          = %s  "
                        upd_query1 += "      , status      = 'D' "
                        upd_query1 += "      , init_status = 'B' "
                        upd_query1 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S')   "
                        upd_query1 += " WHERE  user_id     = %s  "
                        upd_query1 += "   AND  word        = %s  "
                        upd_query1 += "   AND  status      = 'C' "
                        upd_params1 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )
                        cursor.execute(upd_query1, upd_params1)

                        update_word_count += 1

                        upd_query2 = " UPDATE daily_voca "
                        upd_query2 += "    SET num         = %s  "
                        upd_query2 += "      , status      = 'D' "
                        upd_query2 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                        upd_query2 += " WHERE  user_id     = %s  "
                        upd_query2 += "   AND  word        = %s  "
                        upd_params2 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )
                        cursor.execute(upd_query2, upd_params2)

                    except Exception as e:
                        print("Update query failed:", e)

            # Unchecked 된 경우
            for unchecked_word in unchecked_words:
                try:
                    mean_kr_text = get_mean_kr_from_naver_dic(unchecked_word)

                    # mean_kr_text가 None 또는 빈 문자열일 경우 '*N'으로 설정
                    if not mean_kr_text:
                        mean_kr_text = "*N"

                    undone_row_num = undone_row_num + 1

                    # processed_words의 meaning update
                    upd_mean_query =  " UPDATE processed_words   "
                    upd_mean_query += "    SET no      = %s      "
                    upd_mean_query += "      , status  = 'C'     "
                    upd_mean_query += "      , init_status = 'B' "
                    upd_mean_query += "      , mean_kr = %s      "
                    upd_mean_query += "      , start_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                    upd_mean_query += "      , finish_date = NULL "
                    upd_mean_query += "  WHERE user_id     = %s   "
                    upd_mean_query += "    AND word        = %s   "
                    upd_mean_params = (
                        undone_row_num,
                        mean_kr_text,
                        current_username,
                        unchecked_word,
                    )
                    cursor.execute(upd_mean_query, upd_mean_params)

                    # daily_voca의 meaning update
                    upd_mean_daily_voca_query =  " UPDATE daily_voca   "
                    upd_mean_daily_voca_query += "    SET num    =  %s "
                    upd_mean_daily_voca_query += "      , status = 'C' "
                    upd_mean_daily_voca_query += "      , mean   = %s  "
                    upd_mean_daily_voca_query += "      , start_date  = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                    upd_mean_daily_voca_query += "      , finish_date = NULL "
                    upd_mean_daily_voca_query += "  WHERE user_id = %s  "
                    upd_mean_daily_voca_query += "    AND word    = %s  "
                    upd_mean_daily_voca_params = (
                        undone_row_num,
                        mean_kr_text,
                        current_username,
                        unchecked_word,
                    )
                    cursor.execute(
                        upd_mean_daily_voca_query, upd_mean_daily_voca_params
                    )

                    # 2024.01.23 추가
                    proc_query = " UPDATE process_info "
                    proc_query += "    SET undone_cnt     = undone_cnt + 1 "
                    proc_query += "      , undone_tot_cnt = %s "
                    proc_query += "      , done_tot_cnt   = %s "
                    proc_query += "      , create_date    = date_format(now(),'%Y-%m-%d %H:%i:%S') "
                    proc_query += " WHERE  user_id   = %s   "
                    proc_query += "   AND  src_title = %s   "
                    proc_params = (
                        unchecked_words_count,
                        checked_words_count,
                        current_username,
                        selected_title,
                    )

                    proc_cursor.execute(proc_query, proc_params)
                    proc_conn.commit()

                except Exception as e:
                    print("Update mean_kr failed: ", e)

            # 처리 성공 응답
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Word Completed successfully",
                    "update_word_count": update_word_count,
                }
            )

        except json.JSONDecodeError:
            # JSON 파싱 에러 처리
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )

        except mysql.connector.Error as e:
            # MySQL 연결 또는 쿼리 실행 오류 처리
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        except Exception as e:
            # 기타 예외 처리
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        finally:
            close_connection(conn, cursor)
            close_connection(proc_conn, proc_cursor)

    else:
        # POST 요청이 아닐 때의 처리
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )

@login_required(login_url='/login/')
def word_detail(request):
    cur_word = ''
    cur_tag  = ''
    cur_mean = ''
    cur_word_guess = ''
    cur_group_code = ''
    cur_word_eng_example = ''
    cur_word_kor_example = ''
    cur_word_eng_example2 = ''
    cur_word_kor_example2 = ''

    word = request.GET.get("word")
    wrd_title = request.GET.get("wrd_title")

    existing_words = sql_statement_article.sql_dao(request, "sqls_word_detail", "")

    # for 의 결과는 무조건 1 건이다.
    for record in existing_words:
        (
            cur_word,
            cur_word_guess,
            cur_tag,
            cur_mean,
            cur_group_code,
            cur_word_eng_example,
            cur_word_kor_example,
            cur_word_eng_example2,
            cur_word_kor_example2,
        ) = record

    # word detail 화면에 title 별 전체 미완료 단어 보여주기
    all_words_by_title = sql_statement_article.sql_dao(request, "sqls_word_detail2", "")

    rows = []

    for word_record in all_words_by_title:
        each_word = word_record[0]
        rows.append(each_word)

    cur_word_eng_example = cur_word_eng_example.replace("\\n", "\n").strip()
    cur_word_kor_example = cur_word_kor_example.replace("\\n", "\n").strip()
    cur_word_eng_example2 = cur_word_eng_example2.replace("\\n", "\n").strip()
    cur_word_kor_example2 = cur_word_kor_example2.replace("\\n", "\n").strip()

    value = {
        "wrd_title": wrd_title,
        "wrd_rows":  rows,
        "wrd_word":  cur_word,
        "wrd_tag":   cur_tag,
        "wrd_mean":  cur_mean,
        "wrd_group": cur_group_code,
        "wrd_guess": cur_word_guess,
        "wrd_eng_example": cur_word_eng_example,
        "wrd_kor_example": cur_word_kor_example,
        "wrd_eng_example2": cur_word_eng_example2,
        "wrd_kor_example2": cur_word_kor_example2,
    }

    return render(request, "word_detail.html", value)

@login_required(login_url='/login/')  # 로그인 페이지로 리다이렉션
def living_english(request):
    # 변수 초기화
    new_count = 0
    group_codes = get_group_codes(request)
    selectd_version = request.GET.get("check")
    selectd_chapter = request.GET.get("chapter")
    selectd_status = request.GET.get("status")

    # 신규 chapter 정보 생성
    if selectd_version == "new":
        new_count = make_page_info(request)

    # 조건 chapter 정보 조회, chapter가 빈 값이면 최대 chapter 로 조회
    (
        living_english_titles,
        living_english_comp_titles,
        living_english_title_text,
        audio_name_text,
        living_english_eng_text,
        living_english_kor_text,
        living_english_additional_text,
        living_english_topic_dur_start,
        living_english_topic_dur_end,
    ) = show_current_living_english(request, selectd_chapter, selectd_status)

    values = {
        "group_codes": group_codes,
        "living_english_titles": living_english_titles,
        "living_english_comp_titles" : living_english_comp_titles,
        "living_selectd_chapter"     : selectd_chapter,
        "living_english_title_text"  : living_english_title_text,
        "audio_name_text"            : audio_name_text,
        "living_english_eng_text"    : living_english_eng_text,
        "living_english_kor_text"    : living_english_kor_text,
        "living_english_additional_text": living_english_additional_text,
        "living_english_topic_dur_start": living_english_topic_dur_start,
        "living_english_topic_dur_end"  : living_english_topic_dur_end,
        "living_english_new_count"      : new_count,
    }
    return render(request, "living_english.html", values)

@login_required(login_url='/login/')
def save_wordinfo(request):

    saveWord = request.GET.get("txt_word")
    saveGuessing = request.GET.get("txt_guessing")
    saveDefeng = request.GET.get("txt_defeng")
    saveDefkor = request.GET.get("txt_defkor")
    saveEngExample = request.GET.get("txt_eng_example")
    saveKorExample = request.GET.get("txt_kor_example")
    saveEngExample2 = request.GET.get("txt_eng_example2")
    saveKorExample2 = request.GET.get("txt_kor_example2")

    try:

        rtn_code = sql_statement_article.sql_dao(request, "sqlu_save_wordinfo", "")

        saveGuessing = saveGuessing.replace('"', "").strip()

        saveDefeng = saveDefeng.replace('"', "").strip()
        saveDefkor = saveDefkor.replace('"', "").strip()

        saveEngExample = saveEngExample.replace('"', "").strip()
        saveKorExample = saveKorExample.replace('"', "").strip()
        saveEngExample2 = saveEngExample2.replace('"', "").strip()
        saveKorExample2 = saveKorExample2.replace('"', "").strip()

        # 'saveEngExample' 변수에서 줄바꿈 문자를 변경
        saveEngExample = saveEngExample.replace("\n", "\\n").strip()
        saveKorExample = saveKorExample.replace("\n", "\\n").strip()

        # 'saveEngExample2' 변수에서 줄바꿈 문자를 변경
        saveEngExample2 = saveEngExample2.replace("\n", "\\n").strip()
        saveKorExample2 = saveKorExample2.replace("\n", "\\n").strip()

        current_username = ""

        upd_mean_daily_word_params = [
            saveGuessing,
            saveDefeng,
            saveDefkor,
            saveEngExample,
            saveKorExample,
            saveEngExample2,
            saveKorExample2,
            current_username,
            saveWord,
        ]

        rtn_code = sql_statement_article.sql_dao(request, "sqlu_save_wordinfo2", upd_mean_daily_word_params)

    except Exception as e:
        print("Updating Word Info failed: ", e)

    return JsonResponse({"message": "OK"})
@login_required(login_url='/login/')
def complete_word(request):

    completeWord = request.GET.get("complt_word")

    conn, cursor, current_username = create_connection(request)

    try:
        complete_query1 = " UPDATE processed_words    "
        complete_query1 += "    SET status      = 'D' "
        complete_query1 += "      , init_status = 'B' "
        complete_query1 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
        complete_query1 += " WHERE  user_id = %s "
        complete_query1 += "   AND  word    = %s "
        complete_params1 = (current_username, completeWord,)
        cursor.execute(complete_query1, complete_params1)

        complete_query2  = " UPDATE daily_voca   "
        complete_query2 += "    SET status = 'D' "
        complete_query2 += "      , finish_date = date_format(now(),'%Y-%m-%d %H:%i:%S') "
        complete_query2 += " WHERE  user_id = %s "
        complete_query2 += "   AND  word    = %s "
        complete_params2 = (current_username, completeWord,)

        cursor.execute(complete_query2, complete_params2)

    except Exception as e:
        print("Complete query failed:", e)

    finally:
        close_connection(conn, cursor)

    return JsonResponse({"message": "COMPLETED"})
@login_required(login_url='/login/')
def call_process(request):

    curr_undone_cnt, undone_tot_cnt = sql_statement_article.sql_dao(request, "sqls_call_process", "")

    return JsonResponse(
        {"process_cnt": curr_undone_cnt, "undone_tot_cnt": undone_tot_cnt}
    )
@login_required(login_url='/login/')
def goto_mobile(request):

    srcTitle = request.GET.get("src_title")

    conn, cursor, current_username = create_connection(request)

    try:
        mobile_query  = " UPDATE processed_words    "
        mobile_query += "    SET status      = 'C'  "
        mobile_query += "      , finish_date = null "
        mobile_query += "  WHERE user_id     = %s   "
        mobile_query += "    AND src_title   = %s   "
        mobile_query += "    AND init_status = %s   "
        mobile_params = (current_username, srcTitle, "B")
        cursor.execute(mobile_query, mobile_params)

        mobile_query  = " UPDATE daily_voca  "
        mobile_query += "    SET status      = 'C'  "
        mobile_query += "      , finish_date = null "
        mobile_query += "  WHERE user_id     = %s   "
        mobile_query += "    AND src_title   = %s   "
        mobile_query += "    AND word in ( SELECT word FROM processed_words WHERE user_id = %s AND src_title = %s AND init_status = %s ) "
        mobile_params = (current_username, srcTitle, current_username, srcTitle, "B")
        cursor.execute(mobile_query, mobile_params)

        mobile_query  = " UPDATE process_info       "
        mobile_query += "    SET goto_mobile_cnt    = goto_mobile_cnt + 1 "
        mobile_query += "  WHERE user_id     = %s   "
        mobile_query += "    AND src_title   = %s   "
        mobile_params = (current_username, srcTitle)
        cursor.execute(mobile_query, mobile_params)

    except Exception as e:
        print("mobile update failed:", e)

    finally:
        close_connection(conn, cursor)

    return JsonResponse({"result": "Go to Mobile"})

def do_insert_page_info(request, p_chapter_num, p_title_text, p_audio_name):

    conn, cursor, current_username = create_connection(request)

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
        close_connection(conn, cursor)

@login_required(login_url='/login/')
def complete_chapter(request):
    selectd_chapter = request.GET.get("selectd_chapter")

    # 접속 객체 생성
    conn, cursor, current_username = create_connection(request)

    try:
        complete_query  = " UPDATE tb_chapter_title "
        complete_query += "    SET status         = 'D' "
        complete_query += "      , complete_count = complete_count + 1 "
        complete_query += "      , finish_date    = date_format(now(),'%Y-%m-%d %H:%i:%S') "
        complete_query += " WHERE  user_id        = %s "
        complete_query += "   AND  src_chapter    = %s "
        complete_params = (current_username, selectd_chapter,)
        cursor.execute(complete_query, complete_params)

        max_chapter_num = retrieve_ing_chapter_num(request)
        return JsonResponse({"complete_chapter": max_chapter_num})
    except Exception as e:
        print("Chapter Complete query failed:", e)
        return JsonResponse({"message": "완료 오류 발생."})
    finally:
        close_connection(conn, cursor)

'''
#############################################################
# 함수명 : tb_chapter_title 데이블 완료상태, 날짜 최기화
# 작성일 : 2024.07.20
#############################################################
'''
@login_required(login_url='/login/')
def uncomplete_chapter(request):
    selectd_chapter = sql_statement_article.sql_dao(request, "sqls_uncomplete_chapter", "")
    return JsonResponse({"uncomplete_chapter": selectd_chapter})

@csrf_exempt
@login_required(login_url='/login/')
def save_topic(request):
    if request.method == "POST":
        rtn_code = sql_statement_article.sql_dao(request, "sqliu_save_topic", "")

        if rtn_code == 1:
            return JsonResponse({"message": "생성 완료"})
        elif rtn_code == 2:
            return JsonResponse({"message": "갱신 완료"})
@csrf_exempt
@login_required(login_url='/login/')
def create_word(request):
    if request.method == "POST":
       rtn_code = sql_statement_article.sql_dao(request, "sqli_create_word", "")

       if rtn_code == 1:
          return JsonResponse({"message": "신규단어 추가 완료"})
       elif rtn_code == 2:
          return JsonResponse({"message": "신규단어 추가 오류"})