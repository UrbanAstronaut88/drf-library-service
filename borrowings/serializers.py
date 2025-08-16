from rest_framework import serializers
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from notifications.telegram import send_telegram_message
from payments.models import Payment
from payments.stripe_utils import create_stripe_session


class BorrowingListSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date"]

    def validate(self, data):
        book = data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock")
        return data

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        # Create Payment immediately after Borrowing
        money_to_pay = book.daily_fee
        payment = Payment.objects.create(
            borrowing=borrowing,
            user=user,
            money_to_pay=money_to_pay,
            type=Payment.Type.PAYMENT,
        )

        # Stripe Session Generation
        create_stripe_session(payment, self.context["request"])

        # --- Telegram Notification ---
        message = (
            f"📚 New Borrowing Created!\n\n"
            f"👤 User: {user.email}\n"
            f"📖 Book: {book.title}\n"
            f"💵 Daily Fee: {book.daily_fee}$\n"
            f"📅 Expected Return: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)

        return borrowing
