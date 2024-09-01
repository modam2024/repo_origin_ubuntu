from django.contrib.auth.decorators import login_required
# 2024.04.28 : spacy 포함
from django.shortcuts import render

from app_living_english.pkg_mdl_common import mdl_common_lven as app_com_func
from proj_common import mdl_common_proj as proj_comn_func

@login_required(login_url='/login/')  # 로그인 페이지로 리다이렉션
def living_english(request):
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