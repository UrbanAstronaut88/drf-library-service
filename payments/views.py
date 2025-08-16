from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer
from .stripe_utils import create_stripe_session


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        create_stripe_session(payment, self.request)

    @action(detail=True, methods=["get"], url_path="success")
    def success(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)
        payment.status = Payment.Status.PAID
        payment.save()
        return Response({"message": "Payment successful!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="cancel")
    def cancel(self, request, pk=None):
        return Response({"message": "Payment canceled. You can retry later."}, status=status.HTTP_200_OK)
