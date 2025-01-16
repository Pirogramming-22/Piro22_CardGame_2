from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from .models import User
import requests
from django.contrib.auth import logout

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
        return redirect('accounts:main')  # mainpage로 리디렉션
    else:
        print("User authentication failed, redirecting to /")
        return redirect("/")  # 로그인 실패시 메인 페이지로 리디렉션

def main(request):
    return render(request, 'accounts/main.html', {'user': request.user})


def naver_login(request):
    client_id = settings.NAVER_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8000/accounts/login/naver/callback"
    state = "RANDOM_STATE"  
    
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope=name email profile_image gender"
    )

def naver_login_callback(request):
    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    code = request.GET.get("code")
    state = request.GET.get("state")
    
    token_request = requests.post(
        "https://nid.naver.com/oauth2.0/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "state": state,
        },
    )
    token_json = token_request.json()
    
    if "error" in token_json:
        return redirect("/")
        
    access_token = token_json.get("access_token")
    
    profile_request = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    
    if profile_json.get("resultcode") != "00":
        return redirect("/")
        
    response = profile_json.get("response")
    email = response.get("email")
    name = response.get("name")
    profile_image = response.get("profile_image")
    gender = response.get("gender")
    
    if not email or not name:
        return redirect("/")
        
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            social_id=f"naver_{response.get('id')}",
            first_name=name,
        )
        if profile_image:
            user.profile_image = profile_image
        user.save()
            
    login(request, user)
    
    return redirect('accounts:main') if request.user.is_authenticated else redirect("/")

# def main(request):
#     return render(request, 'accounts/main.html')


def social_login(request):
    return render(request, 'accounts/social_login.html')


def start(request):
    if not request.user.is_authenticated:
        # 로그인하지 않은 사용자라면 social_login 페이지로 리디렉션
        return redirect('accounts:social_login')
    
    # 로그인된 사용자라면 start 페이지를 렌더링
    return render(request, 'accounts/start.html', {'user': request.user})

def user_logout(request):
    logout(request)  # 세션 종료
    return redirect('accounts:main')  # 로그아웃 후 리디렉션할 페이지 (예: 메인 페이지)