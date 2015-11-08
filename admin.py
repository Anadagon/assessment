from django.contrib import admin
from assessment.models import Survey, Question, Choice, SurveyImage
from django.contrib.auth.models import User
from django.forms import TextInput, Textarea
from django.db import models

from copy import deepcopy


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    formfield_overrides = {models.TextField: {'widget': Textarea(attrs={'rows': 3,
                                                                        'cols': 40}), }, }


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('question_name',)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class SurveyImageInLine(admin.TabularInline):
    model = SurveyImage
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    prepopulated_fields = { "slug": ("name",),}
    fields = ['name', 'insertion', 'pub_date', 'description', 'external_survey_url', 'minutes_allowed', 'slug']
    inlines = [QuestionInline, SurveyImageInLine]
    actions = ['duplicate']

    def duplicate(self, request, queryset):
        for obj in queryset:
            obj_copy = deepcopy(obj)
            obj_copy.id = None
            obj_copy.save()

            for question in obj.question_set.all():
                question_copy = deepcopy(question)
                question_copy.id = None
                question_copy.save()
                obj_copy.question_set.add(question_copy)

                for choice in question.choice_set.all():
                    choice_copy = deepcopy(choice)
                    choice_copy.id = None
                    choice_copy.save()
                    question_copy.choice_set.add(choice_copy)
            obj_copy.save()

admin.site.unregister(User)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
