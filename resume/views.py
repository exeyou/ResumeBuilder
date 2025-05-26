from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ResumeForm
from .models import Resume

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
        else:
            resume = Resume(user=request.user)

        # Обновление всех полей
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

        resume.is_saved = True  # <-- теперь это "сохранённое" резюме
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