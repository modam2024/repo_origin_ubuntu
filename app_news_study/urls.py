from django.urls import path

from app_news_study.pkg_views import view_news_study

urlpatterns = [
    path('news_study/',    view_news_study.news_study,    name='news_study'),
    path('news_info_eng/', view_news_study.news_info_eng, name='news_info_eng'),
    path('news_info_inf/', view_news_study.news_info_inf, name='news_info_inf'),
    path('save-wordinfo/', view_news_study.save_wordinfo, name='save_wordinfo'),
    path('complete-word/', view_news_study.complete_word, name='complete_word'),
]
