# Generated by Django 5.1.5 on 2025-02-01 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_slot_is_booked'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='worker',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='worker',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
