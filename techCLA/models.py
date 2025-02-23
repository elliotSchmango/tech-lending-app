from django.contrib.auth.models import AbstractUser
from django.db import models

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

class Collection(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private")
    ]

    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
    collection_name = models.CharField(max_length=100)

