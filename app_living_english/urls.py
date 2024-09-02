from django.urls import path

from app_living_english.pkg_views import view_living_english
from app_living_english.pkg_views import view_living_eng_cnvt_tpc
from app_living_english.pkg_views import view_living_eng_morph_analysis

urlpatterns = [
    path('living-english/',   view_living_english.living_english, name='living_english'),
    path('cnvrt_tpc_exec/',   view_living_eng_cnvt_tpc.main_cnvrt_tpc_exec, name='cnvrt_tpc_exec'),
    path('morph_analysis/',   view_living_eng_morph_analysis.submit_topic, name='living_eng_submit_topic'),
]
