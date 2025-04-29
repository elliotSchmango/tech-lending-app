from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q, OuterRef, Subquery, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic import ListView
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Item, ItemImage, Collection, BorrowRequest, Review, RequestAccess
from .forms import ProfilePictureForm, ItemForm, CollectionFormLibrarian, CollectionFormPatron, ReviewForm, RequestAccessForm


def index(request):
    total_notifications = 0
    new_notifications = 0
    access_notifications = 0
    access_pending = 0
    borrow_pending = 0

    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        librarian_alerts = 0
        if request.user.role == 'Librarian':
            role = 'Librarian'
            welcome_message = f"Welcome, {username}! You have librarian privileges."
            collections = Collection.objects.all()
            access_pending = RequestAccess.objects.filter(status="pending").count()
            borrow_pending = BorrowRequest.objects.filter(status="pending").count()
            librarian_alerts = access_pending + borrow_pending
        else:
            role = 'Patron'
            welcome_message = f"Welcome, {username}! Enjoy browsing our collections."
            collections = Collection.objects.filter(creator=request.user) | Collection.objects.filter(visibility="public") | Collection.objects.filter(allowed_users=request.user)
        
        new_notifications = BorrowRequest.objects.filter(
            user=request.user,
            status__in=["approved", "denied"],
            viewed=False
        ).count()

        access_notifications = RequestAccess.objects.filter(
            requester=request.user,
            status__in=["approved", "denied"],
            viewed=False
        ).count()

        total_notifications = new_notifications + librarian_alerts

    else:
        role = 'Anonymous'
        username = ''
        welcome_message = "Welcome to our Catalog! Please log in to access all features."
        collections = Collection.objects.filter(visibility='public')
        

    context = {
        'welcome': welcome_message,
        'username': username,
        'role': role,
        'total_notifications': total_notifications,
        'new_notifications': new_notifications,
        'access_notifications': access_notifications,
        'access_pending': access_pending,
        'borrow_pending': borrow_pending,
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
                return Collection.objects.filter(creator=user) | Collection.objects.filter(visibility="public") | Collection.objects.filter(allowed_users=user)
        else:
            return Collection.objects.filter(visibility="public")
    
def create_collection(request):

    if request.user.role == "Patron":
        FormClass = CollectionFormPatron
    else:
        FormClass = CollectionFormLibrarian

    if request.method == "POST":
        form = FormClass(request.POST)

        items = form.fields['items'].clean(request.POST.getlist('items'))
        visibility = request.POST.get('visibility')

        for item in items:
            other_collections = item.collection_set.filter(visibility="private")
            if other_collections.exists():
                return redirect('item_conflict', item_title=item.title, collection_name=other_collections.first().name)

        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user

            if request.user.role == "Patron":
                collection.visibility = "public"
            elif request.user.role != "Librarian" and collection.visibility == "private":
                messages.error(request, "Only librarians can create private collections.")
                return render(request, 'techCLA/collections/create_collection.html', {'form': form})

            if collection.visibility == "private":
                for item in items:
                    for other_collection in item.collection_set.all():
                        other_collection.items.remove(item)

            collection.save()
            collection.items.set(items)
            return redirect('collection_detail', collection_id=collection.id)
        else:
            pass

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
                print("HERE")
                collection = form.save(commit=False)
                items = form.fields['items'].clean(request.POST.getlist('items'))
                visibility = request.POST.get('visibility', collection.visibility)
        
                for item in items:
                    other_collections = item.collection_set.filter(visibility="private").exclude(id=collection.id)
                    if other_collections.exists():
                        return redirect(
                            f"/collections/item-conflict/{item.title}/{other_collections.first().name}/?collection_id={collection_id}"
                        )
            
                if collection.visibility == "private":
                    for item in items:
                        for other_collection in item.collection_set.exclude(id=collection.id):
                            other_collection.items.remove(item)
                
                collection = form.save()
                collection.items.set(items)
                return redirect('collection_detail', collection_id=collection.id)
            else:
                return render(request, 'techCLA/collections/invalid_form.html', {
                    'form': form,
                    'collection': collection
                })
        else:
            form = FormClass(instance=collection)

        return render(request, 'techCLA/collections/edit_collection.html', {'form': form, 'collection': collection})

    return None
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

    return render(request, 'techCLA/manage_items.html', {'items': items})

@user_passes_test(is_librarian)
def create_item(request):
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

    return render(request, 'techCLA/create_item.html', {'form': form})

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
        if not user.is_authenticated:
            return redirect('account_login')
        return render(request, 'techCLA/collections/access_denied.html', {
            'collection': collection
        })

    items = collection.items.all()
    query = ""

    if request.method == "GET":
        query = request.GET.get("q", "")

        items = items.filter(
            Q(title__icontains=query)
        )

    return render(request, 'techCLA/collection.html', {
        'collection': collection,
        'items': items,
        'query': query,
    })

def item_detail(request, item_name):
    # for i in Item.objects.all():
    #     print(i.title)
    item = get_object_or_404(Item, title=item_name)

    context = {"item": item}

    reviews = Review.objects.filter(item=item).order_by("-date_created")
    context["reviews"] = reviews
    context["form"] = ReviewForm()

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        context["user_review"] = user_review
        if request.method == "POST":
            if "borrow_request" in request.POST:
                if item.status != "available":
                    context["error"] = "This item is not available for borrowing."
                elif BorrowRequest.objects.filter(item=item, user=request.user, status="pending").exists():
                    context["warning"] = "You already have a pending borrow request for this item."
                else:
                    BorrowRequest.objects.create(item=item, user=request.user)
                    context["success"] = "Borrow request submitted successfully."

            elif "submit_review" in request.POST:
                if not user_review:
                    form = ReviewForm(request.POST)
                    if form.is_valid():
                        review = form.save(commit=False)
                        review.item = item
                        review.user = request.user
                        review.save()

                        num_reviews = Review.objects.filter(item=item).count()
                        sum_reviews = Review.objects.filter(item=item).aggregate(Sum("rating"))["rating__sum"]

                        item.rating = sum_reviews / num_reviews
                        item.save()

                        return redirect("item_detail", item_name=item.title)

    return render(request, "techCLA/item.html", context)

@login_required
def private_collections_view(request):
    user = request.user

    if user.is_librarian():
        private_collections = Collection.objects.filter(visibility='private')
        inaccessible = Collection.objects.none()

    else:
        # Patrons see collections they created OR are allowed to access
        created = Collection.objects.filter(visibility='private', creator=user)
        allowed = Collection.objects.filter(visibility='private', allowed_users=user)

        private_collections = (created | allowed).distinct()
        inaccessible = Collection.objects.filter(
            visibility='private'
        ).exclude(
            id__in=private_collections.values_list('id', flat=True)
        )
        #print(inaccessible)
    
    # Fetch alerts for approved/denied requests
    alerts_qs = RequestAccess.objects.filter(
        requester=user,
        status__in=["approved", "denied"],
        viewed=False
    )

    alerts = list(alerts_qs)

    alerts_qs.update(viewed=True)
    req_message = request.session.pop('req_message', None)

    return render(request, 'techCLA/private_collections.html', {
        'private_collections': private_collections,
        'inaccessible': inaccessible,
        'alerts': alerts,
        'req_message':req_message
    })

def my_borrowed_items(request):
    if not request.user.is_authenticated:
        return redirect('')

    if request.method == "POST":
        item_name = request.POST.get("item_return")

        item = Item.objects.get(title=item_name)
        item.status = "available"
        item.save()

    latest_approve_dates = BorrowRequest.objects.filter(item__title=OuterRef("item__title")).order_by("-approved_on")
    borrowed_requests = BorrowRequest.objects.filter(
        user=request.user,
        status="approved",
        approved_on=Subquery(latest_approve_dates.values("approved_on")[:1])
    ).exclude(item__status="available")

    pending_requests = BorrowRequest.objects.filter(user=request.user, status="pending")

    # Fetch alerts for approved/denied requests
    alerts_qs = BorrowRequest.objects.filter(
        user=request.user,
        status__in=["approved", "denied"],
        viewed=False
    )

    alerts = list(alerts_qs) 

    # Mark them as viewed once they visit
    alerts_qs.update(viewed=True)

    context = {
        "borrowed_requests": borrowed_requests,
        "pending_requests": pending_requests,
        "alerts": alerts,
    }

    return render(request, "techCLA/borrowed_items.html", context)

@user_passes_test(is_librarian)
def manage_borrow_requests(request):
    requests = BorrowRequest.objects.select_related('item', 'user').order_by('-requested_on')

    if request.method == "POST":
        action = request.POST.get("action")
        request_id = request.POST.get("request_id")

        borrow_request = BorrowRequest.objects.get(id=request_id)

        if action == "approve":
            borrow_request.approve()
            borrow_request.item.status = "checked_out"
            borrow_request.item.save()
        elif action == "deny":
            borrow_request.deny()

        return redirect("manage_borrow_requests")

    return render(request, "techCLA/manage_requests.html", {
        "requests": requests
    })

class SearchResultsView(ListView):
    model = Collection
    template_name = "techCLA/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user"] = self.request.user
        context["query"] = self.request.GET.get("q", "")
        context["search_by"] = self.request.GET.get("search_by")
        context["advanced_filter"] = self.request.GET.get("advanced_filter")

        return context

    def get_queryset(self):
        user = self.request.user
        query = self.request.GET.get("q", "")
        search_by = self.request.GET.get("search_by")

        if search_by == "collections":
            advanced_filter = self.request.GET.get("advanced_filter", "name")
            visibility_filter = {
                "public": self.request.GET.get("public"),
                "private": self.request.GET.get("private")
            }

            if advanced_filter == "name":
                object_list = Collection.objects.filter(
                    Q(name__icontains=query)
                )
            elif advanced_filter == "creator":
                object_list = Collection.objects.filter(
                    Q(creator__username__icontains=query)
                )
            else:
                object_list = Collection.objects.filter(
                    Q(items__title__icontains=query)
                ).distinct()

            visibility_query = Q()
            for visibility, visibility_status in visibility_filter.items():
                if visibility_status == "true":
                    visibility_query |= Q(visibility=visibility)

            if visibility_query:
                object_list = object_list.filter(visibility_query)

            if not user.is_authenticated:
                object_list = object_list.filter(Q(visibility="public"))
        elif search_by == "items":
            advanced_filter = self.request.GET.get("advanced_filter", "title")
            status_filter = {
                "available": self.request.GET.get("available"),
                "checked_out": self.request.GET.get("checked_out"),
                "repair": self.request.GET.get("under_repair"),
                "other": self.request.GET.get("other")
            }

            if advanced_filter == "title":
                object_list = Item.objects.filter(
                    Q(title__icontains=query)
                )
            elif advanced_filter == "identifier":
                object_list = Item.objects.filter(
                    Q(identifier__icontains=query)
                )
            else:
                object_list = Item.objects.filter(
                    Q(location__icontains=query)
                )

            status_query = Q()
            for status, status_value in status_filter.items():
                if status_value == "true":
                    status_query |= Q(status__icontains=status)

            if status_query:
                object_list = object_list.filter(status_query)

        return object_list

