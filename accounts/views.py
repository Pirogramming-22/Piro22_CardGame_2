from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from .models import User
import requests

def social_login(request):
    return render(request, 'accounts/social_login.html')

def kakao_login(request):
    client_id = settings.KAKAO_API_KEY  # settings에서 바로 가져오기
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )

def kakao_login_callback(request):
    code = request.GET.get("code")
    client_id = settings.KAKAO_API_KEY  # settings에서 바로 가져오기
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"

    # 카카오에서 토큰 요청
    token_request = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    token_json = token_request.json()

    # 에러 처리
    error = token_json.get("error", None)
    if error is not None:
        print(f"Error during token request: {error}")
        return redirect("/")  # 에러 발생 시 메인 페이지로 리디렉션

    access_token = token_json.get("access_token")

    # 프로필 정보 요청
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    # 카카오 계정 정보 확인
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None)

    if email is None:
        print("No email found, redirecting to home.")
        return redirect("/")  # 이메일이 없으면 메인 페이지로 리디렉션

    # 프로필 정보
    properties = profile_json.get("properties")
    nickname = properties.get("nickname")
    profile_image = properties.get("profile_image")

    # 기존 사용자 확인 및 로그인 처리
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            social_id=profile_json.get("id"),
            first_name=nickname,
        )
        if profile_image:
            user.profile_image = profile_image
            user.save()

    login(request, user)  # 로그인 처리

    # 로그인 상태 확인 후 리디렉션
    if request.user.is_authenticated:
        print(f'User logged in: {request.user.is_authenticated}')
        print(f"Redirecting to mainpage...")
        return redirect('accounts:mainpage')  # mainpage로 리디렉션
    else:
        print("User authentication failed, redirecting to /")
        return redirect("/")  # 로그인 실패시 메인 페이지로 리디렉션

def main(request):
    return render(request, 'accounts/main.html', {'user': request.user})
