from django.http import JsonResponse
from django.shortcuts import render

from app_news_study.app_mdl_common import common as app_comn_func
from app_news_study.app_sql_statement import sql_statement
from proj_common import common as proj_comn_func

def news_study(request):

    selected_date = request.GET.get("selected_date")

    # tb_news_info_main 테이블에 오늘 날짜의 데이터가 있는지 확인한다.
    check_today_news, today_news_date, max_news_date = app_comn_func.get_recent_news_date(request)

    if selected_date:
       today_news_date = selected_date
       check_today_news = True

    if check_today_news:
       list_param = {
           "today_news_date": today_news_date,
           "max_news_date": max_news_date
       }
       titles, news_dates = sql_statement.sql_dao(request, "sqls_news_info_titles", list_param)

       values = {
           "titles": titles,
           "news_dates": news_dates,
           "selected_date": today_news_date
       }

       return render(request, "news_study.html", values)

    url = "https://koreajoongangdaily.joins.com/section/currentIssues"
    # 공통 함수의 webdriver를 사용해서 파싱한다.
    html, soup = proj_comn_func.url_parsing_with_webdriver(url, "1")
    # print(soup.prettify())
    # class 명이 정확히 swiper-slide 하나 인것만 찾는다.
    # table = soup.find_all('div', {'class': 'swiper-slide'})
    table = soup.find_all('div', class_='mid-article3')

    '''
    ##################################################
    # 기사 URL을 읽기
    # 신문 기사 URL 30개를 읽어서 DataFrame 에 담는다.
    ################################################## '''
    news_urls = []
    news_order = 0
    ii = 0

    for tbl in table:
        for a_tag in tbl.find_all('a'):
            link = a_tag.get('href')
            if link:  # href가 존재하는지 확인
                each_items = link.split("/")
                if len(each_items) > 6:  # 필요한 모든 세그먼트가 있는지 확인
                    news_max_num = sql_statement.sql_dao(request, "sqls_check_news_info", each_items[-1])

                    if news_max_num: continue

                    list_keyitems = app_comn_func.get_url_keyitems(link)

                    news_info = {
                        'NEWSORDER': 0,
                        'URL': link,
                        'TITLE': each_items[-2].replace("-", " "),
                        'DATE': each_items[4],
                        'DEPT': each_items[5],
                        'SECTION': each_items[6],
                        'KEYNO': each_items[-1],
                        'KEYITEM': list_keyitems
                    }

                    bl_exit = False
                    for each_key_item in list_keyitems:
                        if len(each_key_item['Text']) > 800:
                           bl_exit = True
                           break
                    try:
                        if not bl_exit and len(list_keyitems) > 10:
                            news_order += 1
                            news_info["NEWSORDER"] = news_order
                            # 뉴스 사이트 문장별 상세 정보 저장
                            app_comn_func.save_to_news_info_database(request, news_info)
                            # 뉴스 사이트 일반 정보 저장
                            sql_statement.sql_dao(request, "sqli_main_news_info", news_info)
                            # news_urls.append(news_info)
                    except Exception as e:
                        print(f"알 수 없는 오류가 발생했습니다: {e}")

    # 저장처리가 완료된 이후에 불필요한 데이터 삭제
    sql_statement.sql_dao(request, "sqld_invalid_news_info", "")

    max_news_date

    list_param = {
        "today_news_date": today_news_date,
        "max_news_date": max_news_date
    }

    titles, news_dates = sql_statement.sql_dao(request, "sqls_news_info_titles", list_param)

    values = {
        "titles": titles,
        "news_dates": news_dates,
        "selected_date": today_news_date
    }

    print("response completed2")

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