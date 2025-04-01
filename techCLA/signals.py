from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_migrate, post_delete
from django.dispatch import receiver

from .models import Profile, ItemImage

User = get_user_model()

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Makes sure group exist
    Group.objects.get_or_create(name='Patron')
    Group.objects.get_or_create(name='Librarian')
    Group.objects.get_or_create(name='Admin')

@receiver(post_save, sender=User)
def assign_patron_on_user_creation(sender, instance, created, **kwargs):
    if created:
        # Assign user to 'Patron' group on creation
        group, _ = Group.objects.get_or_create(name='Patron')
        instance.groups.add(group)
        instance.save()
        # Create user profile
        Profile.objects.create(user=instance)

# @receiver(user_signed_up)
# def assign_patron_on_signup(sender, request, user, **kwargs):
#     # Add user to Patrons group on signup
#     group, _ = Group.objects.get_or_create(name="Patron")
#     user.groups.add(group)
#     user.save()

# @receiver(pre_social_login)
# def social_user_signup(sender, request, sociallogin, **kwargs):
#     # Get the user and their Google email
#     user = sociallogin.user
#     if sociallogin.account.provider == 'google':
#         google_email = sociallogin.account.extra_data.get('email')
#         if google_email and user.email != google_email:
#             user.email = google_email
#             user.save()

@receiver(post_delete, sender=ItemImage)
def delete_itemimage_file(sender, instance, **kwargs):
    if instance.profile_picture and instance.profile_picture.name != "default.jpg":
        instance.image.delete(False)

@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and instance.profile_picture.name != "default_profile.jpg":
        instance.profile_picture.delete(False)