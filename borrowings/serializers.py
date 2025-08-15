import attrs
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


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
        book = attrs["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock")
        return attrs

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            **validated_data
        )
        return borrowing
