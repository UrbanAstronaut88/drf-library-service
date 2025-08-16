from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
