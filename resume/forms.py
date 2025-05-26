from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    TEMPLATE_CHOICES = (
        ('template1', 'Шаблон 1'),
        ('template2', 'Шаблон 2'),
    )

    template = forms.ChoiceField(choices=TEMPLATE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Resume
        exclude = ['user', 'template', 'is_saved', 'created_at']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ResumeForm, self).__init__(*args, **kwargs)

        if user:
            profile = getattr(user, 'profile', None)
            if profile:
                self.fields['first_name'].initial = profile.first_name
                self.fields['last_name'].initial = profile.last_name
                self.fields['age'].initial = profile.age
                self.fields['activity'].initial = profile.activity
                self.fields['experience'].initial = profile.experience
