from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('create/', views.ImageCreateView.as_view(), name='create'),
    path('delete/<pk>/', views.ImageDeleteView.as_view(), name='delete'),
]

app_name = 'images'