from django.conf.urls import patterns, url

from assessment import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='assessment_index'),
    url(r'^login/$', views.user_login, name='assessment_login'),
    url(r'^welcome/$', views.landing_page, name='assessment_landpage'),
    url(r'^logout/$', views.user_logout, name='assessment_logout'),
    url(r'^registration/$', views.user_registration, name='assessment_registration'),
    url(r'^users/$', views.user_list, name='assessment_users'),
    url(r'^users/(\d+)$', views.user_results, name='assessment_results'),
    url(r'^users/delete/(\d+)$', views.user_delete, name='assessment_deleteuser'),
    url(r'^surveys/$', views.SurveyListView.as_view(), name='assessment_surveys'),
    url(r'^surveys/(?P<slug>[-\w]+)/$', views.ResultCreateView.as_view(), name='assessment_survey'),
    url(r'^surveys/results/(?P<pk>\d+)/$', views.ResultDetailView.as_view(), name='survey_results'),
    url(r'^results/$', views.ResultListView.as_view(), name="result_list"),
    url(r'^results/(?P<slug>[-\w]+)/$', views.SurveyResultListView.as_view(), name="survey_result_list"),
    url(r'^user/(?P<pk>\d+)/results/$', views.UserResultListView.as_view(), name='user_results'),
    url(r'^authenticate/(?P<profile_token>.+)$', views.user_authenticate, name='assessment_authenticate'),
)
