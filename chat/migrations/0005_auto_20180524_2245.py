# Generated by Django 2.0.5 on 2018-05-24 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20180524_2243'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chathistory',
            old_name='filename',
            new_name='file_name',
        ),
        migrations.RenameField(
            model_name='chathistory',
            old_name='filesize',
            new_name='file_size',
        ),
    ]
