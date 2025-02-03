# Generated by Django 5.1.5 on 2025-02-03 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_worker_off_days_worker_slot_duration_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slot',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='slot',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='slot',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='slot',
            unique_together={('worker', 'date', 'start_time', 'end_time')},
        ),
    ]
