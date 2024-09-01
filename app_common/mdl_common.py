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
