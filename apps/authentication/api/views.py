from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.api.schemas import login_schema, logout_schema, register_schema, password_change
from apps.authentication.api.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
)
from apps.authentication.services import JWTService, PasswordService
from apps.users.api.serializers import UserSerializer
from core.mixins import AtomicMixin


class RegisterView(AtomicMixin, GenericAPIView):
    """
    Представление регистрации нового пользователя.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @register_schema
    def post(self, request, *args, **kwargs):
        """
        Зарегистрировать пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Ответ с данными созданного пользователя.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    """
    Представление авторизация пользователя и выдача JWT.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @login_schema
    def post(self, request, *args, **kwargs):
        """
        Авторизовать пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Access и refresh токены.
        """

        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        tokens = JWTService.create_token_pair(user)

        return Response(
            tokens,
            status=status.HTTP_200_OK,
        )


class LogoutView(GenericAPIView):
    """
    Представление для выхода пользователя.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @logout_schema
    def post(self, request, *args, **kwargs):
        """
        Инвалидировать refresh-токен пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.pop('refresh')
        JWTService.blacklist_refresh_token(user=request.user, refresh_token=refresh_token)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(AtomicMixin, GenericAPIView):
    """
    Представление смены пароля.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @password_change
    def post(self, request, *args, **kwargs):
        """
        Смена пароля.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PasswordService.change_password(user=request.user, new_password=serializer.validated_data['password'])

        return Response(status=status.HTTP_200_OK)
