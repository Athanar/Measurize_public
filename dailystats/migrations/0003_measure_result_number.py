# Generated by Django 3.0.5 on 2020-04-30 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailystats', '0002_auto_20200430_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='measure',
            name='result_number',
            field=models.FloatField(default=0),
        ),
    ]
