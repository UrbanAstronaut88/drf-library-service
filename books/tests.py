from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()

class BookAPITestCase(APITestCase):
    def setUp(self):
        # Creating a basic user
        self.user = User.objects.create_user(email="user@test.com", password="password123")

        # Creating a super user
        self.admin = User.objects.create_superuser(email="admin@test.com", password="adminpassword")

        # Creating a test book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=1.50
        )

    def test_list_books(self):
        """Any user can view the list of books."""
        self.client.force_authenticate(user=self.user)
        url = reverse("book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_create_book_admin(self):
        """Only the administrator can create a book"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 2.0
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_book_non_admin(self):
        """A basic user cannot create a book"""
        self.client.force_authenticate(user=self.user)
        url = reverse("book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 2.0
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_admin(self):
        """Only the administrator can update a book"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("book-detail", args=[self.book.id])
        data = {"inventory": 10}
        response = self.client.patch(url, data, format="json")
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.inventory, 10)

    def test_update_book_non_admin(self):
        """A basic user cannot update a book"""
        self.client.force_authenticate(user=self.user)
        url = reverse("book-detail", args=[self.book.id])
        data = {"inventory": 10}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
