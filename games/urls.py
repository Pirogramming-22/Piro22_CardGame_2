from django.urls import path
from django.urls import path
from . import views
app_name = 'games'

urlpatterns = [
    path('', views.history_list, name='home'),  # 홈 페이지 -> 게임 히스토리 페이지
    path('history/', views.history_list, name='history_list'),  # 게임 히스토리 페이지
    path('attack/', views.attack, name='attack'),  # 공격 페이지

    # 다른 게임 관련 URL 추가 

    #게임 디테일
    path('game_detail/<int:game_id>/', views.game_detail, name='game_detail'), #게임상세페이지
    path('cancel/<int:game_id>/', views.cancel_game, name='cancel_game'), #게임취소처리
    path('counterAttack/<int:game_id>/', views.counter_attack, name='counter_attack'), #반격격
]