# Generated by Django 4.0.6 on 2022-07-23 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='like',
            field=models.IntegerField(default=0),
        ),
    ]