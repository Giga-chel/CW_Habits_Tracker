from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """Регистрация нового пользователя."""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]
