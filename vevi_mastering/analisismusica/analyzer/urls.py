from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.index, name='index'),
    path('results/<int:analysis_id>/', views.results, name='results'),
    path('api/results/<int:analysis_id>/', views.api_results, name='api_results'),
]

