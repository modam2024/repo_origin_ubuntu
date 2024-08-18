    $(document).ready(function() {

        let init_fix_currentTime = $("#topicDurStart").val();
        let end_fix_currentTime  = $("#topicDurEnd").val();

        let pause_currentTime = 0;
        replaceText();

        // play 버튼 클릭시
        $("#start").click(function(){
            let audioElement = $('#myAudio');

            audioElement[0].currentTime=15;
            $("#topic_dur_start").val(audioElement[0].currentTime);
            $("#topic_dur_end").val(audioElement[0].duration-15);

            saveTopicInfo();

            audioElement[0].play();
        });

        // front 버튼 클릭시
        $("#front").click(function(){
            let audioElement = $('#myAudio');
            audioElement[0].pause();

            $("#topic_dur_start").val(15);

            if ( Number(init_fix_currentTime) <= 15 ) {
                $("#topic_dur_end").val(15);
            } else {
                $("#topic_dur_end").val(Number(init_fix_currentTime) - 2);
            }

            if ( Number(init_fix_currentTime) > 15 ) {
                if (pause_currentTime > 15)
                   audioElement[0].currentTime = pause_currentTime;
                else
                    audioElement[0].currentTime = 15;
                document.getElementsByClassName("audio-btn")[0].style.backgroundColor = "gray";
                audioElement[0].play();
            } else {
                alert("기간이 셋팅되지 않았습니다.");
            }

            audioElement = null;
        });

        $("#submitForm").submit(function(e) {
            e.preventDefault();
            $("#resMessage").val('Status: Starting');
            let hddnUrl = $('#hddn_url');
            
            let articleContent = $("#artcl_content1").val()+ $("#artcl_content3").val();
            let selChapter = $("#selChapter").val();
            let sourceUrl  = hddnUrl.val();
            if (sourceUrl === "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx=")
               sourceUrl   = sourceUrl + selChapter;
            
            hddnUrl.val(sourceUrl)
               
            let sourceTitle = $("#selTitle").val();
            let sourceType  = $("#searchGrpCd").val();

            $.ajax({
                url: "/article/submit-article/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    "article": articleContent,
                    "sourceUrl": sourceUrl,
                    "sourceTitle": sourceTitle,
                    "sourceType": sourceType
                }),
                success: function(response) {
                    $("#resMessage").val("Count: " +  response.word_insert_count + " / " + response.word_count + ", Message: " + response.message);
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
            let sourceUrl   = $("#hddn_url").val();
            let sourceTitle = $("#selChapter").val();
            let sourceType  = $("#searchGrpCd").val();
            let url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&source_status=C';
            //window.location.href = url;
            window.open(url, '_blank');
        });
        
        $("#searchButton").click(function() {
            $("#resMessage").val("조회 중입니다.");
            let selectdChapter = $('#titleList option:selected').val();
            let url = BASE_URL + "article/living-english/?chapter="+selectdChapter+"&status=C";
            window.open(url, '_self');
        });
        
        $("#completeButton").click(function() {
            // 선택된 라디오 버튼의 value와 기타 필요한 데이터를 객체로 구성합니다.
            let checked_data = {
                test_answer1: $('input[name="question1"]:checked').val(),
                test_answer2: $('input[name="question2"]:checked').val(),
                test_answer3: $('input[name="question3"]:checked').val(),
                test_order_no: $("#test_order_no").val(),
                test_page_date: $("#test_page_date").val(),
            };

            var url = BASE_URL + "article/feedback-english/?" + $.param(checked_data);
            window.location.href = url;
        });

        // TEST ENGLISH 클릭 이벤트
        $("#backButton").click(function() {
            $("#resMessage").val("테스트 페이지로 이동중입니다.");
            let back_data = {
                check:   "none",
                status:  "C",
                wdate:   $("#test_page_date").val(),
            };
            var url = BASE_URL + "article/test-english/?" + $.param(back_data);
            window.location.href = url;
        });

        // #2024.03.20-titleList 셀렉터에 대한 change 이벤트 핸들러를 설정
        $("#titleList").change(function() {
            // 옵션이 선택될 때 #searchButton 버튼의 클릭 이벤트를 트리거함
            $('#searchButton').click();
        });

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
        
        // txt_word 값과 일치하는 word 링크에 스타일 적용하는 함수
        function applyActiveWordStyle() {
            // 현재 txt_word 값 가져오기
            let currentWord = $('#txt_word').val();
            let chapterLink = $('.chapter-link');
    
            // 모든 word 링크의 스타일 초기화
            chapterLink.removeClass('active-chapter');
    
            // txt_word 값과 일치하는 링크에 스타일 적용
            chapterLink.each(function() {
                if ($(this).text().trim() === currentWord) {
                    $(this).addClass('active-chapter');
                }
            });
        }

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
    });
    