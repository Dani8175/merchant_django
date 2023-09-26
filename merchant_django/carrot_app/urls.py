from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from . import views
from django.conf import settings


urlpatterns = [
    path(r"", views.main, name="main"),
    path(r"login", views.login_view, name="login"),
    path(r"logout", views.logout_request, name="logout"),
    path(r"register", views.register_view, name="register"),
    path(r"chat", views.chat, name="chat"),
    path(r"location", views.location, name="location"),
    path(r"search", views.search, name="search"),
    path(r"trade", views.trade, name="trade"),
    path(r"trade_post/<str:item_id>/", views.trade_post, name="trade_post"),
    path("edit/<int:item_id>/", views.edit, name="edit"),
    path(r"create_form/", views.create_post, name="create_form"),
    path(r"write/", views.write, name="write"),
    path(r"test", views.test, name="test"),
    path("alert/<str:alert_message>/", views.alert, name="alert"),
    path("set_region/", views.set_region_view, name="set_region"),
    path("set_region_certification/", views.main, name="set_region_certification"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
