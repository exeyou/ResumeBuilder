from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .forms import ResumeForm
from .models import Resume
from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile
from docx import Document
import subprocess
from django.utils.text import slugify
import pdfkit
import time
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from weasyprint import HTML, CSS
from django.http import HttpResponse
from django.utils.text import slugify
from django.http import FileResponse, Http404
from django.utils.encoding import smart_str

MAX_DRAFTS = 5

@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, user=request.user)
        if form.is_valid():
            resume_data = form.cleaned_data

            # Создание черновика
            resume = Resume(
                user=request.user,
                first_name=resume_data['first_name'],
                last_name=resume_data['last_name'],
                age=resume_data.get('age'),
                activity=resume_data['activity'],
                experience=resume_data.get('experience') or 0,
                phone=resume_data['phone'],
                email=resume_data['email'],
                address=resume_data['address'],
                education=resume_data['education'],
                about=resume_data['about'],
                template=resume_data['template'],
                is_saved=False  # Черновик!
            )
            resume.save()

            # Перенаправить в предпросмотр
            return redirect('resume:preview_resume', resume_id=resume.id)

    else:
        form = ResumeForm(user=request.user)

    return render(request, 'resume/basic/form.html', {'form': form})



@login_required
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    # Рендерим основной шаблон резюме (например, resume/template_resumes/{template}.html),
    # в который включаем боковое окно редактирования через include
    template_name = f'resume/template_resumes/{resume.template}.html'
    return render(request, template_name, {'resume': resume, 'show_edit_panel': True})


@login_required
def save_resume(request):
    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        template = request.POST.get('template')

        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)

            # Если не переданы ключевые данные, просто отмечаем как is_saved
            if not request.POST.get('first_name') and not request.POST.get('last_name'):
                resume.is_saved = True
                resume.save()
                return redirect('resume:edit_resume', resume_id=resume.id)

        else:
            resume = Resume(user=request.user)

        # Обновление всех полей, если данные пришли
        resume.first_name = request.POST.get('first_name')
        resume.last_name = request.POST.get('last_name')
        resume.age = request.POST.get('age') or None
        resume.activity = request.POST.get('activity')
        resume.experience = request.POST.get('experience') or 0
        resume.phone = request.POST.get('phone')
        resume.email = request.POST.get('email')
        resume.address = request.POST.get('address')
        resume.education = request.POST.get('education')
        resume.about = request.POST.get('about')
        resume.template = template
        resume.is_saved = True

        resume.save()

        return redirect('resume:edit_resume', resume_id=resume.id)

    return redirect('resume:my_resumes')



@login_required
def my_resumes(request):
    resumes = Resume.objects.filter(user=request.user, is_saved=True).order_by('-created_at')
    return render(request, 'resume/basic/my_resumes.html', {'resumes': resumes})



@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()
    return redirect('resume:my_resumes')

@login_required
def preview_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return render(request, f'resume/template_resumes/{resume.template}.html', {'resume': resume})

@login_required
def resume_drafts(request):
    drafts = Resume.objects.filter(user=request.user, is_saved=False).order_by('-created_at')

    # Ограничиваем количество черновиков
    if drafts.count() > MAX_DRAFTS:
        extra = drafts[MAX_DRAFTS:]
        for draft in extra:
            draft.delete()

    return render(request, 'resume/basic/drafts.html', {'drafts': drafts})


@login_required
def download_resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    html_string = render_to_string(
        f'resume/template_resumes/{resume.template}.html',
        {
            'resume': resume,
            'show_edit_panel': False,
            'pdf': True
        },
        request=request
    )

    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 10mm }')])

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"resume_{slugify(resume.first_name or '')}_{slugify(resume.last_name or '')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@login_required
def download_resume_docx(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Рендерим HTML из шаблона
    html_string = render_to_string(
        f'resume/template_resumes/{resume.template}.html',
        {
            'resume': resume,
            'show_edit_panel': False,
            'pdf': True
        },
        request=request
    )

    # Создаем временные файлы
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file, \
         tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as docx_file:

        html_file.write(html_string.encode('utf-8'))
        html_file.flush()

        # Вызываем Pandoc
        try:
            subprocess.run([
                "pandoc",
                html_file.name,
                "-f", "html",
                "-t", "docx",
                "-o", docx_file.name,
                "--embed-resources",  # чтобы включить встроенные стили
                "--standalone"
            ], check=True)

            docx_file.seek(0)
            filename = f"resume_{slugify(resume.first_name or '')}_{slugify(resume.last_name or '')}.docx"

            # Возвращаем ответ
            with open(docx_file.name, "rb") as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except subprocess.CalledProcessError:
            return HttpResponse("Помилка при генерації DOCX через Pandoc.", status=500)