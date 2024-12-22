# Generated by Django 4.2.2 on 2024-12-22 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_appointment_doctor_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendingrequest',
            name='assistant_id',
        ),
        migrations.RemoveField(
            model_name='pendingrequest',
            name='fulfilled_at',
        ),
        migrations.RemoveField(
            model_name='pendingrequest',
            name='user_id',
        ),
        migrations.AddField(
            model_name='pendingrequest',
            name='assistant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.assistant'),
        ),
        migrations.AddField(
            model_name='pendingrequest',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='app.user'),
            preserve_default=False,
        ),
    ]
