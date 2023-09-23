from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from django.utils.html import strip_tags
from django.http import HttpResponse
from .models import CustomUser

# Create your views here.


def index(request):
    return render(request, "index.html")


def main(request):
    return render(request, "main.html")


def chat(request):
    return render(request, "chat.html")


def location(request):
    return render(request, "location.html")


def search(request):
    return render(request, "search.html")


def trade(request):
    return render(request, "trade.html")


def trade_post(request):
    return render(request, "trade_post.html")


def write(request):
    return render(request, "write.html")


def test(request):
    return render(request, "test.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = CustomUser.objects.create_user(username=username, password=password)
            return redirect("login")
        # else:
        #     print(form.non_field_errors())
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("main")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


def logout_request(request):
    logout(request)
    return redirect("main")


def set_region_view(request):
    if request.method == "POST":
        context = {"region": request.POST["region-setting"]}
    return render(request, "location.html", context)


def set_region_certification(request):
    return render(request, "main.html")
