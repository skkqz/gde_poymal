from django.conf import settings
from loguru import logger
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import Token

from apps.users.models import CustomUser


class CookieJWTAuthentication(JWTAuthentication):
    """
    Аутентификация по access-JWT в HttpOnly cookie.

    Bearer-заголовок имеет приоритет. Если заголовка нет, токен
    читается из access-cookie. Ошибки cookie не выбрасываются наружу,
    чтобы публичные view могли работать без валидного access.

    Для cookie-аутентифицированных небезопасных запросов выполняется
    CSRF-проверка: браузер прикладывает cookie автоматически, поэтому
    без неё сторонний сайт мог бы действовать от имени пользователя.
    Запросы с Authorization: Bearer CSRF-проверки не требуют.
    """

    def authenticate(self, request: Request) -> tuple[CustomUser, Token] | None:
        """
        Аутентифицировать запрос по Bearer-заголовку или access-cookie.

        :param request: HTTP-запрос DRF.
        :return: Пользователь и токен или None, если аутентификация не удалась.
        :raises PermissionDenied: Если cookie-запрос с небезопасным методом
            не прошёл CSRF-проверку.
        """

        if self.get_header(request) is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_ACCESS_COOKIE'])

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except (TokenError, AuthenticationFailed):
            logger.debug('Access-cookie не прошла валидацию')
            return None

        if request.method not in SAFE_METHODS:
            SessionAuthentication().enforce_csrf(request)

        return user, validated_token
