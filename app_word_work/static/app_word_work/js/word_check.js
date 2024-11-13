    function redirectToWord(word, wrd_title) {
        // Constructs the URL
        var url = BASE_URL + "app_word_work/word_detail/?word=" + encodeURIComponent(word)  + '&wrd_title=' + encodeURIComponent(wrd_title);
        window.open(url, '_blank'); // Opens the URL in a new tab or window
    }

    $(document).ready(function() { // applied
        // 1초 동안 마우스 변경;
        setCursorShap(1000);

        var sourceTitle   = $('#sourceTitle').val();
        var sourceUrl     = $('#sourceUrl').val();
        var sourceStatus  = $('#sourceStatus').val();
        var sourceType    = $('#sourceType').val();
        var selLevel      = $('#selLevel').val();

        $('#searchGrpCd').val(sourceType);
        $('#searchLevel').val(selLevel);


        // Select ����� ���� ����� ������ ����
        $('#titleList').change(function() {
            var selectedValue = $(this).val();
            $('#sourceUrl').val(selectedValue);
        });
        
        $('#wordStatus').change(function() {
            var selectedValue = $(this).val();
            $('#wordStatus').val(selectedValue);
        });
    
        $("#sourceBtn").click(function() {
           sourceUrl = $('#titleList option:selected').val();
           window.open(decodeURIComponent(sourceUrl), '_blank');
        });

        $("#wordCheckBtn" ).click(function(event) {
            event.preventDefault();  // 이 코드를 추가하여 클릭 이벤트를 막을 수 있습니다.
            // 5초 동안 마우스 변경;
            setCursorShap(5000);
            if ($("#check_step").val() === "A") {
                $("#resMessage").val("1차 완료 재실행 안됨");
                return;
            } else {
                $("#resMessage").val("Starting");
            }
            var checkedWords = $('input[name="rowCheck"]:checked').map(function () {
                return $(this).closest('tr').find('td:nth-child(3)').text();
            }).get();

            var unCheckedWords = $('input[name="rowCheck"]:not(:checked)').map(function () {
                return $(this).closest('tr').find('td:nth-child(3)').text();
            }).get();

            var selectedTitle = $('#titleList option:selected').text();

            var sendStatus = "D";

            var v_url = "";

            alert(location.hostname);
            alert(location.port);

            if (location.hostname === 'modameng.com' && location.port === '8000') {
               v_url = "http://modameng.com:8001/app_word_work/confirm-wordcheck/";
            } else {
                v_url = "/app_word_work/confirm-wordcheck/";
            }

            alert(v_url);

            $.ajax({
                url: v_url,
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    "words": checkedWords,
                    "unchckd_words"  : unCheckedWords,
                    "selected_status": sendStatus,
                    "selected_title" : selectedTitle,
                    "selected_step"  : "A",
                }),
                success: function(response) {
                    $("#resMessage").val(response.message);
                    $("#refreshBtn").click();
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        });

        $("#wordCheckBtn2" ).click(function() {
            // 5초 동안 마우스 변경;
            setCursorShap(5000);
            $("#resMessage").val("Starting");
            var checkedWords = $('input[name="rowCheck"]:checked').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text();
            }).get();
        
            var unCheckedWords = "";
            
            var selectedTitle = $('#titleList option:selected').text();
            
            
            var sendStatus = "D";
        
            $.ajax({
                url: '/app_word_work/confirm-wordcheck/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({ 
                    "words": checkedWords,
                    "unchckd_words"  : unCheckedWords,
                    "selected_status": sendStatus,
                    "selected_title" : selectedTitle,
                    "selected_step"  : "B",
                }),
                success: function(response) {
                    $("#resMessage").val("success(First Finish)");
                    $("#refreshBtn").click();
                }
            });
        });
        
        $("#unDoneProcess").click(function() {
            // 5초 동안 마우스 변경;
            setCursorShap(5000);

            if ($('#wordStatus').val() !== 'D') {
                // Show alert and exit the function
                alert("test alert");
                return;
            }
        
            $("#resMessage").val("UnDone Starting");
            var checkedWords = $('input[name="rowCheck"]:checked').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text(); // üũ�� �ܾ� ���� �ؽ�Ʈ ����
            }).get();
        
            var unCheckedWords = $('input[name="rowCheck"]:not(:checked)').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text(); // üũ���� ���� �ܾ� ���� �ؽ�Ʈ ����
            }).get();
            
            var selectedTitle = $('#titleList option:selected').text();
            
            var sendStatus = "C";
        
            $.ajax({
                url: '/app_word_work/confirm-wordcheck/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({ 
                    "words": checkedWords,
                    "unchckd_words"  : unCheckedWords, // üũ���� ���� �ܾ�鵵 ����
                    "selected_status": sendStatus,
                    "selected_title" : selectedTitle,
                    "selected_step"  : "C",
                }),
                success: function(response) {
                    $("#resMessage").val("UnDone Process");
                    // ���⿡�� Refresh ��ư Ŭ�� �̺�Ʈ�� Ʈ�����մϴ�
                    $("#refreshBtn").click();
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        });
        
        $("#callProcess").click(function() {
            // 5초 동안 마우스 변경;
            setCursorShap(5000);
        
            var sourceTitle   = $('#titleList option:selected').text();

            $.ajax({
                url: '/app_word_work/call-process/',
                type: 'GET',
                data: {
                    "src_title": sourceTitle,
                },
                success: function(response) {
                    $("#resMessage").val(response.process_cnt + " (" + response.undone_tot_cnt + ") ");
                }
            });
        });


        $("#fixWordLevel" ).click(function() {
            // 5초 동안 마우스 변경;
            setCursorShap(5000);
            $("#resMessage").val("Change Level");
            var checkedWords = $('input[name="rowCheck"]:checked').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text();
            }).get();

            $.ajax({
                url: '/app_word_work/change-wordlevel/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    "words": checkedWords,
                }),
                success: function(response) {
                    $("#resMessage").val("Changed Levels");
                    $("#refreshBtn").click();
                }
            });
        });

        $("#gotoInit").click(function() {
        
            var sourceTitle   = $('#titleList option:selected').text();

            $.ajax({
                url: '/goto-init/',
                type: 'GET',
                data: {
                    "src_title": sourceTitle,
                },
                success: function(response) {
                    $("#resMessage").val(response.result);
                    $("#refreshBtn").click();
                }
            });
        });        

        $("#searchBtn").click(function() {
            var searchGrpCd = $('#searchGrpCd option:selected').text();
            var searchLevel = $('#searchLevel option:selected').val();

            var url = '/app_word_work/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(searchGrpCd) + '&sel_level=' + encodeURIComponent(searchLevel) + '&source_status=C';
            window.location.href = url;
        });

        $("#refreshBtn").click(function() {
            // 3초 동안 마우스 변경;
            setCursorShap(3000);

            var selectedTitle  = $('#titleList   option:selected').text();
            var selectedStatus = $('#wordStatus  option:selected').val();

            var searchGrpCd    = $('#searchGrpCd option:selected').text();
            var searchLevel    = $('#searchLevel option:selected').val();

            if (searchGrpCd != "NEWS") {
                $("#sourceBtn").css("display", "none");
            }

            $.ajax({
                url: BASE_URL + 'app_word_work/main-wordtable/',
                type: 'GET',
                data: {
                    'source_title' : selectedTitle,
                    'source_status': selectedStatus,
                    'source_type'  : searchGrpCd,
                    'sel_level'    : searchLevel
                },
                success: function(response) {
                  
                    $("#rows_cnt").val(response.rows_cnt);
                    var check_step = response.step_status;
                    $("#check_step").val(check_step);

                    if (check_step === 'A')
                    {
                        $("#wordCheckBtn").prop("disabled", true);
                        $("#wordCheckBtn").css("background-color", "grey");
                    } else {
                        $("#wordCheckBtn").prop("disabled", false);
                        $("#wordCheckBtn").css("background-color", "#4D92AA");
                    }
                  
                    // Clear existing table rows
                    $(".table-container table tr:not(:first)").remove();

                    var safeTitle = selectedTitle.replace(/'/g, "\\'");

                    $.each(response.rows, function(i, record) {
                        let tmp_star = "";
                        if ( record[5] === 'E' ) {
                            tmp_star = "*";
                        }

                        var rec_number  = record[0]+tmp_star;
                        var rec_word    = record[1];
                        var rec_mean_en = record[2];
                        var rec_mean_kr = record[3];
                        var rec_create_date = record[4];
                      
                        var newRow = $('<tr>');
                        newRow.append($('<td>').html('<input type="checkbox" name="rowCheck" checked>'));
                        newRow.append($('<td>').text(rec_number).attr('onclick', "redirectToWord('" + rec_word + "', '" + safeTitle + "')"));
                        newRow.append($('<td>').text(rec_word));
                        newRow.append($('<td>').text(rec_mean_en));
                        newRow.append($('<td>').text(rec_mean_kr));
                        newRow.append($('<td>').text(rec_create_date));
                        $('.table-container table').append(newRow);
                    });

                    $("#checkAll").prop("checked", true);  // 마스터 체크박스 체크
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        });

        $("#createWord").click(function() {
            var wrdGrpCd = $('#searchGrpCd option:selected').val();
            var wrdTitle = $('#titleList option:selected').text();
            var wrdWord  = $("#txt_word").val();

            $.ajax({
                url: '/app_word_work/create-word/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    "wrd_grpcd": wrdGrpCd,
                    "wrd_title": wrdTitle,
                    "wrd_word": wrdWord,
                }),
                success: function(response) {
                    $("#resMessage").val(response.message);
                    $("#txt_word").val("");
                    $("#refreshBtn").click();
                }
            });
        });
        
        $("#deleteBtn").click(function() {
            // 5초 동안 마우스 변경;
            setCursorShap(5000);

            var selectedTitle = $('#titleList option:selected').text();
        
            $.ajax({
                url: BASE_URL + 'app_word_work/delete-content/',
                type: 'GET',
                data: {
                    'source_title': selectedTitle,
                },
                success: function(response) {
                    $("#resMessage").val("success-delete content");
                    $("#searchBtn").click();
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        });
        
        if (sourceUrl) {
            $("#titleList option").each(function() {
                if ($(this).val() === sourceUrl) {
                    $('#titleList').val($(this).val()).trigger('change');
                }
            });
        }
        
        if (sourceStatus) {
            $("#wordStatus option").each(function() {
                if ($(this).val() === sourceStatus) {
                    $('#wordStatus').val($(this).val()).trigger('change');
                }
            });
        }

        if (selLevel) {
            $("#searchLevel option").each(function() {
                if ($(this).val() === selLevel) {
                    $('#searchLevel').val($(this).val()).trigger('change');
                }
            });
        }
        
        $('table').on('click', 'td:nth-child(3)', function() {
            var word = $(this).text();
            $('#naverWord').val(word);
            speak(word);
        });
        
        $("#checkAll").click(function(){
            $('input[name="rowCheck"]').prop('checked', this.checked);
        });
    
        $('input[name="rowCheck"]').click(function(){
            if ($('input[name="rowCheck"]').length == $('input[name="rowCheck"]:checked').length) {
                $('#checkAll').prop('checked', true);
            } else {
                $('#checkAll').prop('checked', false);
            }
        });

        // $("#backBtn").click(function(){
        //     // 2초 동안 마우스 변경;
        //     setCursorShap(2000);
        //     window.history.back();
        // });

        // TEST ENGLISH 클릭 이벤트
        $("#backBtn").click(function() {
            // 10초 동안 마우스 변경
            setCursorShap(10000);

            var url = "";
            $("#resMessage").val("테스트 페이지로 이동중입니다.");
            let source_gubun = $("#sourceGubun").val();

            if (source_gubun === "test") {
                let back_data = {
                    check:   "none",
                    status:  "C",
                    wdate:   $("#test_page_date").val(),
                };
                url = BASE_URL + "app_test_timer/test-english/?" + $.param(back_data);
                window.location.href = url;
            } else if (source_gubun === "news") {
                let back_data = {
                    selected_date:   $("#selected_date").val(),
                };
                url = BASE_URL + "app_news_study/news_study/?" + $.param(back_data);
                window.location.href = url;
            } else if (source_gubun === "living") {
                let tmp_selected_chapter = $("#selected_chapter").val() || "";
                let back_data = {
                    chapter: tmp_selected_chapter,
                    status : "C",
                };
                url = BASE_URL + "app_living_english/living-english/?" + $.param(back_data);
                window.location.href = url;
            } else {
                alert("호출 페이지가 존재 하지 않습니다.");
            }
        });

        if (sourceType === "ALL") {
            $("#titleList").prop("disabled",  true);
            $("#wordStatus").prop("disabled", true);
            $("#refreshBtn").prop("disabled", true);
            $("#deleteBtn").prop("disabled",  true);
            $("#titleList").css("color",      "white");
            $("#wordStatus").css("color",     "white");
            $("#titleList").css("background-color",  "grey");
            $("#wordStatus").css("background-color", "grey");
            $("#refreshBtn").css("background-color", "grey");
            $("#deleteBtn").css("background-color",  "grey");
        } else {
            $("#titleList").prop("disabled",  false);
            $("#wordStatus").prop("disabled", false);
            $("#refreshBtn").prop("disabled", false);
            $("#deleteBtn").prop("disabled",  false);
            $("#titleList").css("background-color",  "white");
            $("#wordStatus").css("background-color", "white");
            $("#refreshBtn").css("background-color", "#8C0028");
            $("#deleteBtn").css("background-color",  "#8C0028");
        }

        $("#refreshBtn").click();

    });
