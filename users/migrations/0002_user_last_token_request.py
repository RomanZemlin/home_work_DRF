# Generated by Django 4.2.2 on 2023-11-12 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_token_request',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
