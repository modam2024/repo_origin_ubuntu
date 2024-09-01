# 2024.04.28 : spacy 포함
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app_living_english.app_views import living_english_morph as living_eng_morph
from mdl_sql_mapping import sql_mapping as sql_statement
from proj_common import proj_morph_new_words as morph_new_words
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required(login_url='/login/')
def submit_topic(request):
    # POST 요청일 때만 처리
    if request.method == "POST":
        # 작업 : 모든 페이지에서 문장 분석 프로시져 처리 여부 확인용도
        check_cnt = sql_statement.sql_dao(request, "sqls_submit_article_pre_check", "")
        check_cnt = int(check_cnt)  # 문자열을 정수로 변환

        if check_cnt > 0:
            # 작업 : 변환 문장을 조회한다. db_converted_sentn 에 저장된 자료를 조회한다.
            morph_check = sql_statement.sql_dao(request, "sqls_select_tb_converted_sentn", "submit_topic")
            if len(morph_check) == 0:
               # 생활회화 페이지에 특화된 로직이다.
               # submit_sentence 의 앞부분은 한글에 영어로 바꾸는 로직,
               # 뒷부분은 중요단어로 구성된 변환된 문장을 구하는 로직이다.
               living_eng_morph.submit_sentence(request)
            # 처리 성공 응답
            return JsonResponse(
                {"status": "check", "message": "Aleady treated"}, status=200
            )
        # 기존의 submit-article 함수를 모듈화 시켰다.
        rtn_result = morph_new_words.submit_topic(request)

        if rtn_result["status"] == "success":
           morph_check = sql_statement.sql_dao(request, "sqls_select_tb_converted_sentn", "submit_topic")
           if len(morph_check) == 0:
               # 생활회화 페이지에 특화된 로직이다.
               # submit_sentence 의 앞부분은 한글에 영어로 바꾸는 로직,
               # 뒷부분은 중요단어로 구성된 변환된 문장을 구하는 로직이다.
              living_eng_morph.submit_sentence(request)

        return JsonResponse(rtn_result)
    else:
        # POST 요청이 아닐 때의 처리
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )