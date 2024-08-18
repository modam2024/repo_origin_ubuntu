import re

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mdl_common import common as comn_func
from mdl_sql_mapping import create_connection, close_connection
from mdl_sql_mapping import sql_mapping as sql_statement

'''
#######################################################
# Entery Point
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################
'''
@login_required(login_url='/login/')
def test_english(request):
    selectd_version = request.GET.get("check")
    selectd_chapter = request.GET.get("chapter")
    selectd_status  = request.GET.get("status")

    conn, cursor, current_username = create_connection(request)

    if selectd_version == "max":
       # request.GET을 mutable로 만들기
       request.GET   = request.GET.copy()
       tmp_selectd_wdate = sql_statement.sql_dao(request, "sqls_test_info_if_first", "")
       # 새로운 값 추가
       request.GET['wdate'] = tmp_selectd_wdate

    # 변수 초기화
    selectd_wdate   = request.GET.get("wdate")

    df_page_info = pd.DataFrame()
    df_test_page_content = pd.DataFrame()
    df_page_info, df_test_page_content = test_page_info(request)
    dict_test_page_content = df_test_page_content.to_dict('records')
    dict_page_info = df_page_info.to_dict('records')

    values = {
               'test_page_content': dict_test_page_content,
               'test_page_info'   : dict_page_info,
               'select_tag_info'  : "",
             }

    try:
        for each_test_page_content in dict_test_page_content:
            v_trgt_order_no    = dict_page_info[0]['trgt_order_no']
            v_trgt_page_date   = dict_page_info[0]['trgt_page_date']
            v_prve_page_date   = dict_page_info[0]['prve_page_date']
            v_next_page_date   = dict_page_info[0]['next_page_date']
            v_last_page_flag   = dict_page_info[0]['last_page_flag']

            v_question_no      = each_test_page_content['question_no']
            v_question_content = each_test_page_content['question_content']
            v_choice_a = each_test_page_content['choice_a']
            v_choice_b = each_test_page_content['choice_b']
            v_choice_c = each_test_page_content['choice_c']
            v_choice_d = each_test_page_content['choice_d']

            v_test_page_content_cnt = sql_statement.sql_dao(request, "sqls_test_page_content_cnt", v_trgt_page_date)

            if v_test_page_content_cnt < 3:
               insert_query  = " INSERT INTO tb_test_page_info "
               insert_query += " (user_id, trgt_order_no, trgt_page_date, prve_page_date, next_page_date, last_page_flag,  "
               insert_query += " question_no, question_content, choice_a, choice_b, choice_c, choice_d ) "
               insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
               insert_params = ( current_username, v_trgt_order_no, v_trgt_page_date, v_prve_page_date, v_next_page_date, v_last_page_flag,
                                 v_question_no, v_question_content, v_choice_a, v_choice_b, v_choice_c, v_choice_d, )

               cursor.execute(insert_query, insert_params)

    except Exception as e:
        print("test insert failed:", e)

    finally:
        close_connection(conn, cursor)

    existing_pagedates = sql_statement.sql_dao(request, "sqls_test_page_result_info", "")

    # dict_page_info 리스트 초기화
    lst_page_date_info = []

    for rec_page_date in existing_pagedates:
        trgt_order_no, trgt_page_date = rec_page_date

        # 새 딕셔너리 생성
        dict_page_date_info = {
            "order_no"  : trgt_order_no,
            "page_date" : trgt_page_date,
            "test_frq"  : ""
        }

        dict_page_date_info["test_frq"] = sql_statement.sql_dao(request, "sqls_max_frq_test_page", trgt_page_date)

        # 리스트에 딕셔너리 추가
        lst_page_date_info.append(dict_page_date_info)

    # 값을 딕셔너리에 할당할 때는 키를 사용하여 접근
    values['select_tag_info'] = lst_page_date_info

    return render(request, "test_english.html", values)

