# Generated by Django 2.2.5 on 2020-05-11 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_courseorg_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseorg',
            name='学习人数',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseorg',
            name='课程数',
            field=models.IntegerField(default=0),
        ),
    ]