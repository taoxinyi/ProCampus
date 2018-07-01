from django.urls import reverse_lazy
from utils.mixin import AjaxableResponseMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from announcement.models import Announcement
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin


class AnnouncementCreateView(AjaxableResponseMixin, UserPassesTestMixin, CreateView):
    """
    Announcement View
    """
    model = Announcement
    fields = ['content']
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('announcement-list')

    def test_func(self):
        """
        a test function
        :return: boolean; whether the user is staff
        """
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """
        add active-page string to context
        :param kwargs:
        :return:context
        """
        context = super(AnnouncementCreateView, self).get_context_data(**kwargs)
        context['active_page'] = 'announcement-add'
        return context

    def form_valid(self, form):
        """
        return form valid
        :param form: form
        :return:form_valid
        """
        form.instance.author = self.request.user
        return super(AnnouncementCreateView, self).form_valid(form)


class AnnouncementListView(UserPassesTestMixin, ListView):
    """
    Announcement List View
    """
    model = Announcement
    context_object_name = 'announcement_list'

    def test_func(self):
        """
        a test function
        :return: boolean; whether the user is staff
        """
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """
        add active-page string to context
        :param kwargs:
        :return:context
        """
        context = super(AnnouncementListView, self).get_context_data(**kwargs)
        context['active_page'] = 'announcement-list'
        return context


class AnnouncementUpdateView(AjaxableResponseMixin, UserPassesTestMixin, UpdateView):
    """
    Announcement Update View
    """
    model = Announcement
    context_object_name = 'announcement'
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('announcement-list')
    fields = ['content']

    def test_func(self):
        """
        a test function
        :return: boolean; whether the user is staff
        """

    def get_context_data(self, **kwargs):
        """
        add active-page string to context
        :param kwargs:
        :return:context
        """
        context = super(AnnouncementUpdateView, self).get_context_data(**kwargs)
        context['active_page'] = 'announcement-update'
        return context


class AnnouncementDeleteView(AjaxableResponseMixin, UserPassesTestMixin, DeleteView):
    """
    Announcement Delete View
    """
    model = Announcement
    success_url = reverse_lazy('announcement-list')

    def test_func(self):
        """
        a test function
        :return: boolean; whether the user is staff
        """
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        """
        after post delete
        :param request:
        :param args:
        :param kwargs:
        :return: post success status
        """
        super(AnnouncementDeleteView, self).post(request, *args, **kwargs)
        return JsonResponse({'state': 'success'})
