from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from .models import User
import requests
import os

def social_login(request):
    return render(request, 'accounts/social_login.html')

def kakao_login(request):
    client_id = settings.KAKAO_API_KEY
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )

def kakao_login_callback(request):
    code = request.GET.get("code")
    client_id = os.getenv("KAKAO_API_KEY")
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"

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
    
    error = token_json.get("error", None)
    if error is not None:
        return redirect("/")
        
    access_token = token_json.get("access_token")

    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None)
    
    if email is None:
        return redirect("/")
        
    properties = profile_json.get("properties")
    nickname = properties.get("nickname")
    profile_image = properties.get("profile_image")
    
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
    
    login(request, user)
    return redirect('accounts:main') 