// 단어 클릭 이벤트 핸들러 추가
function speaking(order) {
    var news_sentence = $("#artcl_org_content"+order).val();
    var arr_news_sentence = news_sentence.split("....");
    for (news_sentence of arr_news_sentence)
    {
        news_sentence = news_sentence + ".";
        // 2024.10.31 : gtts 사용으로 주석처리
        //splitTextAndSpeakBySentence(news_sentence);
        speak(news_sentence);
    }
}

function convert_speaking(order) {
    var news_sentence = $("#artcl_convert_content"+order).val();
    var arr_news_sentence = news_sentence.split("....");
    for (news_sentence of arr_news_sentence)
    {
        news_sentence = news_sentence + ".";
        // 2024.10.31 : gtts 사용으로 주석처리
        // splitTextAndSpeakBySentence(news_sentence);
        speak(news_sentence);
    }
}

function callEngIdiom(keyno, groupno) {
    var in_keyno   = keyno;
    var in_groupno = groupno;

    $(".news_idiom").empty();

    $.ajax({
        url: BASE_URL + 'app_news_study/news_info_inf/',
        type: 'GET',
        data: {
            'keyno'  : in_keyno,
            'groupno': in_groupno,
        },
        beforeSend: function() {
            $(".news_idiom").empty(); // AJAX 호출 전에 컨텐츠 DIV 비우기
        },
        success: function(response) {
            var allText = "";  // 모든 텍스트를 이 변수에 저장
            $.each(response.rows, function (i, record) {
                allText += record[0] + "\n";  // 줄바꿈 문자를 추가
            });
            $(".news_idiom").val(allText);  // 최종 텍스트를 textarea에 설정
        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
};

$(document).ready(function() { // applied
    // 1초 동안 마우스 변경;
    setCursorShap(1000);
    iTextCnt = 0;

    // initAllTextArea();
    // applyActiveWordStyle();

    // 동적 html 에 함수적용이 아닌 window 에 함수 적용한다.
    // 동적 html 이전에 함수 적용이 가능함
    window.selectNewsTitle = function() {
        setCursorShap(3000);
        var rec_number  = 0
        // <textarea> 내용 초기화
        $('#txt_news_idiom').val('');

        var selectedKeyno = $('#titleList option:selected').val();
        var selectedTitle = $('#titleList option:selected').text();

        $.ajax({
            url: BASE_URL + 'app_news_study/news_info_eng/',
            type: 'GET',
            data: {
                'selected_keyno': selectedKeyno,
                'selected_title': selectedTitle,
            },
            beforeSend: function() {
                $(".content").empty(); // AJAX 호출 전에 컨텐츠 DIV 비우기
            },
            success: function(response) {
                var rec_news_eng_full = ""
                var contentDiv = $(".content"); // 컨텐츠를 추가할 부모 div
                $("#rows_cnt").val(response.rows_cnt);
                $("#ing_cnt").val(response.ing_cnt);
                iTextCnt = response.rows_cnt;

                $.each(response.rows, function (i, record) {
                    rec_number  = i + 1;
                    var rec_groupno = record[1]
                    var rec_keyno   = record[2]

                    var labelDivEng = $('<div>', {class: 'label-div'});
                    var buttonGroupEng = $('<div>', {class: 'label-button-group'});

                    // 영어 예제 부분
                    buttonGroupEng.append($('<label>', {
                        for: 'clearExampleEng' + i,
                        text: rec_number + '-EXAMPLE (ENG)',
                        style: 'color:red; font-weight:bold;'
                    })).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        id: 'clearExampleEng' + i,
                        text: 'Clear Text',
                        style: 'display : none'
                    }).on('click', function() { en_clearing(i); }) ).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        id: 'callEngIdiom' + i,
                        text: 'Idiom',
                        value: ""
                    }).on('click', function() {
                         var btnValue = $(this).val();  // 버튼의 value 값 가져오기
                         callEngIdiom(rec_keyno, btnValue); }) ).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        id: 'speakConvertEng' + i,
                        text: 'convt.Speaking',
                        style: 'background-color: #4D92AA'
                    }).on('click', function() {
                        $('#txt_eng_example'+ i).css("display", "none");
                        $('#artcl_wspace_content' + i).css("display", "block");
                        convert_speaking(i); })).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        id: 'speakExampleEng' + i,
                        text: 'Full Speaking'
                    }).on('click', function() {
                        $('#txt_eng_example'+ i).css("display", "block");
                        $('#artcl_wspace_content' + i).css("display", "none");
                        speaking(i); }) ).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        onclick: 'stopSpeaking()',
                        text: 'Stop'
                    }));

                    labelDivEng.append(buttonGroupEng);
                    labelDivEng.append($('<textarea>', {
                        id: 'txt_eng_example' + i,
                        rows: '5',
                        placeholder: 'Enter Example (ENG) here...'
                    }));
                    labelDivEng.append($('<textarea>', {
                        id: 'artcl_wspace_content' + i,
                        rows: '5',
                        style: 'display: none',
                        placeholder: 'Enter Example (ENG) here...'
                    }));
                    labelDivEng.append($('<textarea>', {
                        id: 'artcl_convert_content' + i,
                        rows: '5',
                        style: 'display : none',
                        placeholder: 'Enter Example (ENG) here...'
                    }));
                    labelDivEng.append($('<textarea>', {
                        id: 'artcl_org_content' + i,
                        rows: '5',
                        style: 'display : none',
                        placeholder: 'Enter Example (ENG) here...'
                    }));

                    // 한국어 예제 부분
                    var labelDivKor = $('<div>', {class: 'label-div'});
                    var buttonGroupKor = $('<div>', {class: 'label-button-group'});

                    buttonGroupKor.append($('<label>', {
                        for: 'clearExampleKor' + i,
                        text: rec_number + '-EXAMPLE (KOR)',
                        style: 'color:red; font-weight:bold;'
                    })).append('&nbsp;');

                    buttonGroupKor.append($('<button>', {
                        type: 'button',
                        id: 'clearExampleKor' + i,
                        text: 'Clear Text',
                        style: 'display : none'
                    }).on('click', function() { kr_clearing(i); }) ).append('&nbsp;');

                    labelDivKor.append(buttonGroupKor);
                    labelDivKor.append($('<textarea>', {
                        id: 'txt_kor_example' + i,
                        rows: '5',
                        placeholder: 'Enter Example (KOR) here...'

                    }));

                    if ( rec_number <= response.rows_cnt) {
                        // Div 추가
                        contentDiv.append(labelDivEng);
                        contentDiv.append(labelDivKor);
                    }
                });

                // 각 문단을 합친 전체 글을 마지막에 대입한다.
                // txt_eng_example300 의 300 은 특별한 의미가 없고 최대한 본 문단과 겹치지 않을 숫자로 젛한 것이다.
                var labelDivEng_full = $('<div>', {class: 'label-div'});
                labelDivEng_full.append($('<textarea>', {
                    id: 'txt_eng_example300',
                    rows: '10',
                    placeholder: 'Enter Example (ENG) here...'
                }));
                contentDiv.append(labelDivEng_full);

                $.each(response.rows, function (i, record) {
                    var rec_news_eng = ""
                    var rec_news_inf = ""
                    var rec_news_kor = ""

                    var rec_whitespace_converted = ""
                    var rec_converted_sentn      = ""
                    var rec_original_sentn       = ""

                    if ( i % 2 == 0 ) {
                        if (i == 0) tmp_eng_order = 0;
                        rec_news_eng = record[0];
                        rec_news_inf = record[1];
                        rec_whitespace_converted = record[3]
                        rec_converted_sentn      = record[4]
                        rec_original_sentn       = record[5]

                        $("#txt_eng_example"       + tmp_eng_order).val(rec_news_eng);
                        $("#artcl_wspace_content"  + tmp_eng_order).val(rec_whitespace_converted);
                        $("#artcl_convert_content" + tmp_eng_order).val(rec_converted_sentn);
                        $("#artcl_org_content"     + tmp_eng_order).val(rec_original_sentn);
                        $("#callEngIdiom"          + tmp_eng_order).val(rec_news_inf);
                        rec_news_eng_full += " " + rec_news_eng
                    } else {
                        rec_news_kor = record[0];
                        $("#txt_kor_example" + tmp_eng_order).val(rec_news_kor);
                        tmp_eng_order += 1
                    }
                });
                // txt_eng_example300 의 300 은 특별한 의미가 없고 최대한 본 문단과 겹치지 않을 숫자로 젛한 것이다.
                $("#txt_eng_example300").val(rec_news_eng_full);
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });

        $("#resMessage").val("");
    };

    // 일자별 기사 조회 버튼 클릭시
    $("#searchBtn").click(function() {
        // 10초 동안 마우스 변경
        setCursorShap(10000);
        var send_date = $('#news_date_list option:selected').val();
        window.location.href = BASE_URL + 'app_news_study/news_study/?selected_date=' + encodeURIComponent(send_date) ;
    });

    $("#completeButton").click(function() {
        // // 10초 동안 마우스 변경
        // setCursorShap(10000);
        //
        // var complt_title = $("#wrd_title").val();
        //
        // var data = {
        //     complt_word: $("#txt_word").val(),
        // };
        //
        // $.ajax({
        //     url: '/complete-word/',
        //     type: 'GET',
        //     data: data,
        //     success: function(response) {
        //       $("#resMessage").val(response.message);
        //       var complt_voca     = "completed-go-to-next-word";
        //       window.location.href = BASE_URL + 'app_news_study/news_study/?word=' + encodeURIComponent(complt_voca)  + '&wrd_title=' + encodeURIComponent(complt_title);
        //     },
        //     error: function(xhr, status, error) {
        //       $("#resMessage").val("error : " + error);
        //     }
        // });
    });

    // "Submit Article" 링크에 클릭 이벤트 리스너 추가
    $("#submitButton").click(function(e) {
        e.preventDefault(); // 기본 앵커 클릭 이벤트 중지
        $('#submitForm').submit(); // 폼 제출
    });

    $("#submitForm").submit(function(e) {
        e.preventDefault();
        // 10초 동안 마우스 변경
        setCursorShap(10000);
        $("#resMessage").val('Status: Starting');

        let sourceType  = "TOPS";
        let v_titleVaule = $('#titleList option:selected').val();
        let v_titleList  = $('#titleList option:selected').text().trim();
        let newsDateList = $('#news_date_list option:selected').text().trim();

        let sourceTitle = `Issue : ${newsDateList} : ${v_titleList}`;

        let articleContent = $("#txt_eng_example300").val();

        let sourceUrl = BASE_URL + "app_news_study/news_study/"+v_titleVaule;
        var new_url   = ""

        $.ajax({
            url: "/proj-common/submit_analysis_words/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "article": articleContent,
                "sourceUrl": sourceUrl,
                "sourceTitle": sourceTitle,
                "sourceType": sourceType
            }),
            success: function(response) {
                new_url = '/app_word_work/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&selected_date=' + encodeURIComponent(newsDateList) + '&source_status=C' + '&gubun=news';
                window.location.href = new_url;
            },
            error: function(xhr) {
                // Handle the error response
                // `xhr` is the XMLHttpRequest object
                let errorMessage = xhr.status + ': ' + xhr.statusText;
                $("#result").html("Error - " + errorMessage);
            }
        });
    });

    function convertExampleEng(news_text_no) {
        // 1초 동안 마우스 변경;
        setCursorShap(1000);
        var news_date = $('#news_date_list option:selected').val();
        let sourceTitle = $('#titleList option:selected').text();

        var articleContent = $("#txt_eng_example" + news_text_no).val();
        let sourceUrl  = BASE_URL + "app_news_study/news_study/?selected_date=" + news_date;
        let sourceType = "TOPS";

        $.ajax({
            url: "/app_news_study/news_convert_sentence/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "news_text_no" : news_text_no,
                "article"      : articleContent,
                "sourceUrl"    : sourceUrl,
                "sourceTitle"  : sourceTitle,
                "sourceType"   : sourceType,
                "news_date"    : news_date
            }),
            success: function (response) {
                $("#resMessage").val("OK");
                var res_news_text_no = response.news_text_no;
                var res_rslt_sentns = response.list_rslt_sentns;

                if (res_rslt_sentns.length > 0) {
                    var v_artcl_wspace_content  = "#artcl_wspace_content" + res_news_text_no;
                    var v_artcl_convert_content = "#artcl_convert_content" + res_news_text_no;
                    var v_artcl_org_content     = "#artcl_org_content" + res_news_text_no;

                    let i = 0;
                    let res_wspc_rslt_sentn   = "";
                    let res_convert_rslt_sentn= "";
                    let res_org_rslt_sentn    = "";

                    for (res_rslt_sentn of res_rslt_sentns)
                    {
                        i += 1;
                        if (i === 1) {
                            res_wspc_rslt_sentn     = res_rslt_sentn[0];
                            res_convert_rslt_sentn  = res_rslt_sentn[1];
                            res_org_rslt_sentn      = res_rslt_sentn[2];
                        } else {
                            res_wspc_rslt_sentn     += "\n" + res_rslt_sentn[0];
                            res_convert_rslt_sentn  += "..." + res_rslt_sentn[1];
                            res_org_rslt_sentn      += "..." + res_rslt_sentn[2];
                        }
                    }

                    $(v_artcl_wspace_content).val(res_wspc_rslt_sentn);
                    $(v_artcl_convert_content).val(res_convert_rslt_sentn);
                    $(v_artcl_org_content).val(res_org_rslt_sentn);
                }
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.status + ': ' + xhr.statusText;
                $("#result").html("Error - " + errorMessage);
            }
        });
    }

    selectNewsTitle();
 });