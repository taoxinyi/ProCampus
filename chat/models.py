from django.db import models
from authentication.models import MyUser


# Create your models here.
class ChatRoomGroup(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class ChatHistory(models.Model):
    room_group = models.ForeignKey(ChatRoomGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    history = models.CharField(max_length=140, null=True)
    time = models.DateTimeField(auto_now=True)
    file_url = models.CharField(max_length=140, null=True)
    file_name = models.CharField(max_length=140, null=True)
    file_size = models.IntegerField(null=True)

    def __str__(self):
        return self.room_group.name
