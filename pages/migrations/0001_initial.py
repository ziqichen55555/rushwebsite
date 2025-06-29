# Generated by Django 5.2 on 2025-06-15 08:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cars', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(blank=True, max_length=100)),
                ('content', models.TextField()),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('image', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CarFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.CharField(max_length=100)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='cars.car')),
            ],
            options={
                'db_table': 'cars_carfeature',
            },
        ),
        migrations.CreateModel(
            name='RushSubscriptionEnquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_plan', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Subscription Price')),
                ('enquiry_answers', models.JSONField(blank=True, null=True, verbose_name='Form Answers')),
                ('source_page', models.CharField(blank=True, max_length=100)),
                ('name', models.CharField(max_length=100, verbose_name='Full Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email Address')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Phone Number')),
                ('contact_method', models.CharField(choices=[('Email', 'Email'), ('Phone', 'Phone')], default='Email', max_length=10, verbose_name='Preferred Contact Method')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Submitted At')),
                ('vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cars.car', verbose_name='Selected Vehicle')),
            ],
            options={
                'verbose_name': 'Rush Subscription Enquiry',
                'verbose_name_plural': 'Rush Subscription Enquiries',
                'db_table': 'rushwebsite_rushsubscriptionenquiry',
                'ordering': ['-created_at'],
            },
        ),
    ]