'''
#######################################################
# 페이지 호출시 데이터 수집 및 전처리하는 함수
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################
'''
def test_page_info(request):
    str_max_sdate = request.GET.get("wdate")

    df_page_info = pd.DataFrame()
    df_questions = pd.DataFrame()
    df_page_info = sql_statement.sql_dao(request, "sqls_test_info_by_date", "")
    df_questions = sql_statement.sql_dao(request, "sqls_test_question_info_by_date", "")

    if df_page_info.empty:
        try:
            url = "https://free.ybmclass.com/free/toeic/toeic_5min_view.asp?wdate={}&page=1".format(
                str_max_sdate
            )

            # 공통 함수의 webdriver를 사용해서 파싱한다.
            html, soup = comn_func.url_parsing_with_webdriver(url, "1")

            dic_content = []
            df_content = []

            '''
            #######################################################
            # 작성일 : 2024.06.20
            # YBM 실전 5분 토익 페이지 정보 생성
            #######################################################
            '''
            v_now_order_no   = ""
            v_prve_page_date = ""
            v_next_page_date = ""
            v_now_page_date  = ""
            v_last_page_flag = "N"

            v_ttitle_view = soup.find(class_=["title-view"])
            if v_ttitle_view:
                for v_prve_next_page_info_tag in v_ttitle_view.find_all("a"):
                    a_href = v_prve_next_page_info_tag.get('href')
                    date_pattern = r'\d{4}-\d{2}-\d{2}'
                    try:
                        page_date = re.search(date_pattern, a_href).group()
                        list_class = v_prve_next_page_info_tag.get('class')
                        if list_class[1] == "btn-prve":
                            v_prve_page_date =  page_date
                        elif list_class[1] == "btn-next":
                            v_next_page_date =  page_date
                    except Exception as e:
                        if list_class[1] == "btn-next":
                            v_next_page_date =  str_max_sdate

            v_all_input = soup.find_all("input")
            for each_input_tag in v_all_input:
                input_name = each_input_tag.get('name')
                if input_name == "toeic_id":
                    v_now_order_no = each_input_tag.get('value')
                elif input_name == "wdate":
                    v_now_page_date = each_input_tag.get('value')

            if not v_next_page_date:
                v_next_page_date = v_now_page_date
                v_last_page_flag = "Y"

            # 각 항목을 딕셔너리로 df_content 리스트에 추가
            dic_content.append({
                'trgt_page_date': v_now_page_date,
                'trgt_order_no' : v_now_order_no,
                'prve_page_date': v_prve_page_date,
                'next_page_date': v_next_page_date,
                'last_page_flag': v_last_page_flag,
            })

            # df_content를 DataFrame으로 변환
            df_page_info = pd.DataFrame(dic_content)

            '''
            #######################################################
            # 작성일 : 2024.06.20
            # YBM 실전 5분 토익 문제 페이지 수집-전치리 데이터 생성
            #######################################################
            '''
            v_toeic_test_box = soup.find(class_=["toeic-test-box"])

            if v_toeic_test_box:
                for dt_content in v_toeic_test_box.find_all("dt"):
                    dt_v_num = dt_content.find(class_=["num"])
                    df_num = "question"+dt_v_num.get_text(strip=True)
                    dt_v_num.decompose() # dt_v_num 요소 제거 후 남은 텍스트 가져오기
                    df_question = dt_content.get_text()

                    # 문자열 내의 모든 줄바꿈 제거
                    df_question = df_question.replace('\n', ' ')
                    df_question = df_question.replace('  ', ' ')

                    # 각 항목을 딕셔너리로 df_content 리스트에 추가
                    df_content.append({
                        'question_no': df_num,
                        'question_content': df_question,
                        'choice_a': '',
                        'choice_b': '',
                        'choice_c': '',
                        'choice_d': '',
                    })

                # df_content를 DataFrame으로 변환
                df = pd.DataFrame(df_content)

                for dd_content in v_toeic_test_box.find_all("dd"):
                    dd_spans = dd_content.find_all("span")
                    for dd_span in dd_spans:
                        v_span = dd_span.get_text()

                        # span 내부에 input 태그 찾기
                        input_tag = dd_span.find('input')
                        if input_tag:
                            # input 태그의 name 속성 출력
                            input_name = input_tag.get('name')
                            if input_name in df['question_no'].values:
                                # DataFrame에서 해당 question_no의 index 찾기
                                index = df.index[df['question_no'] == input_name].tolist()[0]
                                # 해당하는 선택지를 찾아 값을 저장
                                if df.at[index, 'choice_a'] == '':
                                    df.at[index, 'choice_a'] = v_span
                                elif df.at[index, 'choice_b'] == '':
                                    df.at[index, 'choice_b'] = v_span
                                elif df.at[index, 'choice_c'] == '':
                                    df.at[index, 'choice_c'] = v_span
                                elif df.at[index, 'choice_d'] == '':
                                    df.at[index, 'choice_d'] = v_span

                df_questions = df

        except Exception as e:
            print("Finding web-page failed: ", e)
    else:
        print("Geted data from database")

    return df_page_info, df_questions  # while 수행 완료 후 return 함