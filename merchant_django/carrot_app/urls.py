from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from . import views
from django.conf import settings


urlpatterns = [
    path(r"", views.main, name="main"),
    path(r"login", auth_views.LoginView.as_view(), name="login"),
    path(r"logout", auth_views.LogoutView.as_view(), name="logout"),
    path(r"register", views.register_view, name="register"),
    path(r"chat", views.chat, name="chat"),
    path(r"location", views.location, name="location"),
    path(r"search", views.search, name="search"),
    path(r"trade", views.trade, name="trade"),
    path(r"trade_post", views.trade_post, name="trade_post"),
    path(r"write", views.write, name="write"),
    path(r"test", views.test, name="test"),
    path("set_region/", views.set_region_view, name="set_region"),
    path('set_region_certification/', views.main,name="set_region_certification"),

]
