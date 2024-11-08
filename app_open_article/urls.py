from django.urls import path

from app_open_article.pkg_views import views_article

urlpatterns = [
    # 기타 url 패턴들
    path( "open_article/",        views_article.main_view, name='main_view'),
    path("",                      views_article.main_view, name='main_view2'),
]
