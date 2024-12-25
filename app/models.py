from django.db import models
from django.utils import timezone

class Assistant(models.Model):
    assistant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    dob = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    #id document should be a image file
    id_proof = models.ImageField(upload_to='id_documents/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=255, null=True, blank=True,default='available')

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
    profile_picture = models.ImageField(upload_to='profile_pictures/')

class PendingRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    notified = models.BooleanField(default=False)

class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    dob = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    reg_no = models.CharField(max_length=255)
    id_proof = models.ImageField(upload_to='id_proofs/',null=True)
    specialization = models.CharField(max_length=255)
    experience = models.IntegerField()
    address = models.CharField(max_length=255)
class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255)


# Social media schema

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    media = models.ImageField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #one post can be liked by multiple users
    #one user can like multiple posts
    #but a user can like a post only once
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)


