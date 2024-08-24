from django.urls import path

from app_test_timer.app_views import views_five_test
from app_test_timer.app_views import views_five_feedback

urlpatterns = [
    path('test-english/',     views_five_test.test_english,         name='test_english'),
    path('test-result/',      views_five_test.test_result,          name='test_result'),
    path('feedback-english/', views_five_feedback.feedback_english, name='feedback_english'),
    path('timer-start/',      views_five_test.timer_start,          name='timer_start'),
    path('timer-stop/',       views_five_test.timer_stop,           name='timer_stop'),
]
