# 2024.04.28 : spacy 포함

from django.http import HttpResponse

from app_living_english.pkg_mdl_common import mdl_common_lven as app_com_func

'''
#######################################################
# CALL ID : living_english_batch
# 작성일 : 2024.09.02
# 섦 명  : 영어회화 자료 생성 배치 
####################################################### '''
def living_english_batch(request):

    # 변수 초기화
    new_count = 0
    selectd_version = request.GET.get("check")
    selectd_chapter = request.GET.get("chapter")
    selectd_status = request.GET.get("status")

    # 신규 chapter 정보 생성
    if selectd_version == "new":
        new_count = app_com_func.make_page_info(request)

        living_values = {
          "check"  : selectd_version,
          "chapter": selectd_chapter,
          "status" : selectd_status,
        }

    return HttpResponse(new_count)
