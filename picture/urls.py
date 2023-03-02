from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.picture_upload, name="picture-upload"),
    path("upload_dnd/", views.picture_upload_dnd, name="picture-upload-dnd"),
    path("gallery/<str:gallery_name>/upload/", views.picture_upload_to_gallery, name="picture-upload-to-gallery"),

]
