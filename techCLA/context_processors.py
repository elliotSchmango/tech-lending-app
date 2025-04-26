from .models import Collection

def navbar_collections(request):
    public_collections = Collection.objects.filter(visibility='public')

    # first fewe public collections for the navbar
    main_collections = public_collections[:6]
    other_collections = public_collections[6:]

    # priv collections if logged in
    if request.user.is_authenticated:
        private_collections = Collection.objects.filter(visibility='private')
    else:
        private_collections = None

    return {
        'collections': main_collections,  
        'other_collections': other_collections,
        'public_collections': public_collections,
        'private_collections': private_collections,   
    }