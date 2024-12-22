# Generated by Django 4.2.2 on 2024-12-22 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_user_user_name_alter_user_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('doctor_id', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('appointment_time', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('doctor_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=255)),
                ('dob', models.DateTimeField(blank=True, null=True)),
                ('profile_picture', models.ImageField(upload_to='profile_pictures/')),
                ('reg_no', models.CharField(max_length=255)),
                ('id_proof', models.ImageField(null=True, upload_to='id_proofs/')),
            ],
        ),
        migrations.RenameField(
            model_name='pendingrequest',
            old_name='type',
            new_name='category',
        ),
        migrations.RemoveField(
            model_name='assistant',
            name='id_document',
        ),
        migrations.AddField(
            model_name='assistant',
            name='id_proof',
            field=models.ImageField(default=0, upload_to='id_documents/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assistant',
            name='profile_picture',
            field=models.ImageField(default=0, upload_to='profile_pictures/'),
            preserve_default=False,
        ),
    ]