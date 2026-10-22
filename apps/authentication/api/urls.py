from django.urls import path

from apps.authentication.api import views

urlpatterns = [
    path(
        'csrf/',
        views.CsrfTokenView.as_view(),
        name='csrf',
    ),
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register',
    ),
    path(
        'login/',
        views.LoginView.as_view(),
        name='login',
    ),
    path(
        'session/',
        views.SessionView.as_view(),
        name='session',
    ),
    path('refresh/', views.CookieTokenRefreshView.as_view(), name='token-refresh'),
    path(
        'logout/',
        views.LogoutView.as_view(),
        name='logout',
    ),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/request/', views.RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
]
