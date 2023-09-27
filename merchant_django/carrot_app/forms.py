from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegisterForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get("username")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("이미 사용 중인 아이디입니다.")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if (username and password) or (username and not password) or (not username and password) or (not username and not password):  # 아이디와 비밀번호가 모두 입력되었을 경우
            user = CustomUser.objects.filter(username=username).first()  # DB에서 해당 아이디의 유저를 조회

            if not user or not user.check_password(password):
                raise forms.ValidationError("아이디 또는 비밀번호를 다시 확인해 주세요")

        return cleaned_data



class PostForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'price', 'content', 'hope_loc', 'image_url']