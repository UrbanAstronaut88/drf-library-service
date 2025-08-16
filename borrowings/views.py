from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingCreateSerializer, BorrowingListSerializer
from borrowings.services import process_borrowing_creation, process_borrowing_return


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "return_book"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        # Filter for admin by user_id
        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user__id=user_id)
        else:
            queryset = queryset.filter(user=user)

        # Filter by is_active
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() in ["1", "true", "yes"]:
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() in ["0", "false", "no"]:
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def perform_create(self, serializer):
        """Creation of borrowing + notification + reduction in the number of books"""
        borrowing = serializer.save(user=self.request.user)
        process_borrowing_creation(borrowing)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        """Returning a book + late fees"""
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {"detail": "This borrowing is already returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        process_borrowing_return(borrowing)
        return Response(
            {"detail": "Book returned successfully."},
            status=status.HTTP_200_OK
        )
