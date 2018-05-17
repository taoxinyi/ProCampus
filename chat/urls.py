# chat/urls.py
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ChatIndexView.as_view(), name='chat_index'),
    url(r'^(?P<room_name>[^/]+)/$', views.ChatRoomView.as_view(), name='room'),
]
