# Generated by Django 5.1.5 on 2025-02-08 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_booking_payment_status_booking_total_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='platform_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='remaining_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('fee_paid', 'Fee Paid'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=10),
        ),
    ]
