from django.test import TestCase

from .models import User


class UserModelTests(TestCase):
    def test_default_role(self):
        patron = User.objects.create_user(username="testpatron")

        self.assertIs(patron.is_librarian(), False)
        self.assertIs(patron.is_patron(), True)


