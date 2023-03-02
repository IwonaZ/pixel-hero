from exiffield.fields import ExifField
from exiffield.getters import get_datetaken
from exiffield.exceptions import ExifError
import os.path
from io import BytesIO
import uuid

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from Final_Project.settings import THUMBNAIL_SIZE
from gallery.models import Gallery
from PIL import Image, ImageOps 
from taggit.managers import TaggableManager


def get_datetaken_safe(exif):
    """
    Overriding exiffield's get_datetaken to prevent it from throwing
    errors when a picture doesn't include EXIF data.
    """
    try:
        return_value = get_datetaken(exif)
    except ExifError or ValueError:
        return_value = None
    return return_value


class PicturesContainer(models.Model):
    """Container that holds multiple pictures upload"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_images")
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} pictures"


def get_image_upload_path(instance, filename):
    """Get the path to the image files"""
    return "images/user_{pictures_container_user}/{file}".format(
        pictures_container_user=instance.pictures_container.user.username, file=filename
    )


def get_thumb_upload_path(instance, filename):
    """Get path to the thumbnails"""
    return "thumbs/user_{pictures_container_user}".format(pictures_container_user=instance.pictures_container.user.username)


class Picture(models.Model):
    """
    Picture model with automatically generated thumbnail.
    """
    image = models.ImageField(upload_to=get_image_upload_path)

    # author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_images")
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True) 
    gallery = models.ManyToManyField(Gallery, blank=True)

    thumbnail = models.ImageField(upload_to='thumbs')
    pictures_container = models.ForeignKey(PicturesContainer, on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager(blank=True)  # help_text="A comma-separated list of tags."

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    public_picture = models.BooleanField(default=False)
    public_link = models.BooleanField(default=False)

    #  METADATA
    created_on = models.DateTimeField(editable=False, blank=True, null=True, auto_now_add=True)
    exif = ExifField(
        source='image',
        denormalized_fields={
            'created_on': get_datetaken_safe,
        },
    )
    public_exif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Make and save the thumbnail for the picture.
        """
        if not self.make_thumbnail():
            raise Exception(
                "Could not create thumbnail - check if the file type is valid."
            )

        super(Picture, self).save(*args, **kwargs)

    def make_thumbnail(self):
        """
        Create and save the thumbnail for the picture (simple resize with PIL).
        """
        thumb_image = Image.open(self.image)
        # We use our PIL Image object to create the thumbnail, which already has a thumbnail() method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.Without antialiasing the image pattern artifacts may result.
        # thumb_image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        thumb_image = ImageOps.fit(
            thumb_image,
            THUMBNAIL_SIZE,
            bleed=0.0,
            centering=(0.5, 0.5),
        )

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = thumb_name + "_thumb" + thumb_extension

        if thumb_extension in [".jpg", ".jpeg"]:
            FTYPE = "JPEG"
        elif thumb_extension == ".gif":
            FTYPE = "GIF"
        elif thumb_extension == ".png":
            FTYPE = "PNG"
        else:
            return False  # Unrecognized file type
        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        thumb_image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)
        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

    def __str__(self):
        return f"Image {self.pk}"
