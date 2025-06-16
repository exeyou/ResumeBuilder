from django.db import models
from django.contrib.auth.models import User
from django.db.models import BooleanField, DateTimeField


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)
    experience = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    template = models.CharField(max_length=100, default='default')
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.first_name or ''} {self.last_name or ''}"

class TemplateRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField()  # 1–5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'template_name')  # Один пользователь – одна оценка на шаблон

    def __str__(self):
        return f'{self.user.username} rated {self.template_name} → {self.rating}'