from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (index, CatalogView,
                    profile_detail, SignoutView,
                    private_collections_view,
                    collection_detail, create_collection, edit_collection, delete_collection,
                    item_detail, manage_items, edit_item, delete_item)

urlpatterns = [
    # Catalog URLs
    path("", index, name="index"),
    path("catalog/", CatalogView.as_view(), name="catalog"),

    # Profile URLs
    path("profile/", profile_detail, name="profile_detail"),
    path("accounts/logout/", SignoutView.as_view(), name="signout"),

    # Private Collection URL
    path('private-collections/', private_collections_view, name='private_collections'),

    # Collection URLs
    path('collection/<int:collection_id>/', collection_detail, name='collection_detail'),
    path('collection/create/', create_collection, name='create_collection'),
    path('collection/<int:collection_id>/edit/', edit_collection, name='edit_collection'),
    path('collection/<int:collection_id>/delete/', delete_collection, name='delete_collection'),

    # Item URLs
    path('item/<str:item_name>/', item_detail, name='item_detail'),
    path("manage-items/", manage_items, name="manage_items"),
    path("edit-item/<int:item_id>/", edit_item, name="edit_item"),
    path("delete-item/<int:item_id>/", delete_item, name="delete_item"),
    # path("manage-items/create/", create_item, name="create_item"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)