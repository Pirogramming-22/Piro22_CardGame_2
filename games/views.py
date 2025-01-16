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

from django.shortcuts import render, redirect
from .models import Game
from django.urls import reverse
from accounts.models import User
import random
from django.db.models import Q

def attack(request):
    user = request.user  # request.user를 사용하여 로그인된 사용자 가져오기
    
    if not user.is_authenticated:
        return redirect('accounts:social_login')  # 로그인하지 않은 경우 social_login 페이지로 리디렉션

    starting_player = user  # 시작 플레이어는 로그인한 사용자
    users = User.objects.exclude(id=user.id)  # 로그인한 사용자를 제외한 다른 사용자들
    numbers = random.sample(range(1, 11), 5)  # 1부터 10까지의 숫자 중 5개를 랜덤으로 선택

    if request.method == 'POST':
        selected_card = request.POST.get('card')  # 선택된 카드
        defending_player_id = request.POST.get('defending_player')  # 방어할 플레이어의 ID
        
        # 카드가 선택되지 않았으면 경고 메시지 출력
        if not selected_card:
            return render(request, 'games/startgame.html', {
                'error': '⚠️ 카드를 선택해주세요!',  # 경고문
                'numbers': numbers,
                'users': users
            })
        
        # ID로 User 객체를 가져옴
        try:
            defending_player = User.objects.get(id=defending_player_id)
        except User.DoesNotExist:
            return render(request, 'games/startgame.html', {
                'error': 'Defending player does not exist.',
                'numbers': numbers,
                'users': users
            })

        # 게임 생성
        game = Game.objects.create(
            startingPlayer=starting_player,
            startingPlayerNum=selected_card,
            defendingPlayer=defending_player,
            status='ongoing'
        )

        # 게임 목록 페이지로 리디렉션
        game_list_url = reverse('games:history_list')  # 게임 목록 URL
        return redirect(game_list_url)

    # GET 요청 시
    ctx = { 'numbers': numbers, 'users': users }
    return render(request, 'games/startgame.html', ctx)

def history_list(request):
    user = request.user  # request.user를 사용하여 로그인된 사용자 가져오기
    if not user.is_authenticated:
        return redirect('accounts:social_login')  # 로그인하지 않은 경우 social_login 페이지로 리디렉션

    games = Game.objects.filter(
        Q(startingPlayer=user) | Q(defendingPlayer=user)
    )
    game_info = []

    for game in games:
        if game.status == 'ongoing':
            if game.defendingPlayer == user:
                game_info.append({
                    'game_id': game.id,
                    'opponent': game.startingPlayer.name,
                    'status': 'ongoing',
                    'link': f"/counterAttack/{game.id}"
                })
            else:
                game_info.append({
                    'game_id': game.id,
                    'opponent': game.defendingPlayer.name,
                    'status': 'ongoing',
                    'link': f"/cancel/{game.id}"
                })
        elif game.status == 'end':
            if game.winner == 'starting':
                result = '승리' if game.startingPlayer == user else '패배'
            elif game.winner == 'defending':
                result = '승리' if game.defendingPlayer == user else '패배'
            elif game.winner == 'draw':
                result = '무승부'

            game_info.append({
                'game_id': game.id,
                'opponent': game.defendingPlayer.name if game.startingPlayer == user else game.startingPlayer.name,
                'status': f'종료됨 ({result})',
                'link': f"/gamedetail/{game.id}/"
            })

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


#게임 디테일 페이지
from django.shortcuts import render, get_object_or_404, redirect
from .models import Game
from accounts.models import User
from django.contrib.auth.decorators import login_required

@login_required
def game_detail(request, game_id):
    user = request.user
    game = get_object_or_404(Game, id=game_id)


    if game.status == 'ongoing':
        if game.startingPlayer == user:
            # '다른 유저에게 싸움을 건(아직 반격x)' 상태
            context = {
                'game': game,
                'user': user,
                'status': '진행중...',
                'card_number': game.startingPlayerNum,
            }
        elif game.defendingPlayer == user:
            # '다른 유저가 싸움을 걸어온' 상태
            context = {
                'game': game,
                'user': user,
            }
        else:
            context = {'error': '게임 상태를 처리할 수 없습니다.'}

    elif game.status == 'end':
        # '이미 종료된 게임' 상태
        result = {
            '승리': '✨승리!✨',
            '패배': '🥲패배🥲',
            '무승부': '💥무승부💥'
        }


        if game.winner == 'starting':
            if game.startingPlayer == user:
                game_result = result['승리']
                score = f'🎯 {game.startingPlayerNum} 점 획득'
            else:
                game_result = result['패배']
                score = f'💔 {game.defendingPlayerNum} 점 차감'

        elif game.winner == 'defending':
            if game.defendingPlayer == user:
                game_result = result['승리']
                score = f'🎯 {game.defendingPlayerNum} 점 획득'
            else:
                game_result = result['패배']
                score = f'💔 {game.startingPlayerNum} 점 차감'
        elif game.winner == 'draw':
            game_result = result['무승부']
            score = '😐 점수 변동 없음'

        game_result = result.get(game.winner, 'Unknown result')
        context = {
            'game': game,
            'user': user,
            'game_result': game_result,
            'score': score 
        }

    return render(request, 'games/game_detail.html', context)
