# games/views.py
from django.shortcuts import render, redirect
from .models import Game
from django.urls import reverse
from accounts.models import User
import random
from django.db.models import Q

def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None

def attack(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:social_login')

    starting_player = user
    users = User.objects.exclude(id=user.id)
    numbers = random.sample(range(1, 11), 5)

    if request.method == 'POST':
        selected_card = request.POST.get('card')
        defending_player_id = request.POST.get('defending_player')

        # 카드와 방어자가 선택되지 않은 경우
        if not selected_card or not defending_player_id:
            print("카드 또는 방어자 미선택 오류 발생")
            return render(request, 'games/startgame.html', {
                'numbers': numbers,
                'users': users,
            })

        # 방어자 유효성 검증
        try:
            defending_player = User.objects.get(id=defending_player_id)
            Game.objects.create(
                startingPlayer=starting_player,
                startingPlayerNum=int(selected_card),
                defendingPlayer=defending_player,
                status='ongoing'
            )
            print(f"게임 생성 성공: {selected_card} vs {defending_player}")
        except Exception as e:
            print(f"게임 생성 실패: {e}")
            return render(request, 'games/startgame.html', {
                'numbers': numbers,
                'users': users,
            })

        return redirect('games:history_list')

    return render(request, 'games/startgame.html', {'numbers': numbers, 'users': users})



def history_list(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:social_login')

    # 현재 유저가 참여한 모든 게임 가져오기
    games = Game.objects.filter(
        Q(startingPlayer=user) | Q(defendingPlayer=user)
    )
    print(f"유저: {user.first_name}, 게임 수: {games.count()}")  # 디버깅용 로그

    game_info = []

    for game in games:
        # 게임 진행 상태에 따라 구분
        if game.status == 'ongoing':
            if game.startingPlayer == user:  # 내가 공격자인 경우
                game_info.append({
                    'game_id': game.id,
                    'opponent': game.defendingPlayer.first_name,
                    'status': '진행중 ...',
                    'action': '취소하기',
                    'link': f"/cancel/{game.id}/"  # 게임 취소 링크
                })
            elif game.defendingPlayer == user:  # 내가 방어자인 경우
                game_info.append({
                    'game_id': game.id,
                    'opponent': game.startingPlayer.first_name,
                    'status': '진행중 ...',
                    'action': '반격하기',
                    'link': f"/counterAttack/{game.id}/"  # 반격 링크
                })
        elif game.status == 'end':
            # 종료된 경우 결과 처리
            result = '무승부'
            if game.winner == 'starting':
                result = '승리' if game.startingPlayer == user else '패배'
            elif game.winner == 'defending':
                result = '승리' if game.defendingPlayer == user else '패배'

            game_info.append({
                'game_id': game.id,
                'opponent': game.defendingPlayer.first_name if game.startingPlayer == user else game.startingPlayer.first_name,
                'status': f'결과 : ({result})',
                'action': '결과 보기',
                'link': f"/gamedetail/{game.id}/"  # 게임 상세 보기 링크
            })

    print(f"게임 정보: {game_info}")  # 디버깅용 로그

    ctx = {'user': user, 'game_info': game_info}
    return render(request, 'games/gamelist.html', ctx)


 # 게임 종료 후 점수 업데이트
def update_scores(self):
    if self.winner == 'starting':
        self.startingPlayer.score += self.startingPlayerNum  # 공격 유저는 카드를 점수로 얻음
        self.defendingPlayer.score -= self.defendingPlayerNum  # 방어 유저는 카드를 점수에서 차감
    elif self.winner == 'defending':
        self.defendingPlayer.score += self.defendingPlayerNum  # 방어 유저는 카드를 점수로 얻음
        self.startingPlayer.score -= self.startingPlayerNum  # 공격 유저는 카드를 점수에서 차감
    # 무승부일 경우 점수 변동 없음
    self.startingPlayer.save()
    self.defendingPlayer.save()