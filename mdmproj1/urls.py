from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from app_open_article.pkg_views import views_article as article_views
from balance import views as balance_views
from mdl_login_info import views as login_views
from proj_batch import btch_five_test
from proj_batch import btch_living_english
from proj_batch import btch_news_study
from proj_sql_mapping import mdl_mapping_sql_proj as proj_sql_statement
from proj_common import mdl_common_proj as proj_mdl_common


urlpatterns = [
    # 어플리케이션 url 참조

    path('app_open_article/',   include('app_open_article.urls')),
    path('app_word_work/',      include('app_word_work.urls')),
    path('app_news_study/',     include('app_news_study.urls')),
    path('app_test_timer/',     include('app_test_timer.urls')),
    path('app_living_english/', include('app_living_english.urls')),
    # 2024.11.04 추가
    path('app_recognize_speech/', include('app_recognize_speech.urls')),

    # 기타 url 패턴들
    path('', proj_sql_statement.check_login_status, name='check_login_status'),
    path('admin/',    admin.site.urls),
    path('login/',    auth_views.LoginView.as_view(template_name='registration/login.html'),  name='login'),
    path('logout/',   auth_views.LogoutView.as_view(), name='logout'),
    path('register/', login_views.register, name='register'),
    path('balance/',  balance_views.main_view),

    path('test-batch/'                 , btch_five_test.test_batch,         name='test_batch'),
    path('news-batch/'                 , btch_news_study.batch_news_study,  name='engl-batch'),
    path('engl-batch/'                 , btch_living_english.living_english_batch, name='engl-batch'),

    path('proj-common/submit_analysis_words/', proj_mdl_common.submit_analysis_words, name='submit-article'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),

    # 2024.10.31. 추가
    path('text-to-speech/', proj_mdl_common.text_to_speech, name='text_to_speech'),
]
 