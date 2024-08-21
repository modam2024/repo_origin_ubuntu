    $(document).ready(function() {

        let init_fix_currentTime = $("#topicDurStart").val();
        let end_fix_currentTime  = $("#topicDurEnd").val();

        let pause_currentTime = 0;

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

        // back 버튼 클릭시
        $("#back").click(function(){
            let audioElement = $('#myAudio');
            audioElement[0].pause();

            $("#topic_dur_start").val(end_fix_currentTime + 1);

            if ( Number(end_fix_currentTime) <= 15 ) {
                $("#topic_dur_end").val(15);
            } else {
                $("#topic_dur_end").val(audioElement[0].duration-15);
            }

            if ( Number(end_fix_currentTime) > 15 ) {
                if ( pause_currentTime > (end_fix_currentTime + 1) )
                   audioElement[0].currentTime = pause_currentTime;
                else
                   audioElement[0].currentTime = end_fix_currentTime + 1;
                document.getElementsByClassName("audio-btn")[2].style.backgroundColor = "gray";
                audioElement[0].play();
            } else {
                alert("기간이 셋팅되지 않았습니다.");
            }

            audioElement = null;
        });

        // play 버튼 클릭시
        $("#play").click(function() {
            let audioElement  = $('#myAudio');
            let topicDurStart = $('#topic_dur_start');
            let topicDurEnd   = $('#topic_dur_end');

            audioElement[0].pause();

            topicDurStart.val(init_fix_currentTime);
            topicDurEnd.val(end_fix_currentTime);

            if (pause_currentTime > init_fix_currentTime)
               audioElement[0].currentTime = pause_currentTime;
            else
               audioElement[0].currentTime = init_fix_currentTime;

            if (Number(end_fix_currentTime) === 0)
            {
               topicDurEnd.val(audioElement[0].duration);
            }

            audioElement[0].play();
            audioElement = null;
        });

        // stop 버튼 클릭시
        $("#fix").click(function(){
            let audioElement = $('#myAudio');
            let audioBtn     = $(".audio-btn");
            let topicDurEnd  = $("#topic_dur_end");

            audioBtn.css("background-color", "#8C0028");
            audioBtn.css("color", "white");

            if (Number( topicDurEnd.val() ) === 0) {
               topicDurEnd.val(audioElement[0].duration-15);
               end_fix_currentTime = audioElement[0].duration-15;
            }

            saveTopicInfo();

            $("#searchButton").click();
            audioElement = null;
        });

        // stop 버튼 클릭시
        $("#pause").click(function(){
            let audioElement = $('#myAudio');
            audioElement[0].pause();
            pause_currentTime = audioElement[0].currentTime;
            audioElement = null;
        });

        $("#s_point").click(function() {
            let audioElement = $('#myAudio');
            audioElement[0].pause();
            $("#topic_dur_start").val(audioElement[0].currentTime);
            audioElement[0].play();
        });

        $("#e_point").click(function() {
            let audioElement = $('#myAudio');
            audioElement[0].pause();
            $("#topic_dur_end").val(audioElement[0].currentTime);
        });

        $('#myAudio').get(0).addEventListener("timeupdate", function(){
            let audioElement = $('#myAudio');
            let start_time_val = $("#topic_dur_start").val();
            let end_time_val   = $("#topic_dur_end").val();

            // duration 범위를 반복 재생하는 기능
            if (audioElement[0].currentTime > parseInt(end_time_val) &&
                parseInt(end_time_val) > 0 )
            {
                audioElement[0].currentTime = start_time_val;
                audioElement[0].play();
            }
            audioElement = null;
        });

        //Topic Info insert/update ajax function
        function saveTopicInfo()
        {
            let objTopicNum      = document.getElementById("selChapter");
            let objAudioFileDate = document.getElementById("audioNameText");
            let objVolumeSize    = "10";
            let objTopicKr       = document.getElementById("selTitle");
            let objTopicEn       = "N";
            let objTopicDurStart = document.getElementById("topic_dur_start");
            let objTopicDurEnd   = document.getElementById("topic_dur_end");

            let strTopicNum      = objTopicNum.value;
            let strAudioFileDate = objAudioFileDate.value;
            let strVolumeSize    = objVolumeSize;
            let strTopicKr       = objTopicKr.value;
            let strTopicEn       = objTopicEn;
            let strTopicDurStart = objTopicDurStart.value;
            let strTopicDurEnd   = objTopicDurEnd.value;

            $.ajax({
                url: "/article/save-topic/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    "topic_num": strTopicNum,
                    "audio_file_date": strAudioFileDate,
                    "volume_size": strVolumeSize,
                    "topic_kr": strTopicKr,
                    "topic_en": strTopicEn,
                    "topic_dur_start": strTopicDurStart,
                    "topic_dur_end": strTopicDurEnd,
                }),
                success: function() {
                    $("#resMessage").val("save_topic OK");
                },
                error: function(xhr) {
                    // Handle the error response
                    // `xhr` is the XMLHttpRequest object
                    let errorMessage = xhr.status + ': ' + xhr.statusText;
                    $("#result").html("Error - " + errorMessage);
                }
            });
        }
        /*** Audio Play 로직 끝 (2024.03.14) ***/

        let tmpGrpCd = "YBM(TALK)";
        $('#searchGrpCd').val(tmpGrpCd);
        
        applyActiveWordStyle();

        $("#myAudio").prop("volume", 0.4);

        // WORD CLASS LIST 클릭 이벤트
        $("#wordClassList").click(function(e) {
            e.preventDefault();
            window.location.href = BASE_URL + 'article/';
        });

        // "Submit Article" 링크에 클릭 이벤트 리스너 추가
        $('#submitButton').click(function(e) {
            e.preventDefault(); // 기본 앵커 클릭 이벤트 중지
            $('#submitForm').submit(); // 폼 제출
        });

        $("#submitForm").submit(function(e) {
            e.preventDefault();
            $("#resMessage").val('Status: Starting');
            let hddnUrl = $('#hddn_url');

            let artclContent1 = $("#artcl_content1").val();
            let artclContent2 = $("#artcl_content2").val();
            let artclContent3 = $("#artcl_content3").val();
            let articleContent = $("#artcl_content1").val()+ $("#artcl_content3").val();

            let selChapter = $("#selChapter").val();
            let sourceUrl  = hddnUrl.val();
            if (sourceUrl === "https://free.ybmclass.com/free/eng/eng_ybm_view.asp?idx=")
               sourceUrl   = sourceUrl + selChapter;
            
            hddnUrl.val(sourceUrl)
               
            let sourceTitle = $("#selTitle").val();
            let sourceType  = $("#searchGrpCd").val();

            $.ajax({
                url: "/article/morph_analysis/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    "article": articleContent,
                    "artclContent1": artclContent1,
                    "artclContent2": artclContent2,
                    "sourceUrl": sourceUrl,
                    "sourceTitle": sourceTitle,
                    "sourceType": sourceType
                }),
                success: function(response) {
                    var res_check = response.status;
                    if ( res_check == "check" ) {
                        $("#resMessage").val(" Message: " + response.message);
                    } else {
                        $("#resMessage").val("Count: " +  response.word_insert_count + " / " + response.word_count + ", Message: " + response.message);
                    }
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

        $("#cnvrtTpcButton").click(function(e) {
            e.preventDefault();
            let sourceTitle = $("#selChapter").val();
            let sourceType  = $("#searchGrpCd").val();
            let url = '/article/cnvrt_tpc_exec/?topic_num=' + encodeURIComponent(sourceTitle);
            window.open(url, '_blank');
        });
        
        $("#searchButton").click(function() {
            $("#resMessage").val("조회 중입니다.");
            let selectdChapter = $('#titleList option:selected').val();
            let url = BASE_URL + "article/living-english/?chapter="+selectdChapter+"&status=C";
            window.open(url, '_self');
        });
        
        $("#completeButton").click(function() {
            $("#resMessage").val("완료 처리 중입니다.");
            let selectd_chapter = $('#titleList option:selected').val();
            let data = {
                selectd_chapter: selectd_chapter,
            };
            $.ajax({
                url: '/article/complete-chapter/',
                type: 'GET',
                data: data,
                success: function(response) {
                  $("#resMessage").val("완료 했습니다.");
                  $('#titleList').val(response.complete_chapter);
                  $("#searchButton").click();
                },
                error: function(xhr, status, error) {
                  $("#resMessage").val("완료처리 오류 발생 : " + error);
                }
            });
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

        function sync_hight_content_rightside(){
            var content = document.querySelector('.content');
            var rightSide = document.querySelector('.right-side');

            var maxHeight = Math.max(content.offsetHeight, rightSide.offsetHeight);
            content.style.height = maxHeight + 'px';
            rightSide.style.height = maxHeight + 'px';
        };

        sync_hight_content_rightside();

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

        $("#submitButton").click();
    });
    