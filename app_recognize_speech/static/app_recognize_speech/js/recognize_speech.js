$(document).ready(function () {
    var audioContext = new (window.AudioContext || window.webkitAudioContext)();
    var mediaRecorder;
    var audioChunks = [];

    $('#start').click(function () {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({audio: true})
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = []; // Clear previous chunks
                    mediaRecorder.start();
                    $('#status').text("녹음 중...");

                    $('#stop').click(function () {
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            mediaRecorder.stop();
                            stream.getTracks().forEach(track => track.stop()); // Stop audio stream
                            $('#status').text("녹음 중지...");
                        }
                    });

                    mediaRecorder.ondataavailable = function (e) {
                        audioChunks.push(e.data);
                    };

                    mediaRecorder.onstop = function () {
                        var prvResult = "";
                        const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'audio.wav');

                        // Send the audio file to the Django backend
                        $.ajax({
                            url: '/app_recognize_speech/speech/',
                            type: 'POST',
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function (data) {
                                prvResult = $('#prv_result').text();
                                if (prvResult !== "") {
                                    $('#result').text(prvResult + "\n" + "\n" + data.text);
                                } else {
                                    $('#result').text(data.text);
                                    $('#prv_result').text(data.text);
                                }
                                strResult = $('#result').text();
                                $('#prv_result').text(strResult);
                                $('#status').text("녹음 대기 중...");
                            },
                            error: function (xhr, status, error) {
                                $('#result').append('<div>에러: ' + xhr.responseJSON.error + '</div>');
                                $('#status').text("녹음 대기 중...");
                            }
                        });
                    };
                })
                .catch(error => {
                    console.error('Error accessing the microphone', error);
                    alert("마이크 접근 오류: " + error.message);
                });
        } else {
            alert("브라우저가 미디어 장치를 지원하지 않습니다.");
        }
    });
});
