from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class User(AbstractUser):

    
    """ Custom User model """

    LOGIN_EMAIL = "email"
    LOGIN_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_KAKAO, "Kakao"),
    )

    login_method = models.CharField(
        max_length=6, choices=LOGIN_CHOICES, default=LOGIN_KAKAO
    )

    def is_social_login(self):
        return self.login_method in [self.LOGIN_KAKAO]

class KakaoException(Exception):
    pass


class SocialLoginException(Exception):
    pass


class UserManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None
        

class User(models.Model):
    objects = UserManager()