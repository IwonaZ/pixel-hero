from django.contrib import admin

from .models import Picture, PicturesContainer


class PictureInline(admin.TabularInline):
    model = Picture
    

@admin.register(PicturesContainer)
class PicturesContainerAdmin(admin.ModelAdmin):
    inlines = [PictureInline]

class PictureAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "created_on",
    )


admin.site.register(Picture, PictureAdmin)