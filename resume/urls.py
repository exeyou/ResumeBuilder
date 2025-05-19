from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('create/', views.create_resume, name='create_resume'),
    path('preview/<int:resume_id>/<str:template_name>/', views.preview_resume, name='preview_resume'),
]
