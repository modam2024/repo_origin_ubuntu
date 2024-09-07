from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import app_test_timer.pkg_sql_statement.sql_statement as sql_statement
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement

'''
#######################################################
# Entery Point
# 작성일 : 2024.06.20
# 브라우져에서 호출하면 실행되는 main function
#######################################################  '''
@login_required(login_url='/login/')
def feedback_english(request):
    # selectd_order_no = request.GET.get('test_order_no')
    selectd_wdate    = request.GET.get('test_page_date')

    df_page_info, df_feedback_page_content = feedback_page_info(request)

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

        # tb_part5_feedback_page 에는 마지막 결과만 남기기 위해서 먼저 삭제한다.
        if int_test_no > 0:
            feedback_page_value = {
                'trgt_order_no' : v_trgt_order_no,
                'trgt_page_date': v_trgt_page_date,
            }

        existing_pagedates = sql_statement.sql_dao(request, "sqls_test_page_result_info", "")

        # dict_page_info 리스트 초기화
        lst_page_date_info = []
        lst_test_time = []

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

        v_test_time, sum_test_time, remaining_time, crrct_res_ratio = sql_statement.sql_dao(request, "sqls_test_times", selectd_wdate)
        lst_test_time.append(v_test_time)

        # 값을 딕셔너리에 할당할 때는 키를 사용하여 접근
        values['select_tag_info']  = lst_page_date_info
        values['lst_test_time']    = lst_test_time
        values['sum_test_time']    = sum_test_time
        values['remaining_time']   = remaining_time
        values['crrct_res_ratio']  = crrct_res_ratio

    except Exception as e:
        print("feedback content failed:", e)
    finally:
        print("feedback_english completed")

    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "feedback_english")

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
    test_time1   = request.GET.get("test_time1")
    test_time2   = request.GET.get("test_time2")
    test_time3   = request.GET.get("test_time3")

    df_page_info = sql_statement.sql_dao(request, "sqls_feedback_info_by_date", "")
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