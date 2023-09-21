from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from . import views
from django.conf import settings


urlpatterns = [
    path(r"", views.main, name="main"),
    path(r"index", views.index, name="index"),
    path(r"chat", views.chat, name="chat"),
    path(r"location", views.location, name="location"),
    path(r"search", views.search, name="search"),
    path(r"trade", views.trade, name="trade"),
    path(r"trade_post", views.trade_post, name="trade_post"),
    path(r"write", views.write, name="write"),
    path(r"test", views.test, name="test"),
    path("set_region/", views.set_region_view, name="set_region"),
    path('set_region_certification/', views.main,name="set_region_certification"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
