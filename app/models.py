from django.db import models
from django.utils import timezone

class Assistant(models.Model):
    assistant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    dob = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id_document = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

class PendingRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    assistant_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    notified = models.BooleanField(default=False)

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    address = models.TextField(null=True, blank=True)
    dob = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=255)  # Use password hashing
    profile_picture = models.TextField(null=True, blank=True)
    user_name = models.CharField(max_length=100, unique=True)

class PendingRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pending_requests')
    assistant = models.ForeignKey('Assistant', null=True, blank=True, on_delete=models.SET_NULL)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, default='pending')
    notified = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
