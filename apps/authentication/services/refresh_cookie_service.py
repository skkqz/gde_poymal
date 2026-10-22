from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings

from apps.authentication.services.cookie_service import BaseCookieService


class RefreshCookieService(BaseCookieService):
    """
    Сервис управления refresh-cookie.
    """

    cookie_name_setting = 'AUTH_COOKIE'
    cookie_path_setting = 'AUTH_COOKIE_PATH'

    @classmethod
    def set(cls, response: Response, refresh_token: str) -> None:
        """
        Установить refresh-токен в HttpOnly cookie.

        :param response: HTTP-ответ.
        :param refresh_token: Refresh-токен.
        """

        super().set(
            response,
            refresh_token,
            max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        )
