# Generated by Django 4.2.2 on 2024-12-21 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_name',
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(upload_to='profile_pictures/'),
        ),
    ]