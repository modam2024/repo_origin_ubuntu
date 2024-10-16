import json

import mysql.connector
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# 어플리케이션 기반 함수 및 쿼리 라이브러리
import app_living_english.pkg_sql_statement.sql_statement as sql_statement_living
import app_word_work.pkg_sql_statement.sql_statement as sql_statement
# 프로젝트 기반 함수 및 쿼리 라이브러리
from proj_common import mdl_common_proj as proj_comn_func
from proj_sql_mapping import create_connection, close_connection
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement


# 2024.09.23 : app_word_work 로 어플리케이션 분리
@login_required(login_url='/login/')
def main_word_check(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_word_check")

    source_url     = request.GET.get("source_url")
    source_title   = request.GET.get("source_title")
    source_status  = request.GET.get("source_status")
    source_type    = request.GET.get("source_type")
    sel_level      = request.GET.get("sel_level")
    source_gubun   = request.GET.get("gubun")
    test_page_date = request.GET.get("test_page_date")
    selected_date  = request.GET.get("selected_date")
    selected_chapter  = request.GET.get("selected_chapter")

    # existing_words = sql_statement.sql_dao(request, "sqls_main_word_check", "")
    #
    # rows = []
    # rows_cnt = 0
    #
    # for record in existing_words:
    #     cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date = record
    #     rows.append([cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date])
    #     rows_cnt += 1

    existing_titles = sql_statement.sql_dao(request, "sqls_main_word_check2", "")

    titles = [(url, title) for url, title in existing_titles]
    group_codes = proj_comn_func.get_group_codes(request)

    if source_gubun == "living" and not selected_chapter:
        selected_chapter = sql_statement_living.sql_dao(request, "sqls_existing_max_chapter_num", "")

    values = {
        # "rows": rows,
        "titles": titles,
        # "rows_cnt": rows_cnt,
        "source_url": source_url,
        "source_title": source_title,
        "source_status": source_status,
        "source_type": source_type,
        "sel_level": sel_level,
        "group_codes": group_codes,
        "source_gubun": source_gubun,
        "test_page_date": test_page_date,
        "selected_date" : selected_date,
        "selected_chapter": selected_chapter,
    }

    return render(request, "word_check.html", values)

@csrf_exempt
@login_required(login_url='/login/')
def main_word_table(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_word_table")

    source_title  = request.GET.get("source_title")
    source_status = request.GET.get("source_status")
    source_type   = request.GET.get("source_type")
    sel_level     = request.GET.get("sel_level")

    existing_words = sql_statement.sql_dao(request, "sqls_main_word_table", "")

    rows = []
    rows_cnt = 0

    cur_no = 0
    for record in existing_words:
        cur_word, cur_mean_en, cur_tag_text, cur_create_date, level = record
        cur_no = cur_no + 1
        rows.append([cur_no, cur_word, cur_mean_en, cur_tag_text, cur_create_date, level])
        rows_cnt += 1

    step_status = sql_statement.sql_dao(request, "sqls_process_info_step_status", source_title)

    if step_status == "A" or step_status == "B" or step_status == "C":
       step_status = "A"

    # 처리 성공 응답
    return JsonResponse({"rows": rows, "rows_cnt": rows_cnt, "step_status": step_status})

@csrf_exempt
@login_required(login_url='/login/')
def confirm_word_check(request):
    # ## 공통 ## 작업 히스토리 저장
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
            checked_words   = data.get("words")
            unchecked_words = data.get("unchckd_words")
            selected_status = data.get("selected_status")
            selected_title  = data.get("selected_title")
            # selected_step   = data.get("selected_step")

            # process_info 삭제
            rtn_code = sql_statement.sql_dao(request, "sqld_confirm_word_check", selected_title)

            # process_info 생성
            rtn_code = sql_statement.sql_dao(request, "sqli_confirm_word_check", "")

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

                        upd_params1 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )

                        rtn_msg = sql_statement.sql_dao(request, "sqlu_processed_words_init_status_for_a", upd_params1)

                        upd_params2 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )

                        rtn_msg = sql_statement.sql_dao(request, "sqlu_processed_words_status_for_c", upd_params2)

                        update_word_count += 1

                        upd_params3 = (
                            done_row_num,
                            current_username,
                            checked_word,
                        )

                        rtn_msg = sql_statement.sql_dao(request, "sqlu_daily_voca_status_for_all", upd_params3)

                    except Exception as e:
                        print("Update query failed:", e)

            # Unchecked 된 경우
            if unchecked_words:
                for unchecked_word in unchecked_words:
                    try:
                        mean_kr_text = get_mean_kr_from_naver_dic(unchecked_word)

                        # mean_kr_text가 None 또는 빈 문자열일 경우 '*N'으로 설정
                        if not mean_kr_text:
                            mean_kr_text = "*N"

                        undone_row_num = undone_row_num + 1

                        upd_mean_params = (
                            undone_row_num,
                            mean_kr_text,
                            current_username,
                            unchecked_word,
                        )

                        rtn_msg = sql_statement.sql_dao(request, "sqlu_processed_words_status_to_c_for_word", upd_mean_params)

                        proc_params = (
                            unchecked_words_count,
                            checked_words_count,
                            current_username,
                            selected_title,
                        )

                        rtn_msg = sql_statement.sql_dao(request, "sqlu_process_info_counts_for_title", proc_params)

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

