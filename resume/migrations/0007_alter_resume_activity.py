# Generated by Django 5.2.1 on 2025-05-26 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0006_alter_resume_about_alter_resume_activity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='activity',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
