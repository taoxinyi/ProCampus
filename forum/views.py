import datetime
import json
import re

import arrow as arrow
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView

from forum.mixin import UserInfoMixin
from forum.models import Category, Question, Answer, Star
from utils.mixin import AjaxableResponseMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import JsonResponse, Http404
from website.mixin import FrontMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from authentication.models import MyUser


class CategoryCreateView(UserPassesTestMixin, AjaxableResponseMixin, CreateView):
    login_url = reverse_lazy('user-login')
    model = Category
    fields = ['name']
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('category-list')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        context['active_page'] = 'category-add'
        return context


class CategoryListView(UserPassesTestMixin, ListView):
    login_url = reverse_lazy('user-login')
    model = Category
    context_object_name = 'category_list'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['active_page'] = 'category-list'
        return context


class CategoryUpdateView(UserPassesTestMixin, AjaxableResponseMixin, UpdateView):
    login_url = reverse_lazy('user-login')
    model = Category
    context_object_name = 'category'
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('category-list')
    fields = ['name']

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        context['active_page'] = 'category-update'
        return context


class CategoryDeleteView(UserPassesTestMixin, AjaxableResponseMixin, DeleteView):
    login_url = reverse_lazy('user-login')
    model = Category
    success_url = reverse_lazy('category-list')

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        super(CategoryDeleteView, self).post(request, *args, **kwargs)
        return JsonResponse({'state': 'success'})


class QuestionCreateView(LoginRequiredMixin, FrontMixin, CreateView):
    login_url = reverse_lazy('user-login')
    model = Question
    template_name_suffix = '_create_form'
    fields = ['title', 'content', 'category', 'inviting_person', 'is_top']

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['teacher_list'] = MyUser.objects.filter(identity='T').order_by('nickname')
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.show_times = 0
        return super(QuestionCreateView, self).form_valid(form)

    def get_success_url(self):
        questions_list = Question.objects.filter(author=self.request.user).order_by('-publish_time')
        least_question = questions_list[0]
        return reverse('question-detail', kwargs={'pk': least_question.id})


class CategoryQuestionListView(FrontMixin, ListView):
    template_name = 'website/frontend/homepage.html'
    model = Question
    paginate_by = 10
    context_object_name = 'question_list'

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryQuestionListView, self).get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        context['question_list_top'] = Question.objects.filter(category=category, is_top=True)
        context['question_list'] = Question.objects.filter(category=category, is_top=False)
        print("he1re")

        return context


