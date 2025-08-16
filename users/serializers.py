from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "email", "password")

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
