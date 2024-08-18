    // WORD CLASS LIST 클릭 이벤트
    $("#wordClassList").click(function(e) {
        e.preventDefault();
        window.location.href = BASE_URL + 'article/';
    });

    // NEWS SITES 클릭 이벤트
    $("#newsSites").click(function(e) {
        e.preventDefault();
        $("#resMessage").val("NEWS 학습 생성 중입니다.");
        window.location.href = BASE_URL + 'news_study/';
    });

    // WORD CHECK LIST 클릭 이벤트
    $("#wordCheckList").click(function(e) {
        e.preventDefault();

        window.location.href = BASE_URL + 'article/main-wordcheck/?source_url=&source_title=&source_type=NEWS&source_status=C';
    });
    
    $("#livingEnglish").click(function() {
        var userConfirmed = confirm('최종 회차 생성을 하시겠습니까?');
        var url = BASE_URL;
        if (userConfirmed) {
           url = url + "article/living-english/?check=new&chapter=&status=C";
           $("#resMessage").val("신규 회차 생성 중입니다.");
        } else {
           url = url + "article/living-english/?check=max&chapter=&status=C";
           $("#resMessage").val("최신 회차 조회 중입니다.");           
        }
        window.open(url, '_self');
    });

    // TEST ENGLISH 클릭 이벤트
    $("#testEnglish").click(function(e) {
        e.preventDefault();
        $("#resMessage").val("조회 중입니다.");
        var url = BASE_URL;
        url = url + "article/test-english/?check=max&chapter=&status=C";
        window.location.href = url;
    });

    function openDic(word) {
        var encodedWord = encodeURIComponent(word); // Encodes the word for URL
        var url = "http://en.dict.naver.com/#/search?query=" + encodedWord;
        var popupSpecs = "width=600,height=1000,left=200,top=10,resizable=yes,scrollbars=yes,status=yes";
        window.open(url, 'popupWindow', popupSpecs);
    }

    function fnLogout(){
        $("#resMessage").val("로그아웃 중입니다.");
        var url = BASE_URL;
        url = url + "logout";
        window.location.href = url;
    }
    
    //웹브라우져 TTS 기능 사용
    function speak(text) {
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
    
        utterance.onend = function(event) {
            //console.log('음성 재생 완료');
            // 다음 텍스트 재생을 위한 코드 추가 가능
        };
    
        utterance.onerror = function(event) {
            //console.log('음성 재생 오류 발생');
            // 오류 처리 또는 다시 시도 로직 추가 가능
        };
    
        speechSynthesis.speak(utterance);
    }
    
    function splitTextAndSpeak(text) {
        let maxLength  = 200; // 적당한 최대 길이 설정
        let parts = [];
        let currentPart = "";
    
        text.split(/\s+/).forEach(word => {
            if ((currentPart.length + word.length) <= maxLength) {
                currentPart += (currentPart.length > 0 ? " " : "") + word;
            } else {
                parts.push(currentPart);
                currentPart = word;
            }
        });
    
        if (currentPart.length > 0) {
            parts.push(currentPart);
        }
    
        parts.forEach(part => {
            speak(part);
        });
    }
    function splitTextAndSpeakBySentence(text) {
        let maxLength   = 200; // 적당한 최대 길이 설정
        let currentPart = "";
        let parts = [];
        
        let sentences = text.match(/[^\.!\?]+[\.!\?]+/g) || []; // 문장으로 나누기
    
        sentences.forEach(sentence => {
            let trimmedSentence = sentence.trim();
            if (trimmedSentence.length <= maxLength) {
                parts.push(trimmedSentence);
            } else {
                trimmedSentence.split(/\s+/).forEach(word => {
                    if ((currentPart.length + word.length) <= maxLength) {
                        currentPart += (currentPart.length > 0 ? " " : "") + word;
                    } else {
                        parts.push(currentPart);
                        currentPart = word;
                    }
                });
            
                if (currentPart.length > 0) {
                    parts.push(currentPart);
                }
            }
        });
    
        parts.forEach(part => {
            speak(part);
        });
    }
   
    // 단어 클릭 이벤트 핸들러 추가
    $("#naverWord").click(function() {
        var word = $(this).val();
        splitTextAndSpeak(word);
    });
    
    function stopSpeaking() {
        speechSynthesis.cancel();
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
        // 현재 선택된 옵션을 찾습니다.
        var selectedOption = selectElement.options[selectElement.selectedIndex];
        // 선택된 옵션에서 data-page_date 속성을 읽어옵니다.
        var pageDate = selectedOption.getAttribute('data-page_date');

        let back_data = {
            check:   "none",
            status:  "C",
            wdate:   pageDate,
        };
        var url = BASE_URL + "article/test-english/?" + $.param(back_data);
        window.location.href = url;
    }

    window.onunload = function() {
        fnLogout();
    };
