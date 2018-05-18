# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User



class MyUser(models.Model):
    IDENTITY_CHOICE = (
        ('T', u'老师'),
        ('S', u'学生')
    )

    nickname = models.CharField(max_length=32, blank=True, null=True)
    photo = models.ImageField(upload_to='./user/photo/%Y/%m/%d', blank=True, null=True)
    identity = models.CharField(max_length=1, choices=IDENTITY_CHOICE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friend = models.ManyToManyField('self')
    chat_room = models.ManyToManyField('chat.ChatRoomGroup')

    def __str__(self):
        return self.nickname
