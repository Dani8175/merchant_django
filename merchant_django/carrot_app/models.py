from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
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


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
#     )
#     region_certification = models.CharField(max_length=1, default="N")

#     def __str__(self):
#         return f"{self.user.username} Profile"


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
    is_end = models.BooleanField(default=False)
    # False 판매중, True 판매완료

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
    content = models.TextField(null=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name="sender_name")
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="receiver_name"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    last_message = models.OneToOneField('Message', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "Chat"

    def __str__(self):
        current_year = datetime.now().year
        message_year = self.timestamp.year

        if current_year == message_year:
            return f'{self.sender.username} -> {self.receiver.username}: {self.content} ({self.timestamp.strftime("%-m-%-d %H:%M")})'
        else:
            return f'{self.sender.username} -> {self.receiver.username}: {self.content} ({self.timestamp.strftime("%Y-%-m-%-d %H:%M")})'


class ChatRoom(models.Model):
    room_number = models.AutoField(primary_key=True)
    starter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="started_chats"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_chats"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    latest_message_time = models.DateTimeField(null=True, blank=True)
    post = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="chat_rooms", null=True, blank=True
    )
    seller_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"ChatRoom: {self.starter.username} and {self.receiver.username}"


class Message(models.Model):
    chatroom = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="authored_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message: {self.author.username} at {self.timestamp}"

    def save(self, *args, **kwargs):
        self.content = f"{self.author.username}:{self.content}"
        super().save(*args, **kwargs)

    def get_speaker_and_content(self):
        parts = self.content.split(":")
        if len(parts) == 2:
            speaker = parts[0]
            content = parts[1]
            return speaker, content
        else:
            return None, None
