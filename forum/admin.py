from django.contrib import admin
from forum.models import Category, Question, Answer, Comment, Tag


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'inviting_person', 'is_top')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'reply_author', 'content')


class CommentAdmin(admin.ModelAdmin):
    fields = ['from_user', 'to_user', 'like_user', 'dislike_user', 'text', 'is_public', 'is_anonymous']
    filter_horizontal = ('like_user','dislike_user')


class TagAdmin(admin.ModelAdmin):
    fields = ['tag','from_user', 'to_user']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
