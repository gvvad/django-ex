# Generated by Django 2.0.4 on 2018-04-20 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rustbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RusTbotStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('up_time', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=256)),
                ('link', models.CharField(max_length=256)),
                ('author', models.CharField(max_length=256)),
            ],
        ),
    ]
