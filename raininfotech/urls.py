from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("users.urls")),  # Include your users app URLs
    path("api/v1/", include("properties.urls")),
]


# Serve static files (only in development)
urlpatterns += staticfiles_urlpatterns()

# Serve media files (only in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
