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
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from app_living_english.pkg_views import view_living_eng_morph_analysis as morph_analysis
from article import views as article_views
from balance import views as balance_views
from mdl_login_info import views as login_views
from proj_batch import btch_five_test
from proj_batch import btch_living_english
from proj_batch import btch_news_study


urlpatterns = [
    # 어플리케이션 url 참조
    path('app_news_study/',     include('app_news_study.urls')),
    path('app_test_timer/',     include('app_test_timer.urls')),
    path('app_living_english/', include('app_living_english.urls')),

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
    path('article/complete-chapter/'   , article_views.complete_chapter  ,  name='complete_chapter'),
    path('article/uncomplete-chapter/' , article_views.uncomplete_chapter,  name='uncomplete_chapter'),
    path('article/save-topic/'         , article_views.save_topic,          name='save-topic'),
    path('article/create-word/'        , article_views.create_word,         name='create-word'),

    path('test-batch/'                 , btch_five_test.test_batch,         name='test_batch'),
    path('news-batch/'                 , btch_news_study.batch_news_study,  name='engl-batch'),
    path('engl-batch/'                 , btch_living_english.living_english_batch, name='engl-batch'),
]
 