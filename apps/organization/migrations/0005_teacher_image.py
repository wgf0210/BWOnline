# Generated by Django 2.2.5 on 2020-05-11 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20200511_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='image',
            field=models.ImageField(default='', upload_to='teacher/%Y/%m', verbose_name='头像'),
        ),
    ]
