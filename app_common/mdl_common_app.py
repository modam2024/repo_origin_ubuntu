import re

def filter_text(text):
    # 정규 표현식 패턴: 영어 대소문자, 공백, 특수문자, 한글 문자 포함
    pattern = re.compile(r'[a-zA-Z\s\W가-힣]')

    # 정규 표현식과 일치하는 문자만 남기고 합침
    filtered_text = ''.join(pattern.findall(text))

    return filtered_text

def filter_eng_text(text):
    # 정규 표현식 패턴: 영어 대소문자, 공백, 특수문자, 한글 문자 포함
    text = text.replace("A :", "")
    text = text.replace("B :", "")

    pattern = re.compile(r'[a-zA-Z\s\'\’]')
    # 정규 표현식과 일치하는 문자만 남기고 합침
    eng_text = ''.join(pattern.findall(text))

    return eng_text

'''
#######################################################
# handle_contractions
# 축약형을 변환하는 함수 정의
# 작성일 : 2024.09.13
# 작성자 : 이용학
####################################################### '''
def handle_contractions(tokens, index):
    if index + 1 < len(tokens) and tokens[index + 1].text in ["'s", "'re", "'m", "'ve", "'d", "'ll"]:
        return tokens[index].text + tokens[index + 1].text, True
    return tokens[index].text.strip(), False

'''
#######################################################
# CALL ID   : fn_app_commn_prprtn_prcs_convert
# CALLER ID : view_living_english_morph.py > submit_sentence
#             view_five_convert.py > convert_sentence
# 작업내용    : 대상 영문장을 변환문장시 전처리하는 함수이다.
# 작성일 : 2024.09.13
# 작성자 : 이용학
####################################################### '''
def fn_preparation_process_of_convert(sent, p_text_original_sentence):
    # 변환된 텍스트 저장용 리스트
    past_verbs = ['been', 'done', 'had', 'was', 'were', 'did']  # BE 동사 리스트
    be_verbs = ['be', 'am', 'is', 'are', 'was', 'were', 'have', 'has']  # BE 동사 리스트
    modal_verbs = ['will', 'shall', 'can', 'must', 'may', 'might', 'would', 'should', 'could']  # 조동사 리스트

    original_sentence = p_text_original_sentence
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
        elif token.text == '"':
            converted_tokens.append(' ')
        elif token.pos_ == 'DET' and token.text.lower() in ['the', 'a', 'an']:
            converted_tokens.append(',')  # 정관사 및 부정관사
        elif token.pos_ == 'ADP':
            if converted_tokens and converted_tokens[-1] == ',':
                continue  # 앞에 쉼표가 있는 경우 전치사 생략
            converted_tokens.append(' ,,')  # 전치사
        elif token.tag_ == 'TO':
            if converted_tokens and converted_tokens[-1] == ',':
                continue  # 앞에 쉼표가 있는 경우 부정사 생략
            converted_tokens.append(' ,,')  # 부정사 'to'
        elif token.pos_ == 'PRON' and token.dep_ in ['relcl']:
            if converted_tokens and converted_tokens[-1] == ',':
                continue  # 앞에 쉼표가 있는 경우 관계대명사 생략
            converted_tokens.append(' ,,,')  # 관계대명사
        elif token.pos_ == 'CCONJ' or token.pos_ == 'SCONJ':
            if converted_tokens and converted_tokens[-1] == ',':
                continue  # 앞에 쉼표가 있는 경우 접속사 생략
            converted_tokens.append(' ,,,,')  # 접속사
        elif token.pos_ == 'AUX' and token.tag_ == 'MD' and token.text.lower() in modal_verbs:
            converted_tokens.append(' ,,')
        elif token.pos_ == 'VERB' and token.tag_ == 'MD' and token.text.lower() in modal_verbs:
            if token.nbor(1).text.lower() == "n't":
                print('MD')
            else:
                converted_tokens.append(' ,,')
             # VBP 는 verb, non-3rd person singular present, VBZ 는 verb, 3rd person singular present
        elif token.pos_ == 'AUX' and (token.tag_ == 'VBP'  or token.tag_ == 'VBZ' or token.tag_ == 'VB') and token.text.lower() in be_verbs:
             converted_tokens.append(' ,,')
             # 'VBD' 는 verb, past tense, VBN' 는 verb, past participle
        elif (token.pos_ == 'VERB' or token.pos_ == 'AUX') and (token.tag_ == 'VBD' or token.tag_ == 'VBN') and token.text.lower() in past_verbs:
             converted_tokens.append(' ,,')
        else:
            converted_tokens.append(token.text)  # 다른 단어는 그대로 추가

    # 변환된 토큰들을 하나의 텍스트로 결합하여 문장 리스트에 추가
    converted_sentence = ' '.join(converted_tokens)

    return original_sentence, converted_sentence

'''
#######################################################
# CALL ID : fn_app_commn_prprtn_prcs_convert
# 변환문장에서 특수문자 전처리하는 함수이다.
# CALLER ID : view_living_english_morph.py > submit_sentence
#             view_five_convert.py > convert_sentence
# 작성일 : 2024.09.13
# 작성자 : 이용학
####################################################### '''
def fn_comma_process_of_convert(original_sentence, converted_sentence):
    whitespace_converted = ' '.join(converted_sentence.replace(',', '').split())
    translated_sentence = ""
    # translated_sentence = translator.translate(original_sentence.strip(), src='en', dest='ko').text
    result_whitespace_converted = whitespace_converted.strip()
    result_converted_sentn = converted_sentence.strip()
    result_original_sentn = original_sentence.strip()
    result_translated_sentn = translated_sentence

    result_whitespace_converted = result_whitespace_converted.replace(" !", "!")
    result_converted_sentn = result_converted_sentn.replace(" !", "!")
    result_whitespace_converted = result_whitespace_converted.replace(" ?", "?")
    result_converted_sentn = result_converted_sentn.replace(" ?", "?")
    result_whitespace_converted = result_whitespace_converted.replace(" ’", "’")
    result_converted_sentn = result_converted_sentn.replace(" ’", "’")
    result_whitespace_converted = result_whitespace_converted.replace(" ,", ",")
    result_converted_sentn = result_converted_sentn.replace(" ,", ",")
    result_whitespace_converted = result_whitespace_converted.replace(" .", ".")
    result_converted_sentn = result_converted_sentn.replace(" .", ".")
    result_whitespace_converted = result_whitespace_converted.replace(" n’", "n’")
    result_converted_sentn = result_converted_sentn.replace(" n’", "n’")
    result_whitespace_converted = result_whitespace_converted.replace(" - ", "-")
    result_converted_sentn = result_converted_sentn.replace(" - ", "-")

    result_converted_sentn = result_converted_sentn.replace("Ms.", "Ms")
    result_converted_sentn = result_converted_sentn.replace("Miss.", "Miss")
    result_converted_sentn = result_converted_sentn.replace("Mr.", "Mr")
    result_converted_sentn = result_converted_sentn.replace("Dr.", "Dr")

    return result_whitespace_converted, result_converted_sentn, result_original_sentn, result_translated_sentn