@csrf_exempt
@login_required(login_url='/login/')
def word_detail(request):
    # ## 공통 ## 작업 히스토리 저장
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

    existing_words = sql_statement.sql_dao(request, "sqls_word_detail", "")

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
    all_words_by_title = sql_statement.sql_dao(request, "sqls_word_detail2", "")

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
    # ## 공통 ## 작업 히스토리 저장
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
        rtn_code = sql_statement.sql_dao(request, "sqlu_save_wordinfo", "")

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

        rtn_code = sql_statement.sql_dao(request, "sqlu_save_wordinfo2", upd_mean_daily_word_params)

    except Exception as e:
        print("Updating Word Info failed: ", e)

    return JsonResponse({"message": "OK"})

@csrf_exempt
@login_required(login_url='/login/')
def complete_word(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "complete_word")

    completeWord = request.GET.get("complt_word")

    sql_statement.sql_dao(request, "sqlu_processed_words_status", completeWord)
    sql_statement.sql_dao(request, "sqlu_daily_voca_status",      completeWord)

    return JsonResponse({"message": "COMPLETED"})

@csrf_exempt
@login_required(login_url='/login/')
def change_wordlevel(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "change_wordlevel")

    data = json.loads(request.body)
    checked_words = data.get("words")

    sql_statement.sql_dao(request, "sqluu_processed_words_daily_voca_level", checked_words)

    return JsonResponse({"message": "COMPLETED LEVEL CHANGE"})

@login_required(login_url='/login/')
def call_process(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "call_process")

    curr_undone_cnt, undone_tot_cnt = sql_statement.sql_dao(request, "sqls_call_process", "")

    return JsonResponse(
        {"process_cnt": curr_undone_cnt, "undone_tot_cnt": undone_tot_cnt}
    )

def get_mean_kr_from_naver_dic(en_word):
    try:
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
            meaning = meaning.replace("(=)", "").strip()
            meaning = meaning.replace("(→)", "").strip()
            meaning = meaning.replace("(↔)", "").strip()
            meaning_kr += meaning + "\n"

    except Exception as e:
        meaning_kr = ""
        print("Finding meaning_kr failed - ( {} ): ".format(en_word), e)

    return meaning_kr

@login_required(login_url='/login/')
def delete_content(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "delete_content")

    rows_cnt = sql_statement.sql_dao(request, "sqld_delete_content", "")

    # 처리 성공 응답
    return JsonResponse({"rows_cnt": rows_cnt})

# 초기화 버튼 클릭시 (단어검증)
@login_required(login_url='/login/')
def fn_goto_init(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "fn_goto_init")

    srcTitle = request.GET.get("src_title")

    sql_statement.sql_dao(request, "sqlu_processed_words_status2", srcTitle)
    sql_statement.sql_dao(request, "sqlu_daily_voca_status2", srcTitle)

    # process_info 삭제
    rtn_code = sql_statement.sql_dao(request, "sqld_confirm_word_check", srcTitle)

    return JsonResponse({"result": "Go to Init"})

@csrf_exempt
@login_required(login_url='/login/')
def create_word(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "create_word")

    if request.method == "POST":
       data     = json.loads(request.body)
       strGrpCd = data.get("wrd_grpcd")
       strWord  = data.get("wrd_word")

       if strGrpCd == "ALL":
          strGrpCd = "ETC"

       dic_words_info = {
            "word_insert_count": 1,
            "lemma_word" : strWord,
            'tag': "",
            'tag_text': "",
            "source_url": "http://modameng.com:8000/app_word_work/main-wordcheck/?source_url=&source_title=&source_type=ETC&source_status=C",
            "source_type": strGrpCd,
            "source_title": "create new words",
            "mean_en_text": "",
       }
       rtn = proj_sql_statement.sql_dao(request, "sqlii_processed_words", dic_words_info)
       if "sqlii_processed_words" in rtn:
           proj_sql_statement.sql_dao(request, "sqluu_cond_processed_words", dic_words_info)
           return JsonResponse({"message": "신규단어 업데이트 완료"})
       else:
           return JsonResponse({"message": "신규단어 추가 완료"})