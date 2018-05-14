# Generated by Django 2.0.4 on 2018-05-09 21:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tolokatbot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tbotstoremodel',
            name='up_time',
        ),
        migrations.AddField(
            model_name='tbotstoremodel',
            name='add_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]