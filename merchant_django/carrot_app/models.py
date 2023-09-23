from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os


def rename_imagefile_to_uuid(instance, filename):
    upload_to = f"uploads"
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


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    region = models.CharField(max_length=30, null=True)
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
    seller_id = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=70)
    content = models.TextField()
    price = models.IntegerField()
    hope_loc = models.CharField(max_length=40, null=True)
    category_id = models.IntegerField()

    class Meta:
        db_table = "Item"


class Transaction(models.Model):
    trans_id = models.AutoField(primary_key=True)
    buyer_id = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=False)

    # False 판매중, True 판매완료
    def __str__(self):
        return self.status

    class Meta:
        db_table = "Transaction"


class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    image_url = models.FileField(upload_to=rename_imagefile_to_uuid, default="")

    def __str__(self):
        return self.image_url

    class Meta:
        db_table = "Image"


class category(models.Model):
    category_id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"
