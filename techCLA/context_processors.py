from .models import Collection

def navbar_collections(request):
    if request.user.is_authenticated:
        if request.user.role == 'Librarian':
            collections = Collection.objects.all()
        else:
            collections = Collection.objects.filter(visibility='public')
    else:
        collections = Collection.objects.filter(visibility='public')

    main_collections = collections[:5]
    other_collections = collections[5:]

    return {
        'collections': main_collections,
        'other_collections': other_collections,
    }
