from django.contrib import admin

from .models import Gallery


class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
    )
    # Prepopulating slug upon creating gallery
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Gallery, GalleryAdmin)
