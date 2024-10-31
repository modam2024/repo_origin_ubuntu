    //#######################################################
    //# 마우스를 모래시계로 변경하고 시간을 설정할 수 있게 하고,
    //# 설정한 시간이 지나면 마우가 화설표로 변경된다.
    //# 작성일 : 2024.08.25
    //####################################################### '''
    let audio = new Audio("");

    function setCursorShap(p_sec) {
        $('body, body *').css('cursor', 'wait');
        setTimeout(function() {
            $('body, body *').css('cursor', 'default'); // 모든 요소의 커서 스타일을 'default'로 변경
        }, p_sec); // p_sec 밀리초 후에 커서 스타일 적용
    }

    // WORD CLASS LIST 클릭 이벤트
    $("#wordClassList").click(function(e) {
        e.preventDefault();
        // 5초 동안 마우스 변경;
        setCursorShap(5000);
        window.location.href = BASE_URL + 'app_open_article/article/';
    });

    // NEWS SITES 클릭 이벤트
    $("#newsSites").click(function(e) {
        e.preventDefault();
        // 5초 동안 마우스 변경;
        setCursorShap(5000);

        $("#resMessage").val("기사 생성(조회) 중입니다.");
        window.location.href = BASE_URL + 'app_news_study/news_study/';
    });

    // WORD CHECK LIST 클릭 이벤트
    $("#wordCheckList").click(function(e) {
        e.preventDefault();
        // 5초 동안 마우스 변경;
        setCursorShap(5000);
        window.location.href = BASE_URL + 'app_word_work/main-wordcheck/?source_url=&source_title=&source_type=ALL&sel_level=A&source_status=C';
    });
    
    $("#livingEnglish").click(function() {
        // var userConfirmed = confirm('최종 회차 생성을 하시겠습니까?');
        var url = BASE_URL;
        // if (userConfirmed) {
        //    url = url + "app_living_english/living-english/?check=new&chapter=&status=C";
        //    $("#resMessage").val("신규 회차 생성 중입니다.");
        // } else {
           url = url + "app_living_english/living-english/?check=max&chapter=&status=C";
           $("#resMessage").val("최신 회차 조회 중입니다.");           
        // }
        window.open(url, '_self');
    });

    // TEST ENGLISH 클릭 이벤트
    $("#testEnglish").click(function(e) {
        e.preventDefault();
        $("#resMessage").val("조회 중입니다.");
        // 5초 동안 마우스 변경;
        setCursorShap(5000);

        var url = BASE_URL;
        url = url + "app_test_timer/test-english/?check=max&chapter=&status=C";
        window.location.href = url;
    });

    function openDic(word) {
        // 5초 동안 마우스 변경;
        setCursorShap(5000);
        var encodedWord = encodeURIComponent(word); // Encodes the word for URL
        var url = "http://en.dict.naver.com/#/search?query=" + encodedWord;
        var popupSpecs = "width=800,height=1000,left=200,top=10,resizable=yes,scrollbars=yes,status=yes";
        window.open(url, 'popupWindow', popupSpecs);
    }

    function fnLogout(){
        $("#resMessage").val("로그아웃 중입니다.");
        var url = BASE_URL;
        url = url + "logout";
        window.location.href = url;
    }

    //웹브라우져 TTS 기능 사용
    // function speak(text) {
    //     var utterance = new SpeechSynthesisUtterance(text);
    //     utterance.lang = 'en-US';
    //
    //     utterance.onend = function(event) {
    //         //console.log('음성 재생 완료');
    //         // 다음 텍스트 재생을 위한 코드 추가 가능
    //     };
    //
    //     utterance.onerror = function(event) {
    //         //console.log('음성 재생 오류 발생');
    //         // 오류 처리 또는 다시 시도 로직 추가 가능
    //     };
    //
    //     speechSynthesis.speak(utterance);
    // }

    //웹브라우져 TTS 기능 사용
    function speak(text) {
        stopSpeaking();
        // 텍스트를 음성으로 변환 요청을 Ajax로 보냅니다.
        $.ajax({
            url: '/text-to-speech/',
            type: 'POST',
            data: {
                text: text,
                lang: 'ko'
            },
            success: function(data) {
                if (data.status === 'success') {
                    // MP3 파일 URL을 받아서 오디오 객체 생성
                    let audioUrl = data.audio_url;
                    audio = new Audio(audioUrl);

                    // 오디오 재생
                    audio.play();
                } else {
                    console.error('Error:', data.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    // function speak(text) {
    //     stopSpeaking();
    //     // 텍스트를 음성으로 변환 요청을 Ajax로 보냅니다.
    //     $.ajax({
    //         url: '/text-to-speech/',
    //         type: 'POST',
    //         data: {
    //             text: text,
    //             lang: 'en'
    //         },
    //         success: function(data) {
    //             if (data.status === 'success') {
    //                 // Base64 데이터를 디코딩하여 Blob 객체로 변환
    //                 const audioBase64 = data.audio_base64;
    //                 const audioData = atob(audioBase64);  // Base64 디코딩
    //                 const arrayBuffer = new Uint8Array(audioData.length);
    //
    //                 for (let i = 0; i < audioData.length; i++) {
    //                     arrayBuffer[i] = audioData.charCodeAt(i);
    //                 }
    //
    //                 const blob = new Blob([arrayBuffer], { type: 'audio/mpeg' });
    //                 const audioUrl = URL.createObjectURL(blob);
    //                 audio = new Audio(audioUrl);
    //
    //                 // 오디오 재생
    //                 audio.play();
    //             } else {
    //                 console.error('Error:', data.message);
    //             }
    //         },
    //         error: function(xhr, status, error) {
    //             console.error('Error:', error);
    //         }
    //     });
    // }

    // 단어 클릭 이벤트 핸들러 추가
    $("#naverWord").click(function() {
        var word = $(this).val();
        speak(word);
    });
    
    function stopSpeaking() {
        if (audio) {
            audio.pause();          // 오디오 재생을 일시 중지
            audio.currentTime = 0;  // 재생 위치를 처음으로 설정
        }
    }

    function replaceText() {
        var textarea1 = document.getElementById('artcl_content1');
        var text = textarea1.value;
        text = text.replace(/\u00A0/g, '_');
        textarea1.value = text;

        var textarea2 = document.getElementById('artcl_content2');
        var text = textarea2.value;
        text = text.replace(/\u00A0/g, '_');
        textarea2.value = text;

        var textarea3 = document.getElementById('artcl_content3');
        var text = textarea3.value;
        text = text.replace(/\u00A0/g, '_');
        textarea3.value = text;
    }

    // TEST ENGLISH 클릭 이벤트
    function selectedPageDate(selectElement) {
        $("#resMessage").val("조회 중입니다.");
        // 5초 동안 마우스 변경;
        setCursorShap(5000);
        // 현재 선택된 옵션을 찾습니다.
        var selectedOption = selectElement.options[selectElement.selectedIndex];
        // 선택된 옵션에서 data-page_date 속성을 읽어옵니다.
        var pageDate = selectedOption.getAttribute('data-page_date');

        let back_data = {
            check:   "none",
            status:  "C",
            wdate:   pageDate,
        };
        var url = BASE_URL + "app_test_timer/test-english/?" + $.param(back_data);
        window.location.href = url;
    }

    // window.onunload = function() {
    //     fnLogout();
    // };

    var timerInterval;

    // 이전에 선택한 질문을 저장할 변수
    var lastQuestion = null;

    var remainingTime     = 90; // 타이머 시작 시간을 초 단위로 설정 (예: 1분 5초)
    var lastRemainingTime = 90; // 직전 클릭 시의 남은 시간을 저장할 변수

    g_pagedateList2 = "";