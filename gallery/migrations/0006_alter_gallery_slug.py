# Generated by Django 4.0.3 on 2022-03-31 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0005_alter_gallery_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gallery",
            name="slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
