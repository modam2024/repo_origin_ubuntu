import json
import re

import mysql.connector
import spacy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from googletrans import Translator

from app_common import mdl_common_app as comn_func
from proj_sql_mapping import fn_connector as proj_connector
import app_living_english.pkg_sql_statement.sql_statement as sql_statement
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement


# 축약형을 변환하는 함수 정의
def handle_contractions(tokens, index):
    if index + 1 < len(tokens) and tokens[index + 1].text in ["'s", "'re", "'m", "'ve", "'d", "'ll"]:
        return tokens[index].text + tokens[index + 1].text, True
    return tokens[index].text.strip(), False

@csrf_exempt
def submit_sentence(request):
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "submit_sentence")

    # 변환된 텍스트 저장용 리스트
    converted_sentences = []
    list_rslt_sentns = []

    # POST 요청일 때만 처리
    if request.method == "POST":
        word_count = 0
        word_insert_count = 0

        try:
            # 데이터베이스 설정
            conn = proj_connector(request)
            cursor = conn.cursor()
        except mysql.connector.Error as e:
            # MySQL 연결 또는 쿼리 실행 오류 처리
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        try:
            # 요청의 본문을 JSON으로 파싱
            data = json.loads(request.body)
            eng_content = data.get("artclContent1")
            kor_content = data.get("artclContent2")
            article_content = comn_func.filter_text(eng_content)
            filted_eng_content = comn_func.filter_eng_text(kor_content)

            # SpaCy 영어 모델 로드 (사전 학습된 모델)
            nlp = spacy.load('en_core_web_sm')
            # translator = Translator()

            # 뉴스 기사 텍스트를 SpaCy의 nlp 객체로 분석
            doc = nlp(article_content)

            # 문장 단위로 분리된 리스트 생성
            sentences = list(doc.sents)

            tmp_sentence = ""
            tmp_sentences = []
            # 문장에서 각 품사를 변환
            for sent0 in sentences:
                tmp_sent0 = sent0.text
                if tmp_sentence:
                   tmp_sent0 = tmp_sentence + tmp_sent0
                   new_doc0 = nlp(tmp_sent0)
                   sent0 = new_doc0[:]
                   tmp_sentence = ""
                if len(sent0.text) < 4:
                   tmp_sentence = sent0.text
                else:
                   tmp_sentences.append(sent0)

            # 문장에서 각 품사를 변환
            for sent in tmp_sentences:
                # sent.text 변수에서 한글을 영어로 치환한다.
                pattern = re.compile(r'[가-힣\s]')
                tmp_sent = sent.text

                tmp_kor_content = pattern.findall(tmp_sent)
                tmp_kor_content = ''.join(tmp_kor_content)
                tmp_kor_content = tmp_kor_content.strip()

                if tmp_kor_content:
                    tmp_sent = tmp_sent.replace(tmp_kor_content.strip(), filted_eng_content.strip())
                    new_doc = nlp(tmp_sent) # 전체 문장을 재구성하여 새로운 Doc 객체 생성
                    sent = new_doc[:] # 원래 Span 객체의 정보를 이용하여 새 Span 객체 생성

                original_sentence = tmp_sent
                # 어플 공통 : 대상 영문장을 변환문장시 전처리한다.
                original_sentence, converted_sentence = comn_func.fn_preparation_process_of_convert(sent, original_sentence)
                converted_sentences.append((original_sentence, converted_sentence))

            # 결과 출력
            for original_sentence, converted_sentence in converted_sentences:
                # 어플 공통 : 변환문장에서 특수문자 전처리한다.
                result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn = comn_func.fn_comma_process_of_convert(original_sentence, converted_sentence)
                list_rslt_sentns.append((result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn))

            v_test_no = sql_statement.sql_dao(request, "sqli_convert_living_english", list_rslt_sentns)

            # 처리 성공 응답
            return JsonResponse(
                {
                    "whitespace_converted": "success",
                    "converted_sentn": "Article processed successfully",
                    "original_sentn": word_count,
                    "translated_sentn": word_insert_count,
                }
            )

        except json.JSONDecodeError:
            # JSON 파싱 에러 처리
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )

        except Exception as e:
            # 기타 예외 처리
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        finally:
            if conn is not None:
                conn.commit()
                cursor.close()