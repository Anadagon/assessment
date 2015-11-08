import datetime
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.sites.models import get_current_site

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from assessment.models import UserProfile, Survey, Question, Answer, Choice, Result
from assessment.user_forms import *
from assessment.survey_forms import *

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


def index(request):
    if not request.user.is_authenticated():
        return redirect('assessment:assessment_login')
    if not request.user.is_staff:
        return redirect('assessment:assessment_landpage')
    template = 'assessment/base_index.html'
    referer = request.META.get('HTTP_REFERER')
    profile = reverse('assessment:assessment_results', args=(request.user.id,))
    objects = {'referrer': referer, 'profile': profile}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


def user_login(request):
    if request.user.is_authenticated():
        if not request.user.is_staff:
            return redirect('assessment:assessment_landpage')
        else:
            return redirect('assessment:assessment_index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not user.is_staff:
                        return redirect('assessment:assessment_landpage')
                    return redirect('assessment:assessment_index')
                return redirect('assessment:assessment_login')
            return redirect('assessment:assessment_login')
    else:
        form = LoginForm()
    template = 'assessment/base_login.html'
    objects = {'form': form}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


def user_logout(request):
    logout(request)
    return redirect('assessment:assessment_login')


def user_registration(request):
    if not request.user.is_authenticated():
        return redirect('assessment:assessment_login')
    if not request.user.is_staff:
        return redirect('assessment:assessment_index')
    registered = False
    login_url = ''
    if request.method == 'POST':
        post_values = request.POST.copy()
        user_form = RegistrationForm(data=post_values)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data['password1']
            user.set_password(password)
            profile = UserProfile.objects.get(user=user)
            login_url = ''.join(['http://', get_current_site(request).domain, reverse('assessment:assessment_authenticate', args=(profile.profile_token,))])
            user.save()
            registered = True
            user_form = RegistrationForm()
        else:
            print(user_form.errors)
    else:
        user_form = RegistrationForm()
    template = 'assessment/base_registration.html'
    referer = request.META.get('HTTP_REFERER')
    if registered:
        referer = reverse('assessment:assessment_results', args=(user.id,))
    objects = {'user_form': user_form, 'registered': registered, 'referrer': referer, 'login_url': login_url}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


def user_list(request):
    if not request.user.is_authenticated():
        return redirect('assessment:assessment_login')
    if not request.user.is_staff:
        return redirect('assessment:assessment_index')
    users = User.objects.order_by('last_name').exclude(id=1)
    template = 'assessment/base_users.html'
    referer = request.META.get('HTTP_REFERER')
    objects = {'users': users, 'referrer': referer}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


def user_results(request, id):
    if not request.user.is_authenticated():
        return redirect('assessment:assessment_login')
    if not request.user.is_staff:
        if int(request.user.id) != int(id):
            return redirect('assessment:assessment_index')
    updated = False
    if not User.objects.filter(id=id):
        return redirect('assessment:assessment_users')
    user = get_object_or_404(User, pk=id)
    profile = get_object_or_404(UserProfile, user_id=id)
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        user_form.is_valid()
        try:
            user.username = user_form.cleaned_data['username']
            user.email = user_form.cleaned_data['username']
        except:
            pass
        try:
            password = user_form.cleaned_data['password1']
            user.set_password(password)
        except:
            pass
        try:
            user.first_name = user_form.cleaned_data['first_name']
        except:
            pass
        try:
            user.last_name = user_form.cleaned_data['last_name']
        except:
            pass
        user.save()
        try:
            profile.gender = user_form.cleaned_data['gender']
        except:
            pass
        try:
            phone_number = user_form.cleaned_data['phone_number']
            phone_number = [s for s in phone_number if s.isdigit()]
            phone_number = ''.join(phone_number)
            profile.phone_number = phone_number
        except:
            pass
        try:
            profile.job_title = user_form.cleaned_data['job_title']
        except:
            pass
        try:
            profile.job_department = user_form.cleaned_data['job_department']
        except:
            pass
        try:
            profile.job_location = user_form.cleaned_data['job_location']
        except:
            pass
        try:
            profile.company = user_form.cleaned_data['company']
        except:
            pass
        profile.save()
        updated = True
    user_data = dict(list(model_to_dict(user).items()) + list(model_to_dict(profile).items()))
    user_form = UserForm(initial=user_data)
    if request.user.is_staff:
        user_form.fields['password1'] = forms.CharField(max_length=128, required=False, label='Password')
        user_form.fields['password2'] = forms.CharField(max_length=128, required=False, label='Confirm Password')
    login_url = ''.join(['http://', get_current_site(request).domain, reverse('assessment:assessment_authenticate', args=(profile.profile_token,))])
    post_url = reverse('assessment:assessment_results', args=(id,))
    template = 'assessment/base_user.html'
    referer = reverse('assessment:assessment_landpage')
    surveys_next = False
    if request.user.is_staff or request.user.is_superuser:
        referer = request.META.get('HTTP_REFERER')
    if reverse('assessment:assessment_landpage') in request.META.get('HTTP_REFERER') or post_url in request.META.get('HTTP_REFERER'):
        surveys_next = True
    objects = {'userinfo': user, 'user_form': user_form, 'updated': updated, 'referrer': referer, 'post_url': post_url, 'login_url': login_url, 'surveys_next': surveys_next}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


def user_authenticate(request, profile_token):
    profile = UserProfile.objects.filter(profile_token=profile_token)[0]
    user = User.objects.filter(id=profile.user_id)[0]
    user.backend='django.contrib.auth.backends.ModelBackend'
    login(request, user)
    if not user.is_staff:
        return redirect('assessment:assessment_landpage')
    return redirect('assessment:assessment_index')


def user_delete(request, id):
    if not request.user.is_authenticated():
        return redirect('assessment:assessment_login')
    if not request.user.is_staff:
        if int(request.user.id) != int(id):
            return redirect('assessment:assessment_index')
    user = get_object_or_404(User, pk=id)
    profile = get_object_or_404(UserProfile, user_id=id)
    if profile:
        profile.delete()
    if user:
        if user.id != request.user.id:
            user.delete()
    return redirect('assessment:assessment_users')


def landing_page(request):
    profile = reverse('assessment:assessment_results', args=(request.user.id,))
    template = 'assessment/base_landpage.html'
    available_incomplete = Available.objects.filter(user_id=request.user.id)
    surveys_available = []
    for available in available_incomplete:
        surveys_available.append(available.survey)
    objects = {'profile': profile, 'assessments': surveys_available}
    context = RequestContext(request)
    return render_to_response(template, objects, context)


class SurveyListView(LoginRequiredMixin, ListView):
    template_name = 'assessment/base_surveylist.html'
    model = Survey

    def get_context_data(self, **kwargs):
        results = self.request.user.results.all()
        results = Result.objects.filter(user_id=self.request.user.id)
        results_surveys = []
        for result in results:
            results_surveys.append(result.survey)
        available_incomplete = Available.objects.filter(
            user_id=self.request.user.id).exclude(
                survey__in=results_surveys
        )
        surveys_available = []
        for available in available_incomplete:
            surveys_available.append(available.survey)
        context = super(SurveyListView, self).get_context_data(**kwargs)
        context['incomplete_available'] = reversed(surveys_available)
        context['user_results'] = results
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get_queryset(self):
        return Survey.objects.order_by('pub_date')


class UserResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'assessment/base_userresults.html'

    def get_context_data(self, **kwargs):
        context = super(UserResultListView, self).get_context_data(**kwargs)
        context['results'] = Result.objects.filter(user=self.kwargs['pk'])
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        return context


class ResultListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    model = Result
    template_name = 'assessment/base_resultlist.html'

    def get_context_data(self, **kwargs):
        context = super(ResultListView, self).get_context_data(**kwargs)
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super(ResultListView, self).get(request, *args, **kwargs)
        else:
            return redirect('assessment:assessment_surveys')


class SurveyResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'assessment/base_surveyresultlist.html'

    def get_context_data(self, **kwargs):
        context = super(SurveyResultListView, self).get_context_data(**kwargs)
        context['results'] = Result.objects.filter(
                survey__in=Survey.objects.filter(slug=self.kwargs['slug']))
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        return context


class ResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'assessment/base_surveyresult.html'

    def get_context_data(self, **kwargs):
        context = super(ResultDetailView, self).get_context_data(**kwargs)
        context['referrer'] = reverse('assessment:assessment_surveys')
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == self.request.user or self.request.user.is_staff:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            return redirect('assessment:assessment_surveys')


class ResultCreateView(LoginRequiredMixin, CreateView):
    model = Result
    template_name = 'assessment/base_survey.html'
    form_class = ResultCreateForm

    def get_form_kwargs(self):
        survey = Survey.objects.get(slug=self.kwargs['slug'])
        if survey.slug not in self.request.session:
            self.request.session[survey.slug] = str(datetime.datetime.now())
        kwargs = super(ResultCreateView, self).get_form_kwargs()
        kwargs['survey'] = survey
        kwargs['user'] = self.request.user
        kwargs['started_on'] = self.request.session[survey.slug]
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ResultCreateView, self).get_context_data(**kwargs)
        survey = Survey.objects.get(slug=self.kwargs['slug'])
        available = Available.objects.get(user_id=self.request.user.id, survey_id=survey.id)
        external_url = available.url
        user = self.request.user
        started_on = self.request.session[survey.slug]
        delta = datetime.datetime.strptime(str(datetime.datetime.now()), "%Y-%m-%d %H:%M:%S.%f") - datetime.datetime.strptime(started_on, "%Y-%m-%d %H:%M:%S.%f")
        delta = delta.days * 86400 + delta.seconds
        answer_form = ResultCreateForm(survey, user, started_on)
        zipped = zip(answer_form, survey.question_set.all())
        context['survey_form'] = zipped
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        context['survey'] = Survey.objects.get(slug=self.kwargs['slug'])
        context['seconds_allowed'] = survey.minutes_allowed * 60 - delta
        context['external_url'] = external_url
        return context

    def get(self, request, *args, **kwargs):
        survey = Survey.objects.get(slug=self.kwargs['slug'])
        
        if Result.objects.filter(
            survey=survey,
            user=self.request.user).exists():
            return redirect('assessment:assessment_surveys')
        if not Available.objects.filter(user_id=self.request.user.id, survey_id=survey.id).count():
            return redirect('assessment:assessment_surveys')
        return super(ResultCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if Result.objects.filter(
            survey=Survey.objects.get(slug=self.kwargs['slug']),
            user=self.request.user).exists():
            return redirect('assessment:assessment_surveys')
        return super(ResultCreateView, self).post(request, *args, **kwargs)