@login_required
def request_access_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    if request.user in collection.allowed_users.all() or request.user == collection.creator:
        request.session['req_message'] = "You already have access to this collection."
        return redirect('collection_detail', collection.id)

    existing = RequestAccess.objects.filter(requester=request.user, collection=collection).first()
    if existing:
        request.session['req_message'] = "You have already requested access."
        return redirect('private_collections')#('collection_detail', collection.id)

    if request.method == "POST":
        form = RequestAccessForm(request.POST)
        if form.is_valid():
            request_access = form.save(commit=False)
            request_access.requester = request.user
            request_access.collection = collection
            request_access.save()
            request.session['req_message'] = "Access request submitted."
            return redirect('private_collections')
    else:
        form = RequestAccessForm()

    return render(request, 'techCLA/request_access.html', {
        'collection': collection,
        'form': form,
    })

@user_passes_test(is_librarian)
def manage_access_requests_view(request):
    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        access_request = get_object_or_404(RequestAccess, id=request_id)

        if action == 'approve':
            access_request.status = 'approved'
            access_request.viewed = False
            access_request.collection.allowed_users.add(access_request.requester)
            messages.success(request, f"Approved access for {access_request.requester.username}")
        elif action == 'deny':
            access_request.status = 'denied'
            access_request.viewed = False
            messages.info(request, f"Denied access for {access_request.requester.username}")

        access_request.save()
        return redirect('manage_access_requests')

    requests = RequestAccess.objects.filter(status='pending').order_by('-timestamp')
    return render(request, 'techCLA/manage_access_requests.html', {'requests': requests})


User = get_user_model()
@user_passes_test(lambda u: u.groups.filter(name='Librarian').exists())
def promote_user_to_librarian(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            librarian_group = Group.objects.get(name="Librarian")
            user.groups.add(librarian_group)
            messages.success(request, f"{user.username} was promoted to librarian.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        return redirect("promote_user")

    users = User.objects.exclude(groups__name='Librarian')
    return render(request, "techCLA/promote_user.html", {"users": users})

def item_conflict_view(request, item_title, collection_name):
    print("HERE")
    collection_id = request.GET.get("collection_id")
    return render(request, 'techCLA/collections/item_conflict.html', {
        'item_title': item_title,
        'collection_name': collection_name,
        'collection_id': collection_id
    })