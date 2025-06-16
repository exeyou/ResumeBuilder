from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('create/', views.create_resume, name='create_resume'),
    path('preview/<int:resume_id>/', views.preview_resume, name='preview_resume'),
    path('save/', views.save_resume, name='save_resume'),
    path('my/', views.my_resumes, name='my_resumes'),
    path('edit/<int:resume_id>/', views.edit_resume, name='edit_resume'),
    path('delete/<int:resume_id>/', views.delete_resume, name='delete_resume'),
    path('drafts/', views.resume_drafts, name='drafts'),
    path('downloadpdf/<int:resume_id>/', views.download_resume_pdf, name='download_resume_pdf'),
    path('downloaddocx/<int:resume_id>/', views.download_resume_docx, name='download_resume_docx'),
    path('rate-template/', views.rate_template, name='rate_template'),
    path('api/get-template-rating/', views.get_template_rating, name='get_template_rating'),

]