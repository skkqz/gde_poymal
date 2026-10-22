from rest_framework.response import Response

from apps.authentication.services.cookie_service import BaseCookieService


class AccessCookieService(BaseCookieService):
    """
    Сервис управления access-cookie.

    Access-cookie всегда session-cookie: срок жизни ограничен exp JWT.
    """

    cookie_name_setting = 'AUTH_ACCESS_COOKIE'
    cookie_path_setting = 'AUTH_ACCESS_COOKIE_PATH'

    @classmethod
    def set(cls, response: Response, access_token: str) -> None:
        """
        Установить access-токен в session HttpOnly cookie.

        :param response: HTTP-ответ.
        :param access_token: Access-токен.
        """

        super().set(response, access_token)
