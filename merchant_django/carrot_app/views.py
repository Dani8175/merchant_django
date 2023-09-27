from django import forms
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from .forms import PostForm, RegisterForm, LoginForm
from django.utils.html import strip_tags
from django.http import HttpResponse
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import datetime
from django.utils.timesince import timesince


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.


def index(request):
    return render(request, "index.html")


def main(request):
    posts = Item.objects.order_by("-views")
    return render(request, "main.html", {"posts": posts})


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
    searched_items = Item.objects.all()

    if search_query:
        searched_items = searched_items.filter(
            Q(title__icontains=search_query) | Q(hope_loc__icontains=search_query)
        )
        redirect_url = request.path + "?search=" + search_query
    else:
        redirect_url = "/"

    return render(
        request,
        "search.html",
        {
            "search_query": search_query,
            "searched_items": searched_items,
            "redirect_url": redirect_url,
        },
    )


def trade(request):
    sort = request.GET.get("sort")  # sort 값 가져오기

    # sort 값에 따른 처리 로직 작성
    if sort == "latest":
        # 최신순으로 정렬하는 로직 작성
        posts = Item.objects.order_by("-upload_date")
    elif sort == "popular":
        # 인기순으로 정렬하는 로직 작성
        posts = Item.objects.order_by("-views")
    else:
        # 기본 정렬 로직 작성 (예: ID 순서)
        posts = Item.objects.all()

    context = {
        "sort": sort,
        "posts": posts,
    }
    return render(request, "trade.html", context)


def alert(request, alert_message):
    return render(request, "alert.html", {"alert_message": alert_message})


def trade_post(request, item_id):
    item = Item.objects.get(item_id=item_id)
    user = CustomUser.objects.get(username=request.user)

    last_view_time_str = request.session.get(f"last_view_time_{item_id}")
    current_time = datetime.datetime.now()

    if not last_view_time_str or (
        current_time - datetime.datetime.strptime(last_view_time_str, "%Y-%m-%d %H:%M:%S.%f")
    ) >= datetime.timedelta(seconds=5):
        item.views += 1
        item.save()
        request.session[f"last_view_time_{item_id}"] = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    if request.method == "POST":
        item.delete()
        return redirect("trade")

    return render(request, "trade_post.html", {"item": item})


def write(request):
    try:
        user_profile = CustomUser.objects.get(username=request.user)

        if user_profile.region is not None:
            return render(request, "write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except CustomUser.DoesNotExist:
        return redirect("alert", alert_message="로그인이 필요합니다.")


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)  # 임시 저장
            item.seller_name_id = request.user.id  # 작성자 정보 추가 (이 부분을 수정했습니다)
            item.save()  # 최종 저장
            return redirect("trade_post", item_id=item.item_id)  # 저장 후 상세 페이지로 이동
    else:
        form = PostForm()
    return render(request, "main.html", {"form": form})


def edit(request, item_id):
    post = get_object_or_404(Item, item_id=item_id)
    if post:
        post.content = post.content.strip()
    if request.method == "POST":
        post.title = request.POST["title"]
        post.price = request.POST["price"]
        post.content = request.POST["content"]
        post.hope_loc = request.POST["hope_loc"]
        if "image_url" in request.FILES:
            post.image_url = request.FILES["image_url"]
        post.save()
        return redirect("trade_post", item_id=post.item_id)

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
        redirect_url = request.GET.get("next", "/")
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(redirect_url)
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
    return render(request, "main.html")


@login_required
def account(request):
    return render(request, "account.html")

