# coding=utf-8
from django.contrib.auth import logout, login
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, RedirectView, FormView, ListView, UpdateView, TemplateView
from django.urls import reverse_lazy

from announcement.models import Announcement
from forum.models import Category
from website.mixin import FrontMixin
from django.contrib.auth.models import User
from authentication.models import MyUser
from .forms import LoginForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class SignupView(FrontMixin, CreateView):
    """
    The View when the user click signup
    """
    model = MyUser
    fields = ['nickname', 'identity', 'photo']
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('user-login')

    def form_valid(self, form):
        """
        When the user submit the form and it's valid.
        :param form: the form from the frontend
        :return: super
        """
        username = form.data.get('username', '')
        password = form.data.get('password', '')
        email = form.data.get('email', '')
        if User.objects.filter(username=username):
            return render(self.request, 'utils/error_page.html', {'message': '该用户名已被占用'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        form.instance.user = user
        return super(SignupView, self).form_valid(form)

    def form_invalid(self, form):
        """
        When the user submit the form and it's not valid.
        :param form: the form from the frontend
        :return: super
        """
        print(form.errors)
        context = {'message': form.errors, 'announcement': Announcement.objects.all()[0],
                   'category_list': Category.objects.annotate(question_num=Count('question')).order_by('name')}
        return render(self.request, 'utils/error_page.html', context)


class LogoutView(RedirectView):
    """
    The View when the user click logout
    return to home page
    """
    pattern_name = 'homepage'

    def get_redirect_url(self, *args, **kwargs):
        """
        return to home page
        :param args:
        :param kwargs:
        :return:
        """
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


class LoginView(FrontMixin, FormView):
    """
    The view when the user click login
    """
    template_name = 'authentication/user_login.html'
    success_url = reverse_lazy('homepage')
    form_class = LoginForm

    def form_valid(self, form):
        """
        If the form vaild, check database first and redirect to previous page
        :param form:
        :return:
        """
        user = form.login()
        if user is not None:
            if user.is_active:
                login(self.request, user)
                try:
                    # after login, redirecting to previous page
                    next_page = self.request.GET['next']
                    return HttpResponseRedirect(next_page)
                except:
                    return super(LoginView, self).form_valid(form)


            else:
                return self.response_error_page('你的账户尚未激活')
        else:
            return self.response_error_page('用户名或密码错误')

    def response_error_page(self, msg):
        """
        return error page
        :param msg: the error message
        :return: rendered view of error page
        """
        context = {'message': msg, 'announcement': Announcement.objects.all()[0],
                   'category_list': Category.objects.annotate(question_num=Count('question')).order_by('name')}
        return render(self.request, 'utils/error_page.html', context)


class UserListView(UserPassesTestMixin, ListView):
    """
    The view of User list
    """
    login_url = reverse_lazy('user-login')
    model = MyUser
    paginate_by = 30
    context_object_name = 'user_list'
    template_name = 'authentication/user_list.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['active_page'] = 'myuser-list'
        return context


class UserPhotoChangeView(LoginRequiredMixin, FrontMixin, UpdateView):
    """
    The view when the user want to change photo
    """
    login_url = reverse_lazy('user-login')
    success_url = reverse_lazy('homepage')
    template_name = 'authentication/photo_change_form.html'
    fields = ['photo']
    model = MyUser

    def form_valid(self, form):
        """
        if form vaild and the id is the same, change photo for the user
        :param form:
        :return:
        """
        if int(self.kwargs['pk']) != self.request.user.myuser.id:
            return self.response_error_page('权限错误')
        return super(UserPhotoChangeView, self).form_valid(form)

    def response_error_page(self, msg):
        """
        show error page
        :param msg: error msg
        :return:
        """
        return render(self.request, 'utils/error_page.html', {'message': msg, 'myuser': self.request.user.myuser})
