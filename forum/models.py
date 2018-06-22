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


class Comment(models.Model):
    from_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="comment_from_user")
    to_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="comment_to_user")
    like_user = models.ManyToManyField(MyUser, related_name="comment_like_user")
    dislike_user = models.ManyToManyField(MyUser, related_name="comment_dislike_user")
    text = models.CharField(max_length=300)
    time = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        return "From:%s,like:%s,dislike:%s" % (self.from_user, self.like_user.count(), self.dislike_user.count())


class Tag(models.Model):
    from_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="tag_from_user")
    to_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="tag_to_user")
    tag = models.CharField(max_length=30)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag


class Star(models.Model):
    from_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="star_from_user")
    to_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="star_to_user")
    value = models.IntegerField(null=True)

    def __str__(self):
        return "From:%s,To:%s,Value:%s" % (self.from_user, self.to_user, self.value)


class RequestReplyFriend(models.Model):
    request_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="request_user")
    reply_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="reply_user")
