from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]

