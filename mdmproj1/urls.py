"""
URL configuration for mdmproj1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
 """

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from app_news_study import views as news_study_views
from article import cnvrt_tpc_exec as cnvrt_tpc_exec
from article import morph_analysis as morph_analysis
from article import views as article_views
from article import views_five_feedback as article_views_feedback
from article import views_five_test as article_views_test
from balance import views as balance_views
from mdl_login_info import views as login_views

urlpatterns = [
    # 기타 url 패턴들
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
    path('admin/',   admin.site.urls),
    path('login/',   auth_views.LoginView.as_view(template_name='registration/login.html'),  name='login'),
    path('logout/',  auth_views.LogoutView.as_view(), name='logout'),
    path('register/', login_views.register, name='register'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # 홈 페이지 URL 패턴
    path('balance/', balance_views.main_view),
    path('article/'                  , article_views.main_view         , name='main-article'),
    path('article/submit-article/'   , article_views.submit_article    ,  name='submit-article'),
    path('article/main-wordcheck/'   , article_views.main_word_check   ,  name='main-word-check'),
    path('article/delete-content/'   , article_views.delete_content    ,  name='delete-content'),
    path('article/main-wordtable/'   , article_views.main_word_table   ,  name='main-word-table'),
    #path('article/submit-wordcheck/' , article_views.submit_word_check ,  name='submit-word-check'),
    path('article/confirm-wordcheck/', article_views.confirm_word_check,  name='confirm-word-check'),
    path('article/call-process/'     , article_views.call_process      ,  name='call-process'),
    path('article/goto-mobile/'      , article_views.goto_mobile       ,  name='goto-mobile'),
    
    path('article/word_detail/'        , article_views.word_detail       ,  name='word_detail'),
    path('article/save-wordinfo/'      , article_views.save_wordinfo     ,  name='save_wordinfo'),
    path('article/complete-word/'      , article_views.complete_word     ,  name='complete_word'),
    path('article/living-english/'     , article_views.living_english    ,  name='living_english'),
    path('article/complete-chapter/'   , article_views.complete_chapter  ,  name='complete_chapter'),
    path('article/uncomplete-chapter/' , article_views.uncomplete_chapter,  name='uncomplete_chapter'),
    path('article/save-topic/'         , article_views.save_topic,          name='save-topic'),
    path('article/create-word/'        , article_views.create_word,         name='create-word'),

    path('article/test-english/'       , article_views_test.test_english,         name='test_english'),
    path('article/feedback-english/'   , article_views_feedback.feedback_english, name='feedback_english'),

    path('article/cnvrt_tpc_exec/'     , cnvrt_tpc_exec.main_cnvrt_tpc_exec, name='cnvrt_tpc_exec'),
    path('article/morph_analysis/'     , morph_analysis.submit_topic,        name='submit_topic'),

    path('news_study/', news_study_views.news_study, name='news_study'),
    path('news_study/news_info_eng/', news_study_views.news_info_eng, name='news_info_eng'),
    path('news_study/news_info_inf/', news_study_views.news_info_inf, name='news_info_inf'),

    path('save-wordinfo/', news_study_views.save_wordinfo, name='save_wordinfo'),
    path('complete-word/', news_study_views.complete_word, name='complete_word'),

]
 