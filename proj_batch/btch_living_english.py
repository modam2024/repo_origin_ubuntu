import re

import pandas as pd
from django.http import HttpResponse

import app_test_timer.pkg_sql_statement as app_con
import app_test_timer.pkg_sql_statement.sql_statement as sql_statement
from proj_common import mdl_common_prj as proj_comn_func

'''
#######################################################
# CALL ID : living_english_batch
# 작성일 : 2024.09.02
# 섦 명  : 영어회화 자료 생성 배치 
####################################################### '''
def living_english_batch(request):

    # 변수 초기화
    new_count = 0
    group_codes = proj_comn_func.get_group_codes(request)
    selectd_version = request.GET.get("check")
    selectd_chapter = request.GET.get("chapter")
    selectd_status = request.GET.get("status")

    # 신규 chapter 정보 생성
    if selectd_version == "new":
        new_count = app_com_func.make_page_info(request)

    return HttpResponse(new_count)
