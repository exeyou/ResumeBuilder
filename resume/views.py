from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.text import slugify
from django.utils.encoding import smart_str
from django.views.decorators.http import require_POST
from django.http import HttpResponse, FileResponse, JsonResponse, Http404
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings

from datetime import timedelta
import tempfile
import subprocess
import time
import os

from docx import Document
from weasyprint import HTML, CSS
import pdfkit

from .forms import ResumeForm
from .models import Resume, TemplateRating

MAX_DRAFTS = 5

def get_template_rating_info(template_name):
    ratings = TemplateRating.objects.filter(template_name=template_name)
    total = ratings.count()
    if total == 0:
        return {'average': 0, 'count': 0}
    avg = round(sum(r.rating for r in ratings) / total, 1)
    return {'average': avg, 'count': total}

@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resume_data = form.cleaned_data

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
                is_saved=False,
                photo=request.FILES.get('photo'),
                photo_caption=resume_data.get('photo_caption'),
                attachment=request.FILES.get('attachment'),
                attachment_caption=resume_data.get('attachment_caption'),
            )

            resume.save()

            return redirect('resume:preview_resume', resume_id=resume.id)
    else:
        form = ResumeForm(user=request.user)

    return render(request, 'resume/basic/form.html', {'form': form})



@login_required
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    template_name = f'resume/template_resumes/{resume.template}.html'
    return render(request, template_name, {'resume': resume, 'show_edit_panel': True})


@login_required
def save_resume(request):
    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        template = request.POST.get('template')

        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)

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
        resume.photo_caption = request.POST.get('photo_caption')
        resume.attachment_caption = request.POST.get('attachment_caption')
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

    html_string = render_to_string(
        f'resume/template_resumes/{resume.template}.html',
        {
            'resume': resume,
            'show_edit_panel': False,
            'pdf': True
        },
        request=request
    )

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file, \
         tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as docx_file:

        html_file.write(html_string.encode('utf-8'))
        html_file.flush()


        try:
            subprocess.run([
                "pandoc",
                html_file.name,
                "-f", "html",
                "-t", "docx",
                "-o", docx_file.name,
                "--embed-resources",
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


@require_POST
@login_required
def rate_template(request):
    template_name = request.POST.get('template')
    rating = int(request.POST.get('rating', 0))

    if template_name and 1 <= rating <= 5:
        obj, created = TemplateRating.objects.update_or_create(
            user=request.user,
            template_name=template_name,
            defaults={'rating': rating}
        )
        return JsonResponse({'success': True, 'rating': rating})

    return JsonResponse({'success': False, 'error': 'Invalid input'})


@login_required
def get_template_rating(request):
    template_name = request.GET.get('template')
    if not template_name:
        return JsonResponse({'error': 'No template provided'}, status=400)

    ratings = TemplateRating.objects.filter(template_name=template_name)
    count = ratings.count()
    avg = round(sum(r.rating for r in ratings) / count, 1) if count > 0 else 0
    user_rating = TemplateRating.objects.filter(template_name=template_name, user=request.user).first()

    return JsonResponse({
        'average': avg,
        'count': count,
        'user_rating': user_rating.rating if user_rating else 0
    })


@login_required
def copy_resume(request, resume_id):
    original_resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Create a new instance with copied fields
    new_resume = Resume.objects.create(
        user=request.user,
        first_name=original_resume.first_name,
        last_name=original_resume.last_name,
        age=original_resume.age,
        activity=original_resume.activity,
        experience=original_resume.experience,
        phone=original_resume.phone,
        email=original_resume.email,
        address=original_resume.address,
        education=original_resume.education,
        about=original_resume.about,
        template=original_resume.template,
        is_saved=original_resume.is_saved,
        photo_caption=original_resume.photo_caption,
        attachment_caption=original_resume.attachment_caption,
    )

    # Copy photo file if exists
    if original_resume.photo:
        photo_content = original_resume.photo.read()
        new_resume.photo.save(
            os.path.basename(original_resume.photo.name),
            ContentFile(photo_content)
        )

    # Copy attachment file if exists
    if original_resume.attachment:
        attachment_content = original_resume.attachment.read()
        new_resume.attachment.save(
            os.path.basename(original_resume.attachment.name),
            ContentFile(attachment_content)
        )

    new_resume.save()
    return redirect('resume:my_resumes')


@login_required
def preview_resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    html_string = render_to_string(
        f'resume/template_resumes/{resume.template}.html',
        {
            'resume': resume,
            'show_edit_panel': False,
            'pdf': True  # включаем стили для PDF
        },
        request=request
    )

    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 10mm }')])

    return HttpResponse(pdf, content_type='application/pdf')

