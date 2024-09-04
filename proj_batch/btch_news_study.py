from django.http import HttpResponse

from app_news_study.pkg_mdl_common import mdl_common_nwst as app_comn_func
from app_news_study.pkg_sql_statement import sql_statement
from proj_common import mdl_common_proj as proj_comn_func


def batch_news_study(request):
    selected_date = request.GET.get("selected_date")

    # tb_news_info_main 테이블에 오늘 날짜의 데이터가 있는지 확인한다.
    check_today_news, today_news_date, max_news_date = app_comn_func.get_recent_news_date(request)

    if check_today_news:
       list_param = {
           "today_news_date": today_news_date,
           "max_news_date": max_news_date
       }
       titles, news_dates = sql_statement.sql_dao(request, "sqls_news_info_titles", list_param)

       return HttpResponse("FROM DB")

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

    res_value = sql_statement.sql_dao(request, "sqli_batch_news_study_hist", news_info)

    return HttpResponse("CREATE NEWS FINISH")
