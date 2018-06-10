import re

import arrow

from authentication.models import MyUser
from .models import Category, Question
from django.db.models import Count


class CategoryMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(CategoryMixin, self).get_context_data(*args, **kwargs)
        context['category_list'] = Category.objects.annotate(question_num=Count('question')).order_by('name')
        return context


class UserInfoMixin(object):
    def my_replace(self, match):
        match_string = match.group()
        category = int(match_string[1])
        img_index = match.group(1)
        return '<img src="/static/emoji/%s.%s" style="width:%s0px;vertical-align:baseline">' % (
            match_string[1:-1], "gif" if category == 1 else "png", '5' if category == 5 else '3')

    def convert_to_html(self, raw_comment):
        return re.sub(r'\|\d_(\d+)\|', self.my_replace, raw_comment)

    def get_most_category(self, the_user):

        question_category_count = the_user.user.question_set.all().order_by().values(
            'category').annotate(
            Count('category'))
        answer_list = the_user.user.answer_set.select_related().order_by('-publish_time').all()
        category_count_dict = {}
        for answer in answer_list:
            try:
                category_count_dict[answer.question.category_id] += 1
            except:
                category_count_dict[answer.question.category_id] = 1
        for i in question_category_count:
            try:
                category_count_dict[i['category']] += i['category__count']
            except:
                category_count_dict[i['category']] = i['category__count']

        l = sorted(category_count_dict, key=category_count_dict.get)
        l.reverse()
        u = []
        for i in l:
            u.append(Category.objects.get(id=i))
        return u
