# Generated by Django 2.2.5 on 2020-05-13 23:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_course_is_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerCourse',
            fields=[
            ],
            options={
                'verbose_name': '轮播课程',
                'verbose_name_plural': '轮播课程',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('course.course',),
        ),
    ]
