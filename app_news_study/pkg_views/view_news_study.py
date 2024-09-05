from django.http import JsonResponse
from django.shortcuts import render

from app_news_study.pkg_mdl_common    import mdl_common_news as app_comn_func
from app_news_study.pkg_sql_statement import sql_statement
from proj_common import mdl_common_proj as proj_comn_func

def news_study(request):
    selected_date = request.GET.get("selected_date")

    # tb_news_info_main 테이블에 오늘 날짜의 데이터가 있는지 확인한다.
    check_today_news, today_news_date, max_news_date = app_comn_func.get_recent_news_date(request)

    if selected_date:
       max_news_date = selected_date

    titles, news_dates = sql_statement.sql_dao(request, "sqls_news_info_titles", max_news_date)

    values = {
       "titles": titles,
       "news_dates": news_dates,
       "selected_date": today_news_date
    }

    return render(request, "news_study.html", values)

def news_info_eng(request):
    selected_keyno = request.GET.get("selected_keyno")

    news_info_engs = sql_statement.sql_dao(request, "sqls_selected_news_info_eng", selected_keyno)

    rows = []
    rows_cnt = 0

    cur_no = 0
    for news_info_eng in news_info_engs:
        keyitem  = news_info_eng['keyitem']
        groupno  = news_info_eng['groupno']
        newstype = news_info_eng['newstype']
        keyno    = news_info_eng['keyno']

        rows.append([keyitem, groupno, keyno])
        if newstype == "ENG":
           rows_cnt += 1

    # 처리 성공 응답
    return JsonResponse({"rows": rows, "rows_cnt": rows_cnt})

def news_info_inf(request):
    p_keyno = request.GET.get("keyno")
    p_groupno = request.GET.get("groupno")

    values = {
        "keyno": p_keyno,
        "groupno": p_groupno,
    }

    news_info_infs = sql_statement.sql_dao(request, "sqls_news_info_inf", values)

    rows = []

    for news_info_inf in news_info_infs:
        keyitem_inf = news_info_inf['keyitem']

        rows.append([keyitem_inf])

    # 처리 성공 응답
    return JsonResponse({"rows": rows})

def save_wordinfo(request):
    print("save_wordinfo")
    return JsonResponse({"message": "OK"})

def complete_word(request):
    print("complete_word")
    return JsonResponse({"message": "COMPLETED"})