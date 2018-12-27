# Generated by Django 2.0.8 on 2018-12-14 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TbotChatModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=32, unique=True)),
                ('up_date', models.DateTimeField(auto_now_add=True)),
                ('awaiting', models.TextField(default='')),
                ('tag_mask', models.IntegerField(default=-1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TbotStoreModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('up_time', models.DateTimeField(auto_now=True)),
                ('title_en', models.CharField(max_length=256)),
                ('title_ru', models.CharField(max_length=256)),
                ('link', models.CharField(max_length=256)),
                ('year', models.IntegerField(default=0)),
                ('poster', models.CharField(max_length=256)),
                ('tag', models.IntegerField(default=-1)),
            ],
        ),
    ]
