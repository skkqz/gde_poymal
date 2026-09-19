from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.api.schemas import login_schema, logout_schema, me_schema, register_schema
from apps.authentication.api.serializers import (
    RegisterSerializer,
    LoginSerializer, LogoutSerializer,
)
from apps.authentication.services import JWTService
from apps.users.api.serializers import UserSerializer


class RegisterView(GenericAPIView):
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


class MeView(APIView):
    """
    Представление получения текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    @me_schema
    def get(self, request, *args, **kwargs):
        """
        Вернуть данные текущего пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Данные пользователя.
        """

        serializer = UserSerializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
