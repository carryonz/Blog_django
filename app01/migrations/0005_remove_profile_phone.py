# Generated by Django 2.1 on 2019-07-02 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='phone',
        ),
    ]
