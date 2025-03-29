from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import index, borrow_item, update_profile, manage_items, edit_item, delete_item, CatalogView
urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.CatalogView.as_view(), name="catalog"),
    # path("catalog/<str:item_name>/", item_detail, name="item_detail"),
    path('catalog/<str:item_name>/borrow/', borrow_item, name='borrow_item'),
    # path("profile/", profile, name="profile"),
    path("profile/update-profile/", update_profile, name="update_profile"),
    path("manage-items/", manage_items, name="manage_items"),
    # path("manage-items/create/", create_item, name="create_item"),
    path("edit-item/<int:item_id>/", edit_item, name="edit_item"),
    path("delete-item/<int:item_id>/", delete_item, name="delete_item"),
    # path("create-collection/", create_collection, name="create_collection"),
    # path("manage-collections/", manage_collections, name="manage_collections"),
    # path("borrowed-items/", borrowed_items, name="my_borrowed_items"),
    # path("collection/<str:collection_name>/", collection_detail, name="collection_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)