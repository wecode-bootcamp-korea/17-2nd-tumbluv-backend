# Generated by Django 3.1.7 on 2021-03-09 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20210304_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
