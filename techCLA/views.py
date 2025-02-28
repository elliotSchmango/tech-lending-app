from django.shortcuts import render
from django.views import generic

from .models import Collection


def index(request):
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        if request.user.role == 'librarian':
            role = 'librarian'
            welcome_message = f"Welcome, {username}! You have administrative privileges."
        else:
            role = 'patron'
            welcome_message = f"Welcome, {username}! Enjoy browsing our collections."
    else:
        role = 'anonymous'
        username = ''
        welcome_message = "Welcome to our Catalog! Please log in to access all features."
    
    context = {
        'welcome': welcome_message,
        'username': username,
        'role': role,
    }
    
    return render(request, 'techCLA/index.html', context)


class CatalogView(generic.ListView):
    template_name = "techCLA/catalog.html"
    context_object_name = "all_collections"

    def get_queryset(self):
        return Collection.objects
