from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import SignUpForm
from django.utils.html import strip_tags

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
    form = UserCreationForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("main")
        else:
            error_message = form.errors.get("username", "")
        if error_message:
            error_message = error_message.as_text()
    return render(
        request,
        "registration/register.html",
        {"form": form, "error_message": strip_tags(form.errors.get("username", ""))},
    )


# def login_view(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#                 login(request, user)
#                 return redirect("main")
#             else:
#                 form.add_error(None, "로그인에 실패했습니다.")
#     else:
#         form = AuthenticationForm(request)
#     return render(request, "login.html", {"form": form})


def logout_request(request):
    logout(request)
    return redirect("main")


def set_region_view(request):
    if request.method == "POST":
        context = {"region": request.POST["region-setting"]}
    return render(request, "location.html", context)


def set_region_certification(request):
    return render(request, "main.html")
