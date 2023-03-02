# Generated by Django 4.0.3 on 2022-04-12 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0018_rename_created_picturescontainer_uploaded_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picture',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='picture',
            name='longitude',
        ),
        migrations.AddField(
            model_name='picture',
            name='public_exif',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]