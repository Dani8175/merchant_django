from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from django.utils.html import strip_tags
from django.http import HttpResponse
from .models import *
from django.db.models import Q
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.


def index(request):
    return render(request, "index.html")


def main(request):
    return render(request, "main.html")


def chat(request):
    return render(request, "chat.html")


# def location(request):
#     return render(request, "location.html")


# 동네 인증
@login_required
def location(request):
    try:
        user_profile = UserProfile.objects.get(user_id=request.user)
        region = user_profile.region
    except UserProfile.DoesNotExist:
        region = None

    return render(request, 'location.html', {'region': region})


def search(request):
    search_query = request.GET.get("search")
    searched_items = Item.objects.filter(
        Q(title__icontains=search_query) | Q(hope_loc__icontains=search_query)
    )
    return render(
        request, "search.html", {"search_query": search_query, "searched_items": searched_items}
    )


def trade(request):
    posts = Item.objects.all()

    return render(request, "trade.html", {"posts": posts})


def trade_post(request, item_id):
    item = Item.objects.get(item_id=item_id)

    last_view_time_str = request.session.get(f"last_view_time_{item_id}")
    current_time = datetime.datetime.now()

    if not last_view_time_str or (
        current_time - datetime.datetime.strptime(last_view_time_str, "%Y-%m-%d %H:%M:%S.%f")
    ) >= datetime.timedelta(seconds=5):
        item.views += 1
        item.save()
        request.session[f"last_view_time_{item_id}"] = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    return render(request, "trade_post.html", {"item": item})


def write(request):
    post = Item.objects.all()
    return render(request, "write.html", {"post": post})


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


# def set_region_view(request):
#     if request.method == "POST":
#         context = {"region": request.POST["region-setting"]}
#     return render(request, "location.html", context)




@login_required
def set_region(request):
    if request.method == "POST":
        region = request.POST.get('region-setting')

        if region:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                user_profile.region = region
                user_profile.save()

                return redirect('location')
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})
        else:
            return JsonResponse({"status": "error", "message": "Region cannot be empty"})
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)



# 동네인증 완료
@login_required
def set_region_certification(request):
    if request.method == "POST":
        request.user.profile.region_certification = 'Y'
        request.user.profile.save()
        messages.success(request, "인증되었습니다")
        return redirect("location")