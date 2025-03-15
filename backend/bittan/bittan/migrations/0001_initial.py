# Generated by Django 5.0 on 2025-03-13 20:02

import bittan.models.swish_payment_request
import datetime
import django.db.models.deletion
import django_enumfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChapterEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('total_seats', models.IntegerField()),
                ('max_tickets_per_payment', models.IntegerField(default=8)),
                ('sales_stop_at', models.DateTimeField()),
                ('reservation_duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('swish_message', models.TextField(max_length=50)),
                ('event_at', models.DateTimeField()),
                ('door_open_before', models.DurationField(default=datetime.timedelta(seconds=3600))),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expires_at', models.DateTimeField()),
                ('swish_id', models.TextField(blank=True, null=True)),
                ('status', models.TextField(choices=[('RESERVED', 'Reserved'), ('PAID', 'Paid'), ('FAILED_EXPIRED_RESERVATION', 'Failed Expired Reservation'), ('FAILED_ADMIN', 'Failed Admin')])),
                ('email', models.TextField(blank=True, null=True)),
                ('sent_email', models.BooleanField(default=False)),
                ('payment_started', models.BooleanField(default=False)),
                ('payment_method', models.TextField(blank=True, choices=[('SWISH', 'Swish'), ('ADMIN_GENERATED', 'Admin Generated')], null=True)),
                ('time_paid', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SwishPaymentRequestModel',
            fields=[
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('status', django_enumfield.db.fields.EnumField(default=3, enum=bittan.models.swish_payment_request.PaymentStatus)),
                ('error_code', django_enumfield.db.fields.EnumField(enum=bittan.models.swish_payment_request.PaymentErrorCode, null=True)),
                ('date_paid', models.DateTimeField(null=True)),
                ('amount', models.IntegerField()),
                ('external_uri', models.TextField(null=True)),
                ('token', models.TextField(null=True)),
                ('swish_api_response', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('is_visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.TextField(unique=True)),
                ('time_created', models.DateTimeField()),
                ('times_used', models.IntegerField(default=0)),
                ('chapter_event', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bittan.chapterevent')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bittan.payment')),
                ('ticket_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bittan.tickettype')),
            ],
        ),
        migrations.AddField(
            model_name='chapterevent',
            name='ticket_types',
            field=models.ManyToManyField(to='bittan.tickettype'),
        ),
    ]
