# Generated by Django 5.0.2 on 2024-02-18 21:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="student_date_of_birth",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]