from django.urls import path

from app_living_english.app_views import views_living_english
from app_living_english.app_views import living_english_cnvt_tpc

urlpatterns = [
    path('living-english/',   views_living_english.living_english, name='living_english'),
    path('cnvrt_tpc_exec/',   living_english_cnvt_tpc.main_cnvrt_tpc_exec, name='cnvrt_tpc_exec'),
]
