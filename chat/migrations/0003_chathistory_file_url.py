# Generated by Django 2.0.5 on 2018-05-24 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20180515_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='chathistory',
            name='file_url',
            field=models.CharField(max_length=140, null=True),
        ),
    ]
