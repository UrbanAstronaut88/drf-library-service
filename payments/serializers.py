from rest_framework import serializers
from borrowings.models import Borrowing
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(
        queryset=Borrowing.objects.all(),
    )

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["user"]
