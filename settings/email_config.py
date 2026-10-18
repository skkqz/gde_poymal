import os

import environ

from settings import BASE_DIR

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
backend = env('MAILER_BACKEND', default='console')


if backend == 'smtp':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('MAILER_HOST', default='')
    EMAIL_PORT = env.int('MAILER_PORT', default=587)
    EMAIL_USE_TLS = env.bool('MAILER_USE_TLS', default=True)
    EMAIL_HOST_USER = env('MAILER_USERNAME', default='')
    EMAIL_HOST_PASSWORD = env('MAILER_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = env('MAILER_FROM_EMAIL', default='')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
