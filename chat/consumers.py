# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from authentication.models import MyUser
from chat.models import ChatRoomGroup, ChatHistory
from channels.db import database_sync_to_async
from datetime import datetime
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.myuser = await  self.get_myuser()
        self.username = self.get_username()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.save_group()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        s = await  self.get_history()
        await self.send(text_data=json.dumps({
            'message': s,
            'type': 'clear'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author_id': self.myuser.id if self.user.is_authenticated else 0,
                'image': str(self.myuser.photo) if self.user.is_authenticated else "",
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        await  self.save_history(message)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        author_id = event['author_id']
        time = event['time']
        isAuthor = "0"
        if self.user.is_authenticated and author_id == self.myuser.id:
            isAuthor = "1"
        print(isAuthor, time, type(time))
        if (event['image'] == ""):
            image = '/static/image/default.png'
        else:
            image = '/media/' + event['image']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'image': image,
            'isAuthor': isAuthor,
            'time': time,
            'author': MyUser.objects.get(user_id=author_id).nickname if author_id > 0 else "Anonymous"
        }))

    @database_sync_to_async
    def get_myuser(self):
        return MyUser.objects.get(user_id=self.user.id) if self.user.is_authenticated else None

    def get_username(self):
        return self.myuser.nickname if self.user.is_authenticated else "Anonymous"

    @database_sync_to_async
    def save_group(self):
        ChatRoomGroup.objects.get_or_create(name=self.room_group_name)

    @database_sync_to_async
    def save_history(self, history):
        """
        save to db
        :param history:
        :return:
        """
        group = ChatRoomGroup.objects.get(name=self.room_group_name)
        ChatHistory.objects.create(room_group=group, history=history, user=self.myuser)

    @database_sync_to_async
    def get_history(self):
        """
        get history when first connect
        :return:
        """
        s = []
        for i in ChatRoomGroup.objects.get(name=self.room_group_name).chathistory_set.all():
            d = {}
            d["message"] = i.history
            d["image"] = '/media/' + str(i.user.photo) if i.user else '/static/image/default.png'
            d["isAuthor"] = "1" if self.myuser == i.user else "0"
            d["time"] = i.time.strftime('%Y-%m-%d %H:%M:%S')
            d["author"] = i.user.nickname if i.user else "Anonymous"
            s.append(d)
        return s
