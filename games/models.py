from django.db import models
from accounts.models import User # 수정 필요

class Game(models.Model):
    STATUS_CHOICES = [
        ('ongoing', '진행중'),
        ('end', '종료됨'),
    ]

    WINNER_CHOICES = [
        ('starting', '공격 유저 승리'),
        ('defending', '방어 유저 승리'),
        ('draw', '무승부'),
    ]

    startingPlayer = models.ForeignKey(User, verbose_name="공격한 유저", on_delete=models.CASCADE, related_name='games_started')
    startingPlayerNum = models.IntegerField("공격 숫자", default=0)

    defendingPlayer = models.ForeignKey(User, verbose_name="공격 받은 유저", on_delete=models.CASCADE, related_name='games_defended')
    defendingPlayerNum = models.IntegerField("반격 숫자", default=0)

    status = models.CharField("게임 상태", max_length=50, choices=STATUS_CHOICES, default='ongoing')

    winner = models.CharField("승자", max_length=50, choices=WINNER_CHOICES, blank=True, null=True)
    