from django.urls import path
from django.urls import path, include
from . import views

app_name = 'announcement'

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
]

