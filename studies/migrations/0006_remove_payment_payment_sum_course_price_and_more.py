# Generated by Django 4.2.2 on 2023-11-10 13:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studies', '0005_course_owner_lesson_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='payment_sum',
        ),
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.PositiveIntegerField(default=1000, verbose_name='Стоимость курса'),
        ),
        migrations.AddField(
            model_name='payment',
            name='is_successful',
            field=models.BooleanField(default=False, verbose_name='Статус платежа'),
        ),
        migrations.AddField(
            model_name='payment',
            name='session',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Сессия для оплаты'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('1', 'Наличные'), ('2', 'Безнал')], verbose_name='Метод платежа'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_payments', to=settings.AUTH_USER_MODEL),
        ),
    ]
