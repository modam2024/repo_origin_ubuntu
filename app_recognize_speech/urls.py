from django.urls import path

from app_recognize_speech.pkg_views import view_recognize_speech

urlpatterns = [
    path('index/', view_recognize_speech.index, name='index'),
    path('speech/',    view_recognize_speech.speech,    name='speech'),
]
