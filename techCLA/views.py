from django.contrib.auth.views import LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Item, ItemImage,Collection, BorrowRequest
from django.http import HttpResponse
from .forms import ProfilePictureForm, ItemForm, CollectionFormLibrarian,CollectionFormPatron
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages


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

    main_collections = collections[:5]          # first 5 in navbar
    other_collections = collections[5:]         # rest in hamburger

    context = {
        'welcome': welcome_message,
        'username': username,
        'role': role,
        'collections': main_collections, 
        'other_collections': other_collections,
    }
    
    return render(request, 'techCLA/index.html', context)

def profile_detail(request):
    if request.user.is_authenticated:
        #print("HERE",request)
        if request.method == "POST":
            #print("HERE2")
            form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
            
            if form.is_valid():
                form.save()
        else:
            form = ProfilePictureForm(instance=request.user.profile)

        return render(request, "techCLA/profile.html", {"form": form})

class SignoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        last_url = request.META.get("HTTP_REFERER", "")

        context = {
            "backaction_url": last_url
        }

        return render(request, "account/logout.html", context)

class CatalogView(generic.ListView):
    template_name = "techCLA/catalog.html"
    context_object_name = "all_collections"

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_librarian():
                return Collection.objects.all()
            else:
                return Collection.objects.filter(creator=user) | Collection.objects.filter(visibility="public")
        else:
            return Collection.objects.filter(visibility="public")
        #return Collection.objects.all()
    
def create_collection(request):
    # Determine which form to use
    if request.user.role == "Patron":
        FormClass = CollectionFormPatron
    else:
        FormClass = CollectionFormLibrarian

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user

            if request.user.role == "Patron":
                collection.visibility = "public"
            elif request.user.role != "Librarian" and collection.visibility == "private":
                messages.error(request, "Only librarians can create private collections.")
                return render(request, 'techCLA/collections/create_collection.html', {'form': form})

            collection.save()
            form.save_m2m()
            return redirect('collection_detail', collection_id=collection.id)
    else:
        form = FormClass()

    return render(request, 'techCLA/collections/create_collection.html', {'form': form})

def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.user.is_librarian() or collection.creator == request.user:

        if request.user.role == "Patron":
            FormClass = CollectionFormPatron
        else:
            FormClass = CollectionFormLibrarian

        if request.method == "POST":
            form = FormClass(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect('collection_detail', collection_id=collection_id)
        else:
            form = FormClass(instance=collection)
        
        return render(request, 'techCLA/collections/edit_collection.html', {'form': form})
    # else:
    #     return redirect('collection_list')

def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    if request.user == collection.creator or request.user.is_librarian():
        if request.method == "POST":
            collection.delete()
            return redirect('catalog')

    return render(request, 'techCLA/collections/delete_collection.html', {'collection': collection})

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
    
    user = request.user
    has_access = (
        collection.visibility == 'public' or
        (user.is_authenticated and (user == collection.creator or user.is_librarian())) or
        (user.is_authenticated and collection.allowed_users.filter(id=user.id).exists())
    )

    if not has_access:
        return render(request, 'techCLA/collections/access_denied.html', {'collection': collection})

    items = collection.items.all()

    return render(request, 'techCLA/collection.html', {
        'collection': collection,
        'items': items
    })

def item_detail(request, item_name):
    # for i in Item.objects.all():
    #     print(i.title)
    item = get_object_or_404(Item, title=item_name)
    return render(request, "techCLA/item.html", {"item": item})

@login_required
def private_collections_view(request):
    user = request.user

    if user.is_librarian():
        private_collections = Collection.objects.filter(visibility='private')
    else:
        # Patrons see collections they created OR are allowed to access
        created = Collection.objects.filter(visibility='private', creator=user)
        allowed = Collection.objects.filter(visibility='private', allowed_users=user)

        private_collections = (created | allowed).distinct()

    return render(request, 'techCLA/private_collections.html', {
        'private_collections': private_collections
    })

def my_borrowed_items(request):
    if not request.user.is_authenticated:
        return redirect('')

    borrowed_requests = BorrowRequest.objects.filter(user=request.user, status="approved")
    pending_requests = BorrowRequest.objects.filter(user=request.user, status="pending")

    context = {
        "borrowed_requests": borrowed_requests,
        "pending_requests": pending_requests,
    }

    return render(request, "techCLA/borrowed_items.html", context)