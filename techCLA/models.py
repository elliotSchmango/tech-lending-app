from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils import timezone

class User(AbstractUser):

    @property
    def role(self):
        """Returns the user's primary group as a role name."""
        groups = self.groups.values_list('name', flat=True)
        if "Librarian" in groups:
            return "Librarian"
        elif "Patron" in groups:
            return "Patron"
        elif "Admin" in groups:
            return "Admin"
        else:
            return "Anonymous"

    def is_librarian(self):
        return self.groups.filter(name='Librarian').exists()
    
    def is_patron(self):
        return self.groups.filter(name='Patron').exists()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default="default_profile.jpg")
    bio = models.TextField(blank=True, null=True)

class Collection(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private")
    ]

    name = models.CharField(max_length=100, unique=True, default="Untitled Collection")
    description = models.TextField(blank=True, null=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_collections",null=True)
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)  
    items = models.ManyToManyField('Item', blank=True)

    def clean(self):
        if self.visibility == 'private' and self.pk:
            for item in self.items.all():
                if item.collection_set.exclude(id=self.id).exists():
                    raise ValidationError(
                        f"Item '{item.title}' is already in another collection. "
                        f"Items in private collections must be exclusive."
                    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

class Item(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("checked_out", "Checked Out"),
        ("repair", "Under Repair"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    identifier = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True, default="item_images/default.jpg")

    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], default=0, null=True, blank=True) 
    comments = models.TextField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_images")
    image = models.ImageField(upload_to='item_images/')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # delete method to ensure the image file is deleted from S3
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

class BorrowRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default="pending")
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    denied_on = models.DateTimeField(blank=True, null=True)
    viewed = models.BooleanField(default=False)

    def approve(self):
        self.status = "approved"
        self.approved_on = timezone.now()
        self.viewed = False
        self.save()

    def deny(self):
        self.status = "denied"
        self.denied_on = timezone.now()
        self.viewed = False
        self.save()

class RequestAccess(models.Model):
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('requester', 'collection')  # Prevent duplicate requests

    def __str__(self):
        return f"{self.requester.username} → {self.collection.name} ({self.status})"