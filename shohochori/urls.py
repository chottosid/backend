"""
URL configuration for shohochori project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('user/login/', views.user_login),
    path('user/register/', views.user_register),
    path('pending/send/', views.send_request),
    path('pending/requests/<int:assistantId>/', views.get_pending_requests),
    path('pending/confirm/', views.confirm_request),
    path('pending/notification/<int:user_id>/', views.get_notification),
    path('pending/check/<int:user_id>/', views.check_request),
    path('assistant/login/', views.assistant_login),
    path('assistant/register/', views.assistant_register),
    path('doctor/login/', views.doctor_login),
    path('doctor/register/', views.doctor_register),
    path('doctor/appointment/add/', views.add_appointment),
    path('doctor/appointment/confirm/', views.confirm_appointment),
    path('doctor/appointment/user/<int:user_id>/', views.get_user_appointments),
    path('doctor/appointment/doctor/<int:doctor_id>/', views.get_doctor_appointments),
    path('doctor/all/', views.get_doctors),
    path("assistant/all/", views.get_assistants),
    path("pending/requests/user/<int:user_id>/", views.get_pending_requests_user),
    path("pending/completed/", views.completed_request),
    path("user/feed/post/", views.post_feed),
    path("user/feed/comment/", views.comment),
    path("user/notifications/all/<int:user_id>/", views.get_all_notifications),
    path("user/feed/<int:post_id>/", views.get_post),
    path("user/feed/all/<int:uid>/", views.get_all_posts),
    path("user/feed/like/", views.like_post),
]

# Serve media files

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)