from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from .models import User, Collection, Item, BorrowRequest


class UserModelTests(TestCase):
    def test_default_role(self):
        patron = User.objects.create_user(username="testpatron")

        self.assertIs(patron.is_librarian(), False)
        self.assertIs(patron.is_patron(), True)


class CollectionModelTests(TestCase):
    def test_default_visibility(self):
        collection = Collection.objects.create()

        self.assertIs(collection.visibility, "public")


class ItemModelTests(TestCase):
    def test_default_status(self):
        item = Item.objects.create()

        self.assertIs(item.status, "available")


class BorrowModelTests(TestCase):
    def test_default_request_status(self):
        borrow_request = BorrowRequest.objects.create(item=Item.objects.create(), user=User.objects.create_user("test"))

        self.assertIs(borrow_request.status, "pending")

    def test_approve(self):
        borrow_request = BorrowRequest.objects.create(item=Item.objects.create(), user=User.objects.create_user("test"))
        borrow_request.approve()

        self.assertIs(borrow_request.status, "approved")

    def test_deny(self):
        borrow_request = BorrowRequest.objects.create(item=Item.objects.create(), user=User.objects.create_user("test"))
        borrow_request.deny()

        self.assertIs(borrow_request.status, "denied")

class PrivateCollectionsTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="Librarian")
        Group.objects.get_or_create(name="Patron")

        self.librarian = User.objects.create_user("lib", password="pass")
        self.librarian.groups.add(Group.objects.get(name="Librarian"))

        self.patron = User.objects.create_user("pat", password="pass")
        self.patron.groups.add(Group.objects.get(name="Patron"))

        self.own = Collection.objects.create(name="Patron's Private", visibility="private", creator=self.patron)
        self.shared = Collection.objects.create(name="Shared", visibility="private", creator=self.librarian)
        self.shared.allowed_users.add(self.patron)
        self.hidden = Collection.objects.create(name="Librarian Only", visibility="private", creator=self.librarian)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("private_collections"), follow=True)
        self.assertContains(response, "Sign in")

    def test_patron_sees_own_and_shared_only(self):
        self.client.login(username="pat", password="pass")
        response = self.client.get(reverse("private_collections"), follow=True)
        collections = response.context["private_collections"]

        self.assertIn(self.own, collections)
        self.assertIn(self.shared, collections)
        self.assertNotIn(self.hidden, collections)

    def test_librarian_sees_all_private(self):
        self.client.login(username="lib", password="pass")
        response = self.client.get(reverse("private_collections"), follow=True)
        collections = response.context["private_collections"]

        self.assertIn(self.own, collections)
        self.assertIn(self.shared, collections)
        self.assertIn(self.hidden, collections)