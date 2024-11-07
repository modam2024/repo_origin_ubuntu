import io
import subprocess
import wave

import speech_recognition as sr
import webrtcvad
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='/login/')
def index(request):
    return render(request, "recognize_speech.html")


def convert_to_wav(audio_data):
    # 메모리에 있는 데이터를 WAV 파일로 변환
    source = io.BytesIO(audio_data)
    target = io.BytesIO()

    command = [
        "ffmpeg",
        "-i", "pipe:0",  # 입력이 stdin에서 오는 것을 의미
        "-acodec", "pcm_s16le",  # 출력 오디오 코덱을 PCM 16비트 리틀 엔디언으로 설정
        "-ar", "16000",  # 오디오 샘플링 레이트를 16000Hz로 설정
        "-ac", "1",  # 오디오 채널을 모노로 설정
        "-f", "wav",  # 출력 형식을 WAV로 명시적 지정
        "pipe:1"  # 출력이 stdout으로 가는 것을 의미
    ]

    result = subprocess.run(command, input=source.read(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception("ffmpeg error:", result.stderr)
    target.write(result.stdout)
    target.seek(0)
    return target


def extract_voice_segments(audio_stream):
    vad = webrtcvad.Vad(3)  # 민감도 설정 (0~3, 3이 가장 민감)
    voice_frames = []

    # 오디오 파일 읽기
    with wave.open(audio_stream, 'rb') as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        assert sample_rate in [8000, 16000, 32000, 48000], "지원되지 않는 샘플 레이트입니다."
        assert channels == 1, "Mono 오디오만 지원됩니다."

        frame_duration = 30  # 30ms 프레임
        frame_size = int(sample_rate * frame_duration / 1000) * 2  # 16-bit PCM 형식

        audio_frames = wf.readframes(wf.getnframes())

        # VAD로 사람 목소리 부분 감지
        for i in range(0, len(audio_frames), frame_size):
            frame = audio_frames[i:i + frame_size]
            if len(frame) < frame_size:
                break
            if vad.is_speech(frame, sample_rate):
                voice_frames.append(frame)

    # 사람 목소리만 포함된 오디오 스트림 생성
    output_stream = io.BytesIO()
    with wave.open(output_stream, 'wb') as out_wf:
        out_wf.setnchannels(1)
        out_wf.setsampwidth(2)
        out_wf.setframerate(sample_rate)
        out_wf.writeframes(b''.join(voice_frames))
    output_stream.seek(0)
    return output_stream


@csrf_exempt
def speech(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 2
        audio_file = request.FILES['audio']
        audio_data = audio_file.read()

        try:
            # 오디오 데이터를 WAV 형식으로 변환
            audio_stream = convert_to_wav(audio_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        try:
            # 사람 목소리만 추출
            voice_only_stream = extract_voice_segments(audio_stream)
        except Exception as e:
            return JsonResponse({'error': f"Voice extraction error: {str(e)}"}, status=500)

        with sr.AudioFile(voice_only_stream) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language="ko-KR")
            # text = recognizer.recognize_google(audio, language = "en-US")
            print(text)
            return JsonResponse({'text': text}, status=200)
        except sr.UnknownValueError:
            return JsonResponse({'error': "Could not understand audio"}, status=400)
        except sr.RequestError:
            return JsonResponse({'error': "Google Speech Recognition service error"}, status=500)
    return HttpResponseBadRequest('Invalid request')
