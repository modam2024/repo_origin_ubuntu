    $(document).ready(function() {

        applyActiveWordStyle();

        getText();

        // 단어 클릭 이벤트 핸들러 추가
        $("#txt_word").click(function() {
            var word = $(this).val();
            splitTextAndSpeak(word);
        });

        // 변형된 대화 내용 재생
        $(".speakSentence").click(function() {
            var cnvt_text = ""

            // 버튼에 해당하는 textarea의 ID를 동적으로 가져옵니다.
            var buttonId = $(this).attr('id');
            var index = buttonId.replace('speakSentence', '');  // '1', '2' 등의 숫자를 추출

            var txtAreaId = "#converted_sentn" + index;  // 해당 텍스트 영역의 ID 생성
            var tmp_cnvt_text = $(txtAreaId).val();  // 텍스트 영역의 값을 가져옵니다.
            if ( index == "0") {
                $("#converted_sentn0-1").show();
                $("#converted_sentn0-2").hide();
                tmp_cnvt_text = tmp_cnvt_text.replace(":", "")
            }
            cnvt_text = splitCnvtText(tmp_cnvt_text)
            splitTextAndSpeakBySentence(cnvt_text);  // 추출된 단어로 함수 호출
        });

        // 오리지날 대화 내용 재생
        $(".originalSpeech").click(function() {
            var cnvt_text = ""
            var txtAreaId = "";  // 해당 텍스트 영역의 ID 생성

            // 버튼에 해당하는 textarea의 ID를 동적으로 가져옵니다.
            var buttonId = $(this).attr('id');
            var index = buttonId.replace('originalSpeech', '');  // '1', '2' 등의 숫자를 추출
            if ( index == "0") {
                $("#converted_sentn0-1").hide();
                $("#converted_sentn0-2").show();
                txtAreaId = "#converted_sentn0-2";  // 해당 텍스트 영역의 ID 생성
            } else {
                txtAreaId = "#original_sentn" + index;  // 해당 텍스트 영역의 ID 생성
            }

            var tmp_cnvt_text = $(txtAreaId).val();  // 텍스트 영역의 값을 가져옵니다.

            cnvt_text = splitCnvtText(tmp_cnvt_text)
            cnvt_text = cnvt_text.replace(":", "")

            splitTextAndSpeakBySentence(cnvt_text);  // 추출된 단어로 함수 호출
        });

        $('textarea').blur(function(e) {
            $("#submitButton").click();
        });

        // 모든 '.word-link' 클래스를 가진 <a> 태그에 대해 클릭 이벤트 리스너를 추가
        // 동적으로 클래스명이 구성되기 때문에 상위의 document 에 이벤트를 전달한다.
        $(document).on('click', '.word-link', function(e) {
            e.preventDefault();
            // '#submitButton' 클릭 이벤트를 프로그래밍적으로 호출
            $("#submitButton").click();
            var targetUrl = $(this).attr('href'); // 목표 URL 추출
            window.location.href = targetUrl;
        });

        function applyActiveWordStyle() {
            // 현재 txt_word 값 가져오기
            var currentWord = $('#txt_word').val();

            // 모든 word 링크의 스타일 초기화
            $('.word-link').removeClass('active-word');

            // txt_word 값과 일치하는 링크에 스타일 적용
            $('.word-link').each(function() {
                if ($(this).text().trim() === currentWord) {
                    $(this).addClass('active-word');
                }
            });
        }
        function getText() {
            // 필드 ID를 기반으로 모든 값을 가져와서 하나의 문자열로 결합
            function collectAndConcatenateText(baseId, count) {
                let text = "";
                for (let i = 1; i <= count; i++) {
                    text += " " + $(`#${baseId}${i}`).val();
                }
                return text;
            }

            // 문자열을 처리하고 해당 결과를 지정된 입력 필드에 설정
            function processAndDisplayText(sourceText, outputElementId) {
                let processedText = splitCnvtAllText(sourceText);  // 외부 함수를 호출하여 문자열을 변환
                processedText = processedText.replace(":", "").trim();
                $(`#${outputElementId}`).val(processedText);
            }

            const whitespaceConvertedText = collectAndConcatenateText("whitespace_converted", 10);
            const originalText = collectAndConcatenateText("original_sentn", 10);
            const convertedText = collectAndConcatenateText("converted_sentn", 10);

            processAndDisplayText(whitespaceConvertedText, "converted_sentn0-1");
            processAndDisplayText(originalText, "converted_sentn0-2");
            processAndDisplayText(convertedText, "converted_sentn0");
        }
        function splitCnvtText(text) {
            var cnvt_text = ""
            var cnvt_text_arr = text.split(":");  // 텍스트 영역의 값을 가져옵니다.

            if (cnvt_text_arr.length == 2) {
                cnvt_text = cnvt_text_arr[1].trim();
            } else if (cnvt_text_arr.length > 2)   {
                cnvt_text = cnvt_text_arr[1].trim() + cnvt_text_arr[2].trim();
            } else {
                cnvt_text = cnvt_text_arr[0].trim();
            }
            return cnvt_text;
        }
        function splitCnvtAllText(text) {
            var tmp_text = text.replace(/undefined/g, "");
            var cnvt_text_arr = tmp_text.split("A :");  // 텍스트 영역의 값을 가져옵니다.

            var second_text = ""
            for (var each_text_A of cnvt_text_arr)
            {
                var cnvt_text_B_arr = each_text_A.trim().split("B :");
                for (var each_text_B of cnvt_text_B_arr) {
                    second_text += "\n" + each_text_B.trim();
                }
            }

            return second_text
        }
     });