# chat/consumers.py
import datetime
import os

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from authentication.models import MyUser
from chat.models import ChatRoomGroup, ChatHistory
from channels.db import database_sync_to_async
import protobuf.chat_message_pb2 as ChatMessage
import protobuf.notification_message_pb2 as Notification
import json

from forum.models import RequestReplyFriend, Tag, Comment


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.myuser = self.user.myuser
        self.username = self.get_username()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.room_object = await self.save_group()

        self.file_size = 0
        self.current_size = 0
        self.filename = ""
        self.current_bytes = b""
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # get serialized history and send to this client
        s = await  self.get_history()
        await self.send(bytes_data=s)
        # send to all clients in this group about this client's arrival
        chat_message = ChatMessage.ChatMessage()
        chat_message.type = ChatMessage.ChatMessage.CLIENT_ENTER
        chat_message_item = ChatMessage.ChatMessageItem()
        chat_message_item.clientId = self.user.id
        chat_message_item.clientName = self.user.myuser.nickname
        chat_message_item.imageUrl = self.get_user_image_url(self.user)
        chat_message.chat_message_item.extend([chat_message_item])
        b = chat_message.SerializeToString()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_enter',
                'protobuf': b

            }
        )
        await self.add_current_user_to_db()

    async def disconnect(self, close_code):
        # Leave room group
        chat_message = ChatMessage.ChatMessage()
        chat_message.type = ChatMessage.ChatMessage.CLIENT_LEAVE
        chat_message_item = ChatMessage.ChatMessageItem()
        chat_message_item.clientId = self.user.id
        chat_message_item.clientName = self.user.myuser.nickname
        chat_message.chat_message_item.extend([chat_message_item])
        b = chat_message.SerializeToString()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_leave',
                'protobuf': b
            })
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.delete_from_db()

    # Receive message from WebSocket
    async def receive(self, bytes_data):
        chat_message_item = ChatMessage.ChatMessageItem()
        try:
            chat_message_item.ParseFromString(bytes_data)
            if chat_message_item.fileSize > 0:
                self.file_size = chat_message_item.fileSize
                self.current_size = 0
                self.filename = chat_message_item.fileName
            else:
                chat_message_item.timeStamp = int(datetime.datetime.now().timestamp())
                bytes_data = chat_message_item.SerializeToString()

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'chat_message',
                     'protobuf': bytes_data}
                )
                await  self.save_history(chat_message_item.message)
        except Exception:
            self.current_size += len(bytes_data)
            self.current_bytes += bytes_data

            if self.current_size == self.file_size:
                directory = os.path.join("media", "user", str(self.myuser.id))
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file_rename = self.filename.split('.')[0] + \
                              datetime.datetime.now().strftime("_%Y%m%d%H%M%S.") + \
                              self.filename.split('.')[1] \
                    if '.' in self.filename else self.filename + datetime.datetime.now().strftime(
                    "_%Y%m%d%H%M%S")

                file_url = os.path.join(directory, file_rename)
                test_file = open(file_url, "wb")
                test_file.write(self.current_bytes)
                test_file.close()
                await self.save_history(is_file=True, file_name=self.filename, file_size=self.file_size,
                                        file_url=file_url)
                self.current_bytes = b""
                self.current_size = ""
                chat_message_item.timeStamp = int(datetime.datetime.now().timestamp())
                chat_message_item.clientId = self.user.id
                chat_message_item.fileName = self.filename
                chat_message_item.fileSize = self.file_size
                chat_message_item.fileUrl = file_url
                bytes_data = chat_message_item.SerializeToString()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'chat_message',
                     'protobuf': bytes_data}
                )

    # Receive message from room group
    async def chat_message(self, event):
        chat_message_item = ChatMessage.ChatMessageItem()
        chat_message_item.ParseFromString(event['protobuf'])
        author_id = chat_message_item.clientId
        if author_id == 0:
            image = '/static/image/default.png'
        else:
            image = self.get_user_image_url(User.objects.get(id=author_id))
        chat_message_item.imageUrl = image
        chat_message_item.clientName = MyUser.objects.get(user_id=author_id).nickname if author_id > 0 else "Anonymous"
        chat_message = ChatMessage.ChatMessage()
        # which is default
        chat_message.type = 0
        chat_message.chat_message_item.extend([chat_message_item])
        b = chat_message.SerializeToString()
        # Send message to WebSocket
        await self.send(bytes_data=b)

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
        await self.send(bytes_data=event['protobuf'])

    # Receive client leave from room group
    async def client_leave(self, event):
        await self.send(bytes_data=event['protobuf'])

    @database_sync_to_async
    def get_myuser(self):
        return MyUser.objects.get(user_id=self.user.id) if self.user.is_authenticated else None

    def get_username(self):
        return self.myuser.nickname if self.user.is_authenticated else "Anonymous"

    @database_sync_to_async
    def add_current_user_to_db(self):

        self.myuser.chat_room.add(self.room_object)

    @database_sync_to_async
    def delete_from_db(self):
        self.myuser.chat_room.remove(self.room_object)

    @database_sync_to_async
    def save_group(self):
        return ChatRoomGroup.objects.get_or_create(name=self.room_group_name)[0]

    @database_sync_to_async
    def save_history(self, history=None, is_file=False, file_name=None, file_size=None, file_url=None):

        group = ChatRoomGroup.objects.get(name=self.room_group_name)
        if (is_file):
            ChatHistory.objects.create(room_group=group, user=self.myuser, file_name=file_name,
                                       file_size=file_size, file_url=file_url)
        else:
            ChatHistory.objects.create(room_group=group, history=history, user=self.myuser)

    @database_sync_to_async
    def get_history(self):
        chat_message = ChatMessage.ChatMessage()
        chat_message.type = ChatMessage.ChatMessage.CHAT_MESSAGE
        for i in ChatRoomGroup.objects.get(name=self.room_group_name).chathistory_set.all():
            chat_message_item = chat_message.chat_message_item.add()
            if i.file_size:
                chat_message_item.fileName = i.file_name
                chat_message_item.fileUrl = i.file_url
                chat_message_item.fileSize = i.file_size
            else:
                try:
                    chat_message_item.message = i.history
                except Exception:
                    chat_message_item.message = ""
            chat_message_item.clientId = i.user.user.id if i.user else 0
            chat_message_item.imageUrl = self.get_user_image_url(
                i.user.user) if i.user else '/static/image/default.png'
            chat_message_item.timeStamp = int(i.time.timestamp())
            chat_message_item.clientName = i.user.nickname if i.user else "Anonymous"
        for current_user in self.room_object.myuser_set.all():
            current_client = chat_message.current_client.add()
            current_client.imageUrl = self.get_user_image_url(current_user.user)
            current_client.clientId = current_user.user.id
            current_client.clientName = current_user.nickname
        return chat_message.SerializeToString()


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = self.scope['url_route']['kwargs']['myuser_id']
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        wait_for_reply_list = RequestReplyFriend.objects.filter(reply_user_id=self.user.myuser.id)

        notification = Notification.Notification()
        list_notification_item = []
        for o in wait_for_reply_list:
            notification_item = Notification.NotificationItem()
            notification_item.type = Notification.NotificationItem.REQUEST_ADD_FRIEND
            notification_item.fromClientId = o.request_user.id
            notification_item.fromClientName = o.request_user.nickname
            from_client = await self.get_myuser(notification_item.fromClientId)
            notification_item.imageUrl = self.get_user_image_url(from_client)
            list_notification_item.append(notification_item)
        notification.notification_item.extend(list_notification_item)
        s = notification.SerializeToString()

        await self.send(bytes_data=s)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket, send it to corresponding group
    async def receive(self, bytes_data):
        notification_item = Notification.NotificationItem()
        notification_item.ParseFromString(bytes_data)
        print(notification_item)
        # if the user confirms becoming friends, make them friend in the database
        request_person_id = notification_item.fromClientId
        reply_person_id = notification_item.toClientId
        if notification_item.type == Notification.NotificationItem.AGREE_ADD_FRIEND:
            await  self.make_friends(request_person_id, reply_person_id)
            await self.delete_request_from_db(request_person_id, reply_person_id)
            notification_type = "agree_add_friend"
            group_id = str(request_person_id)

        elif notification_item.type == Notification.NotificationItem.REQUEST_ADD_FRIEND:
            await self.add_request_to_db(request_person_id, reply_person_id)
            notification_type = "request_add_friend"
            group_id = str(reply_person_id)

        elif notification_item.type == Notification.NotificationItem.DISAGREE_ADD_FRIEND:
            await self.delete_request_from_db(request_person_id, reply_person_id)
            notification_type = "disagree_add_friend"
            group_id = str(request_person_id)

        elif notification_item.type == Notification.NotificationItem.REQUEST_DELETE_FRIEND:
            await  self.delete_friends(request_person_id, reply_person_id)
            notification_type = "request_delete_friend"
            group_id = str(reply_person_id)

        elif notification_item.type == Notification.NotificationItem.ADD_TAG:
            await  self.add_tag_to_db(request_person_id, reply_person_id, notification_item.tag)
            notification_type = "add_tag"
            group_id = str(reply_person_id)

        elif notification_item.type == Notification.NotificationItem.ADD_COMMENT:
            is_public = notification_item.isPublic
            is_anonymous = notification_item.isAnonymous
            await  self.add_comment_to_db(request_person_id, reply_person_id, notification_item.text, is_public,
                                          is_anonymous)
            notification_type = "add_comment"
            group_id = str(reply_person_id)

        elif notification_item.type == Notification.NotificationItem.LIKE_COMMENT:
            await self.save_comment(notification_item.commentId, request_person_id, True)
            notification_type = "like_comment"
            group_id = str(reply_person_id)
        elif notification_item.type == Notification.NotificationItem.DISLIKE_COMMENT:
            await self.save_comment(notification_item.commentId, request_person_id, False)
            notification_type = "dislike_comment"
            group_id = str(reply_person_id)

        elif notification_item.type == Notification.NotificationItem.CANCEL_LIKE_COMMENT:
            await self.cancel_comment(notification_item.commentId, request_person_id, True)
            notification_type = "cancel_dislike_comment"
            group_id = str(reply_person_id)
        elif notification_item.type == Notification.NotificationItem.CANCEL_DISLIKE_COMMENT:
            await self.cancel_comment(notification_item.commentId, request_person_id, False)
            notification_type = "cancel_dislike_comment"
            group_id = str(reply_person_id)
            # group send to the reply person group
        await self.channel_layer.group_send(
            group_id,
            {
                'type': notification_type,
                'protobuf': bytes_data
            })

        # Receive request_add_friend message from group
        # Send it to the frontend of this user for confirmation

    async def request_add_friend(self, event):
        bytes_data = event['protobuf']
        notification_item = Notification.NotificationItem()
        notification_item.ParseFromString(bytes_data)
        request_person = await self.get_myuser(notification_item.fromClientId)
        notification_item.fromClientName = request_person.nickname
        notification_item.fromClientId = request_person.user.id
        notification_item.imageUrl = self.get_user_image_url(request_person)
        notification = Notification.Notification()
        notification.notification_item.extend([notification_item])
        print(notification)
        s = notification.SerializeToString()
        await self.send(bytes_data=s)

    # Receive agree_add_friend message from group
    # Send back to the frontend of this request user
    async def agree_add_friend(self, event):
        bytes_data = event['protobuf']
        notification_item = Notification.NotificationItem()
        notification_item.ParseFromString(bytes_data)
        reply_person = await self.get_myuser(notification_item.toClientId)
        notification_item.toClientName = reply_person.nickname
        notification_item.toClientId = reply_person.user.id

        notification_item.imageUrl = self.get_user_image_url(reply_person)
        notification = Notification.Notification()
        notification.notification_item.extend([notification_item])
        print(notification)

        s = notification.SerializeToString()
        await self.send(bytes_data=s)

    # Receive disagree_add_friend message from group
    # Send back to the frontend of this request user
    async def disagree_add_friend(self, event):
        bytes_data = event['protobuf']
        notification_item = Notification.NotificationItem()
        notification_item.ParseFromString(bytes_data)
        reply_person = await self.get_myuser(notification_item.toClientId)
        notification_item.toClientName = reply_person.nickname
        notification_item.toClientId = reply_person.user.id
        notification_item.imageUrl = self.get_user_image_url(reply_person)
        notification = Notification.Notification()
        notification.notification_item.extend([notification_item])
        print(notification)

        s = notification.SerializeToString()
        await self.send(bytes_data=s)

    # Receive request_delete_friend message from group
    # Send it to the frontend of this user for confirmation
    async def request_delete_friend(self, event):
        bytes_data = event['protobuf']
        notification_item = Notification.NotificationItem()
        notification_item.ParseFromString(bytes_data)
        request_person = await self.get_myuser(notification_item.fromClientId)
        notification_item.fromClientName = request_person.nickname
        notification_item.fromClientId = request_person.user.id
        notification_item.imageUrl = self.get_user_image_url(request_person)
        notification = Notification.Notification()
        notification.notification_item.extend([notification_item])
        print(notification)

        s = notification.SerializeToString()
        await self.send(bytes_data=s)

    def get_user_image_url(self, myuser):

        if myuser.photo:
            image = '/media/' + str(myuser.photo)
        elif myuser.identity == "T":
            image = '/static/image/default.png'
        else:
            image = '/static/image/default1.png'
        return image

    @database_sync_to_async
    def get_myuser(self, id):
        return MyUser.objects.get(id=id) if self.user.is_authenticated else None

    @database_sync_to_async
    def save_comment(self, comment_id, myuser_id, is_like):
        comment = Comment.objects.get(id=comment_id)
        myuser = MyUser.objects.get(id=myuser_id)
        if is_like:
            comment.like_user.add(myuser)
            comment.dislike_user.remove(myuser)
        else:
            comment.dislike_user.add(myuser)
            comment.like_user.remove(myuser)
        comment.save()

    @database_sync_to_async
    def cancel_comment(self, comment_id, myuser_id, is_original_like):
        comment = Comment.objects.get(id=comment_id)
        myuser = MyUser.objects.get(id=myuser_id)
        if is_original_like:
            comment.like_user.remove(myuser)
        else:
            comment.dislike_user.remove(myuser)
        comment.save()

    @database_sync_to_async
    def make_friends(self, request_person_id, reply_person_id):
        request_person = MyUser.objects.get(id=request_person_id)
        reply_person = MyUser.objects.get(id=reply_person_id)
        request_person.friend.add(reply_person)

    @database_sync_to_async
    def delete_friends(self, request_person_id, reply_person_id):
        request_person = MyUser.objects.get(id=request_person_id)
        reply_person = MyUser.objects.get(id=reply_person_id)
        request_person.friend.remove(reply_person)

    @database_sync_to_async
    def add_request_to_db(self, request_person_id, reply_person_id):
        RequestReplyFriend(request_user_id=request_person_id, reply_user_id=reply_person_id).save()

    @database_sync_to_async
    def delete_request_from_db(self, request_person_id, reply_person_id):
        RequestReplyFriend.objects.filter(request_user_id=request_person_id, reply_user_id=reply_person_id).delete()

    @database_sync_to_async
    def add_tag_to_db(self, request_person_id, reply_person_id, tag_list):
        for tag in tag_list:
            query_result = Tag.objects.all().filter(from_user_id=request_person_id, to_user_id=reply_person_id,
                                                    tag=tag)
            if len(query_result) == 0:
                Tag(from_user_id=request_person_id, to_user_id=reply_person_id, tag=tag).save()
            else:
                query_result.delete()

    @database_sync_to_async
    def add_comment_to_db(self, request_person_id, reply_person_id, comment, is_public, is_anonymous):
        Comment(from_user_id=request_person_id, to_user_id=reply_person_id, text=comment, is_public=is_public,
                is_anonymous=is_anonymous).save()
