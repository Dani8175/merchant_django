import re
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
import openai
import json
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import requests

# Create your views here.


def index(request):
    return render(request, "index.html")


def main(request):
    posts = Item.objects.filter(is_end=False).order_by("-views")
    return render(request, "main.html", {"posts": posts})


def chat(request, room_num=None):
    chats = Chat.objects.filter(Q(receiver=request.user.id) | Q(sender=request.user.id)).order_by(
        "-timestamp"
    )
    if room_num is not None:
        room = get_object_or_404(Chat, chat_id=room_num)
        if request.method == "POST":
            room.item.is_end = True
            room.item.save()
            room.save()
            return redirect("chat", room.chat_id)
    else:
        room = None

    if not chats:
        chats = None  # 채팅이 없는 경우에는 chats 변수를 None으로 설정하여 링크 생성을 방지

    return render(request, "chat.html", {"chats": chats, "room": room})


# def location(request):
#     return render(request, "location.html")


# 동네 인증
@login_required
def location(request):
    try:
        user_profile = CustomUser.objects.get(username=request.user)
        region = user_profile.region
    except CustomUser.DoesNotExist:
        region = None

    return render(request, "location.html", {"region": region})


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


def update_chat_count(request):
    # chat 테이블에서 item_id가 동일한 항목들을 찾아서 count
    chat_count_by_item = Chat.objects.values("item_id").annotate(chat_count=Count("item_id"))

    # item 테이블의 chat_count 컬럼에 값 업데이트
    for chat in chat_count_by_item:
        item_id = chat["item_id"]
        chat_count = chat["chat_count"]
        Item.objects.filter(item_id=item_id).update(chat_count=chat_count)


def trade(request):
    sort = request.GET.get("sort")  # sort 값 가져오기
    update_chat_count(request)
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


def extract_post_number(url):
    match = re.search(r"post/(\d+)/", url)
    if match:
        return match.group(1)
    return None


def trade_post(request, item_id):
    item = Item.objects.get(item_id=item_id)

    try:
        reverse_chat = Chat.objects.get(Q(item_id=item_id) & Q(sender=request.user))
    except Chat.DoesNotExist:
        reverse_chat = None

    last_view_time_str = request.session.get(f"last_view_time_{item_id}")
    current_time = datetime.datetime.now()

    if not last_view_time_str or (
        current_time - datetime.datetime.strptime(last_view_time_str, "%Y-%m-%d %H:%M:%S.%f")
    ) >= datetime.timedelta(seconds=5):
        item.views += 1
        item.save()
        request.session[f"last_view_time_{item_id}"] = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    if request.method == "POST" and "delete" in request.POST:
        item.delete()
        return redirect("trade")
    elif request.method == "POST" and "urlPart" in request.POST:
        url_part = request.POST.get("urlPart")
        post_number = extract_post_number(url_part)

        chats = Chat.objects.filter(item_id=post_number, sender=request.user)
        if not chats.exists():
            Chat.objects.create(item_id=post_number, sender=request.user, receiver=item.seller_name)

        # request.session["post_number"] = post_number

        return redirect("chat")

    return render(request, "trade_post.html", {"item": item, "reverse_chat": reverse_chat})


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
        region = request.POST.get("region-setting")

        if region:
            try:
                customuser, created = CustomUser.objects.get_or_create(username=request.user)
                customuser.region = region
                customuser.save()

                # return render(request, "location.html", {"customuser": customuser})
                return redirect("location")
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
        # request.user.profile.region_certification = "Y"
        # request.user.profile.save()
        messages.success(request, "인증되었습니다")
        return redirect("location")
    # return render(request, "main.html")


@login_required
def account(request):
    posts = Item.objects.filter(seller_name=request.user)
    return render(request, "account.html", {"posts": posts})


def village_store(request):
    return render(request, "village_store.html")


def search_places(query):
    api_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_MAPS_API_KEY}"}
    params = {"query": query}
    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()
    return data


class ChatBot:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.messages = []

    def ask(self, question):
        self.messages.append({"role": "user", "content": question})
        res = self.__ask__()
        return res

    def __ask__(self):
        completion = openai.ChatCompletion.create(
            # model 지정
            model=self.model,
            messages=self.messages,
        )
        response = completion.choices[0].message["content"]
        self.messages.append({"role": "assistant", "content": response})
        return response

    def show_messages(self):
        return self.messages

    def clear(self):
        self.messages.clear()


def execute_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        question = data.get("question")
        chatbot = ChatBot()
        response = chatbot.ask(question)
        return JsonResponse({"response": response})
    return render(request, "post_list.html")


def index(request):
    return render(request, "carrot_app/chat_index.html")


# 채팅방 열기
# def chat_room(request, pk):
#     user = request.user
#     chat_room = get_object_or_404(ChatRoom, pk=pk)

