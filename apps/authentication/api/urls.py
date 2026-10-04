from django.urls import path

from apps.authentication.api import views

urlpatterns = [
    path('csrf/', views.CsrfTokenView.as_view(), name='csrf',),
    path('register/', views.RegisterView.as_view(), name='register',),
    path('login/', views.LoginView.as_view(), name='login',),
    path('refresh/', views.CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout',),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),

]