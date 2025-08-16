from unittest.mock import patch, MagicMock

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from datetime import date, timedelta

User = get_user_model()

class PaymentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="pass"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=3,
            daily_fee=1.5
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.user)

    @patch("payments.stripe_utils.stripe.checkout.Session.create")
    def test_create_payment(self, mock_stripe_create):
        mock_session = MagicMock()
        mock_session.id = "sess_123"
        mock_session.url = "http://example.com/session"
        mock_stripe_create.return_value = mock_session

        url = "/payments/"
        data = {
            "borrowing": self.borrowing.id,
            "status": "PENDING",
            "type": "PAYMENT",
            "money_to_pay": "10.50",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.session_id, "sess_123")
        self.assertEqual(payment.session_url, "http://example.com/session")

    def test_list_payments(self):
        Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            money_to_pay="10.50",
            session_url="http://example.com/session",
            session_id="sess_123",
            user=self.user
        )
        url = "/payments/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_detail(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            money_to_pay="10.50",
            session_url="http://example.com/session",
            session_id="sess_123",
            user=self.user
        )
        url = f"/payments/{payment.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], payment.id)
