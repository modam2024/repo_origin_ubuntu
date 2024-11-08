import os

import nltk
from django.contrib.auth.decorators import login_required
# 2024.04.28 : spacy 포함
from django.shortcuts import render

from proj_common import mdl_common_proj as proj_comn_func
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement

# NLTK 데이터 디렉토리 설정 (사용자의 홈 디렉토리 아래)
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'apache_nltk_data')

# NLTK 데이터 디렉토리 존재 여부 확인 및 생성
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# NLTK 리소스 다운로드 (서버 시작 시 한 번만 수행)
nltk.download("punkt", download_dir=nltk_data_dir)
nltk.download("averaged_perceptron_tagger", download_dir=nltk_data_dir)
nltk.download("wordnet", download_dir=nltk_data_dir)

# # nltk 리소스 다운로드 (서버 시작 시 한 번만 수행하면 됩니다)
# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")
# nltk.download("wordnet")

# 단어 추출 첫화면 조회, group_code 셋팅
@login_required(login_url='/login/')
def main_view(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "main_view")

    group_codes = proj_comn_func.get_group_codes(request)

    values = {
        "group_codes": group_codes,
    }

    return render(request, "article.html", values)