class QuestionDetailView(FrontMixin, ListView):
    model = Answer
    template_name = 'forum/question_detail.html'
    paginate_by = 10
    context_object_name = 'answer_list'

    def get_queryset(self):
        question = Question.objects.get(pk=self.kwargs['pk'])
        question.show_times += 1
        question.save()
        return Answer.objects.filter(question=question).order_by('-publish_time').reverse()

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(*args, **kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context


class AnswerCreateView(LoginRequiredMixin, FrontMixin, CreateView):
    model = Answer
    template_name = 'forum/answer_create_form.html'
    fields = ['content']
    login_url = reverse_lazy('user-login')

    def get_context_data(self, *args, **kwargs):
        context = super(AnswerCreateView, self).get_context_data(*args, **kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('question-detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.question = Question.objects.get(pk=self.kwargs['pk'])
        return super(AnswerCreateView, self).form_valid(form)


class ReplyCreateView(LoginRequiredMixin, FrontMixin, CreateView):
    model = Answer
    template_name = 'forum/reply_create_form.html'
    fields = ['content']
    login_url = reverse_lazy('user-login')

    def get_context_data(self, *args, **kwargs):
        context = super(ReplyCreateView, self).get_context_data(*args, **kwargs)
        context['answer'] = Answer.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        answer = Answer.objects.get(pk=self.kwargs['pk'])

        return reverse('question-detail', kwargs={'pk': answer.question.pk})

    def form_valid(self, form):
        answer = Answer.objects.get(pk=self.kwargs['pk'])
        question = answer.question
        form.instance.author = self.request.user
        form.instance.question = question
        form.instance.reply_author = answer.author.myuser

        return super(ReplyCreateView, self).form_valid(form)


class QuestionListView(UserPassesTestMixin, ListView):
    model = Question
    login_url = reverse_lazy('user-login')
    context_object_name = 'question_list'
    template_name = 'forum/question_list.html'

    def test_func(self):
        return self.request.user.is_staff


class QuestionDeleteView(UserPassesTestMixin, AjaxableResponseMixin, DeleteView):
    login_url = reverse_lazy('user-login')
    model = Question
    success_url = reverse_lazy('question-list')

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        super(QuestionDeleteView, self).post(request, *args, **kwargs)
        return JsonResponse({'state': 'success'})


class PersonalQuestionListView(LoginRequiredMixin, FrontMixin, ListView, UserInfoMixin):
    login_url = reverse_lazy('user-login')
    paginate_by = 10
    template_name = 'forum/question_weight2.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.filter(author_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(PersonalQuestionListView, self).get_context_data(**kwargs)
        the_user = MyUser.objects.get(user_id=self.kwargs['pk'])
        current_user = MyUser.objects.get(user_id=self.request.user.id)
        context['theuser'] = the_user
        context['currentuser'] = current_user
        context['isSelf'] = False
        context['isFriend'] = False
        # all of the user's tag and count
        # sample output
        # <QuerySet [{'count': 3, 'tag': 'good'}, {'count': 1, 'tag': 'bad'}]>
        context['all_tag_dict'] = list(the_user.tag_to_user.all(). \
                                       values('tag').annotate(count=Count('tag')).order_by('-count'))
        # all of  current user's tag about this user
        # sample output
        # < QuerySet[{'tag': 'good'}, {'tag': 'smart'}] >
        context['selected_tag_list'] = list(
            current_user.tag_from_user.all().filter(to_user_id=the_user.id).values('tag'))
        context['theuser_category_list'] = self.get_most_category(the_user)
        if the_user.id == current_user.id:
            context['isSelf'] = True
        elif the_user in current_user.friend.all():
            context['isFriend'] = True
        context['question_list'] = Question.objects.filter(author_id=self.kwargs['pk'])
        context['last_time'] = arrow.get(the_user.user.last_login).humanize(locale="zh")
        return context


class PersonalAnswerListView(FrontMixin, ListView, UserInfoMixin):
    paginate_by = 10
    template_name = 'forum/answer_weight.html'
    context_object_name = 'question_asked_list'

    def get_queryset(self):
        answers = Answer.objects.filter(author_id=self.kwargs['pk'])
        question_asked_list = list(set([item.question for item in answers]))
        question_asked_list.reverse()
        return question_asked_list

    def get_context_data(self, *args, **kwargs):
        context = super(PersonalAnswerListView, self).get_context_data(**kwargs)
        self.the_user = the_user = MyUser.objects.get(user_id=self.kwargs['pk'])
        current_user = MyUser.objects.get(user_id=self.request.user.id)
        context['theuser'] = the_user
        context['currentuser'] = current_user
        context['isSelf'] = False
        context['isFriend'] = False
        # all of the user's tag and count
        # sample output
        # <QuerySet [{'count': 3, 'tag': 'good'}, {'count': 1, 'tag': 'bad'}]>
        context['all_tag_dict'] = list(the_user.tag_to_user.all(). \
                                       values('tag').annotate(count=Count('tag')).order_by('-count'))
        # all of  current user's tag about this user
        # sample output
        # < QuerySet[{'tag': 'good'}, {'tag': 'smart'}] >
        context['selected_tag_list'] = list(
            current_user.tag_from_user.all().filter(to_user_id=the_user.id).values('tag'))
        context['theuser_category_list'] = self.get_most_category(the_user)
        if the_user.id == current_user.id:
            context['isSelf'] = True
        elif the_user in current_user.friend.all():
            context['isFriend'] = True
        context['question_list'] = Question.objects.filter(author_id=self.kwargs['pk'])
        context['last_time'] = arrow.get(the_user.user.last_login).humanize(locale="zh")
        return context


class QuestionSearchView(FrontMixin, ListView):
    paginate_by = 10
    template_name = 'website/frontend/homepage.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.filter(title__contains=self.request.GET.get('keyword', ''))


class PersonalInvitingListView(FrontMixin, ListView):
    paginate_by = 10
    template_name = 'website/frontend/homepage.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Question.objects.filter(inviting_person=MyUser.objects.get(pk=self.kwargs['pk']))


class PersonalReplyListView(FrontMixin, ListView):
    paginate_by = 10
    template_name = 'forum/reply_weight.html'
    context_object_name = 'reply_list'

    def get_queryset(self):
        return Answer.objects.filter(reply_author=MyUser.objects.get(pk=self.kwargs['pk'])).order_by('-publish_time')


class FriendView(LoginRequiredMixin, FrontMixin, TemplateView):
    login_url = reverse_lazy('user-login')
    template_name = 'forum/friend_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FriendView, self).get_context_data(**kwargs)
        context['friend_list'] = MyUser.objects.get(user_id=self.request.user.id).friend.all().order_by()
        return context


class UserInfoView(LoginRequiredMixin, FrontMixin, ListView, UserInfoMixin):
    login_url = reverse_lazy('user-login')
    template_name = 'forum/user_info.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def get_queryset(self):
        self.theuser = MyUser.objects.get(user_id=self.kwargs['pk'])
        the_user = MyUser.objects.get(user_id=self.kwargs['pk'])
        current_user = MyUser.objects.get(user_id=self.request.user.id)
        return_list = []
        comment_list = the_user.comment_to_user.all().order_by('-time').filter(
            Q(is_public=True) | (Q(is_public=False) & Q(
                from_user_id=current_user.id))) if the_user.id != current_user.id else the_user.comment_to_user.all().order_by(
            '-time')
        for comment in comment_list:
            return_list.append({"pk": comment.id, "text": self.convert_to_html(comment.text),
                                "author": "匿名" if comment.is_anonymous
                                else MyUser.objects.get(id=comment.from_user_id).nickname,
                                "author_id": 0 if comment.is_anonymous else MyUser.objects.get(
                                    id=comment.from_user_id).user_id,
                                "time": arrow.get(comment.time).humanize(locale="zh"),
                                "like_user_count": comment.like_user.count(),
                                "dislike_user_count": comment.dislike_user.count(),
                                "is_like": current_user in comment.like_user.all(),
                                "is_dislike": current_user in comment.dislike_user.all(),
                                "is_author": comment.from_user_id == current_user.id,
                                "is_private": not comment.is_public}

                               )
        if self.request.GET.get('type', 'count') == 'count':
            """
            if sorted by total like & dislike count then change the return_list
            """
            return_list = sorted(return_list, key=lambda k: k['like_user_count'] + k['dislike_user_count'],
                                 reverse=True)
        return return_list

    def get_context_data(self, *args, **kwargs):
        context = super(UserInfoView, self).get_context_data(**kwargs)
        the_user = MyUser.objects.get(user_id=self.kwargs['pk'])
        current_user = MyUser.objects.get(user_id=self.request.user.id)
        context['theuser'] = the_user
        context['currentuser'] = current_user
        context['isSelf'] = False
        context['isFriend'] = False
        # Get the all star evaluation of this user
        context['average_star'], context['star_count_list'] = self.get_star_average_and_count_list(the_user.id)
        try:
            context['previous_star'] = Star.objects. \
                filter(from_user_id=current_user.id, to_user_id=the_user.id)[0].value
        except:
            context['previous_star'] = 0
        print(context['average_star'], context['star_count_list'])
        # all of the user's tag and count
        # sample output
        # <QuerySet [{'count': 3, 'tag': 'good'}, {'count': 1, 'tag': 'bad'}]>
        context['all_tag_dict'] = list(the_user.tag_to_user.all(). \
                                       values('tag').annotate(count=Count('tag')).order_by('-count'))
        # all of  current user's tag about this user
        # sample output
        # < QuerySet[{'tag': 'good'}, {'tag': 'smart'}] >
        context['selected_tag_list'] = list(
            current_user.tag_from_user.all().filter(to_user_id=the_user.id).values('tag'))
        context['theuser_category_list'] = self.get_most_category(the_user)
        if the_user.id == current_user.id:
            context['isSelf'] = True
        elif the_user in current_user.friend.all():
            context['isFriend'] = True
        context['question_list'] = Question.objects.filter(author_id=self.kwargs['pk'])
        context['last_time'] = arrow.get(the_user.user.last_login).humanize(locale="zh")
        context['pagination_type'] = self.request.GET.get('type', 'count')

        print(context['pagination_type'])
        return context

    def get_star_average_and_count_list(self, to_user_id):
        """

        :param to_user_id: the user who receives the star
        :return: average score of star, 0 if total count is 0
                 list of star count of length 5
                 e.g. [1,2,5,6,2] means the value of 1,2,3,4,5 is 1,2,5,6,2 respectfully
        """
        all_star_list = list(
            Star.objects.filter(to_user_id=to_user_id).values('value').annotate(
                count=Count('value')).order_by('value')
        )
        star_count_list = [0, 0, 0, 0, 0]
        total_sum = 0
        total_count = 0
        for d in all_star_list:
            value = d['value']
            count = d['count']
            star_count_list[value - 1] = count
            total_sum += value * count
            total_count += count
        return total_sum / total_count if total_count != 0 else 0, star_count_list
