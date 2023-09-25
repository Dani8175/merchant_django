from django.shortcuts import render, redirect
from .models import items

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
    post = items.objects.all()
    return render(request, "write.html", {"post": post})


def test(request):
    return render(request, "test.html")
