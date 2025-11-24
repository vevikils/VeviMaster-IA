from django.urls import path
from . import views

app_name = 'mastering'

urlpatterns = [
    path('', views.upload_audio, name='upload'),
    path('download/<str:filename>/', views.download_master, name='download'),
]
