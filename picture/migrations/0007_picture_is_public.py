# Generated by Django 4.0.3 on 2022-04-04 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0006_alter_picture_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
