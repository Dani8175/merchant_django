from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import os

# Create your models here.


class CustomUser(AbstractUser):
    region = models.CharField(max_length=30, null=True)
    # 기타 필요한 메서드 또는 속성 정의


class Transaction(models.Model):
    trans_id = models.AutoField(primary_key=True)
    buyer_id = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    item_id = models.IntegerField()
    status = models.BooleanField(default=False)
    # False 미판매, True 판매완료


class items(models.Model):
    item_id = models.IntegerField(("ID"), primary_key=True)
    title = models.CharField(max_length=70)
    content = models.TextField()
    price = models.IntegerField()
    hope_loc = models.CharField(max_length=40)
    category_id = models.IntegerField()
    seller_id_id = models.BigIntegerField()
