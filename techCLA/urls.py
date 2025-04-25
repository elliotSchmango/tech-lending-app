from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (index, CatalogView,
                    profile_detail, SignoutView,
                    private_collections_view,
                    collection_detail, create_collection, edit_collection, delete_collection,
                    item_detail, manage_items, create_item, edit_item, delete_item,
                    SearchResultsView,
                    my_borrowed_items, manage_borrow_requests,request_access_view,manage_access_requests_view,
                    promote_user_to_librarian,item_conflict_view)

urlpatterns = [
    # Catalog URLs
    path("", index, name="index"),
    path("catalog/", CatalogView.as_view(), name="catalog"),

    # Profile URLs
    path("profile/", profile_detail, name="profile_detail"),
    path("accounts/logout/", SignoutView.as_view(), name="signout"),

    # Private Collection
    path('private-collections/', private_collections_view, name='private_collections'),

    # Collection URLs
    path('collection/<int:collection_id>/', collection_detail, name='collection_detail'),
    path('collection/create/', create_collection, name='create_collection'),
    path('collection/<int:collection_id>/edit/', edit_collection, name='edit_collection'),
    path('collection/<int:collection_id>/delete/', delete_collection, name='delete_collection'),
    path('collections/item-conflict/<str:item_title>/<str:collection_name>/', item_conflict_view, name='item_conflict'),

    # Item URLs
    path('item/<str:item_name>/', item_detail, name='item_detail'),
    path("manage-items/", manage_items, name="manage_items"),
    path("manage-items/create/", create_item,  name="create_item"),
    path("edit-item/<int:item_id>/", edit_item, name="edit_item"),
    path("delete-item/<int:item_id>/", delete_item, name="delete_item"),

    # Search
    path("search/", SearchResultsView.as_view(), name="search_results"),

    # Borrow Requests
    path('borrowed-items/', my_borrowed_items, name='my_borrowed_items'),
    path("borrow-requests/", manage_borrow_requests, name="manage_borrow_requests"),

    # Collection Access Requests URLs
    path('collections/<int:collection_id>/request-access/', request_access_view, name='request_access'),
    path('collections/access-requests/', manage_access_requests_view, name='manage_access_requests'),

    # User Role Management
    path("promote-user/", promote_user_to_librarian, name="promote_user"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)