from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from . import views
from .views import index, item_detail, manage_items, edit_item, delete_item, CatalogView, collection_detail, \
    profile_detail, delete_collection, SignoutView, private_collections_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.CatalogView.as_view(), name="catalog"),

    # Profile URLs
    path("profile/", profile_detail, name="profile_detail"),
    path("accounts/logout/", SignoutView.as_view(), name="signout"),
    
    # Private Collection URL
    path('private-collections/', views.private_collections_view, name='private_collections'),

    # Collections and Item URLs
    path('collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collection/create/', views.create_collection, name='create_collection'),
    path('collection/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collection/<int:collection_id>/delete/', delete_collection, name='delete_collection'),
    path('item/<str:item_name>/', item_detail, name='item_detail'),

    # Catalog Manage URLs
    path("manage-items/", manage_items, name="manage_items"),
    # path("manage-items/create/", create_item, name="create_item"),
    path("edit-item/<int:item_id>/", edit_item, name="edit_item"),
    path("delete-item/<int:item_id>/", delete_item, name="delete_item"),

    #Borrow Requests
    path('borrowed-items/', views.my_borrowed_items, name='my_borrowed_items'),
    path("borrow-requests/", views.manage_borrow_requests, name="manage_borrow_requests"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)