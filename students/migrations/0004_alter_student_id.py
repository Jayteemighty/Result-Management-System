# Generated by Django 5.0.2 on 2024-03-29 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0003_rename_student_roll_student_student_matricno"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
