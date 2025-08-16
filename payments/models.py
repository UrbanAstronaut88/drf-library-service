from django.conf import settings
from django.db import models
from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PAYMENT
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(blank=True, null=True, max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.status}"
