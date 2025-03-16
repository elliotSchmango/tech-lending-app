from django.test import TestCase

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
