from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    age = forms.IntegerField(min_value=0, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    education = forms.CharField(widget=forms.Textarea, required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    activity = forms.CharField(max_length=255, required=False)
    experience = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'age', 'phone', 'address', 'education',
                  'about', 'activity', 'experience']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                age=self.cleaned_data.get('age'),
                phone=self.cleaned_data.get('phone'),
                address=self.cleaned_data.get('address'),
                education=self.cleaned_data.get('education'),
                about=self.cleaned_data.get('about'),
                activity=self.cleaned_data.get('activity'),
                experience=self.cleaned_data.get('experience'),
                email=self.cleaned_data['email'],
            )
        return user


class LoginForm(AuthenticationForm):
    pass

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'age', 'phone', 'email',
                  'address', 'education', 'about', 'activity', 'experience']
