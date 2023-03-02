from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_pictures, name="all_pictures"),
    path("delete/", views.delete_multiple_pictures, name='delete-multiple-pictures'),
    path("download/", views.download_multiple_pictures, name='download-multiple-pictures'),
    path("tag/<slug:tag_slug>/",views.all_tagged_pictures, name="all_tagged_pictures"),
    path("new_gallery/", views.new_gallery, name="new_gallery"),
    path("<slug:gallery>/", views.gallery_detail, name="gallery_detail"),
    path(
        "picture_detail/<uuid:uuid>/delete_picture/",
        views.delete_picture,
        name="delete_picture",
    ),
    path(
        "picture_detail/<uuid:uuid>/",
        views.edit_picture,
        name="edit_picture",
    ),
    path(
        "picture_detail/<uuid:uuid>/<slug:galleryid>/",
        views.edit_gallery_picture,
        name="edit_gallery_picture",
    ),
    path("<slug:gallery>/delete_gallery/", views.delete_gallery, name="delete_gallery"),
    
]
