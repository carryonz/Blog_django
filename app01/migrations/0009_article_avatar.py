# Generated by Django 2.1 on 2019-07-03 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0008_article_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='article/%Y%m%d/'),
        ),
    ]
