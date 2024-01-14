# Generated by Django 4.2.4 on 2023-11-08 09:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discoveries', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discovery',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 11, 8, 9, 35, 49, 269198, tzinfo=datetime.timezone.utc), verbose_name='Год открытия'),
        ),
        migrations.AlterField(
            model_name='discovery',
            name='date_complete',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 8, 9, 35, 49, 269198, tzinfo=datetime.timezone.utc), verbose_name='Дата завершения'),
        ),
        migrations.AlterField(
            model_name='discovery',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 8, 9, 35, 49, 269198, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='discovery',
            name='date_of_formation',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 8, 9, 35, 49, 269198, tzinfo=datetime.timezone.utc), verbose_name='Дата формирования'),
        ),
    ]
