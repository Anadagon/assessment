import datetime
import pickle

from django import forms
from django.db import models
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError

from assessment.models import Survey, Result, Choice, Question, Answer


class ResultCreateForm(forms.ModelForm):

    def __init__(self, survey, user, started_on, *args, **kwargs):
        super(ResultCreateForm, self).__init__(*args, **kwargs)
        self.user = user      # required for the save method.
        self.survey = survey  # required for the save method.
        self.started_on = started_on  # required for the save method.
        for question in survey.question_set.all():
            if question.question_type == Question.TRUEFALSE or question.question_type == Question.MULTICHOICE or question.question_type == Question.RANGE:
                self.fields.insert(len(self.fields), str(question.id),
                           forms.ModelChoiceField(queryset=Choice.objects.filter(
                               question=question), widget=forms.RadioSelect(), empty_label=None, required=False, help_text=question.question_name))
                self.fields[str(question.id)].label = str(question)
            elif question.question_type == Question.DISPOSITION:
                for choice in question.choice_set.all():
                    self.fields[str(question.id) + choice.choice_value] = forms.CharField(help_text=choice.question.question_name, max_length=3, label=choice.choice_value,
                        required=False, widget=forms.TextInput(attrs={'size': '1', 'id': str(question.id) + choice.choice_value}))
            elif question.question_type == Question.TEXT:
                self.fields.insert(len(self.fields), str(question.id),
                           forms.CharField(widget=forms.Textarea(attrs={'class': "col-md-12", 'rows': 30}), required=False, help_text=question.question_name))
                self.fields[str(question.id)].label = str(question)
            elif question.question_type == Question.EXTERNAL:
                self.fields.insert(len(self.fields), str(question.id),
                           forms.CharField(required=False))
                self.fields[str(question.id)].label = str(question)
            elif question.question_type == Question.MULTISELECT:
                self.fields.insert(len(self.fields), str(question.id),
                           forms.ModelMultipleChoiceField(queryset=Choice.objects.filter(
                               question=question), widget=forms.CheckboxSelectMultiple(), required=False, help_text=question.question_name))
                self.fields[str(question.id)].label = str(question)

    def clean(self):
        cleaned_data = super(ResultCreateForm, self).clean()
        for question in self.survey.question_set.all():
            if question.question_type == Question.DISPOSITION:
                answer_string = ''
                answer_sum = 0
                for choice in question.choice_set.all():
                    try:
                        answer_string += choice.choice_value + ':' + str(cleaned_data.get(str(question.id) + choice.choice_value)) + ', '
                        answer_sum += int(cleaned_data.get(str(question.id) + choice.choice_value))
                    except ValueError:
                        raise ValidationError("Enter Numeric values, write zeros for blank answers")
                if answer_string is not '':
                    if answer_sum != question.question_sum:
                        raise ValidationError("Questions which ask for numerical values must sum to " + str(question.question_sum))
                self.cleaned_data[str(question.id)] = answer_string
        return self.cleaned_data

    def save(self, *args, **kwargs):
        """
        Django has already validated all the answers at this point.
        """
        instance = super(ResultCreateForm, self).save(commit=False)
        instance.user = self.user
        instance.survey = self.survey
        total_score = 0
        for question in self.survey.question_set.all():
            if question.question_type == Question.TRUEFALSE or question.question_type == Question.MULTICHOICE:
                for choice in question.choice_set.all():
                    if choice == self.cleaned_data[str(question.id)]:
                        total_score += choice.weight
            elif question.question_type == Question.MULTISELECT:
                for choice in question.choice_set.all():
                    if choice in self.cleaned_data[str(question.id)]:
                        total_score += choice.weight
        instance.started_on = self.started_on
        instance.score = "%s" % total_score
        instance.excess_seconds = 0
        if self.survey.minutes_allowed > 0:
            delta = datetime.datetime.now() - datetime.datetime.strptime(self.started_on, "%Y-%m-%d %H:%M:%S.%f")
            delta = delta.days * 86400 + delta.seconds
            if delta > 60 * self.survey.minutes_allowed:
                instance.excess_seconds = delta - 60 * self.survey.minutes_allowed
        instance.save()

        # bulk_create Answer Objects start here!
        response_id = instance.id                                       # 1. grab the id of the newly created response.
        start_ans_id = response_id * 1000                               # 2. Multiply by 1000. This is the initial answer id. 1000 because no survey will be that long
        end_ans_id = start_ans_id + self.survey.question_set.count()    # 3. survey_instance.question_set.count() has the amount of questions
        ans_ids = list(range(start_ans_id, end_ans_id))                 # 4. Generate a list over which to iterate,
        q_answers = []
        for question in self.survey.question_set.all():
            if self.cleaned_data[str(question.id)]:
                cleaned_answer = self.cleaned_data[str(question.id)]
                if not isinstance(cleaned_answer, models.Model) and not isinstance(cleaned_answer, str):
                    choices_list = [cleaned_answer.choice_value for cleaned_answer in cleaned_answer]
                    cleaned_answer = ', '.join(choices_list)
                q_answers.append(cleaned_answer)
            else:
                q_answers.append("No Response")
        zipped = zip(ans_ids, self.survey.question_set.all(), q_answers) # Zip it so we can create Answer instances.
        data = [Answer(id=answer_id,          # the data is actually a list of answers_instances.
                       result=instance,       # They will be committed to disk on the bulk_create() method.
                       question=question_obj,
                       answer=ans_value) for answer_id, question_obj, ans_value in zipped]
        Answer.objects.bulk_create(data) #used Bulk_create to save IO resources
        return instance

    class Meta:
        model = Result
        fields = '__all__'


class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """Check that at least one service has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        cleaned_data = self.cleaned_data
        if not any(cleaned_data):
            for cleaned_data in self.cleaned_data:
                raise forms.ValidationError('At least one item required.')