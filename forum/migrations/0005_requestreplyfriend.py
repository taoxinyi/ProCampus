# Generated by Django 2.0.5 on 2018-05-16 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_myuser_friend'),
        ('forum', '0004_question_is_top'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestReplyFriend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reply_user', to='authentication.MyUser')),
                ('request_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_user', to='authentication.MyUser')),
            ],
        ),
    ]