from django.contrib import admin
from models import Answer, Question, Page, Test, QuestionAnswer, QuestionOnPage, PageInTest


class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 1


class QuestionOnPageInline(admin.TabularInline):
    model = QuestionOnPage
    extra = 1


class PageInTestInline(admin.TabularInline):
    model = PageInTest
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionAnswerInline, QuestionOnPageInline]


class AnswerAdmin(admin.ModelAdmin):
    inlines = [QuestionAnswerInline]


class PageAdmin(admin.ModelAdmin):
    inlines = [QuestionOnPageInline, PageInTestInline]


class TestAdmin(admin.ModelAdmin):
    inlines = [PageInTestInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Test, TestAdmin)