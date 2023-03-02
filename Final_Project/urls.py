from django.contrib import admin
from django.urls import path, include
from landing_page import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("", views.home, name="home"),
    path("", include("picture.urls")),
    path("gallery/", include("gallery.urls")),
    path("", include("main_page.urls")),
    path("maps/", include('maps.urls')), # temporary
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
