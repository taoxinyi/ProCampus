# chat/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from authentication.models import MyUser
from forum.models import Answer, Question
from website.mixin import FrontMixin
import json


class ChatIndexView(LoginRequiredMixin, FrontMixin, TemplateView):
    template_name = 'chat/index.html'
    login_url = reverse_lazy('user-login')

    def get_context_data(self, **kwargs):
        context = super(ChatIndexView, self).get_context_data(**kwargs)
        context['friend_list'] = self.request.user.myuser.friend.all()

        return context


class ChatRoomView(LoginRequiredMixin, FrontMixin, TemplateView):
    template_name = 'chat/room.html'
    login_url = reverse_lazy('user-login')

    def get_context_data(self, **kwargs):
        context = super(ChatRoomView, self).get_context_data(**kwargs)
        room_name = self.kwargs['room_name']
        context['room_name_json'] = mark_safe(json.dumps(room_name))
        return context
