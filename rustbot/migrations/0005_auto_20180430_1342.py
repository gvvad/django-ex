# Generated by Django 2.0.4 on 2018-04-30 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rustbot', '0004_auto_20180428_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rustbotstore',
            name='tag',
            field=models.IntegerField(default=-1),
        ),
    ]