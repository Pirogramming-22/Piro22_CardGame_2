from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.main, name='main'),  
    path('login/kakao/', views.kakao_login, name='kakao-login'),
    path('login/kakao/callback/', views.kakao_login_callback, name='kakao-callback'),
    path('login/naver/', views.naver_login, name='naver-login'),
    path('login/naver/callback/', views.naver_login_callback, name='naver-callback'),
    path('login/naver/', views.naver_login, name='naver-login'),
    path('login/naver/callback/', views.naver_login_callback, name='naver-callback'),
    path('social_login', views.social_login, name="social_login"),
    path('start/', views.start, name='start'), 
    path('logout/', views.user_logout, name='logout'),
    path('mainpage/', views.main, name='mainpage'),
]