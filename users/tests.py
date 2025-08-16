from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    def test_user_registration(self):
        response = self.client.post(reverse("user-register"), {
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_profile_access(self):
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("user-profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
