from django.urls import path

from app_word_work.pkg_views import view_word_work

urlpatterns = [
    # 기타 url 패턴들
    path('main-wordcheck/',    view_word_work.main_word_check,    name='main-word-check'),
    path('delete-content/',    view_word_work.delete_content,     name='delete-content'),
    path('main-wordtable/',    view_word_work.main_word_table,    name='main-word-table'),
    path('confirm-wordcheck/', view_word_work.confirm_word_check, name='confirm-word-check'),
    path('call-process/',      view_word_work.call_process,       name='call-process'),
    path('goto-init/',         view_word_work.fn_goto_init,        name='goto-init'),

    path('word_detail/',       view_word_work.word_detail,        name='word_detail'),
    path('save-wordinfo/',     view_word_work.save_wordinfo,      name='save_wordinfo'),
    path('complete-word/',     view_word_work.complete_word,      name='complete_word'),
    path('create-word/',       view_word_work.create_word,        name='create-word'),
]
