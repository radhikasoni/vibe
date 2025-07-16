from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('api/v1/create-vibe/', views.CreateVibeView.as_view(), name="create_vibe"),
]