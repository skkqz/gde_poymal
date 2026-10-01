from django.middleware.csrf import get_token

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from loguru import logger

from apps.authentication.api import schemas
from apps.authentication.api.serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
)
from apps.authentication.services.change_password_service import PasswordService
from apps.authentication.services.jwt_service import JWTService
from apps.authentication.services.refresh_cookie_service import RefreshCookieService

from apps.users.api.serializers import UserSerializer
from core.mixins import AtomicMixin, CsrfProtectMixin


class CsrfTokenView(APIView):
    """
    Выдаёт CSRF-cookie SPA-клиенту.

    Клиент вызывает этот эндпоинт при загрузке, чтобы гарантированно
    получить csrftoken для последующих state-changing запросов.
    Аутентификация отключена — эндпоинт публичный и не должен падать
    при инвалидном Authorization-заголовке.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        """
        Установить CSRF-cookie в ответе.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Пустой ответ 204 с Set-Cookie csrftoken.
        """

        # get_token() помечает запрос флагом CSRF_COOKIE_NEEDS_UPDATE,
        # CsrfViewMiddleware.process_response увидит его и добавит cookie.
        get_token(request)

        logger.debug(
            f'Выдан CSRF-токен клиенту с IP={request.META.get("REMOTE_ADDR")}',
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(AtomicMixin, GenericAPIView):
    """
    Представление регистрации нового пользователя.

    CSRF здесь намеренно отключён (и так по умолчанию в DRF):
    пользователь ещё не аутентифицирован, cookie-сессии нет,
    а CSRF-cookie может отсутствовать на момент первого запроса.
    Защищать от CSRF нечего — у жертвы нет cookie, которую можно
    было бы использовать в межсайтовой атаке.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @schemas.register_schema
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

        logger.info(
            f'Зарегистрирован новый пользователь: id={user.pk} email={user.email}',
        )

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    """
    Представление авторизации пользователя.

    Access-токен возвращается в теле ответа, refresh-токен
    устанавливается в HttpOnly cookie. CSRF отключён по той же
    причине, что и в регистрации: пользователь ещё не имеет
    cookie-аутентификации, защищать нечего.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @schemas.login_schema
    def post(self, request, *args, **kwargs):
        """
        Авторизовать пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Access-токен и данные пользователя.
        """

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

        RefreshCookieService.set(response, str(refresh))

        logger.info(
            f'Пользователь авторизован: id={user.pk} email={user.email} '
            f'ip={request.META.get("REMOTE_ADDR")}',
        )

        return response


class CookieTokenRefreshView(CsrfProtectMixin, TokenRefreshView):
    """
    Обновление access-токена.

    Refresh-токен читается из HttpOnly cookie, новый access
    возвращается в теле ответа. При включённой ротации refresh-токен
    также переустанавливается в cookie.

    Защита CSRF обязательна: refresh происходит по cookie без
    Authorization-заголовка, поэтому запрос неотличим от
    межсайтового. DRF по умолчанию освобождает APIView от
    CsrfViewMiddleware, поэтому защиту включаем явно через
    CsrfProtectMixin.
    """

    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        """
        Обновить access-токен по refresh-токену из cookie.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Новый access-токен (и обновлённая refresh-cookie).
        :raises InvalidToken: Если refresh-токен невалиден, просрочен или забанен.
        """

        refresh_token = RefreshCookieService.get_from_request(request)

        if not refresh_token:
            logger.warning(
                f'Refresh не выполнен: refresh-cookie отсутствует '
                f'(ip={request.META.get("REMOTE_ADDR")})',
            )
            return Response(
                {'detail': 'Refresh-токен не найден.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # request.data может быть immutable (JSON) — делаем копию
        data = request.data.copy()
        data['refresh'] = refresh_token
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            # Без этой обёртки просроченный или уже забаненный токен
            # приводит к 500, а не к 401.
            logger.warning(
                f'Refresh отклонён: невалидный refresh-токен ({exc})',
            )
            raise InvalidToken(str(exc)) from exc

        new_access = serializer.validated_data.get('access')
        new_refresh = serializer.validated_data.get('refresh')

        response = Response({'access': new_access}, status=status.HTTP_200_OK)

        # При ROTATE_REFRESH_TOKENS=True simplejwt вернёт новый refresh
        if new_refresh:
            RefreshCookieService.set(response, new_refresh)

        logger.debug(
            f'Access-токен обновлён (ротация refresh={bool(new_refresh)})',
        )

        return response


class LogoutView(CsrfProtectMixin, GenericAPIView):
    """
    Представление выхода пользователя.

    Refresh-токен берётся из HttpOnly cookie, добавляется в чёрный
    список и удаляется с клиента. CSRF-защита обязательна: запрос
    идентифицируется cookie без Authorization-заголовка, поэтому
    без неё злоумышленник может принудительно разлогинить жертву
    с любого сайта.
    """

    permission_classes = [IsAuthenticated]

    @schemas.logout_schema
    def post(self, request, *args, **kwargs):
        """
        Инвалидировать refresh-токен пользователя и удалить cookie.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Пустой ответ 204.
        """

        refresh_token = RefreshCookieService.get_from_request(request)

        if refresh_token:
            try:
                JWTService.blacklist_refresh_token(
                    user=request.user,
                    refresh_token=refresh_token,
                )
                logger.info(
                    f'Пользователь вышел из системы: '
                    f'id={request.user.pk} email={request.user.email}',
                )
            except ValidationError as exc:
                # Токен уже использован, просрочен или в блэклисте.
                # Пользователь всё равно должен выйти — не блокируем.
                logger.info(
                    f'Выход из системы: refresh-токен пользователя '
                    f'id={request.user.pk} уже недействителен ({exc.detail})',
                )
        else:
            logger.warning(
                f'Выход из системы без refresh-cookie: id={request.user.pk}',
            )

        response = Response(status=status.HTTP_204_NO_CONTENT)
        RefreshCookieService.delete(response)
        return response


class PasswordChangeView(AtomicMixin, GenericAPIView):
    """
    Представление смены пароля.

    CSRF не требуется: аутентификация идёт по Authorization-заголовку
    (JWT), а не по cookie. Сторонний сайт не может подставить чужой
    Bearer-токен, потому что не имеет к нему доступа. Если когда-нибудь
    в DEFAULT_AUTHENTICATION_CLASSES появится SessionAuthentication —
    оберни view в CsrfProtectMixin.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @schemas.password_change
    def post(self, request, *args, **kwargs):
        """
        Сменить пароль пользователя.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Пустой ответ 200.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PasswordService.change_password(
            user=request.user,
            new_password=serializer.validated_data['new_password'],
        )

        logger.info(
            f'Пользователь сменил пароль: '
            f'id={request.user.pk} email={request.user.email}',
        )

        return Response(status=status.HTTP_200_OK)