import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
import whisper

def transcription(request):
    return render(request, 'transcription.html')

@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):

        # Whisper 모델 로드 (서버 시작 시 로드)
        model = whisper.load_model("base")

        audio_file = request.FILES['audio']
        audio_path = f'uploads/{audio_file.name}'

        # 파일 저장
        os.makedirs('uploads', exist_ok=True)
        with open(audio_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        print("11111111111111111111")
        print(audio_path)
        # Whisper를 이용한 음성 텍스트 변환
        result = model.transcribe(audio_path, language='ko')
        print("2222222222222222")
        print(result['text'])
        return JsonResponse({'text': result['text']})

    return JsonResponse({'error': '파일이 없습니다.'}, status=400)
