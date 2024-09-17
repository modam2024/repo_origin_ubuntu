import json
import re

import mysql.connector
import spacy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googletrans import Translator

from app_common import mdl_common_app as comn_func
import app_test_timer.pkg_sql_statement.sql_statement as sql_statement
from proj_sql_mapping import  fn_connector as proj_connector
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement

@csrf_exempt
def convert_sentence(request):
    # 학습 이력 남기기
    res_value = proj_sql_statement.sql_dao(request, "sqli_click_study_hist", "convert_sentence")

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

            question_no     = data.get("question_no")
            source_url      = data.get("sourceUrl")
            source_title    = data.get("sourceTitle")
            source_type     = "YBM(TEST)"
            topic_num       = data.get("topic_num")

            tmp_values = {
                "topic_num"   : topic_num,
                "question_no" : question_no,
            }
            # 연속 공백을 정답으로 치환한 문장을 받아온다.
            article_content = sql_statement.sql_dao(request, "sqls_fdbck_question_content", tmp_values)

            # SpaCy 영어 모델 로드 (사전 학습된 모델)
            nlp = spacy.load('en_core_web_sm')

            # 뉴스 기사 텍스트를 SpaCy의 nlp 객체로 분석
            doc = nlp(article_content)

            # 문장 단위로 분리된 리스트 생성
            sentences = list(doc.sents)

            # 문장에서 각 품사를 변환
            for sent in sentences:
                original_sentence = sent.text
                # 어플 공통 : 대상 영문장을 변환문장시 전처리한다.
                original_sentence, converted_sentence = comn_func.fn_preparation_process_of_convert(sent, original_sentence)
                converted_sentences.append((original_sentence, converted_sentence))

            # 결과 출력
            for original_sentence, converted_sentence in converted_sentences:
                # 어플 공통 : 변환문장에서 특수문자 전처리한다.
                result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn = comn_func.fn_comma_process_of_convert(original_sentence, converted_sentence)
                list_rslt_sentns.append((result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn))

            convert_values = {
                "question_no" : question_no,
                "source_url"  : source_url,
                "source_title": source_title,
                "source_type" : source_type,
                "topic_num"   : topic_num,
                "list_rslt_sentns": list_rslt_sentns,
            }

            v_test_no = sql_statement.sql_dao(request, "sqli_convert_test_timer", convert_values)

            # 처리 성공 응답
            return JsonResponse(
                {
                    "message": "success",
                    "topic_num": topic_num,
                    "question_no": question_no,
                    "list_rslt_sentns": list_rslt_sentns
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
