from django.contrib import admin
from django.urls import path, include

import settings

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
