    $(document).ready(function() {
      
        // Hidden 필드의 값들을 읽어서 입력 필드나 텍스트 영역에 설정
        $('#txt_word').val($('#wrd_word').val());
        $('#txt_guessing').val($('#wrd_guess').val());        
        $('#txt_defeng').val($('#wrd_tag').val());
        $('#txt_defkor').val($('#wrd_mean').val());        
        $('#txt_eng_example').val($('#wrd_eng_example').val());
        $('#txt_kor_example').val($('#wrd_kor_example').val());
        $('#txt_eng_example2').val($('#wrd_eng_example2').val());
        $('#txt_kor_example2').val($('#wrd_kor_example2').val());
        
        var orgGuessing      = $('#txt_guessing').height();
        
        var orgEngExpHeight  = $('#txt_eng_example').height();
        var orgEngExp2Height = $('#txt_eng_example2').height();
        
        var orgKorHeight  = $('#txt_kor_example').height();
        var orgKor2Height  = $('#txt_kor_example2').height();                
        
        if ($('#wrd_word').val() == 'completed-go-to-next-word') 
        {
          $("#resMessage").val('COMPLETED');
        }
        
        initAllTextArea();
        
        applyActiveWordStyle();

        // WORD CLASS LIST 클릭 이벤트
        $("#wordClassList").click(function(e) {
            e.preventDefault();
            window.location.href = BASE_URL + 'article/';
        });

        $("#submitForm").submit(function(e) {
            e.preventDefault();

            $("#result").html("Status: Starting");                
            
            var articleContent = $("#artcl_content").val();
            var sourceUrl      = $("#src_url").val(); 
            var sourceTitle    = $("#src_title").val(); 
            var sourceType     = $("#src_type").val(); 

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
                    $("#result").html("Status: " + response.status + ", Count: " +  response.word_insert_count + " / " + response.word_count + ", Message: " + response.message);
                },
                error: function(xhr, status, error) {
                    // Handle the error response
                    // `xhr` is the XMLHttpRequest object
                    var errorMessage = xhr.status + ': ' + xhr.statusText;
                    $("#result").html("Error - " + errorMessage);
                }
            });
        });
        
        // 단어 클릭 이벤트 핸들러 추가
        $("#txt_word").click(function() {
            var word = $(this).val();
            splitTextAndSpeak(word);
        });        
        
        // 단어 클릭 이벤트 핸들러 추가
        $("#speakDefEng").click(function() {
            var word = $("#txt_defeng").val();
            splitTextAndSpeak(word);
        });        
        
        // 영문 예문 클릭 이벤트 핸들러 추가
        $("#speakExampleEng").click(function() {
           var txtAreaExampleEng = $('#txt_eng_example');
           /*
           if (txtAreaExampleEng.height() != orgEngExpHeight) {
              txtAreaExampleEng.height(orgEngExpHeight);
           } else {
              txtAreaExampleEng.height(txtAreaExampleEng.prop('scrollHeight')); 
           }   
           */
           var word = txtAreaExampleEng.val();
           splitTextAndSpeakBySentence(word);
        });        
        
        // 영문 예문 클릭 이벤트 핸들러 추가
        $("#speakExampleEng2").click(function() {
           var txtAreaExampleEng2 = $('#txt_eng_example2');
           /*          
           if (txtAreaExampleEng2.height() != orgEngExp2Height) {
              txtAreaExampleEng2.height(orgEngExp2Height);
           } else {
              txtAreaExampleEng2.height(txtAreaExampleEng2.prop('scrollHeight')); 
           }
           */
           var word = txtAreaExampleEng2.val();
           splitTextAndSpeakBySentence(word);
        });
        
        $('#expandGuessing').click(function() {
           var  txtAreaGuessing = $('#txt_guessing');

           if (txtAreaGuessing.height() != orgGuessing) {
              txtAreaGuessing.height(orgGuessing);
           } else {
              txtAreaGuessing.height(txtAreaGuessing.prop('scrollHeight'));
           }
        });
        
        // 영문 예문 클릭 이벤트 핸들러 추가
        $("#expandExampleEng").click(function() {
           var txtAreaExampleEng = $('#txt_eng_example');
          
           if (txtAreaExampleEng.height() != orgEngExpHeight) {
              txtAreaExampleEng.height(orgEngExpHeight);
           } else {
              txtAreaExampleEng.height(txtAreaExampleEng.prop('scrollHeight')); 
           }
        });      

        // 영문 예문 클릭 이벤트 핸들러 추가
        $("#expandExampleEng2").click(function() {
           var txtAreaExampleEng2 = $('#txt_eng_example2');
          
           if (txtAreaExampleEng2.height() != orgEngExp2Height) {
              txtAreaExampleEng2.height(orgEngExp2Height);
           } else {
              txtAreaExampleEng2.height(txtAreaExampleEng2.prop('scrollHeight')); 
           }
        });      

        
        // 한글 예문 클릭 이벤트 핸들러 추가
        $("#expandKor").click(function() {
           var txtAreaKor = $('#txt_kor_example');
          
           if (txtAreaKor.height() != orgKorHeight) {
              txtAreaKor.height(orgKorHeight);
           } else {
              txtAreaKor.height(txtAreaKor.prop('scrollHeight')); 
           }   
        });      
        
        // 한글 예문 클릭 이벤트 핸들러 추가
        $("#expandKor2").click(function() {
           var txtAreaKor2 = $('#txt_kor_example2');
          
           if (txtAreaKor2.height() != orgKor2Height) {
              txtAreaKor2.height(orgKor2Height);
           } else {
              txtAreaKor2.height(txtAreaKor2.prop('scrollHeight')); 
           }   
        });
        
        $("#clearWord").click(function() {
            $("#txt_word").val("").height('auto');
        });
        
        $("#clearGuessing").click(function() {
            $("#txt_guessing").val("").height('auto');
        });
        
        $("#clearDefEng").click(function() {
            $("#txt_defeng").val("").height('auto');
        });
        
        $("#clearDefKor").click(function() {
            $("#txt_defkor").val("").height('auto');
        });
        
        $("#clearExampleEng").click(function() {
            $("#txt_eng_example").val("").height('auto');
        });
        
        $("#clearExampleKor").click(function() {
            $("#txt_kor_example").val("").height('auto');
        });
        
        $("#clearExampleEng2").click(function() {
            $("#txt_eng_example2").val("").height('auto');
        });
        
        $("#clearExampleKor2").click(function() {
            $("#txt_kor_example2").val("").height('auto');
        });

        $("#submitButton").click(function() {
            var data = {
                txt_word: $("#txt_word").val(),
                txt_guessing: $("#txt_guessing").val(),
                txt_defeng: $("#txt_defeng").val(),
                txt_defkor: $("#txt_defkor").val(),
                txt_eng_example:  $("#txt_eng_example").val(),
                txt_kor_example:  $("#txt_kor_example").val(),
                txt_eng_example2: $("#txt_eng_example2").val(),
                txt_kor_example2: $("#txt_kor_example2").val()
            };
        
            $.ajax({
                url: '/article/save-wordinfo/',
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
        
        $("#completeButton").click(function() {
          
           var complt_title    = $("#wrd_title").val(); 
          
            var data = {
                complt_word: $("#txt_word").val(),
            };
        
            $.ajax({
                url: '/article/complete-word/',
                type: 'GET',
                data: data,
                success: function(response) {
                  $("#resMessage").val(response.message);
                  var complt_voca     = "completed-go-to-next-word"; 
                  window.location.href = BASE_URL + 'article/word_detail/?word=' + encodeURIComponent(complt_voca)  + '&wrd_title=' + encodeURIComponent(complt_title);
                },
                error: function(xhr, status, error) {
                  $("#resMessage").val("error : " + error);
                }
            });
        });

        $("#createWord").click(function() {
            var wrdTitle  = $("#wrd_title").val();
            var wrdWord   = $("#txt_word").val();
            var wrdGroup   = $("#wrd_group").val();
            var sendStatus = "C";

            $.ajax({
                url: '/article/create-word/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    "wrd_word": wrdWord,
                    "wrd_status": sendStatus,
                    "wrd_title": wrdTitle,
                    "wrd_group": wrdGroup,

                }),
                success: function(response) {
                    $("#resMessage").val(response.message);
                }
            });
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

        // txt_word 값과 일치하는 word 링크에 스타일 적용하는 함수
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
        
        // txt_word 값과 일치하는 word 링크에 스타일 적용하는 함수
        function initAllTextArea() {
           var txtAreaExampleEng  = $("#txt_eng_example");
           var txtAreaExampleEng2 = $("#txt_eng_example2");
           var txtAreaExampleKor  = $("#txt_kor_example");
           var txtAreaExampleKor2 = $("#txt_kor_example2");           
           
           txtAreaExampleEng.height(txtAreaExampleEng.prop('scrollHeight'));
           txtAreaExampleEng2.height(txtAreaExampleEng2.prop('scrollHeight'));
           txtAreaExampleKor.height(txtAreaExampleKor.prop('scrollHeight'));
           txtAreaExampleKor2.height(txtAreaExampleKor2.prop('scrollHeight'));
        }
     });