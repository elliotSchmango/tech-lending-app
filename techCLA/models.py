from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patron')

    def is_librarian(self):
        return self.role == 'librarian'

class Collection(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private")
    ]

    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
    collection_name = models.CharField(max_length=100)

