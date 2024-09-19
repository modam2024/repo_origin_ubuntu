import re

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

import app_test_timer.pkg_sql_statement as app_con
import app_test_timer.pkg_sql_statement.sql_statement as sql_statement
from proj_common import mdl_common_proj as proj_comn_func
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement

'''
#######################################################
# Entery Point
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################
'''
@login_required(login_url='/login/')
def test_english(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "test_english")

    select_page_date  = request.GET.get("wdate")

    conn, cursor, current_username = app_con.create_connection(request)

    selectd_wdate = sql_statement.sql_dao(request, "sqls_part5_test_page_max_date", "")

    if select_page_date:
       selectd_wdate = select_page_date

    df_page_info, df_test_page_content = test_page_info(request, selectd_wdate)
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

            test_values = {
                'trgt_order_no'   : v_trgt_order_no,
                'trgt_page_date'  : v_trgt_page_date,
                'prve_page_date'  : v_prve_page_date,
                'next_page_date'  : v_next_page_date,
                'last_page_flag'  : v_last_page_flag,
                'question_no'     : v_question_no,
                'question_content': v_question_content,
                'choice_a': v_choice_a,
                'choice_b': v_choice_b,
                'choice_c': v_choice_c,
                'choice_d': v_choice_d,
            }

            res_value = sql_statement.sql_dao(request, "sqli_test_page_content_create", test_values)

            if res_value == 1:
               break

    except Exception as e:
        print("test insert failed:", e)

    finally:
        app_con.close_connection(conn, cursor)

    existing_pagedates = sql_statement.sql_dao(request, "sqls_test_page_result_info", "")

    # dict_page_info 리스트 초기화
    lst_page_date_info   = []
    lst_test_time        = []
    lst_classified_words = []

    for rec_page_date in existing_pagedates:
        trgt_order_no, trgt_page_date = rec_page_date

        # 새 딕셔너리 생성
        dict_page_date_info = {
            "order_no"  : trgt_order_no,
            "page_date" : trgt_page_date,
            "test_frq"  : "",
        }

        dict_page_date_info["test_frq"]   = sql_statement.sql_dao(request, "sqls_max_frq_test_page", trgt_page_date)

        # 리스트에 딕셔너리 추가
        lst_page_date_info.append(dict_page_date_info)

    v_test_time, sum_test_time, remaining_time, crrct_res_ratio = sql_statement.sql_dao(request, "sqls_test_times", selectd_wdate)

    lst_test_time.append(v_test_time)

    # 값을 딕셔너리에 할당할 때는 키를 사용하여 접근
    values['select_tag_info'] = lst_page_date_info
    values['lst_test_time']   = lst_test_time
    values['sum_test_time']   = sum_test_time
    values['remaining_time']  = remaining_time
    values['crrct_res_ratio'] = crrct_res_ratio

    # 어휘분석의 결과 리스트
    v_classified_words = sql_statement.sql_dao(request, "sqls_classified_words", selectd_wdate)
    lst_classified_words.append(v_classified_words)
    values['lst_classified_words']   = lst_classified_words

    return render(request, "test_english.html", values)

'''
#######################################################
# 토익 파트 5 테스트 결과 저장
# 작성일 : 2024.06.20
# 토익 파트 5 테스트 결과 저장
#######################################################
'''
@login_required(login_url='/login/')
def test_result(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "test_result")

    df_page_info, df_feedback_page_content = feedback_test_page_info(request)
    dict_feedback_page_content = df_feedback_page_content.to_dict('records')
    dict_page_info = df_page_info.to_dict('records')

    values = {
               'feedback_page_content': dict_feedback_page_content,
               'feedback_page_info': dict_page_info,
               'select_tag_info': "",
             }

    try:
        v_trgt_order_no = dict_page_info[0]['trgt_order_no']
        v_trgt_page_date = dict_page_info[0]['trgt_page_date']

        v_test_no = sql_statement.sql_dao(request, "sqls_max_frq_test_page", v_trgt_page_date)

        int_test_no = int(v_test_no) + 1

        # tb_part5_feedback_page 와 tb_part5_feedback_page_statistic 에는 마지막 결과만 남기기 위해서 먼저 삭제한다.
        if int_test_no > 0:
            feedback_page_value = {
                'trgt_order_no' : v_trgt_order_no,
                'trgt_page_date': v_trgt_page_date,
            }
            res_sql_delete = sql_statement.sql_dao(request, "sqld_feedback_page_content", feedback_page_value)

        statistic_value = {
            'trgt_order_no'  : "",
            'trgt_page_date' : "",
        }

        for each_feedback_page_content in dict_feedback_page_content:
            each_feedback_page_content['test_no']         = int_test_no
            each_feedback_page_content['trgt_order_no']   = v_trgt_order_no
            each_feedback_page_content['trgt_page_date']  = v_trgt_page_date

            statistic_value['trgt_order_no']   = v_trgt_order_no
            statistic_value['trgt_page_date']  = v_trgt_page_date

            res_sql_insert = sql_statement.sql_dao(request, "sqli_feedback_page_content", each_feedback_page_content)

        res_sql_statistc = sql_statement.sql_dao(request, "sqli_feedback_page_statistic", statistic_value)

    except Exception as e:
        print("feedback & test_result content creation failed:", e)

    finally:
        print("test_result completed")

    return JsonResponse(
        {"res": "OK"}
    )

