# Generated by Django 2.0.5 on 2018-05-24 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chathistory_file_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='chathistory',
            name='filename',
            field=models.CharField(max_length=140, null=True),
        ),
        migrations.AddField(
            model_name='chathistory',
            name='filesize',
            field=models.IntegerField(null=True),
        ),
    ]
