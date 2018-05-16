from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from DjangoUeditor.models import UEditorField
from authentication.models import MyUser


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_time = models.DateTimeField(auto_now_add=True)
    show_times = models.IntegerField(default=0)
    content = UEditorField(imagePath="forum/question/image/", filePath="forum/question/files/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    inviting_person = models.ForeignKey(MyUser, null=True, default=None, blank=True, on_delete=models.CASCADE)
    is_top = models.BooleanField(default=False)

    class Meta:
        ordering = ['-publish_time']

    def __str__(self):
        return self.title


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_author = models.ForeignKey(MyUser, null=True, default=None, blank=True, on_delete=models.CASCADE)
    publish_time = models.DateTimeField(auto_now_add=True)
    content = UEditorField(imagePath="forum/question/image/", filePath="forum/question/files/")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.author.__str__() + '\'s answer'
