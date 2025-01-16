from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.social_login, name='main'),  
    # path('login', views.login, name='login'),
    # path('signup', views.signup, name='signup'),
    path('login/kakao/', views.kakao_login, name='kakao-login'),
    path('login/kakao/callback/', views.kakao_login_callback, name='kakao-callback'),
    # path('social_login', views.social_login, name="social_login"),
]