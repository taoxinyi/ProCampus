# Generated by Django 2.0.5 on 2018-06-04 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20180604_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='tag',
            field=models.CharField(default='{}', max_length=300),
        ),
    ]
