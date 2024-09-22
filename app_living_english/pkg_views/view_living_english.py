from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import app_living_english.pkg_sql_statement.sql_statement as sql_statement
from app_living_english.pkg_mdl_common import mdl_common_living as app_com_func
from proj_common import mdl_common_proj as proj_comn_func
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement


# 2024.04.28 : spacy 포함
@login_required(login_url='/login/')  # 로그인 페이지로 리다이렉션
def living_english(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "living_english")

    # 변수 초기화
    new_count = 0
    group_codes = proj_comn_func.get_group_codes(request)
    selectd_version = request.GET.get("check")
    selectd_chapter = request.GET.get("chapter")
    selectd_status = request.GET.get("status")

    # 신규 chapter 정보 생성
    if selectd_version == "new":
        new_count = app_com_func.make_page_info(request)

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
    ) = app_com_func.show_current_living_english(request, selectd_chapter, selectd_status)

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

'''
#############################################################
# FUNC ID : save_topic
# 함수명 : 생활회화 데이블 전체 데이터 저장 / 업데이트
# 작성일 : 2024.07.20
#############################################################  '''
@csrf_exempt
@login_required(login_url='/login/')
def save_topic(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "save_topic")

    if request.method == "POST":
        rtn_code = sql_statement.sql_dao(request, "sqliu_save_topic", "")

        if rtn_code == 1:
            return JsonResponse({"message": "생성 완료"})
        elif rtn_code == 2:
            return JsonResponse({"message": "갱신 완료"})

'''
#############################################################
# FUNC ID   : complete_chapter
# CALLER ID : living_english.js
# 함수명     : tb_chapter_title 데이블 완료상태, 날짜 저장
# 작성일     : 2024.07.20
#############################################################
'''
@login_required(login_url='/login/')
def complete_chapter(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "complete_chapter")

    selectd_chapter = request.GET.get("selectd_chapter")

    try:
        sql_statement.sql_dao(request, "sqlu_update_complete_chapter", selectd_chapter)

        max_chapter_num = proj_sql_statement.sql_dao(request, "sqls_retrieve_ing_chapter_num", selectd_chapter)
        return JsonResponse({"complete_next_chapter": max_chapter_num})
    except Exception as e:
        print("Chapter Complete query failed:", e)
        return JsonResponse({"message": "완료 오류 발생."})

'''
#############################################################
# FUNC ID   : uncomplete_chapter
# CALLER ID : living_english.js
# 함수명     : tb_chapter_title 데이블 완료상태, 날짜 최기화
# 작성일     : 2024.07.20
############################################################# '''
@login_required(login_url='/login/')
def uncomplete_chapter(request):
    # ## 공통 ## 작업 히스토리 저장
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "uncomplete_chapter")

    selectd_chapter = sql_statement.sql_dao(request, "sqls_uncomplete_chapter", "")

    return JsonResponse({"uncomplete_chapter": selectd_chapter})