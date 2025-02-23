from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in, user_signed_up
from allauth.socialaccount.signals import pre_social_login

User = get_user_model()

# Assign user to group after login
@receiver(user_logged_in)
def assign_user_to_group(sender, request, user, **kwargs):
    if user.is_librarian(): 
        group = Group.objects.get(name="Librarian")
    elif user.is_patron():
        group = Group.objects.get(name="Patron")
    else:
        group = Group.objects.get(name="Anonymous")
    
    # Add user to the group (if not already a member)
    if not user.groups.filter(name=group.name).exists():
        user.groups.add(group)

@receiver(user_signed_up)
def assign_user_to_group_on_signup(sender, request, user, **kwargs):
    # Add user to Patrons group on signup
    group = Group.objects.get(name="Patron")
    
    user.groups.add(group)

@receiver(pre_social_login)
def social_user_signup(sender, request, sociallogin, **kwargs):
    # Get the user and their Google email
    user = sociallogin.user
    if sociallogin.account.provider == 'google':
        google_email = sociallogin.account.extra_data.get('email')
        if google_email and user.google_email != google_email:
            user.email = google_email
            user.save()