'''
##############################################################
# 페이지 호출시 데이터 수집 및 전처리하는 함수
# 작성일 : 2024.06.20
# 수정일 : 2024.09.04
# 브라우져에서 호출하면 실행되는 main function
# sqls_test_info_if_first 안의 로직으로 다음일자를 새로 가져왔다면 
# 디비에 해당 값이 없기 때문에 기존에는 다시 웹크롤링을 했지만, 
# 웹크롤링은 배치프로그램에서 수행하기 때문에 본 함수에서 제거했다.  
# 그러므로 'p_max_sdate' 의 날짜는 현재 디비에 있는 현재일자여야 한다.
##############################################################
'''
def test_page_info(request, p_max_sdate):
    str_max_sdate = p_max_sdate

    df_page_info = sql_statement.sql_dao(request, "sqls_test_info_by_date", str_max_sdate)
    df_questions = sql_statement.sql_dao(request, "sqls_test_question_info_by_date", str_max_sdate)

    return df_page_info, df_questions  # while 수행 완료 후 return 함

def timer_start(request):

    return JsonResponse(
        {"res": "OK"}
    )

def timer_stop(request):

    return JsonResponse(
        {"res": "OK"}
    )

'''
#######################################################
# CALL ID : feedback_test_page_info
# 페이지 호출시 데이터 수집 및 전처리하는 함수
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################   '''
def feedback_test_page_info(request):
    # 변수 초기화
    test_answer1 = request.GET.get("test_answer1")
    test_answer2 = request.GET.get("test_answer2")
    test_answer3 = request.GET.get("test_answer3")
    test_time1   = request.GET.get("test_time1")
    test_time2   = request.GET.get("test_time2")
    test_time3   = request.GET.get("test_time3")
    test_order_no = request.GET.get("test_order_no")
    test_page_date = request.GET.get("test_page_date")

    df_page_info = pd.DataFrame()
    df_questions = pd.DataFrame()

    df_page_info = sql_statement.sql_dao(request, "sqls_feedback_info_by_date", "")

    if df_page_info.empty:
        try:
            url = "https://free.ybmclass.com/free/toeic/toeic_5min_contents2.asp?toeic_id={}&wdate={}&page=1".format(
                test_order_no, test_page_date
            )

            # 공통 함수의 webdriver를 사용해서 파싱한다.
            html, soup = proj_comn_func.url_parsing_with_webdriver(url, "1")

            dic_content = []
            lst_content = []

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

            # 각 항목을 딕셔너리로 df_content 리스트에 추가
            dic_content.append({
                'trgt_order_no' : test_order_no,
                'trgt_page_date': test_page_date,
            })

            # df_content를 DataFrame으로 변환
            df_page_info = pd.DataFrame(dic_content)

            '''
            #######################################################
            # 작성일 : 2024.06.20
            # YBM 실전 5분 토익 문제 페이지 수집-전치리 데이터 생성
            #######################################################
            '''
            v_toeic_test_box = soup.find(class_=["cont-box"])

            if v_toeic_test_box:
                for dt_content in v_toeic_test_box.find_all("dt"):
                    dt_v_num = dt_content.find(class_=["num"])
                    df_num = "question"+dt_v_num.get_text(strip=True)
                    dt_v_num.decompose() # dt_v_num 요소 제거 후 남은 텍스트 가져오기
                    df_question = dt_content.get_text()

                    # # 문자열 내의 모든 줄바꿈 제거
                    df_question = df_question.replace('\n', ' ')
                    df_question = df_question.replace('  ', ' ')

                    # 각 항목을 딕셔너리로 df_content 리스트에 추가
                    lst_content.append({
                        'question_no': df_num,
                        'question_content': df_question,
                        'choice_a': '',
                        'choice_b': '',
                        'choice_c': '',
                        'choice_d': '',
                        'your_answer': '',
                        'correct_answer': '',
                        'result_value'  : '',
                        'test_time': '',
                        'feedback'   : '',
                    })

                # lst_content를 DataFrame으로 변환
                df_content = pd.DataFrame(lst_content)

                for dd_content in v_toeic_test_box.find_all("dd"):
                    dd_spans = dd_content.find_all("span")
                    for dd_span in dd_spans:
                        v_span = dd_span.get_text()

                        # span 내부에 input 태그 찾기
                        input_tag = dd_span.find('input')
                        if input_tag:
                            # input 태그의 name 속성 출력
                            input_name = input_tag.get('name')
                            if input_tag.get('checked') == "checked":
                               input_value = input_tag.get('value')
                            else:
                                input_value = ""
                            if input_name in df_content['question_no'].values:
                                # DataFrame에서 해당 question_no의 index 찾기
                                index = df_content.index[df_content['question_no'] == input_name].tolist()[0]
                                # 해당하는 선택지를 찾아 값을 저장
                                if df_content.at[index, 'choice_a'] == '':
                                   df_content.at[index, 'choice_a'] = v_span
                                elif df_content.at[index, 'choice_b'] == '':
                                   df_content.at[index, 'choice_b'] = v_span
                                elif df_content.at[index, 'choice_c'] == '':
                                   df_content.at[index, 'choice_c'] = v_span
                                elif df_content.at[index, 'choice_d'] == '':
                                   df_content.at[index, 'choice_d'] = v_span
                                if input_value != "":
                                   df_content.at[index, 'correct_answer'] = input_value
                                if index == 0:
                                   df_content.at[index, 'your_answer'] = test_answer1
                                   df_content.at[index, 'test_time']   = test_time1
                                elif index == 1:
                                   df_content.at[index, 'your_answer'] = test_answer2
                                   df_content.at[index, 'test_time']   = test_time2
                                elif index == 2:
                                   df_content.at[index, 'your_answer'] = test_answer3
                                   df_content.at[index, 'test_time']   = test_time3

                for index, row in df_content.iterrows():
                    if row['correct_answer'] == row['your_answer']:
                        df_content.at[index, 'result_value'] = "Y"
                    else:
                        df_content.at[index, 'result_value'] = "N"

                df_questions = df_content

            '''
            #######################################################
            # 문제별 해석 추출 함수
            # 작성일 : 2024.06.20
            # YBM 실전 5분 토익 문제 페이지 수집-전치리 데이터 생성
            #######################################################
            '''
            lst_explanation = []
            df_explanation = pd.DataFrame()
            v_ul_explanation = soup.find_all("ul", class_=["explanation"])
            if v_ul_explanation:
                for ii, ul_explanation in enumerate(v_ul_explanation):
                    li_element = ul_explanation.find("li")
                    if li_element:  # li 태그가 있는지 확인
                        li_explanation = li_element.get_text().strip()
                    else:
                        li_explanation = "No explanation found"  # li 태그가 없을 경우의 처리

                    li_num = "question" + str(ii + 1)  # 문자열과 정수를 올바르게 연결

                    # 각 항목을 딕셔너리로 df_content 리스트에 추가
                    lst_explanation.append({
                        'question_no': li_num,
                        'question_feedback': li_explanation,
                    })

                    for explanation_dict in lst_explanation:
                        # 딕셔너리의 키 'question_no'와 'question_feedback'에 접근
                        v_explanation = explanation_dict['question_no']
                        question_feedback = explanation_dict['question_feedback']

                        # 값을 출력
                        if v_explanation in df_questions['question_no'].values:
                            # DataFrame에서 해당 question_no의 index 찾기
                            index = df_questions.index[df_questions['question_no'] == v_explanation].tolist()[0]
                            # 해당하는 선택지를 찾아 값을 저장
                            if df_questions.at[index, 'feedback'] == '':
                               df_questions.at[index, 'feedback'] = question_feedback

        except Exception as e:
            print("Finding web-page failed-2: ", e)
    else:
        df_questions = sql_statement.sql_dao(request, "sqls_feedback_question_info_by_date", "")

        for index, row in df_questions.iterrows():
            if index == 0:
                df_questions.loc[index, 'your_answer'] = test_answer1
                df_questions.loc[index, 'test_time'] = test_time1
            elif index == 1:
                df_questions.loc[index, 'your_answer'] = test_answer2
                df_questions.loc[index, 'test_time'] = test_time2
            elif index == 2:
                df_questions.loc[index, 'your_answer'] = test_answer3
                df_questions.loc[index, 'test_time'] = test_time3

            if row['correct_answer'] == df_questions.loc[index, 'your_answer']:
                df_questions.loc[index, 'result_value'] = "Y"
            else:
                df_questions.loc[index, 'result_value'] = "N"

    return df_page_info, df_questions   # while 수행 완료 후 return 함