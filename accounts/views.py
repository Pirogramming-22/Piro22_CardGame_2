from django.shortcuts import render

def login(request):
    return render(request, 'base.html')  # 임시로 base.html 렌더링 시켜놓음 (초기 로그인 페이지)


