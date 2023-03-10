# Generated by Django 4.0.3 on 2022-04-08 08:00

from django.db import migrations, models
import exiffield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0014_picture_tags_alter_picture_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='created_on',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='picture',
            name='exif',
            field=exiffield.fields.ExifField(default={}, editable=False),
        ),
    ]
