    function redirectToWord(word, wrd_title) {
        // Constructs the URL
        var url = BASE_URL + "article/word_detail/?word=" + encodeURIComponent(word)  + '&wrd_title=' + encodeURIComponent(wrd_title);
        window.open(url, '_blank'); // Opens the URL in a new tab or window
    }

    $(document).ready(function() {
        var sourceTitle   = $('#sourceTitle').val();
        var sourceUrl     = $('#sourceUrl').val();
        var sourceStatus  = $('#sourceStatus').val();
        var sourceType    = $('#sourceType').val();
    
        $('#searchGrpCd').val(sourceType);
    
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
  
        $("#wordCheckBtn").click(function() {
            $("#resMessage").val("Starting");
            var checkedWords = $('input[name="rowCheck"]:checked').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text(); // üũ�� �ܾ� ���� �ؽ�Ʈ ����
            }).get();
        
            var unCheckedWords = $('input[name="rowCheck"]:not(:checked)').map(function() {
                return $(this).closest('tr').find('td:nth-child(3)').text(); // üũ���� ���� �ܾ� ���� �ؽ�Ʈ ����
            }).get();
            
            var selectedTitle = $('#titleList option:selected').text();
            
            
            var sendStatus = "D";
        
            $.ajax({
                url: '/article/confirm-wordcheck/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({ 
                    "words": checkedWords,
                    "unchckd_words": unCheckedWords, // üũ���� ���� �ܾ�鵵 ����
                    "selected_status": sendStatus,
                    "selected_title": selectedTitle,
                }),
                success: function(response) {
                    $("#resMessage").val("success(First Finish)");
                    $("#refreshBtn").click();
                }
            });
        });
        
        $("#unDoneProcess").click(function() {
        
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
                url: '/article/confirm-wordcheck/',
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({ 
                    "words": checkedWords,
                    "unchckd_words": unCheckedWords, // üũ���� ���� �ܾ�鵵 ����
                    "selected_status": sendStatus,
                    "selected_title": selectedTitle,
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
        
            var sourceTitle   = $('#titleList option:selected').text();

            $.ajax({
                url: '/article/call-process/',
                type: 'GET',
                data: {
                    "src_title": sourceTitle,
                },
                success: function(response) {
                    $("#resMessage").val(response.process_cnt + " (" + response.undone_tot_cnt + ") ");
                }
            });
        });
        
        $("#gotoMobile").click(function() {
        
            var sourceTitle   = $('#titleList option:selected').text();

            $.ajax({
                url: '/article/goto-mobile/',
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
            
            var url = '/article/main-wordcheck/?source_url=' + encodeURIComponent(sourceUrl) + '&source_title=' + encodeURIComponent(sourceTitle) + '&source_type=' + encodeURIComponent(searchGrpCd)  + '&source_status=C';
            window.location.href = url; 
        });
        
        $("#refreshBtn").click(function() {
            var selectedTitle = $('#titleList option:selected').text();
            var selectedStatus = $('#wordStatus option:selected').val();
        
            //selectedTitle  = encodeURIComponent(selectedTitle);
            //selectedStatus = encodeURIComponent(selectedStatus);
        
            $.ajax({
                url: BASE_URL + 'article/main-wordtable/',
                type: 'GET',
                data: {
                    'source_title': selectedTitle,
                    'source_status': selectedStatus
                },
                success: function(response) {
                  
                    $("#rows_cnt").val(response.rows_cnt);
                  
                    // Clear existing table rows
                    $(".table-container table tr:not(:first)").remove();

                    var safeTitle = selectedTitle.replace(/'/g, "\\'");

                    $.each(response.rows, function(i, record) {
                      
                        var rec_number  = record[0];
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
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        });
        
        $("#deleteBtn").click(function() {
            var selectedTitle = $('#titleList option:selected').text();
        
            $.ajax({
                url: BASE_URL + 'article/delete-content/',
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
        
        $('table').on('click', 'td:nth-child(3)', function() {
            var word = $(this).text();
            $('#naverWord').val(word);
            splitTextAndSpeak(word);
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
        
        $("#refreshBtn").click();
    });
