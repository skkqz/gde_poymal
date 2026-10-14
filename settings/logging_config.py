import os

import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env.bool('DEBUG', default=False)

# Базовый форматтер для продакшена
VERBOSE_FORMATTER = {
    'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

# Для разработки — добавляем путь к файлу для удобства отладки
DEBUG_FORMATTER = {
    'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

CONSOLE_HANDLER = {
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': VERBOSE_FORMATTER,
        'debug': DEBUG_FORMATTER,
    },
    'handlers': {
        'console': CONSOLE_HANDLER,
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        # Ошибки запросов — в консоль с уровнем ERROR
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Security-события (подозрительные запросы и т.п.)
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Логи приложений
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

if not DEBUG:
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(LOG_DIR, 'app.log'),
        'maxBytes': 10 * 1024 * 1024,  # 10 МБ
        'backupCount': 5,
        'formatter': 'verbose',
        'encoding': 'utf-8',
    }

    LOGGING['root']['handlers'].append('file')

    LOGGING['loggers']['django.request']['handlers'].append('file')
    LOGGING['loggers']['django.security']['handlers'].append('file')

    for logger_name in ('apps', 'apps.users', 'apps.authentication'):
        LOGGING['loggers'][logger_name]['handlers'].append('file')
