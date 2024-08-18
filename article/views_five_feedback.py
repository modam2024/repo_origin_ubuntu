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
#######################################################  '''
@login_required(login_url='/login/')
def feedback_english(request):
    df_page_info = pd.DataFrame()
    df_feedback_page_content = pd.DataFrame()
    df_page_info, df_feedback_page_content = feedback_page_info(request)
    dict_feedback_page_content = df_feedback_page_content.to_dict('records')
    dict_page_info = df_page_info.to_dict('records')

    values = {
               'feedback_page_content': dict_feedback_page_content,
               'feedback_page_info': dict_page_info,
               'select_tag_info': "",
             }

    conn, cursor, current_username = create_connection(request)

    try:
        v_trgt_order_no = dict_page_info[0]['trgt_order_no']
        v_trgt_page_date = dict_page_info[0]['trgt_page_date']

        v_test_no = sql_statement.sql_dao(request, "sqls_max_frq_test_page", v_trgt_page_date)

        int_test_no = int(v_test_no) + 1

        if int_test_no > 0:
            delete_query = " DELETE FROM tb_feedback_page_info "
            delete_query += "  WHERE  user_id        = %s "
            delete_query += "    AND  trgt_order_no  = %s "
            delete_query += "    AND  trgt_page_date = %s "
            delete_param = (current_username, v_trgt_order_no, v_trgt_page_date,)
            cursor.execute(delete_query, delete_param)

        for each_feedback_page_content in dict_feedback_page_content:

            v_question_no      = each_feedback_page_content['question_no']
            v_question_content = each_feedback_page_content['question_content']
            v_choice_a = each_feedback_page_content['choice_a']
            v_choice_b = each_feedback_page_content['choice_b']
            v_choice_c = each_feedback_page_content['choice_c']
            v_choice_d = each_feedback_page_content['choice_d']
            v_your_answer    = each_feedback_page_content['your_answer']
            v_correct_answer = each_feedback_page_content['correct_answer']
            v_result_value   = each_feedback_page_content['result_value']
            v_feedback       = each_feedback_page_content['feedback']

            insert_query = " INSERT INTO tb_feedback_page_info "
            insert_query += " (user_id, trgt_order_no, trgt_page_date, question_no, question_content, choice_a, choice_b, choice_c, choice_d, "
            insert_query += "  your_answer, correct_answer, result_value, feedback ) "
            insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            insert_params = ( current_username, v_trgt_order_no, v_trgt_page_date, v_question_no, v_question_content, v_choice_a, v_choice_b,
                              v_choice_c, v_choice_d, v_your_answer, v_correct_answer, v_result_value, v_feedback)

            cursor.execute(insert_query, insert_params)

            insert_query = " INSERT INTO tb_test_result "
            insert_query += " (user_id, test_no, trgt_order_no, trgt_page_date, question_no, your_answer, correct_answer, result_value ) "
            insert_query += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            insert_params = ( current_username, int_test_no, v_trgt_order_no, v_trgt_page_date, v_question_no, v_your_answer, v_correct_answer, v_result_value)

            cursor.execute(insert_query, insert_params)

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

    except Exception as e:
        print("feedback content failed:", e)
    finally:
        close_connection(conn, cursor)

    return render(request, "feedback_english.html", values)

'''
#######################################################
# 페이지 호출시 데이터 수집 및 전처리하는 함수
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################   '''
def feedback_page_info(request):
    # 변수 초기화
    test_answer1 = request.GET.get("test_answer1")
    test_answer2 = request.GET.get("test_answer2")
    test_answer3 = request.GET.get("test_answer3")
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
            html, soup = comn_func.url_parsing_with_webdriver(url, "1")

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
                        'result_value': '',
                        'feedback': '',
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
                                elif index == 1:
                                   df_content.at[index, 'your_answer'] = test_answer2
                                elif index == 2:
                                   df_content.at[index, 'your_answer'] = test_answer3

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
            print("Finding web-page failed: ", e)
    else:
        df_questions = sql_statement.sql_dao(request, "sqls_feedback_question_info_by_date", "")

        for index, row in df_questions.iterrows():
            if index == 0:
                row['your_answer'] = test_answer1
            elif index == 1:
                row['your_answer'] = test_answer2
            elif index == 2:
                row['your_answer'] = test_answer3

            if row['correct_answer'] == row['your_answer']:
                row['result_value'] = "Y"
            else:
                row['result_value'] = "N"

    return df_page_info, df_questions   # while 수행 완료 후 return 함