#     # 내 ID가 포함된 방만 가져오기
#     chat_rooms = ChatRoom.objects.filter(Q(receiver_id=user) | Q(starter_id=user)).order_by(
#         "-latest_message_time"
#     )  # 최신 메시지 시간을 기준으로 내림차순 정렬

#     # 각 채팅방의 최신 메시지를 가져오기
#     chat_room_data = []
#     for room in chat_rooms:
#         latest_message = Message.objects.filter(chatroom=room).order_by("-timestamp").first()
#         if latest_message:
#             chat_room_data.append(
#                 {
#                     "chat_room": room,
#                     "latest_message": latest_message.content,
#                     "timestamp": latest_message.timestamp,
#                 }
#             )

#     # 상대방 정보 가져오기
#     if chat_room.receiver == user:
#         opponent = chat_room.starter
#     else:
#         opponent = chat_room.receiver

#     opponent_user = User.objects.get(pk=opponent.pk)

#     # post의 상태 확인 및 처리
#     if chat_room.post is None:
#         seller = None
#         post = None
#     else:
#         seller = chat_room.post.user
#         post = chat_room.post

#     return render(
#         request,
#         "carrot_app/chat_room.html",
#         {
#             "chat_room": chat_room,
#             "chat_room_data": chat_room_data,
#             "room_name": chat_room.pk,
#             "seller": seller,
#             "post": post,
#             "opponent": opponent_user,
#         },
#     )


# # 채팅방 생성 또는 참여
# def create_or_join_chat(request, pk):
#     post = get_object_or_404(Item, pk=pk)
#     user = request.user
#     chat_room = None
#     created = False

#     # 채팅방이 이미 존재하는지 확인
#     chat_rooms = ChatRoom.objects.filter(
#         Q(starter=user, receiver=post.user, post=post)
#         | Q(starter=post.user, receiver=user, post=post)
#     )
#     if chat_rooms.exists():
#         chat_room = chat_rooms.first()
#     else:
#         # 채팅방이 존재하지 않는 경우, 새로운 채팅방 생성
#         chat_room = ChatRoom(starter=user, receiver=post.user, post=post)
#         chat_room.save()
#         created = True

#     return JsonResponse({"success": True, "chat_room_id": chat_room.pk, "created": created})


# # 가장 최근 채팅방 가져오기
# @login_required
# def get_latest_chat(request, pk):
#     user = request.user
#     # 1) 해당 pk인 채팅방 중 가장 최신 채팅방으로 리디렉션
#     try:
#         latest_chat_with_pk = ChatRoom.objects.filter(
#             Q(post_id=pk) & (Q(receiver=user) | Q(starter=user))
#         ).latest("latest_message_time")
#         return JsonResponse({"success": True, "chat_room_id": latest_chat_with_pk.room_number})
#     except ChatRoom.DoesNotExist:
#         pass

#     # 2) 위 경우가 없다면 내가 소속된 채팅방 전체 중 가장 최신 채팅방으로 리디렉션
#     try:
#         latest_chat = ChatRoom.objects.filter(Q(receiver=user) | Q(starter=user)).latest(
#             "latest_message_time"
#         )
#         return JsonResponse({"success": True, "chat_room_id": latest_chat.room_number})

#     # 3) 모두 없다면 현재 페이지로 리디렉션
#     except ChatRoom.DoesNotExist:
#         return redirect("carrot_app:alert", alert_message="진행중인 채팅이 없습니다.")


# # nav/footer에서 채팅하기 눌렀을 때
# @login_required
# def get_latest_chat_no_pk(request):
#     user = request.user
#     try:
#         latest_chat = ChatRoom.objects.filter(
#             Q(receiver=user) | Q(starter=user), latest_message_time__isnull=False
#         ).latest("latest_message_time")
#         return redirect("carrot_app:chat_room", pk=latest_chat.room_number)

#     except ChatRoom.DoesNotExist:
#         return redirect("carrot_app:alert", alert_message="진행중인 채팅이 없습니다.")


# @method_decorator(login_required, name="dispatch")
# class ConfirmDealView(View):
#     def post(self, request, post_id):
#         post = get_object_or_404(Item, pk=post_id)
#         user = request.user

#         chat_rooms = ChatRoom.objects.filter(
#             Q(post_id=post_id),
#             (Q(receiver=user) | Q(starter=user)),
#             latest_message_time__isnull=False,
#         )

#         if chat_rooms.exists():
#             chat_room = chat_rooms.latest("latest_message_time")

#             if chat_room.starter == user:
#                 other_user = chat_room.receiver
#             else:
#                 other_user = chat_room.starter

#             # buyer를 설정하고, product_sold를 Y로 설정
#             post.buyer = other_user
#             post.product_sold = "Y"
#             post.save()

#             # 거래가 확정되면 새로고침
#             return redirect("carrot_app:chat_room", pk=chat_room.room_number)
#         else:
#             # 채팅방이 존재하지 않을 때의 처리
#             messages.error(request, "Chat room does not exist.")
#             return redirect("carrot_app:chat_room", pk=post_id)
