from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os
from datetime import datetime

from django.conf import settings


def rename_imagefile_to_uuid(instance, filename):
    upload_to = f""
    ext = filename.split(".")[-1]
    uuid = uuid4().hex
    filename = "{}.{}".format(uuid, ext)

    return os.path.join(upload_to, filename)


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    region = models.CharField(max_length=100, null=True)
    region_certification = models.CharField(max_length=1, default='N')

    def __str__(self):
        return f'{self.user.username} Profile'

class CustomUser(AbstractUser):
    objects = CustomUserManager()
    region = models.CharField(max_length=30, null=True)
    # manner = models.IntegerField(default=36.5)
    # buy_item_count = models.IntegerField(default=0)
    # sell_item_count = models.IntegerField(default=0)

    class Meta:
        db_table = "User"

    # 추후 view에서 region 사용시
    # from django.contrib.auth.decorators import login_required

    # @login_required
    # def my_view(request):
    #     user = request.user
    #     custom_user = user.customuser
    #     custoum_user.region = #gps기반 위치 ##시 ##구 ##동
    #     custom_user.save()
    # class Meta:
    #     db_table = "User"


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    seller_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=70)
    content = models.TextField()
    price = models.IntegerField()
    hope_loc = models.CharField(max_length=40, null=True)
    views = models.IntegerField(default=0)
    category = models.ForeignKey(
        "Category",
        on_delete=models.DO_NOTHING,
        related_name="category_number",
        default=None,
        null=True,
    )
    image_url = models.FileField(upload_to=rename_imagefile_to_uuid, default="")
    chat_count = models.IntegerField(default=0)

    def update_chat_count(self):
        self.chat_count = Chat.objects.filter(item=self).count()
        self.save()

    class Meta:
        db_table = "Item"

    def __str__(self):
        return self.title


class Transaction(models.Model):
    trans_id = models.AutoField(primary_key=True)
    buyer_name = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=False)

    # False 판매중, True 판매완료
    def __str__(self):
        return self.status

    class Meta:
        db_table = "Transaction"


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"


class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    content = models.TextField()
    sender = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name="sender_name")
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="receiver_name"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Chat"

    def __str__(self):
        current_year = datetime.now().year
        message_year = self.timestamp.year

        if current_year == message_year:
            return f'{self.sender.username} -> {self.receiver.username}: {self.content} ({self.timestamp.strftime("%-m-%-d %H:%M")})'
        else:
            return f'{self.sender.username} -> {self.receiver.username}: {self.content} ({self.timestamp.strftime("%Y-%-m-%-d %H:%M")})'
