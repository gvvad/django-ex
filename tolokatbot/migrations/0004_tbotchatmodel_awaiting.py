# Generated by Django 2.0.4 on 2018-05-19 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tolokatbot', '0003_auto_20180518_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbotchatmodel',
            name='awaiting',
            field=models.TextField(default=''),
        ),
    ]