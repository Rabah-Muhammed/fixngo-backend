# Generated by Django 5.1.5 on 2025-03-07 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_roommember_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roommember',
            name='user',
        ),
    ]
