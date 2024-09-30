import json
import re

import mysql.connector
# 2024.04.28 : spacy 포함
import spacy
from django.views.decorators.csrf import csrf_exempt
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from proj_sql_mapping import create_connection, close_connection
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement

def fn_spacy_ner(p_nlp, p_word, p_stop_words):
    spacy_tokens = p_nlp(p_word)
    for ent in spacy_tokens.ents:
        if ent.label_ in ("PERSON", "ORG", "DATE", "TIME", "GPE", "NORP", "MONEY", "EVENT", "LOC", "FAC", "PRODUCT", "WORK_OF_ART", "LAW", "ORDINAL"):
            return 1
        else:
            return 0

    if p_word in p_stop_words:
        return 1
    else:
        return 0

def get_wordnet_pos(treebank_tag, lemma):
    if lemma.lower() in [
        "do",
        "did",
        "don",
        "does",
        "can",
        "shall",
        "will",
        "didn",
        "be",
        "been",
        "is",
        "was",
        "were",
        "have",
        "has",
        "had",
        "haven",
        "hasn",
        "hadn",
        "doesn",
        "would",
        "should",
        "could",
        "wouldn",
        "shouldn",
        "couldn",
    ]:
        return None  # "be"와 "have" 동사의 여러 형태를 제외합니다.
    # Treebank 품사 태그를 WordNet 품사 태그로 변환
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        # 동사 중에서도 특정 동사 유형을 제외
        if treebank_tag in ["MD"]:
            return None  # None을 반환하여 해당 단어를 무시
        else:
            return wordnet.VERB
    elif treebank_tag.startswith("N"):
        return wordnet.NOUN
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:
        # WordNetLemmatizer에서 사용되지 않는 태그의 경우 None 반환
        return None

def fn_word_syns_en(p_word):
    # 단어의 의미를 찾기
    syns = wordnet.synsets(p_word)
    def_list_en = ""

    for i, syn in enumerate(syns):
        if i == 0:
            def_list_en = ""
        elif i < 3:
            if def_list_en != "":
                def_list_en += " , " + syn.definition()
            else:
                def_list_en = syn.definition()
        else:
            break

    return def_list_en

