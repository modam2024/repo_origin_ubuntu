    $(document).ready(function() { // applied
        // 1초 동안 마우스 변경;
        setCursorShap(1000);

        // WORD CLASS LIST
        $("#wordClassList").click(function(e) {
            e.preventDefault();
            window.location.href = BASE_URL + 'article/';
        });

        // "Submit Article" 링크에 클릭 이벤트 리스너 추가
        $('#submitButton').click(function(e) {
            e.preventDefault(); // 기본 앵커 클릭 이벤트 중지
            // 10초 동안 마우스 변경
            setCursorShap(10000);
            $('#submitForm').submit(); // 폼 제출
        });

        $("#submitForm").submit(function(e) {
            e.preventDefault();

            $("#resMessage").val('Status: Starting');
            
            var articleContent = $("#artcl_content").val();
            var sourceUrl      = $("#src_url").val(); 
            var sourceTitle    = $("#src_title").val(); 
            var sourceType     = $("#src_type").val(); 

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
                    $("#resMessage").val("Count: " +  response.word_insert_count + " / " + response.word_count + ", Message: " + response.message);
                },
                error: function(xhr, status, error) {
                    // Handle the error response
                    // `xhr` is the XMLHttpRequest object
                    var errorMessage = xhr.status + ': ' + xhr.statusText;
                    $("#result").html("Error - " + errorMessage);
                }
            });
        });
        
        $("#clearButton").click(function() {
            $("#artcl_content").val("");
            $("#result").html("");
        });

        $("#allClearButton").click(function() {
            $("#artcl_content").val("");
            $("#src_url").val("");
            $("#src_title").val("");
            $("#src_type option:eq(0)").prop('selected', true);
            $("#result").html("");
        });

        $("#wordCheckButton").click(function(e) {
            e.preventDefault();
            // 10초 동안 마우스 변경
            setCursorShap(10000);
            var sourceUrl = $("#src_url").val();
            var sourceTitle = $("#src_title").val(); 
            var sourceType  = $("#src_type").val(); 
            var url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(sourceType)  + '&source_status=C';
            window.location.href = url;
        });
    });
    