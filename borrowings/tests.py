from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.utils import timezone
from decimal import Decimal

from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class BorrowingAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="admin123")

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.HARD,
            inventory=2,
            daily_fee=Decimal("5.00")
        )

    @patch("borrowings.services.send_borrowing_notification")
    def test_create_borrowing_decreases_inventory(self, mock_telegram):
        """Verification of borrowing creation and inventory reduction"""
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowing-list")
        data = {
            "book": self.book.id,
            "expected_return_date": timezone.now().date() + timezone.timedelta(days=7)
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)

        # Checking the creation of Payment
        payment = Payment.objects.get(borrowing=borrowing)
        self.assertEqual(payment.money_to_pay, self.book.daily_fee)
        self.assertEqual(payment.user, self.user)

    @patch("borrowings.services.send_borrowing_notification")
    def test_return_book_increases_inventory(self, mock_telegram):
        """Checking the return of a book"""
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date()
        )
        self.book.inventory = 1
        self.book.save()

        url = reverse("borrowing-return-book", kwargs={"pk": borrowing.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)
