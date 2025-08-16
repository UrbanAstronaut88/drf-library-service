from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "borrowing",
        "type",
        "status",
        "money_to_pay",
        "session_id",
    )

    list_filter = (
        "status",
        "type",
    )

    search_fields = (
        "user__email",
        "borrowing__book__title",
        "session_id",
    )

    ordering = ("-id",)
