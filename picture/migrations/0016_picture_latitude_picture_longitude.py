# Generated by Django 4.0.3 on 2022-04-08 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0015_picture_created_on_picture_exif'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='latitude',
            field=models.CharField(blank=True, editable=False, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='picture',
            name='longitude',
            field=models.CharField(blank=True, editable=False, max_length=20, null=True),
        ),
    ]
