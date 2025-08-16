from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from borrowings.models import Borrowing
from payments.models import Payment
from notifications.telegram import send_borrowing_notification


def create_borrowing(user, book, expected_return_date):
    """Creates a booking and sends a notification to Telegram"""
    if book.inventory <= 0:
        raise ValueError("No books available in inventory")
    book.inventory -= 1
    book.save()

    borrowing = Borrowing.objects.create(
        user=user,
        book=book,
        borrow_date=timezone.now().date(),
        expected_return_date=expected_return_date,
    )

    # Telegram notification
    send_borrowing_notification(borrowing)

    return borrowing


def process_borrowing_creation(borrowing):
    """Processing a new booking: inventory reduction and notification"""
    book = borrowing.book
    if book.inventory <= 0:
        raise ValueError("No books available in inventory")
    book.inventory -= 1
    book.save()

    # Creating a payment for a reservation
    Payment.objects.create(
        borrowing=borrowing,
        user=borrowing.user,
        money_to_pay=book.daily_fee,
        type=Payment.Type.PAYMENT,
        status=Payment.Status.PENDING,
    )

    # Sending a notification in Telegram
    send_borrowing_notification(borrowing)


def process_borrowing_return(borrowing):
    """Processing book returns and charging fines for overdue books"""
    today = timezone.now().date()

    borrowing.actual_return_date = today
    borrowing.book.inventory += 1
    borrowing.book.save()
    borrowing.save()

    overdue_days = (today - borrowing.expected_return_date).days
    if overdue_days > 0:
        fine_amount = (
            Decimal(overdue_days) *
            borrowing.book.daily_fee *
            Decimal(getattr(settings, "FINE_MULTIPLIER", 2))
        )
        Payment.objects.create(
            borrowing=borrowing,
            user=borrowing.user,
            type=Payment.Type.FINE,
            status=Payment.Status.PENDING,
            money_to_pay=fine_amount
        )
