from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from . import views
from .views import index, borrow_item, update_profile, manage_items, edit_item, delete_item, CatalogView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path('catalog/<str:item_name>/borrow/', borrow_item, name='borrow_item'),
    path("catalog/", views.CatalogView.as_view(), name="catalog"),
    path("profile/update-profile/", update_profile, name="update_profile"),
    path("manage-items/", manage_items, name="manage_items"),
    path("edit-item/<int:item_id>/", edit_item, name="edit_item"),
    path("delete-item/<int:item_id>/", delete_item, name="delete_item"),
    path('collections/create/', views.create_collection, name='create_collection'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)