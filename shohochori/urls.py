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

urlpatterns = [
    path('user/login/', views.user_login),
    path('user/register/', views.user_register),
    path('pending/send/', views.send_request),
    path('pending/requests/', views.get_pending_requests),
    path('pending/confirm/', views.confirm_request),
    path('pending/notification/<int:user_id>/', views.get_notification),
    path('pending/check/<int:user_id>/', views.check_request),
    path('assistant/login/', views.assistant_login),
    path('assistant/register/', views.assistant_register),
]