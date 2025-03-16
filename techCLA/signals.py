from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in, user_signed_up
from allauth.socialaccount.signals import pre_social_login
from .models import Profile, ItemImage
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Makes sure group exist
    Group.objects.get_or_create(name='Patron')
    Group.objects.get_or_create(name='Librarian')
    Group.objects.get_or_create(name='Admin')

@receiver(user_signed_up)
def assign_patron_on_signup(sender, request, user, **kwargs):
    # Add user to Patrons group on signup
    group, _ = Group.objects.get_or_create(name="Patron")
    user.groups.add(group)
    user.save()

# @receiver(pre_social_login)
# def social_user_signup(sender, request, sociallogin, **kwargs):
#     # Get the user and their Google email
#     user = sociallogin.user
#     if sociallogin.account.provider == 'google':
#         google_email = sociallogin.account.extra_data.get('email')
#         if google_email and user.email != google_email:
#             user.email = google_email
#             user.save()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_delete, sender=ItemImage)
def delete_itemimage_file(sender, instance, **kwargs):
    if instance.profile_picture and instance.profile_picture.name != "default.jpg":
        instance.image.delete(False)

@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and instance.profile_picture.name != "default_profile.jpg":
        instance.profile_picture.delete(False)