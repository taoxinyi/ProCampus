# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from authentication.models import MyUser
from chat.models import ChatRoomGroup, ChatHistory
from channels.db import database_sync_to_async
from datetime import datetime
import json

from forum.models import RequestReplyFriend


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.myuser = self.user.myuser
        self.username = self.get_username()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        self.room_object = await self.save_group()
        current_list = await self.return_to_current_list_and_add_to_db()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        s = await  self.get_history()
        await self.send(text_data=json.dumps({
            'message': s,
            'type': 'clear',
            'current_list': current_list
        }))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_enter',
                'id': self.user.id,
                'name': self.user.myuser.nickname,
                'image': self.get_user_image_url(self.user)

            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_leave',
                'id': self.user.id,
                'name': self.user.myuser.nickname,
                'image': self.get_user_image_url(self.user)

            })
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.delete_from_db()

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
                'author_id': self.user.id if self.user.is_authenticated else 0,
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
        if self.user.is_authenticated and author_id == self.user.id:
            isAuthor = "1"
        if author_id == 0:
            image = '/static/image/default.png'
        else:
            image = self.get_user_image_url(User.objects.get(id=author_id))
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "chat_message",
            'message': message,
            'image': image,
            'isAuthor': isAuthor,
            'time': time,
            'author_id': author_id,
            'author': MyUser.objects.get(user_id=author_id).nickname if author_id > 0 else "Anonymous"
        }))

    def get_user_image_url(self, user):

        if user.myuser.photo:
            image = '/media/' + str(user.myuser.photo)
        elif user.myuser.identity == "T":
            image = '/static/image/default.png'
        else:
            image = '/static/image/default1.png'
        return image

    # Receive client enter from room group
    async def client_enter(self, event):
        await self.send(text_data=json.dumps(event))

    # Receive client leave from room group
    async def client_leave(self, event):
        print(event)
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_myuser(self):
        return MyUser.objects.get(user_id=self.user.id) if self.user.is_authenticated else None

    def get_username(self):
        return self.myuser.nickname if self.user.is_authenticated else "Anonymous"

    @database_sync_to_async
    def return_to_current_list_and_add_to_db(self):

        s = []
        for current_user in self.room_object.myuser_set.all():
            d = {}
            d['image'] = self.get_user_image_url(current_user.user)
            d['id'] = current_user.user.id
            d['name'] = current_user.nickname
            s.append(d)

        # add
        self.myuser.chat_room.add(self.room_object)
        return s

    @database_sync_to_async
    def delete_from_db(self):
        self.myuser.chat_room.remove(self.room_object)

    @database_sync_to_async
    def save_group(self):
        return ChatRoomGroup.objects.get_or_create(name=self.room_group_name)[0]

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

        s = []
        for i in ChatRoomGroup.objects.get(name=self.room_group_name).chathistory_set.all():
            d = {}
            d["message"] = i.history
            d['image'] = self.get_user_image_url(
                i.user.user) if i.user else '/static/image/default.png'
            d["author_id"] = i.user.user.id if i.user else 0
            d["isAuthor"] = "1" if self.user.is_authenticated and self.myuser == i.user else "0"
            d["time"] = i.time.strftime('%Y-%m-%d %H:%M:%S')
            d["author"] = i.user.nickname if i.user else "Anonymous"
            s.append(d)
        return s


class FriendConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = self.scope['url_route']['kwargs']['myuser_id']
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        wait_for_reply_list = RequestReplyFriend.objects.filter(reply_user_id=self.user.myuser.id)
        for o in wait_for_reply_list:
            await self.send(text_data=json.dumps({
                'request_person': o.request_user.nickname,
                'request_person_id': o.request_user.id,
                'type': "request_add_friend",
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket, send it to corresponding group
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # if the user confirms becoming friends, make them friend in the database
        request_person_id = text_data_json['request_person']
        reply_person_id = text_data_json['reply_person']
        if (text_data_json['type'] == "agree_add_friend"):
            await  self.make_friends(request_person_id, reply_person_id)
            await self.delete_request_from_db(request_person_id, reply_person_id)
        if (text_data_json['type'] == "request_add_friend"):
            await self.add_request_to_db(request_person_id, reply_person_id)
        await self.channel_layer.group_send(
            str(text_data_json['group']),
            text_data_json
        )

    # Receive request_add_friend message from group
    # Send it to the frontend of this user for confirmation
    async def request_add_friend(self, event):
        request_person = await self.get_myuser(event['request_person'])

        await self.send(text_data=json.dumps({
            'request_person': request_person.nickname,
            'request_person_id': request_person.id,
            'type': "request_add_friend",
        }))

    # Receive agree_add_friend message from group
    # Send back to the frontend of this request user
    async def agree_add_friend(self, event):
        reply_person = await self.get_myuser(event['reply_person'])
        await self.send(text_data=json.dumps({
            'reply_person': reply_person.nickname,
            'reply_person_id': reply_person.id,
            'type': "agree_add_friend",

        }))

    @database_sync_to_async
    def get_myuser(self, id):
        return MyUser.objects.get(id=id) if self.user.is_authenticated else None

    @database_sync_to_async
    def make_friends(self, request_person_id, reply_person_id):
        request_person = MyUser.objects.get(id=request_person_id)
        reply_person = MyUser.objects.get(id=reply_person_id)
        request_person.friend.add(reply_person)

    @database_sync_to_async
    def add_request_to_db(self, request_person_id, reply_person_id):
        RequestReplyFriend(request_user_id=request_person_id, reply_user_id=reply_person_id).save()

    @database_sync_to_async
    def delete_request_from_db(self, request_person_id, reply_person_id):
        RequestReplyFriend.objects.filter(request_user_id=request_person_id, reply_user_id=reply_person_id).delete()
