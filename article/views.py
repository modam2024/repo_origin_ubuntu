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

from proj_sql_mapping import create_connection, close_connection
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement
from proj_sql_mapping import mdl_mapping_sql_article as sql_statement_article
from proj_common import mdl_common_proj as proj_comn_func
from proj_common import mdl_morph_words_proj as morph_new_words

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

# 단어 추출 첫화면 조회, group_code 셋팅
@login_required(login_url='/login/')
def main_view(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_view")

    group_codes = proj_comn_func.get_group_codes(request)

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
        html, soup = proj_comn_func.url_parsing_with_webdriver(url, "1")

        # 단어의 의미 추출
        meanings = []
        mean_list = soup.find(class_=["mean_list", "mean_list_multi", "mean_list multi", "word_class"])

        # mean_list가 None이 아니면 실행될 코드
        if mean_list is not None:
            print("meaning of {} is completed(1)".format(en_word))
        else:
            html, soup = proj_comn_func.url_parsing_with_webdriver(url, "2")
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

@login_required(login_url='/login/')
def main_word_check(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_word_check")

    source_url     = request.GET.get("source_url")
    source_title   = request.GET.get("source_title")
    source_status  = request.GET.get("source_status")
    source_type    = request.GET.get("source_type")
    source_gubun   = request.GET.get("gubun")
    test_page_date = request.GET.get("test_page_date")
    selected_date  = request.GET.get("selected_date")

    existing_words = sql_statement_article.sql_dao(request, "sqls_main_word_check", "")

    rows = []
    rows_cnt = 0

    for record in existing_words:
        cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date = record
        rows.append([cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date])
        rows_cnt += 1

    existing_titles = sql_statement_article.sql_dao(request, "sqls_main_word_check2", "")

    titles = [(url, title) for url, title in existing_titles]
    group_codes = proj_comn_func.get_group_codes(request)

    values = {
        "rows": rows,
        "titles": titles,
        "rows_cnt": rows_cnt,
        "source_url": source_url,
        "source_title": source_title,
        "source_status": source_status,
        "source_type": source_type,
        "group_codes": group_codes,
        "source_gubun": source_gubun,
        "test_page_date": test_page_date,
        "selected_date": selected_date,
    }

    return render(request, "word_check.html", values)

@login_required(login_url='/login/')
def main_word_table(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_word_table")

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
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "delete_content")

    rows_cnt = sql_statement_article.sql_dao(request, "sqld_delete_content", "")

    # 처리 성공 응답
    return JsonResponse({"rows_cnt": rows_cnt})

@csrf_exempt
@login_required(login_url='/login/')
def confirm_word_check(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "confirm_word_check")

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
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "word_detail")

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

@login_required(login_url='/login/')
def save_wordinfo(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "save_wordinfo")

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
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "complete_word")

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
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "call_process")

    curr_undone_cnt, undone_tot_cnt = sql_statement_article.sql_dao(request, "sqls_call_process", "")

    return JsonResponse(
        {"process_cnt": curr_undone_cnt, "undone_tot_cnt": undone_tot_cnt}
    )

# 단어검증 화면 초기화 버튼 클릭시
@login_required(login_url='/login/')
def goto_mobile(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "goto_mobile")

    srcTitle = request.GET.get("src_title")

    conn, cursor, current_username = create_connection(request)

    try:
        mobile_query  = " UPDATE processed_words    "
        mobile_query += "    SET status      = 'C'  "
        mobile_query += "      , init_status = 'A'  "
        mobile_query += "      , start_date  = null "
        mobile_query += "      , finish_date = null "
        mobile_query += "  WHERE user_id     = %s   "
        mobile_query += "    AND src_title   = %s   "
        mobile_params = (current_username, srcTitle)
        cursor.execute(mobile_query, mobile_params)

        mobile_query  = " UPDATE daily_voca  "
        mobile_query += "    SET status         = 'C'  "
        mobile_query += "      , start_date     = null "
        mobile_query += "      , priority_date  = null "
        mobile_query += "      , finish_date    = null "
        mobile_query += "  WHERE user_id     = %s   "
        mobile_query += "    AND src_title   = %s   "
        mobile_query += "    AND word in ( SELECT word FROM processed_words WHERE user_id = %s AND src_title = %s ) "
        mobile_params = (current_username, srcTitle, current_username, srcTitle)
        cursor.execute(mobile_query, mobile_params)

        # process_info 삭제
        rtn_code = sql_statement_article.sql_dao(request, "sqld_confirm_word_check", srcTitle)

    except Exception as e:
        print("mobile update failed:", e)

    finally:
        close_connection(conn, cursor)

    return JsonResponse({"result": "Go to Mobile"})

@csrf_exempt
@login_required(login_url='/login/')
def create_word(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "create_word")

    if request.method == "POST":
       rtn_code = sql_statement_article.sql_dao(request, "sqli_create_word", "")

       if rtn_code == 1:
          return JsonResponse({"message": "신규단어 추가 완료"})
       elif rtn_code == 2:
          return JsonResponse({"message": "신규단어 추가 오류"})