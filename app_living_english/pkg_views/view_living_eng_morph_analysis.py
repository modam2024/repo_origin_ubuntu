# 2024.04.28 : spacy 포함
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app_living_english.pkg_views import view_living_english_morph as living_eng_morph
from proj_sql_mapping import mdl_mapping_sql_proj as sql_statement
from proj_common import mdl_morph_words_proj as morph_new_words
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required(login_url='/login/')
def submit_topic(request):
    res_value = sql_statement.sql_dao(request, "sqli_click_study_hist", "submit_topic")

    # POST 요청일 때만 처리
    if request.method == "POST":
       # 작업 : 변환 문장을 조회한다. db_converted_sentn 에 저장된 자료를 조회한다.
       morph_check = sql_statement.sql_dao(request, "sqls_proj_converted_sentn", "submit_topic")

       if len(morph_check) == 0:
           # 생활회화 페이지에 특화된 로직이다.
           # submit_sentence 의 앞부분은 한글에 영어로 바꾸는 로직,
           # 뒷부분은 중요단어로 구성된 변환된 문장을 구하는 로직이다.
           living_eng_morph.submit_sentence(request)

           return JsonResponse({
                  "status": "success",
                  "message": "converting sentences successfully"}, status=200 )
       else:
           # 성공 응답
           return JsonResponse( {"status": "check", "message": "Aleady treated"}, status=200 )

