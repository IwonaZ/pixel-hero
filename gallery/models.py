from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Gallery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=80, null=False, blank=False)
    slug = models.SlugField(null=True, blank=True, unique=True)

    class Meta:
        verbose_name = "gallery"
        verbose_name_plural = "galleries"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Automatically create slug upon saving model.
        """
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
