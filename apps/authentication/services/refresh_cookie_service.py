from typing import Any

from django.conf import settings
from django.http import HttpRequest
from loguru import logger
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings


class RefreshCookieService:
    """
    Сервис управления refresh-cookie.

    Инкапсулирует знание о том, как и где хранится refresh-токен:
    имя cookie, флаги безопасности, путь. Все параметры берутся из
    settings.SIMPLE_JWT — конфигурация в одном месте, сервис только
    применяет её к Response.

    Используется в login (установка), refresh (переустановка при
    ротации), logout (удаление).
    """

    @staticmethod
    def _config(name: str) -> Any:
        """
        Достать параметр cookie из настроек SimpleJWT.

        :param name: Имя параметра (AUTH_COOKIE, AUTH_COOKIE_PATH, ...).
        :return: Значение из настроек.
        :raises KeyError: Если параметр отсутствует в конфигурации.
        """

        return settings.SIMPLE_JWT[name]

    @classmethod
    def set(cls, response: Response, refresh_token: str) -> None:
        """
        Установить refresh-токен в HttpOnly cookie.

        :param response: HTTP-ответ, в который устанавливается cookie.
        :param refresh_token: Строковое значение refresh-токена.
        """

        response.set_cookie(
            key=cls._config('AUTH_COOKIE'),
            value=refresh_token,
            max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
            secure=cls._config('AUTH_COOKIE_SECURE'),
            httponly=cls._config('AUTH_COOKIE_HTTP_ONLY'),
            samesite=cls._config('AUTH_COOKIE_SAMESITE'),
            path=cls._config('AUTH_COOKIE_PATH'),
        )

        logger.debug(
            f'Refresh-cookie установлена (name={cls._config("AUTH_COOKIE")}, path={cls._config("AUTH_COOKIE_PATH")})',
        )

    @classmethod
    def delete(cls, response: Response) -> None:
        """
        Удалить refresh-cookie с клиента.

        Путь и SameSite должны совпадать с параметрами установки,
        иначе браузер не удалит cookie.

        :param response: HTTP-ответ, из которого удаляется cookie.
        """

        response.delete_cookie(
            key=cls._config('AUTH_COOKIE'),
            path=cls._config('AUTH_COOKIE_PATH'),
            samesite=cls._config('AUTH_COOKIE_SAMESITE'),
        )

        logger.debug(
            f'Refresh-cookie удалена (name={cls._config("AUTH_COOKIE")})',
        )

    @classmethod
    def get_from_request(cls, request: HttpRequest) -> str | None:
        """
        Прочитать refresh-токен из cookie запроса.

        :param request: HTTP-запрос.
        :return: Значение refresh-токена или None, если cookie нет.
        """

        token = request.COOKIES.get(cls._config('AUTH_COOKIE'))

        if token is None:
            logger.debug('Refresh-cookie отсутствует в запросе')

        return token
