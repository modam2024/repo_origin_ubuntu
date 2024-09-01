from django.urls import path

from app_test_timer.pkg_views import view_five_test
from app_test_timer.pkg_views import view_five_feedback
from app_test_timer.pkg_mdl_common import view_five_convert

urlpatterns = [
    path('test-english/',     view_five_test.test_english,         name='test_english'),
    path('test-result/',      view_five_test.test_result,          name='test_result'),
    path('feedback-english/', view_five_feedback.feedback_english, name='feedback_english'),
    path('timer-start/',      view_five_test.timer_start,          name='timer_start'),
    path('timer-stop/',       view_five_test.timer_stop,           name='timer_stop'),
    path('convert_sentence/', view_five_convert.convert_sentence,  name='convert_sentence'),
]
