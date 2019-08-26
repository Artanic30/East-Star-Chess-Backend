from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=20, default='你还没有设置哦', unique=False)
    username = models.CharField(max_length=20, primary_key=True, unique=True, default='')
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    remark = models.CharField(max_length=50, default='你还没有设置哦')
    email = models.EmailField(default='', max_length=50)
    ups = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ups_user', verbose_name='profile_ups', null=True)
    downs = models.ForeignKey('User', on_delete=models.CASCADE, related_name='downs_user', verbose_name='profile_downs', null=True)


class Board(models.Model):
    board = models.CharField(max_length=300)
    sign = models.IntegerField(default=1)
    players = models.ManyToManyField(User, through='BoardInfo')


class BoardInfo(models.Model):
    players = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    createTime = models.DateField(auto_now_add=True)
    endTime = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'lin_BoardInfo'
