    function  artcl_contents_display() {
        $('#artcl_content1').css("display", "block");
        $('#artcl_wspace_content1').css("display", "none");
        $('#artcl_org_content1').css("display", "none");
        $('#artcl_content2').css("display", "block");
        $('#artcl_wspace_content2').css("display", "none");
        $('#artcl_org_content2').css("display", "none");
        $('#artcl_content3').css("display", "block");
        $('#artcl_wspace_content3').css("display", "none");
        $('#artcl_org_content3').css("display", "none");
    }

    // 변환된 문장의 스피킹 실행
    function setupSpeakConvEngHandler(index) {
        $("#speakConvEng" + index).click(function() {
            // 1초 동안 마우스 변경;
            setCursorShap(1000);
            artcl_contents_display();

            if (index == 1) {
                $('#artcl_content1').css(       "display", "none");
                $('#artcl_wspace_content1').css("display", "block");
            } else if (index == 2) {
                $('#artcl_content2').css(       "display", "none");
                $('#artcl_wspace_content2').css("display", "block");
            } else if (index == 3) {
                $('#artcl_content3').css(       "display", "none");
                $('#artcl_wspace_content3').css("display", "block");
            }

            var text = $('#artcl_wspace_content' + index).val().trim();
            splitTextAndSpeakBySentence(text);
        });
    }

    // 함수를 정의합니다. 이 부분은 페이지의 스크립트 섹션 어디에서나 위치할 수 있으나,
    // 일반적으로는 스크립트 섹션의 시작 부분에 위치합니다.
    function setupSpeakOrgEngHandler(index) {
        $("#speakExampleEng" + index).click(function() {
            // 1초 동안 마우스 변경;
            setCursorShap(1000);
            artcl_contents_display();

            if (index == 1) {
                $('#artcl_content1').css(    "display", "none");
                $('#artcl_org_content1').css("display", "block");
            } else if (index == 2) {
                $('#artcl_content2').css(    "display", "none");
                $('#artcl_org_content2').css("display", "block");
            } else if (index == 3) {
                $('#artcl_content3').css(    "display", "none");
                $('#artcl_org_content3').css("display", "block");
            }

            var text = $('#artcl_org_content' + index).val().trim();
            splitTextAndSpeakBySentence(text);
        });
    }

    $(document).ready(function() { // applied
        // 1초 동안 마우스 변경;
        setCursorShap(1000);

        let pause_currentTime = 0;
        replaceText();

        // $("#submitForm").submit(function(e) {
        //     e.preventDefault();
        //     $("#resMessage").val('Status: Starting');
        //     let hddnUrl = $('#hddn_url');
        //
        //     let articleContent = $("#artcl_content1").val()+ $("#artcl_content3").val();
        //     let selChapter = $("#selChapter").val();
        //     let sourceUrl  = hddnUrl.val();
        //     if (sourceUrl === "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx=")
        //        sourceUrl   = sourceUrl + selChapter;
        //
        //     hddnUrl.val(sourceUrl)
        //
        //     let sourceTitle = $("#selTitle").val();
        //     let sourceType  = $("#searchGrpCd").val();
        //
        //     $.ajax({
        //         url: "/article/submit-article/",
        //         type: "POST",
        //         contentType: "application/json",
        //         data: JSON.stringify({
        //             "article": articleContent,
        //             "sourceUrl": sourceUrl,
        //             "sourceTitle": sourceTitle,
        //             "sourceType": sourceType
        //         }),
        //         success: function(response) {
        //             $("#resMessage").val("Count: " +  response.word_insert_count + " / " + response.word_count + ", Message: " + response.message);
        //         },
        //         error: function(xhr) {
        //             // Handle the error response
        //             // `xhr` is the XMLHttpRequest object
        //             let errorMessage = xhr.status + ': ' + xhr.statusText;
        //             $("#result").html("Error - " + errorMessage);
        //         }
        //     });
        // });
        
        $('#clearButton').click(function() {
            $('#artcl_content').val("");
            $('#src_url').val("");
            $('#src_title').val("");
            $('#src_type option:eq(0)').prop('selected', true);
            $('#result').html("");
        });

        $("#wordCheckButton").click(function(e) {
            e.preventDefault();
            let sourceUrl   = $("#hddn_url").val();
            let sourceTitle = $("#selChapter").val();
            let sourceType  = $("#searchGrpCd").val();

            let url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&source_status=C';
            //window.location.href = url;
            window.open(url, '_blank');
        });

        // TEST ENGLISH 클릭 이벤트
        $("#backButton").click(function() {
            // 10초 동안 마우스 변경
            setCursorShap(10000);

            $("#resMessage").val("테스트 페이지로 이동중입니다.");

            let back_data = {
                check:   "none",
                status:  "C",
                wdate:   $("#test_page_date").val(),
            };
            var url = BASE_URL + "app_test_timer/test-english/?" + $.param(back_data);
            window.location.href = url;
        });

        // #2024.03.20-titleList 셀렉터에 대한 change 이벤트 핸들러를 설정
        $("#titleList").change(function() {
            // 옵션이 선택될 때 #searchButton 버튼의 클릭 이벤트를 트리거함
            $('#searchButton').click();
        });

        function convertExampleEng(question_no) {
            // 1초 동안 마우스 변경;
            setCursorShap(1000);
            var test_order_no  = $("#test_order_no").val();
            var test_page_date = $("#test_page_date").val();

            let sourceTitle = `Part 5 : ${test_order_no} : ${test_page_date}`;

            var articleContent = $("#artcl_content" + question_no).val();
            let sourceUrl  = BASE_URL + "app_test_timer/feedback-english/?&test_order_no=" + test_order_no + "&test_page_date=" + test_page_date;
            let sourceType = "YBM(TEST)";

            $.ajax({
                url: "/app_test_timer/convert_sentence/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    "question_no" : question_no,
                    "article"     : articleContent,
                    "sourceUrl"   : sourceUrl,
                    "sourceTitle" : sourceTitle,
                    "sourceType"  : sourceType,
                    "topic_num"   : test_order_no
                }),
                success: function (response) {
                    $("#resMessage").val("OK");
                    var res_question_no = response.question_no;
                    var res_rslt_sentns = response.list_rslt_sentns;

                    if (res_rslt_sentns.length > 0) {
                        var v_artcl_wspace_content = "#artcl_wspace_content" + res_question_no;
                        var v_artcl_org_content    = "#artcl_org_content" + res_question_no;
                        // 첫 번째 결과만 사용
                        $(v_artcl_wspace_content).val(res_rslt_sentns[0][0]);
                        $(v_artcl_org_content).val(res_rslt_sentns[0][2]);
                    }
                },
                error: function (xhr, status, error) {
                    var errorMessage = xhr.status + ': ' + xhr.statusText;
                    $("#result").html("Error - " + errorMessage);
                }
            });
        }

        $("#convertExampleEng1").click(function() {
            convertExampleEng(1);
        });
        $("#convertExampleEng2").click(function() { convertExampleEng(2); });
        $("#convertExampleEng3").click(function() { convertExampleEng(3); });

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

        // 원문 예문 클릭 이벤트 핸들러 추가
        setupSpeakOrgEngHandler(1);
        setupSpeakOrgEngHandler(2);
        setupSpeakOrgEngHandler(3);

        // 변환 예문 클릭 이벤트 핸들러 추가
        setupSpeakConvEngHandler(1);
        setupSpeakConvEngHandler(2);
        setupSpeakConvEngHandler(3);

        $('#convertExampleEng1').click();
        $('#convertExampleEng2').click();
        $('#convertExampleEng3').click();
    });
    