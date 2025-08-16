from rest_framework import serializers
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.models import Payment


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
        fields = ["id", "book", "expected_return_date"]

    def validate(self, data):
        book = data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock")
        return data

    def create(self, validated_data):
        user = validated_data.pop("user")
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        book = validated_data["book"]
        Payment.objects.create(
            borrowing=borrowing,
            user=user,
            money_to_pay=book.daily_fee,
            type=Payment.Type.PAYMENT,
            status=Payment.Status.PENDING
        )

        return borrowing
