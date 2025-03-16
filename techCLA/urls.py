from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views

from . import views
from .views import borrow_item

urlpatterns = [
    path("", views.index, name="index"),
    path('catalog/<str:item_name>/borrow/', borrow_item, name='borrow_item'),
    path("catalog/", views.CatalogView.as_view(), name="catalog")
]

