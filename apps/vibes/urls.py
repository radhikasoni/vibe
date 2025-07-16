from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('api/v1/create-vibe/', views.CreateVibeView.as_view(), name="create_vibe"),
    path('api/v1/vibe-history/', views.VibeHistoryView.as_view(), name='vibe_history'),
]