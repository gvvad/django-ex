# Generated by Django 2.0.4 on 2018-04-22 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rustbot', '0002_rustbotstore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rustbotchat',
            name='chat_id',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]