from datetime import timedelta

from .base import env

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME_MIN', default=15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('REFRESH_TOKEN_LIFETIME_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    # Настройки Cookie
    'AUTH_COOKIE': 'refresh_token',  # имя cookie для refresh
    'AUTH_COOKIE_SECURE': not env.bool('DEBUG', default=False),  # True в проде
    'AUTH_COOKIE_HTTP_ONLY': True,  # JS не может прочитать
    'AUTH_COOKIE_SAMESITE': 'Lax',  # защита от CSRF
    'AUTH_COOKIE_PATH': '/api/auth/',  # cookie уходит только на auth-эндпоинты
}
