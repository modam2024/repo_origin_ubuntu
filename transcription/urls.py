from django.urls import path

from transcription.pkg_views.view_transcription import transcription, transcribe_audio

urlpatterns = [
    path('transcription/', transcription,    name='transcription'),     # 메인 페이지
    path('transcribe/',    transcribe_audio, name='transcribe_audio'),  # 파일 업로드 처리
]

