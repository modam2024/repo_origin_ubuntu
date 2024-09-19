    $(document).ready(function() { // applied
        // 1초 동안 마우스 변경;
        setCursorShap(1000);

        // Part 5 테스트 문제의 밑줄을 만들어 주는 함수
        replaceText();

        // WORD CLASS LIST 클릭 이벤트
        $("#wordClassList").click(function(e) {
            e.preventDefault();
            window.location.href = BASE_URL + 'article/';
        });

        $("#prve_page_flag_y").click(function(e) {
            e.preventDefault();
            // 20초 동안 마우스 변경
            setCursorShap(20000);
            $("#resMessage").val("조회 중입니다.");
            $(this).css('background-color', 'lightgray');
            str_prve_page_date = $("#prve_page_date").val();
            window.location.href = BASE_URL + 'app_test_timer/test-english/?wdate='+str_prve_page_date +'&check=none&chapter=&status=C';
        });

        $("#last_page_flag_y").click(function(e) {
            e.preventDefault();
            // 20초 동안 마우스 변경
            setCursorShap(20000);
            $("#resMessage").val("조회 중입니다.");
            $(this).css('background-color', 'lightgray');
            str_next_page_date = $("#next_page_date").val();
            window.location.href = BASE_URL + 'app_test_timer/test-english/?wdate='+str_next_page_date +'&check=none&chapter=&status=C';
        });

        // "Submit Article" 링크에 클릭 이벤트 리스너 추가
        $('#submitButton').click(function(e) {
            e.preventDefault(); // 기본 앵커 클릭 이벤트 중지
            $('#submitForm').submit(); // 폼 제출
        });

        $("#submitForm").submit(function(e) {
            e.preventDefault();
            // 10초 동안 마우스 변경
            setCursorShap(10000);
            $("#resMessage").val('Status: Starting');

            let sourceType  = "YBM(TEST)";
            let selChapter  = $('#pagedateList option:selected').val();
            let arr_pagedateList = $('#pagedateList option:selected').text().trim().split(":")
            let v_pagedateList = arr_pagedateList[0].trim()

            let sourceTitle = `Part 5 : ${selChapter} : ${v_pagedateList}`;

            let articleContent = $("#artcl_content1").val() + " " + $("#artcl_content2").val() + " " + $("#artcl_content3").val() + " ";
            articleContent += $("#lbl_a1").text() + " " + $("#lbl_a2").text() + " " + $("#lbl_a3").text() + " "
            articleContent += $("#lbl_b1").text() + " " + $("#lbl_b2").text() + " " + $("#lbl_b3").text() + " "
            articleContent += $("#lbl_c1").text() + " " + $("#lbl_c2").text() + " " + $("#lbl_c3").text() + " "

            let sourceUrl   = BASE_URL + "app_test_timer/test-english/?trgt_order_no=" + selChapter;
            let test_page_date     = $('#test_page_date').val();

            var new_url = ""
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
                    new_url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&test_page_date=' + encodeURIComponent(test_page_date) + '&source_status=C' + '&gubun=test';
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
        
        $('#clearButton').click(function() {
            $('#artcl_content').val("");
            $('#src_url').val("");
            $('#src_title').val("");
            $('#src_type option:eq(0)').prop('selected', true);
            $('#result').html("");
        });

        $("#wordCheckButton").click(function(e) {
            e.preventDefault();
            // 10초 동안 마우스 변경
            setCursorShap(10000);

            let sourceUrl   = $("#hddn_url").val();
            let sourceTitle = $("#selChapter").val();
            let sourceType  = $("#searchGrpCd").val();
            let url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&source_status=C';
            //window.location.href = url;
            window.open(url, '_blank');
        });
        
        $("#searchButton").click(function() {
            // 10초 동안 마우스 변경
            setCursorShap(10000);
            $("#resMessage").val("조회 중입니다.");

            let selectdChapter = $('#titleList option:selected').val();
            let url = BASE_URL + "article/living-english/?chapter="+selectdChapter+"&status=C";
            window.open(url, '_self');
        });

        $("#feedbackButton").click(function() {
            let sel_orderno      = $('#pagedateList').val();
            let selectedText     = $('#pagedateList option:selected').text();
            let arr_selectedText = selectedText.split(":");
            selectedText         = arr_selectedText[0].trim();
            let sel_feqno        = parseInt(arr_selectedText[1].trim());

            if (sel_feqno > 0) {
                let feedback_url = BASE_URL + "app_test_timer/feedback-english/?&test_order_no=" + sel_orderno + "&test_page_date=" + selectedText;
                window.open(feedback_url, "_blank")
            } else {
                alert("제출된 회차가 없습니다.")
            }
        });

        $("#completeButton").click(function() {
            // 10초 동안 마우스 변경
            setCursorShap(10000);

            let opt_ans1   = $('input[name="question1"]:checked').val() || "1";
            let opt_ans2   = $('input[name="question2"]:checked').val() || "2";
            let opt_ans3   = $('input[name="question3"]:checked').val() || "3";

            let test_time1 = parseInt($("#stop_time1").text(), 10);
            let test_time2 = parseInt($("#stop_time2").text(), 10);
            let test_time3 = parseInt($("#stop_time3").text(), 10);

            let sum_test_time = test_time1 + test_time2 + test_time3;

            if (sum_test_time === 0) {
                alert("문제 푼 시간이 0 입니다.");
                $('body, body *').css('cursor', 'default');
                return;  // 함수 실행 중단
            }

            let unselected = [];
            if (opt_ans1 === "1") { unselected.push("문제 1"); }
            if (opt_ans2 === "2") { unselected.push("문제 2"); }
            if (opt_ans3 === "3") { unselected.push("문제 3"); }

            if ( unselected.length > 0 && unselected.length < 3 ) {
                alert("정답 선택이 안된 문제가 있습니다: [" + unselected.join(", ") + "]");
                $('body, body *').css('cursor', 'default');
                return;  // 함수 실행 중단
            }

            let checked_data = {
                test_answer1: opt_ans1,
                test_answer2: opt_ans2,
                test_answer3: opt_ans3,
                test_time1  : test_time1,
                test_time2  : test_time2,
                test_time3  : test_time3,
                test_order_no: $("#test_order_no").val(),
                test_page_date: $("#test_page_date").val(),
            };

            $.ajax({
                url: "/app_test_timer/test-result/",
                type: 'GET',
                data: checked_data,
                success: function(response) {
                    var url = BASE_URL + "app_test_timer/feedback-english/?" + $.param(checked_data);
                    // 데이터 전송 전에 일시적으로 지연을 주고 페이지 이동
                    setTimeout(function() {
                        window.location.href = url;
                        // 페이지가 이동하면 자동으로 커서가 원래 상태로 돌아갈 것입니다
                    }, 2000); // 2초 동안 기다린 후 페이지 이동
                },
                error: function(xhr, status, error) {
                  $("#resMessage").val("error : " + error);
                }
            });
        });

        // #2024.03.20-titleList 셀렉터에 대한 change 이벤트 핸들러를 설정
        $("#titleList").change(function() {
            // 옵션이 선택될 때 #searchButton 버튼의 클릭 이벤트를 트리거함
            $('#searchButton').click();
        });

        // ############################
        //          FUNCTION 끝
        // ############################

        // 모든 '.chapter-link' 클래스를 가진 <a> 태그에 대해 클릭 이벤트 리스너를 추가
        // 동적으로 클래스명이 구성되기 때문에 상위의 document 에 이벤트를 전달한다.
        $(document).on('click', '.chapter-link', function(e) {
            e.preventDefault();
            let selectd_chapter = $(this).attr('href'); // 목표 URL 추출
            let data = {
                selectd_chapter: selectd_chapter,
            };
            $.ajax({
                url: '/article/uncomplete-chapter/',
                type: 'GET',
                data: data,
                success: function() {
                  $("#resMessage").val("미완료 처리 했습니다.");
                  $("#searchButton").click();
                },
                error: function(xhr, status, error) {
                  $("#resMessage").val("미완료처리 오류 발생 : " + error);
                }
            });
        });

        let selChapter = $("#selChapter").val();
        let newCount   = $('#newCount').val();
        if (selChapter === '') {
            let firstOptionValue = $('#titleList option:first').val();
            $('#selChapter').val(firstOptionValue);
        } else {
            $('#selChapter').val(selChapter);
            $('#titleList').val(selChapter);
        }
        if (newCount > 0) {
           $("#resMessage").val(newCount+ " 건 생성 완료했습니다.");
        } else {
           $("#resMessage").val("조회 완료했습니다.");          
        }

        if ( Number($('#topicDurStart').val()) > 0 && Number($('#topicDurEnd').val()) > 0) {
            let audioBtn = $(".audio-btn");
            audioBtn.css("background-color", "#8C0028");
            audioBtn.css("color", "white");
        } else {
            $('#front').prop("disabled", true);
            $('#play').prop("disabled", true);
            $('#back').prop("disabled", true);
        }

        // 모든 textarea 요소를 선택하고 각 요소에 대해 함수를 실행합니다.
        $('textarea').each(function() {
            var currentText = $(this).val();
            $(this).val(currentText.replace(/\n/g, " "));
            $(this).val(currentText.replace(/  /g, " "));
        });

        $('#start_btn').click(function() {
            // 타이머가 이미 작동 중인지 확인
            if (!timerInterval) {
                timerInterval = setInterval(function() {
                    remainingTime -= 1;
                    var seconds = Math.abs(remainingTime);  // 음수가 되면 절대값을 사용하여 표시

                    // 초를 화면에 표시, 음수일 때는 부호를 유지
                    $('#time').text((remainingTime < 0 ? "-" : "") + seconds.toString().padStart(2, '0') + " 초");

                }, 1000);
            }
        });

        // 라디오 버튼 클릭 이벤트 핸들러를 각 문제에 대해 설정
        ['question1', 'question2', 'question3'].forEach(function(question, index) {
            $('input[type="radio"][name="' + question + '"]').click(function() {
                var init_time = $('#stop_time' + (index + 1)).text(); // 텍스트를 가져옴
                init_time = parseInt(init_time, 10); // 문자열을 정수로 변환

                // 타이머가 작동 중인지 확인
                if (timerInterval) {
                    var timeSpent = lastRemainingTime - remainingTime;

                    timeSpent = parseInt(timeSpent, 10) + init_time;

                    // 다른 질문이 선택되었다면 새로운 시간을 표시
                    $('#stop_time' + (index + 1)).text(timeSpent);

                    // 현재 질문을 마지막 질문으로 업데이트
                    lastQuestion = question;
                    lastRemainingTime = remainingTime;
                }
            });
        });

        $("#resMessage").val("조회가 완료됐습니다.");
    });
