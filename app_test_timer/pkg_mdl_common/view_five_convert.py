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

# 축약형을 변환하는 함수 정의
def handle_contractions(tokens, index):
    if index + 1 < len(tokens) and tokens[index + 1].text in ["'s", "'re", "'m", "'ve", "'d", "'ll"]:
        return tokens[index].text + tokens[index + 1].text, True
    return tokens[index].text.strip(), False

@csrf_exempt
def convert_sentence(request):
    # 변환된 텍스트 저장용 리스트
    converted_sentences = []
    list_rslt_sentns = []
    modal_verbs = ['will', 'shall', 'can', 'must', 'may', 'might', 'would', 'should', 'could']  # 조동사 리스트

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
            # eng_content = data.get("artclContent1")
            # kor_content = data.get("artclContent2")
            # article_content = comn_func.filter_text(eng_content)
            # filted_eng_content = comn_func.filter_eng_text(kor_content)

            question_no     = data.get("question_no")
            article_content = data.get("article")
            source_url      = data.get("sourceUrl")
            source_title    = data.get("sourceTitle")
            source_type     = "YBM(TEST)"
            topic_num       = data.get("topic_num")
            # SpaCy 영어 모델 로드 (사전 학습된 모델)
            nlp = spacy.load('en_core_web_sm')

            # 뉴스 기사 텍스트를 SpaCy의 nlp 객체로 분석
            doc = nlp(article_content)

            # 문장 단위로 분리된 리스트 생성
            sentences = list(doc.sents)

            # tmp_sentence = ""
            # tmp_sentences = []
            # # 문장에서 각 품사를 변환
            # for sent0 in sentences:
            #     tmp_sent0 = sent0.text
            #     if tmp_sentence:
            #        tmp_sent0 = tmp_sentence + tmp_sent0
            #        new_doc0 = nlp(tmp_sent0)
            #        sent0 = new_doc0[:]
            #        tmp_sentence = ""
            #     if len(sent0.text) < 4:
            #        tmp_sentence = sent0.text
            #     else:
            #        tmp_sentences.append(sent0)

            # 문장에서 각 품사를 변환
            for sent in sentences:
                # # sent.text 변수에서 한글을 영어로 치환한다.
                # pattern = re.compile(r'[가-힣\s]')
                # tmp_sent = sent.text
                #
                # tmp_kor_content = pattern.findall(tmp_sent)
                # tmp_kor_content = ''.join(tmp_kor_content)
                # tmp_kor_content = tmp_kor_content.strip()
                #
                # if tmp_kor_content:
                #     tmp_sent = tmp_sent.replace(tmp_kor_content.strip(), filted_eng_content.strip())
                #     new_doc = nlp(tmp_sent) # 전체 문장을 재구성하여 새로운 Doc 객체 생성
                #     sent = new_doc[:] # 원래 Span 객체의 정보를 이용하여 새 Span 객체 생성

                original_sentence = sent.text
                converted_tokens = []
                skip_token = False
                for i, token in enumerate(sent):
                    if skip_token:
                        skip_token = False
                        continue
                    contraction, is_contraction = handle_contractions(sent, i)
                    if is_contraction:
                        # 공백 제거를 위한 정규 표현식
                        contraction_no_spaces = re.sub(r'\s+', '', contraction)
                        converted_tokens.append(contraction_no_spaces)
                        skip_token = True
                    elif token.text == ',':
                        converted_tokens.append(',')
                    elif token.pos_ == 'DET' and token.text.lower() in ['the', 'a', 'an']:
                        converted_tokens.append(',')  # 정관사 및 부정관사
                    elif token.pos_ == 'ADP':
                        if converted_tokens and converted_tokens[-1] == ',':
                            continue  # 앞에 쉼표가 있는 경우 전치사 생략
                        converted_tokens.append(',,')  # 전치사
                    elif token.tag_ == 'TO':
                        if converted_tokens and converted_tokens[-1] == ',':
                            continue  # 앞에 쉼표가 있는 경우 부정사 생략
                        converted_tokens.append(',,')  # 부정사 'to'
                    elif token.pos_ == 'PRON' and token.dep_ in ['relcl']:
                        if converted_tokens and converted_tokens[-1] == ',':
                            continue  # 앞에 쉼표가 있는 경우 관계대명사 생략
                        converted_tokens.append(',,,')  # 관계대명사
                    elif token.pos_ == 'CCONJ' or token.pos_ == 'SCONJ':
                        if converted_tokens and converted_tokens[-1] == ',':
                            continue  # 앞에 쉼표가 있는 경우 접속사 생략
                        converted_tokens.append(',,,,')  # 접속사
                    elif token.pos_ == 'VERB' and token.tag_ == 'MD' and token.text.lower() in modal_verbs:
                         if token.nbor(1).text.lower() == "n't":
                             print('MD')
                         else:
                             converted_tokens.append(',,')
                    else:
                        converted_tokens.append(token.text)  # 다른 단어는 그대로 추가
                # 변환된 토큰들을 하나의 텍스트로 결합하여 문장 리스트에 추가
                converted_sentence = ' '.join(converted_tokens)
                converted_sentences.append((original_sentence, converted_sentence))

            # 결과 출력
            for original_sentence, converted_sentence in converted_sentences:
                result_original_sentn   = original_sentence.strip()
                result_converted_sentn  = converted_sentence.strip()

                result_converted_sentn      = result_converted_sentn.replace(" !", "!")
                result_converted_sentn      = result_converted_sentn.replace(" ?", "?")
                result_converted_sentn      = result_converted_sentn.replace(" ’", "’")
                result_converted_sentn      = result_converted_sentn.replace(" ,", ",")
                result_converted_sentn      = result_converted_sentn.replace(" .", ".")
                result_converted_sentn      = result_converted_sentn.replace(" n’", "n’")
                list_rslt_sentns.append((result_converted_sentn, result_original_sentn))

                convert_values = {
                    "question_no" : question_no,
                    "source_url"  : source_url,
                    "source_title": source_title,
                    "source_type" : source_type,
                    "topic_num"   : topic_num,
                    "list_rslt_sentns": list_rslt_sentns,
                }

            v_test_no = sql_statement.sql_dao(request, "sqli_test_timer_converted_sentn", convert_values)

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