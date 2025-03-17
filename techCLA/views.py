from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Collection, Item
from django.http import HttpResponse
from .forms import ProfilePictureForm


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

def borrow_item(request, item_name):
    for i in Item.objects.all():
        print(i.title)
    item = get_object_or_404(Item, title=item_name)
    return render(request, "techCLA/borrow.html", {"item": item})

def update_profile(request):
    if request.user.is_authenticated:
        #print("HERE",request)
        if request.method == "POST":
            #print("HERE2")
            form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
            
            if form.is_valid():
                form.save()
        else:
            form = ProfilePictureForm(instance=request.user.profile)

        return render(request, "techCLA/update.html", {"form": form})


class CatalogView(generic.ListView):
    template_name = "techCLA/catalog.html"
    context_object_name = "all_collections"

    def get_queryset(self):
        return Collection.objects
