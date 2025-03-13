from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

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
    template_name = 'techCLA/borrow.html'
    return render(request, template_name, {'item': item_name})