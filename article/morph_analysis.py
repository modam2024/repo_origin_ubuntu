# 2024.04.28 : spacy 포함
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from article import morph as comn_morph
from mdl_sql_mapping import sql_mapping as sql_statement
from mdl_common import common_morph_process as comn_mph_process
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required(login_url='/login/')
def submit_topic(request):
    # POST 요청일 때만 처리
    if request.method == "POST":

        check_cnt = sql_statement.sql_dao(request, "sqls_submit_article_pre_check", "")
        check_cnt = int(check_cnt)  # 문자열을 정수로 변환

        if check_cnt > 0:
            morph_check = sql_statement.sql_dao(request, "sqls_select_tb_converted_sentn", "submit_topic")
            if len(morph_check) == 0:
               comn_morph.submit_sentence(request)
            # 처리 성공 응답
            return JsonResponse(
                {"status": "check", "message": "Aleady treated"}, status=200
            )
        # 기존의 submit-article 함수를 모듈화 시켰다.
        rtn_result = comn_mph_process.submit_topic(request)

        if rtn_result["status"] == "success":
           morph_check = sql_statement.sql_dao(request, "sqls_select_tb_converted_sentn", "submit_topic")
           if len(morph_check) == 0:
              comn_morph.submit_sentence(request)

        return JsonResponse(rtn_result)
    else:
        # POST 요청이 아닐 때의 처리
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )