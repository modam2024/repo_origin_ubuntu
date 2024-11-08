# 2024.04.28 : spacy 포함
from django.views.decorators.csrf import csrf_exempt

import app_living_english.pkg_sql_statement.sql_statement as sql_statement
from proj_sql_mapping import create_connection, close_connection
from proj_common import mdl_common_proj as proj_comn_func

# PAGE INFO 생성함수, 2024-02-21
def make_page_info(request):
    # 변수 초기화
    err_cnt = 0
    new_chapter_cnt = 0
    number = 1
    max_chapter_num = int(retrieve_max_chapter_num(request))

    title_text = "YBM"

    chapter_values = {
        "chapter_num": max_chapter_num,
        "title_text": title_text,
        "audio_name": "YBM",
    }

    while True:  # 무한 루프
        if number > 1:
            max_chapter_num += 1

        if number > 4000:
            break
        else:
            number += 1

        try:
            url = "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx={}".format(
                max_chapter_num
            )

            # 공통 함수의 webdriver를 사용해서 파싱한다.
            html, soup = proj_comn_func.url_parsing_with_webdriver(url, "1")

            # <audio> 태그 찾기
            audio_tag = soup.find("audio")

            # 존재하지 않는 페이지 처리
            if not audio_tag:
                print(
                    f"Page for chapter {max_chapter_num} does not exist or has no audio."
                )
                break

            # 'src' 속성 추출
            src_value = audio_tag["src"]

            # 파일명 추출 (마지막 '/' 이후의 내용)
            file_name = src_value.split("/")[-1]

            # 확장자 제거 및 출력
            audio_name = file_name.split(".")[0]

            # YBM 생활영어 제목 찾기
            title_view = soup.find(class_=["title-view"])
            if title_view:
                for title in title_view.find_all("strong"):
                    title_text = title.get_text(strip=True)

            chapter_values = {
                "chapter_num": max_chapter_num,
                "title_text": title_text,
                "audio_name": audio_name,
            }

            # CHAPTER 3가지 정보 테이블 저장
            incr_cnt = do_insert_page_info( request, chapter_values )
            new_chapter_cnt += int(incr_cnt)

            # 신규 회차의 CONTENT 생성
            # <dl> 태그의 내용을 추출합니다.
            text = ""
            dl_tags = soup.find_all("dl")

            for dl in dl_tags:
                text += dl.get_text(separator="\n", strip=True) + "\n"

            # A와 B 기준으로 텍스트를 그룹화
            txt_eng_map = []
            txt_kor_map = []
            txt_additional_map = []
            prv_ab_text = "A"
            tmp_ab_text = ""
            tmp_ab_text2 = ""
            grouped_text = "A"
            lines = text.split("\n")
            loop = 0
            for line in lines:
                line = line.replace("A ", " A ")
                line = line.replace("B ", " B ")

                if line.startswith("A"):
                    tmp_ab_text = "A"
                elif line.startswith("B"):
                    tmp_ab_text = "B"
                elif line.startswith("2"):
                    tmp_ab_text2 = "B2"
                elif line.startswith("[A"):
                    tmp_ab_text = "C"
                elif line.startswith("해설"):
                    tmp_ab_text = "D"
                else:
                    if tmp_ab_text == "A" or tmp_ab_text == "B" or tmp_ab_text == "C":
                        if prv_ab_text != tmp_ab_text:
                            prv_ab_text = tmp_ab_text
                            if tmp_ab_text == "C":
                                if loop == 1:
                                    txt_kor_map.append(grouped_text)
                                grouped_text = line
                                txt_additional_map.append(grouped_text)
                            elif tmp_ab_text2 == "B2":
                                if loop == 0:
                                    txt_eng_map.append(grouped_text)
                                    grouped_text = tmp_ab_text + " " + line
                                    loop = loop + 1
                                else:
                                    txt_kor_map.append(grouped_text)
                                    grouped_text = tmp_ab_text + " " + line
                            elif tmp_ab_text2 != "B2":
                                txt_eng_map.append(grouped_text)
                                grouped_text = tmp_ab_text + " " + line
                            else:
                                txt_eng_map.append(grouped_text)
                                grouped_text = tmp_ab_text + " " + line
                        elif tmp_ab_text == "C":
                            grouped_text = ""
                            grouped_text += line
                            txt_additional_map.append(grouped_text)
                        else:
                            if (
                                line.startswith("2")
                                or line.startswith("3")
                                or line.startswith("오디오")
                                or line.startswith("해석")
                            ):
                                grouped_text = grouped_text + ""
                            else:
                                grouped_text += " " + line
                    elif tmp_ab_text == "D":
                        txt_engs = ""
            if new_chapter_cnt > 0:
                txt_engs = "\n\n"
                eng_num = 1
                for each_eng in txt_eng_map:
                    txt_engs += each_eng + "\n\n"
                    do_saving_each_content(
                        request, "eng", eng_num, max_chapter_num, each_eng
                    )
                    eng_num += 1

                txt_kors = "\n\n"
                kor_num = 1
                for each_kor in txt_kor_map:
                    txt_kors += each_kor + "\n\n"
                    do_saving_each_content(
                        request, "kor", kor_num, max_chapter_num, each_kor
                    )
                    kor_num += 1

                txt_additionals = "\n\n"
                additional_num = 1
                for each_additional in txt_additional_map:
                    txt_additionals += each_additional + "\n\n"
                    do_saving_each_content(
                        request, "add", additional_num, max_chapter_num, each_additional
                    )
                    additional_num += 1

        except Exception as e:
            print("Finding web-page failed: ", e)
            if int(err_cnt > 0) and int(max_chapter_num) > 4730:
                break
            else:
                err_cnt += 1

    # 2024.09.02 - 신규 생활회화 생성 배치 히스토리 저장
    hist_value = sql_statement.sql_dao(request, "sqli_batch_living_english_hist", chapter_values)

    return new_chapter_cnt  # while 수행 완료 후 return 함

def show_current_living_english(request, selectd_chapter, selectd_status):

    # 데이터베이스 연결 초기화
    conn, cursor, current_username = create_connection(request)

    v_topic_dur_start = 0
    v_topic_dur_end   = 0

    # 전체 titles 정보와 선택된 chapter 정보를 조회한다.
    titles, comp_titles, selectd_chapter, title_text, audio_name = fetch_titles(
        request, selectd_chapter, selectd_status
    )

    # 생활회화 화면 오디오의 제목별 오디오 대화 시작시간과 완료시간을 조회한다.
    v_topic_dur_start, v_topic_dur_end = sql_statement.sql_dao(request, "sqls_living_english_topic", selectd_chapter)

    try:
        txt_eng_data, txt_kor_data, txt_additional_data, content_cnt = (
            retrieve_content_info(request, selectd_chapter)
        )
        if int(content_cnt) > 0:
            txt_engs = "\n\n"
            eng_num = 1
            for each_eng in txt_eng_data:
                each_eng = each_eng[0]
                txt_engs += each_eng + "\n\n"
                eng_num += 1

            txt_kors = "\n\n"
            kor_num = 1
            for each_kor in txt_kor_data:
                each_kor = each_kor[0]
                txt_kors += each_kor + "\n\n"
                kor_num += 1

            txt_additionals = "\n\n"
            additional_num = 1
            for each_additional in txt_additional_data:
                each_additional = each_additional[0]
                txt_additionals += each_additional + "\n\n"
                additional_num += 1

            return (
                titles,
                comp_titles,
                title_text,
                audio_name,
                txt_engs,
                txt_kors,
                txt_additionals,
                v_topic_dur_start,
                v_topic_dur_end,
            )

    except Exception as e:
        print("Error occurred:", e)
        return ""

    finally:
        close_connection(conn, cursor)

@csrf_exempt
def do_saving_each_content(request, p_type, p_seq_num, p_chapter_num, p_each_stmt):
    conn, cursor, current_username = create_connection(request)

    content_values = {
        "type"        : p_type,
        "seq_num"     : p_seq_num,
        "chapter_num" : p_chapter_num,
        "each_stmt"   : p_each_stmt,
    }

    # 상태별 영어회화 음성파일 재생 정보 조회
    sql_statement.sql_dao(request, "sqli_living_english_content", content_values)


# MAX CHAPTER NUM 조회함수, 2024-02-21
def retrieve_max_chapter_num(request):

    # 생활회화 화면 오디오의 제목별 오디오 대화 시작시간과 완료시간을 조회한다.
    existing_max_chapter_num = sql_statement.sql_dao(request, "sqls_existing_max_chapter_num", "")

    return existing_max_chapter_num

def fetch_titles(request, selectd_chapter, selectd_status):

    rtn_selectd_chapter    = ""
    rtn_title_text         = ""
    rtn_selectd_voice_date = ""

    # 상태별 영어회화 음성파일 재생 정보 조회
    existing_titles = sql_statement.sql_dao(request, "sqls_fetch_titles", selectd_status)

    # 결과를 리스트로 변환
    titles = [
        (chapter, title, voice_date)
        for chapter, title, voice_date in existing_titles
    ]

    for title in titles:
        if title[0] == selectd_chapter:
            rtn_selectd_chapter = title[0]
            rtn_title_text = title[1]
            rtn_selectd_voice_date = title[2]
            break
    else:
        # for 루프가 break 없이 정상 종료되면, 첫 번째 항목으로 기본값을 설정
        rtn_selectd_chapter = titles[0][0] if titles else ""
        rtn_title_text = titles[0][1] if titles else ""
        rtn_selectd_voice_date = titles[0][2] if titles else ""

    # 완료된 영어회화 정보 조회
    existing_comp_titles = sql_statement.sql_dao(request, "sqls_fetch_titles2", "")

    # 결과를 리스트로 변환
    comp_titles = [
        (chapter, title, voice_date)
        for chapter, title, voice_date in existing_comp_titles
    ]

    return (
        titles,
        comp_titles,
        rtn_selectd_chapter,
        rtn_title_text,
        rtn_selectd_voice_date,
    )

def do_insert_page_info(request, chapter_values):

    res_value = sql_statement.sql_dao(request, "sqli_page_info", chapter_values)
    return res_value

def retrieve_content_info(request, p_selectd_chapter):

    # first part - english
    selectd_eng_content = sql_statement.sql_dao(request, "sqls_living_english_content_english", p_selectd_chapter)

    # second part - korean
    selectd_kor_content = sql_statement.sql_dao(request, "sqls_living_english_content_korean", p_selectd_chapter)

    # third part - additional
    selectd_add_content = sql_statement.sql_dao(request, "sqls_living_english_content_additional", p_selectd_chapter)

    # total count
    return_cnt = sql_statement.sql_dao(request, "sqls_living_english_content_resultcnt", p_selectd_chapter)

    return selectd_eng_content, selectd_kor_content, selectd_add_content, return_cnt
