# resume/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ResumeForm
from .models import Resume
from django.contrib.auth.decorators import login_required

@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, user=request.user)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            template = form.cleaned_data['template']
            return redirect('resume:preview_resume', resume_id=resume.id, template_name=template)
    else:
        form = ResumeForm(user=request.user)
    return render(request, 'resume/form.html', {'form': form})

@login_required
def preview_resume(request, resume_id, template_name):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return render(request, f'resume/{template_name}.html', {'resume': resume})
