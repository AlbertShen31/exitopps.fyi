from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', views.Privacy.as_view(), name='privacy'),
]