from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """Регистрация нового пользователя."""

    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
