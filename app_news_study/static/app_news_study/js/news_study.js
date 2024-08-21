// 단어 클릭 이벤트 핸들러 추가
function speaking(order) {
    var news_sentence = $("#txt_eng_example"+order).val();
    splitTextAndSpeak(news_sentence);
};

// proj_mdm_prep 사용
function callEngIdiom(keyno, groupno) {
    var in_keyno   = keyno;
    var in_groupno = groupno;

    $(".news_idiom").empty();

    $.ajax({
        url: BASE_URL + 'news_study/news_info_inf/',
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

$(document).ready(function() {

    // initAllTextArea();
    // applyActiveWordStyle();

    // 동적 html 에 함수적용이 아닌 window 에 함수 적용한다.
    // 동적 html 이전에 함수 적용이 가능함
    window.selectNewsTitle = function() {
        // <textarea> 내용 초기화
        $('#txt_news_idiom').val('');

        var selectedKeyno = $('#titleList option:selected').val();

        $.ajax({
            url: BASE_URL + 'news_study/news_info_eng/',
            type: 'GET',
            data: {
                'selected_keyno': selectedKeyno,
            },
            beforeSend: function() {
                $(".content").empty(); // AJAX 호출 전에 컨텐츠 DIV 비우기
            },
            success: function(response) {
                $("#rows_cnt").val(response.rows_cnt);

                $.each(response.rows, function (i, record) {
                    var rec_number  = i + 1;
                    var rec_groupno = record[1]
                    var rec_keyno   = record[2]

                    var contentDiv = $(".content"); // 컨텐츠를 추가할 부모 div

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
                        text: 'Clear Text'
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
                        id: 'speakExampleEng' + i,
                        text: 'Speaking'
                    }).on('click', function() { speaking(i); }) ).append('&nbsp;');

                    buttonGroupEng.append($('<button>', {
                        type: 'button',
                        onclick: 'stopSpeaking()',
                        text: 'Stop Speaking'
                    }));

                    labelDivEng.append(buttonGroupEng);
                    labelDivEng.append($('<textarea>', {
                        id: 'txt_eng_example' + i,
                        rows: '5',
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
                        text: 'Clear Text'
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

                $.each(response.rows, function (i, record) {
                    var rec_news_eng = ""
                    var rec_news_inf = ""
                    var rec_news_kor = ""

                    if ( i % 2 == 0 ) {
                        if (i == 0) tmp_eng_order = 0;
                        rec_news_eng = record[0];
                        rec_news_inf = record[1];
                        $("#txt_eng_example" + tmp_eng_order).val(rec_news_eng);
                        $("#callEngIdiom"    + tmp_eng_order).val(rec_news_inf);
                    } else {
                        rec_news_kor = record[0];
                        $("#txt_kor_example" + tmp_eng_order).val(rec_news_kor);
                        tmp_eng_order += 1
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });

        $("#resMessage").val("");
    };

    // 일자별 기사 조회 버튼 클릭시
    $("#searchBtn").click(function() {
        var send_date = $('#searchGrpCd option:selected').val();
        window.location.href = BASE_URL + 'news_study/?selected_date=' + encodeURIComponent(send_date) ;
    });

    //proj_mdm_prep 사용
    $("#submitButton").click(function() {
        var data = {
        };

        $.ajax({
            url: '/save-wordinfo/',
            type: 'GET',
            data: data,
            success: function(response) {
              $("#resMessage").val(response.message);
            },
            error: function(xhr, status, error) {
              $("#resMessage").val("error : " + error);
            }
        });
    });

    //proj_mdm_prep 사용
    $("#submitButton").click(function() {
        var data = {
        };

        $.ajax({
            url: '/save-wordinfo/',
            type: 'GET',
            data: data,
            success: function(response) {
              $("#resMessage").val(response.message);
            },
            error: function(xhr, status, error) {
              $("#resMessage").val("error : " + error);
            }
        });
    });

    //proj_mdm_prep 사용
    $("#completeButton").click(function() {

       var complt_title = $("#wrd_title").val();

        var data = {
            complt_word: $("#txt_word").val(),
        };

        $.ajax({
            url: '/complete-word/',
            type: 'GET',
            data: data,
            success: function(response) {
              $("#resMessage").val(response.message);
              var complt_voca     = "completed-go-to-next-word";
              window.location.href = BASE_URL + 'news_study/?word=' + encodeURIComponent(complt_voca)  + '&wrd_title=' + encodeURIComponent(complt_title);
            },
            error: function(xhr, status, error) {
              $("#resMessage").val("error : " + error);
            }
        });
    });

    // proj_mdm_prep 사용
    $(document).on('blur', 'textarea:not(.news_idiom)', function(e) {
        $("#submitButton").click();
    });

    selectNewsTitle();
 });