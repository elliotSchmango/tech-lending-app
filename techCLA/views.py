from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Item, ItemImage,Collection
from django.http import HttpResponse
from .forms import ProfilePictureForm, ItemForm, CollectionForm
from django.contrib.auth.decorators import user_passes_test

def index(request):
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        if request.user.role == 'Librarian':
            role = 'Librarian'
            welcome_message = f"Welcome, {username}! You have administrative privileges."
            collections = Collection.objects.all()
        else:
            role = 'Patron'
            welcome_message = f"Welcome, {username}! Enjoy browsing our collections."
            collections = Collection.objects.filter(visibility='public')
    else:
        role = 'Anonymous'
        username = ''
        welcome_message = "Welcome to our Catalog! Please log in to access all features."
        collections = Collection.objects.filter(visibility='public')

    context = {
        'welcome': welcome_message,
        'username': username,
        'role': role,
        'collections': collections, 
    }
    
    return render(request, 'techCLA/index.html', context)

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

        return render(request, "techCLA/update_profile.html", {"form": form})

class CatalogView(generic.ListView):
    template_name = "techCLA/catalog.html"
    context_object_name = "all_collections"

    def get_queryset(self):
        return Collection.objects.all()
    
def create_collection(request):
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user

            if request.user.role == "Patron":
                collection.visibility = "public"
            collection.save()

            return redirect('collection_detail', collection_id=collection.id)
    else:
        form = CollectionForm()
    return render(request, 'techCLA/collections/create_collection.html', {'form': form})

def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user.is_librarian() or collection.creator == request.user:
        if request.method == "POST":
            form = CollectionForm(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect('collection_detail', collection_id=collection_id)
        else:
            form = CollectionForm(instance=collection)
        return render(request, 'techCLA/collections/edit_collection.html', {'form': form})
    # else:
    #     return redirect('collection_list')

def is_librarian(user):
    return user.is_authenticated and user.groups.filter(name='Librarian').exists()

@user_passes_test(is_librarian)
def manage_items(request):
    items = Item.objects.all()

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        files = request.FILES.getlist('additional_images')  # Multiple image support

        if form.is_valid():
            item = form.save()

            # Save additional images
            for file in files:
                ItemImage.objects.create(item=item, image=file)

            return redirect('manage_items')

    else:
        form = ItemForm()

    return render(request, 'techCLA/manage_items.html', {'form': form, 'items': items})

@user_passes_test(is_librarian)
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage_items')
    else:
        form = ItemForm(instance=item)

    return render(request, 'techCLA/edit_item.html', {'form': form, 'item': item})

@user_passes_test(is_librarian)
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":  # Confirm deletion
        item.delete()
        return redirect('manage_items')

    return render(request, 'techCLA/delete_item.html', {'item': item})

def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    items = Item.objects.filter(
        collections=collection
    ).prefetch_related('itemimage_set')

    return render(request, 'techCLA/collection.html', {
        'collection': collection,
        'items': items
    })

def item_detail(request, item_name):
    for i in Item.objects.all():
        print(i.title)
    item = get_object_or_404(Item, title=item_name)
    return render(request, "techCLA/item.html", {"item": item})