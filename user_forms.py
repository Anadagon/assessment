from django import forms
from django.contrib.auth.models import User
from assessment.models import UserProfile, Survey, Available, MAX_LENGTH
from django.contrib.auth.forms import UserCreationForm
import random, string


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class UserForm(UserCreationForm):
    username = forms.EmailField(max_length=MAX_LENGTH, label='E-mail Address')
    password1 = forms.CharField(widget=forms.HiddenInput, max_length=128, required=False, label='Password')
    password2 = forms.CharField(widget=forms.HiddenInput, max_length=128, required=False, label='Confirm Password')
    first_name = forms.CharField(max_length=MAX_LENGTH, required=True)
    last_name = forms.CharField(max_length=MAX_LENGTH, required=True)
    gender_choices = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('r', 'Rather not say'),
    )
    gender = forms.ChoiceField(widget=forms.RadioSelect, required=False, choices=gender_choices)
    phone_number = forms.CharField(required=False, max_length=200)
    job_title = forms.CharField(required=False, max_length=200)
    job_department = forms.CharField(required=False, max_length=200)
    job_location = forms.CharField(required=False, max_length=200)
    company = forms.CharField(required=False, max_length=200)
    
    def save(self, commit=False):
        user = super(UserForm, self).save(commit=False)
        password = self.cleaned_data['password1']
        if password == self.cleaned_data['password2']:
            user.set_password(password)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['username']
        user.save()
        try:
            profile = user.get_profile()
        except:
            profile = UserProfile(user=user)

        profile.gender = self.cleaned_data['gender']
        phone_number = self.cleaned_data['phone_number']
        phone_number = [s for s in phone_number if s.isdigit()]
        phone_number = ''.join(phone_number)
        profile.phone_number = phone_number
        profile.job_title = self.cleaned_data['job_title']
        profile.job_department = self.cleaned_data['job_department']
        profile.job_location = self.cleaned_data['job_location']
        profile.company = self.cleaned_data['company']
        profile.assessment_protocol = self.cleaned_data['assessment_protocol']
        profile.save()

        return user


class RegistrationForm(UserForm):
    internal_surveys = Survey.objects.filter(external_survey_url__iexact='')
    external_surveys = Survey.objects.exclude(external_survey_url__iexact='')

    def __init__(self, *args, **kwargs):   
        super(RegistrationForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(max_length=MAX_LENGTH, label='E-mail Address')
    password1 = forms.CharField(max_length=128, required=True, label='Password')
    password2 = forms.CharField(max_length=128, required=True, label='Confirm Password')
    assessment_protocol = forms.CharField(required=False, max_length=MAX_LENGTH)
    staff_choices = (
        ('t', 'Yes'),
        ('f', 'No'),
    )

    is_staff = forms.ChoiceField(widget=forms.RadioSelect, choices=staff_choices, initial='f', label='Admin')
    survey_list = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=internal_surveys, required=False)
    for survey in external_surveys:
        external_url = survey.name + '_url'
        locals()[external_url] = forms.CharField(max_length=255, label=survey.name + " url", required=False)
    
    def save(self, commit=False):
        user = super(UserForm, self).save(commit=False)
        password1 = forms.CharField(max_length=128, required=True, label='Password')
        password2 = forms.CharField(max_length=128, required=True, label='Confirm Password')
        if password1 == password2:
            password = self.cleaned_data['password1']
            user.set_password(password)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['username']
        staff = self.cleaned_data['is_staff']
        if staff != 'f':
            user.is_staff = 't'
            user.is_superuser = 't'
        user.save()
        try:
            profile = user.get_profile()
        except:
            profile = UserProfile(user=user)
        profile.gender = self.cleaned_data['gender']
        phone_number = self.cleaned_data['phone_number']
        phone_number = [s for s in phone_number if s.isdigit()]
        phone_number = ''.join(phone_number)
        profile.phone_number = phone_number
        profile.job_title = self.cleaned_data['job_title']
        profile.job_department = self.cleaned_data['job_department']
        profile.job_location = self.cleaned_data['job_location']
        profile.company = self.cleaned_data['company']
        profile.assessment_protocol = self.cleaned_data['assessment_protocol']
        profile.profile_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        profile.save()

        for survey in self.cleaned_data['survey_list']:
            s = Available(user=user, survey=survey)
            s.save()
        for survey in Survey.objects.exclude(external_survey_url__iexact=''):
            external_url = survey.name + '_url'
            if external_url in self.cleaned_data and self.cleaned_data[external_url] is not '':
                s = Available(user=user, survey=survey, url=self.cleaned_data[external_url])
                s.save()
        return user
