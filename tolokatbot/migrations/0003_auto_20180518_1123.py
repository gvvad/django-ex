# Generated by Django 2.0.4 on 2018-05-18 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tolokatbot', '0002_auto_20180510_0006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tbotchatmodel',
            old_name='notif_date',
            new_name='up_date',
        ),
        migrations.RenameField(
            model_name='tbotchatmodel',
            old_name='chat_id',
            new_name='user_id',
        ),
    ]
