from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.users.api.urls')),
    path('api/auth/', include('apps.authentication.api.urls')),
]

# Документация только для dev режима.
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
    # Раздача медиа файлов в dev
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
