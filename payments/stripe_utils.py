import stripe
from django.conf import settings
from django.urls import reverse

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_session(payment: Payment, request):
    success_url = request.build_absolute_uri(reverse("payment-success", args=[payment.id]))
    cancel_url = request.build_absolute_uri(reverse("payment-cancel", args=[payment.id]))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "USD",
                "product_data": {
                    "name": f"Borrowing: {payment.borrowing.book.title}",
                },
                "unit_amount": int(payment.money_to_pay * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    # Save session_id and session_url
    payment.session_id = session.id
    payment.session_url = session.url
    payment.save()

    return session.url