@csrf_exempt
def submit_topic(request):
    word_count = 0
    word_insert_count = 0

    # 데이터베이스 설정, 커서 생성22
    conn, cursor, current_username = create_connection(request)

    try:
        # 요청의 본문을 JSON으로 파싱
        data = json.loads(request.body)
        article_content = data.get("article")
        source_url = data.get("sourceUrl")  # 소스 Url 추가
        source_title = data.get("sourceTitle")  # 소스 Title 추가
        source_type = data.get("sourceType")  # 소스 Type 추가

        # spacy 초기화
        nlp = spacy.load('en_core_web_sm')  # 영어 모델을 로드
        from spacy.lang.en.stop_words import STOP_WORDS

        # WordNetLemmatizer 초기화
        lemmatizer = WordNetLemmatizer()

        '''
        텍스트 토큰화(Tokenization): 기사 내용을 개별 단어나 토큰으로 분리(word_tokenize)
        품사 태깅(Part-of-Speech Tagging): 분리된 각 단어에 대해 품사를 태깅(pos_tag)
        레마타이제이션(Lemmatization): 태깅된 품사 정보를 바탕으로, 단어를 그 기본형으로 변환 (lemmatizer.lemmatize)
        '''
        # 기사 내용을 단어로 토큰화 및 품사 태깅
        tokens = word_tokenize(article_content)
        tagged = pos_tag(tokens) # 텍스트를 토큰화한 후 각 토큰(단어)에 대해 품사를 태깅
        tag_text = ""

        for word, tag in tagged:
            wntag = get_wordnet_pos(tag, word) # 품사 정보 변환

            if wntag:
                # 단어를 기본형으로 레마타이즈 (레마타이즈 뜻: 사전형 또는 기본형(lemma)으로 변환하는 과정)
                lemma = lemmatizer.lemmatize(word, pos=wntag)
                # 알파벳 이외의 문자 및 길이가 2글자 이하인 단어 및 마침표로 끝나는 단어 필터링

                ''' 
                정규 표현식 ^[a-zA-Z]+$의 각 부분은 다음과 같은 의미를 가집니다:
                ^: 문자열의 시작을 나타냅니다.
                [a-zA-Z]: 소문자 a부터 z까지, 대문자 A부터 Z까지 중 하나의 문자와 일치합니다.
                +: 바로 앞의 패턴(여기서는 [a-zA-Z])이 하나 이상 연속적으로 나타나야 함을 의미합니다.
                $: 문자열의 끝을 나타냅니다.
                '''

                bl_spacy_ner = fn_spacy_ner(nlp, word, STOP_WORDS)

                if re.match(r"^[a-zA-Z]+$", lemma) and len(lemma) > 2 and bl_spacy_ner == 0:
                    # 마지막에 점이 있는 경우 제거
                    if lemma.endswith("."):
                        lemma = lemma[:-1]  # 마지막 점 제거

                    # 단어를 소문자로 변환
                    lemma = lemma.lower()
                    word_count += 1

                    if tag == "NNP":
                        tag_text = "고유 명사, 단수형"
                    elif tag == "NN":
                        tag_text = "명사, 단수형 또는 집합형"
                    elif tag == "NNS":
                        tag_text = "명사, 복수형"
                    elif tag == "VBG":
                        tag_text = "동사, 동명사 또는 현재 분사형"
                    elif tag == "VBN":
                        tag_text = "동사, 과거 분사형"
                    elif tag == "JJ":
                        tag_text = "형용사"
                    elif tag == "VBD":
                        tag_text = "동사, 과거 시제"
                    elif tag == "VB":
                        tag_text = "동사, 기본형"
                    elif tag == "RB":
                        tag_text = "부사"
                    elif tag == "JJR":
                        tag_text = "형용사, 비교급"
                    elif tag == "NNPS":
                        tag_text = "고유 명사, 복수형"
                    elif tag == "JJS":
                        tag_text = "형용사, 최상급"
                    elif tag == "VBP":
                        tag_text = "동사, 3인칭 단수가 아닌 현재형"
                    elif tag == "RP":
                        tag_text = "조사"
                    elif tag == "VBZ":
                        tag_text = "동사, 3인칭 단수 현재형"

                    existing_word = proj_sql_statement.sql_dao(request, "sqls_processed_words",  lemma)

                    # 이미 데이터베이스에 해당 단어가 완료되지 않은 상태면 다시 url, title, 영문뜻, 날짜들을 갱신해 준다.
                    if existing_word and existing_word[1] != "D":
                        dic_words_info = {
                            "existing_word_2": existing_word[2],
                            "word_insert_count": 0,
                            "lemma_word": lemma,
                            'tag': tag,
                            'tag_text': tag_text,
                            "source_url": source_url,
                            "source_type": source_type,
                            "source_title": source_title,
                            "mean_en_text": "",
                        }
                        proj_sql_statement.sql_dao(request, "sqluu_cond_processed_words", dic_words_info)

                    if not existing_word:

                        # 데이터베이스에 해당 단어가 없으면 INSERT 쿼리 실행
                        try:
                            word_insert_count += 1

                            dic_words_info = {
                                "word_insert_count": word_insert_count,
                                "lemma_word": lemma,
                                'tag': tag,
                                'tag_text': tag_text,
                                "source_url": source_url,
                                "source_type": source_type,
                                "source_title": source_title,
                                "mean_en_text": "",
                            }
                            proj_sql_statement.sql_dao(request, "sqlii_processed_words", dic_words_info)

                        except Exception as e:
                            print("Insert query failed:", e)

                        except mysql.connector.IntegrityError as e:
                            # IntegrityError는 중복 오류를 나타냅니다.
                            if e.errno == 1062:
                                # 중복된 단어를 무시하고 계속 진행
                                pass
                            else:
                                # 다른 IntegrityError에 대한 예외 처리
                                raise

        result_response = {
            "status": "success",
            "message": "Article processed successfully",
            "word_count": word_count,
            "word_insert_count": word_insert_count,
        }

        # 처리 성공 응답
        return result_response

    except json.JSONDecodeError:
        # JSON 파싱 에러 처리
        result_response = {"status": "error", "message": "Invalid JSON", "status_num" : "400"}
        return result_response

    except mysql.connector.Error as e:
        # MySQL 연결 또는 쿼리 실행 오류 처리
        result_response = {"status": "error", "message": str(e), "status_num" : "500"}
        return result_response

    except Exception as e:
        # 기타 예외 처리
        result_response = {"status": "error", "message": str(e), "status_num" : "500"}
        return result_response

    finally:
        close_connection(conn, cursor)