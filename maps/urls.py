from django.urls import path
from . import views

urlpatterns = [
    # Same url as picture_detail, this is just a placeholder
    path("<uuid:uuid>/", views.picture_detail_map, name="picture_detail_map"),
]
