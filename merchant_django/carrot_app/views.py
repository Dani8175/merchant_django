from django.shortcuts import render, redirect

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

def set_region_view(request):
    if request.method == 'POST':
        context = {'region' : request.POST['region-setting']}
    return render(request, 'location.html', context)

def set_region_certification(request):
    return render(request, "main.html")