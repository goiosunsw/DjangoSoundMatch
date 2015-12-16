from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index/$', views.ScenarioListView.as_view(), name='list'),
    url(r'^(?P<subject_id>[0-9]+)/sound/$', views.SoundPage, name='soundpage'),
    url(r'^(?P<subject_id>[0-9]+)/next/$', views.NextExp, name='next'),
    url(r'^(?P<subject_id>[0-9]+)/soundadj/$', views.SoundPage, name='soundadjustpage'),
    url(r'^(?P<subject_id>[0-9]+)/thanks/$', views.ThanksPage, name='thanks'),
    url(r'^(?P<trial_id>[0-9]+)/process/$', views.ProcessPage, name='process'),
    url(r'^(?P<trial_id>[0-9]+)/processadj/$', views.ProcessAdjustPage, name='processadj'),
    url(r'^(?P<pk>[0-9]+)/new/$', views.NewSubjectView.as_view(), name='new'),
    url(r'^subjects/$', views.SubjectList.as_view(), name='subjectlist'),
    url(r'^subject_detail/(?P<pk>[0-9]+)$', views.SubjectDetail.as_view(), name='subjectdetail'),
]
