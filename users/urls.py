from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import UserRegistrationView, UserProfileView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
