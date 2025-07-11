from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    TEMPLATE_CHOICES = (
        ('template1', 'Шаблон 1'),
        ('template2', 'Шаблон 2'),
        ('template3', 'Шаблон 3'),
        ('template4', 'Шаблон 4'),
        ('template5', 'Шаблон 5'),
        ('template6', 'Шаблон 6'),
        ('template7', 'Шаблон 7'),
        ('template8', 'Шаблон 8'),
        ('template9', 'Шаблон 9')
    )

    template = forms.ChoiceField(choices=TEMPLATE_CHOICES, widget=forms.RadioSelect)
    photo = forms.ImageField(required=False)
    attachment = forms.FileField(required=False)
    photo_caption = forms.CharField(required=False)
    attachment_caption = forms.CharField(required=False)

    class Meta:
        model = Resume
        exclude = ['user', 'template', 'is_saved', 'created_at']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'profile'):
            profile = user.profile
            self.fields['first_name'].initial = profile.first_name
            self.fields['last_name'].initial = profile.last_name
            self.fields['age'].initial = profile.age
            self.fields['phone'].initial = profile.phone
            self.fields['email'].initial = profile.email
            self.fields['address'].initial = profile.address
            self.fields['education'].initial = profile.education
            self.fields['about'].initial = profile.about
            self.fields['activity'].initial = profile.activity
            self.fields['experience'].initial = profile.experience

