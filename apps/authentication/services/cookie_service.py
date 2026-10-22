from typing import Any

from django.conf import settings
from django.http import HttpRequest
from loguru import logger
from rest_framework.response import Response


class BaseCookieService:
    """
    Базовый сервис управления HttpOnly cookie.

    Наследники задают настройки имени cookie и пути. Общие флаги
    безопасности берутся из settings.SIMPLE_JWT.
    """

    cookie_name_setting: str
    cookie_path_setting: str

    @classmethod
    def _config(cls, name: str) -> Any:
        """
        Получить параметр cookie из настроек SimpleJWT.

        :param name: Имя параметра.
        :return: Значение параметра.
        """

        return settings.SIMPLE_JWT[name]

    @classmethod
    def set(cls, response: Response, value: str, max_age: int | None = None) -> None:
        """
        Установить cookie.

        :param response: HTTP-ответ.
        :param value: Значение cookie.
        :param max_age: Время жизни в секундах; None — session-cookie.
        """

        response.set_cookie(
            key=cls._config(cls.cookie_name_setting),
            value=value,
            max_age=max_age,
            secure=cls._config('AUTH_COOKIE_SECURE'),
            httponly=cls._config('AUTH_COOKIE_HTTP_ONLY'),
            samesite=cls._config('AUTH_COOKIE_SAMESITE'),
            path=cls._config(cls.cookie_path_setting),
        )

        logger.debug(
            f'Cookie установлена (name={cls._config(cls.cookie_name_setting)}, '
            f'path={cls._config(cls.cookie_path_setting)})',
        )

    @classmethod
    def delete(cls, response: Response) -> None:
        """
        Удалить cookie.

        :param response: HTTP-ответ.
        """

        response.delete_cookie(
            key=cls._config(cls.cookie_name_setting),
            path=cls._config(cls.cookie_path_setting),
            samesite=cls._config('AUTH_COOKIE_SAMESITE'),
        )

        logger.debug(
            f'Cookie удалена (name={cls._config(cls.cookie_name_setting)})',
        )

    @classmethod
    def get_from_request(cls, request: HttpRequest) -> str | None:
        """
        Прочитать cookie из запроса.

        :param request: HTTP-запрос.
        :return: Значение cookie или None.
        """

        token = request.COOKIES.get(cls._config(cls.cookie_name_setting))

        if token is None:
            logger.debug(
                f'Cookie отсутствует в запросе (name={cls._config(cls.cookie_name_setting)})',
            )

        return token
