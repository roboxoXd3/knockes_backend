# Generated by Django 5.1.7 on 2025-03-22 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_usertokenlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertokenlog',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
