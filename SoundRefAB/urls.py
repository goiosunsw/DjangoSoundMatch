from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^main/$', views.MainView, name='main'),
    url(r'^index/$', views.ScenarioListView.as_view(), name='list'),
    url(r'^(?P<subject_id>[0-9]+)/sound/$', views.SoundPage, name='soundpage'),
    url(r'^(?P<subject_id>[0-9]+)/soundadj/$', views.SoundAdjustPage, name='soundadjustpage'),
    url(r'^(?P<subject_id>[0-9]+)/soundintro/$', views.SoundIntro, name='intropage'),
    url(r'^(?P<subject_id>[0-9]+)/multicomment/$', views.SoundIntro, name='multicommentpage'),
    url(r'^(?P<trial_id>[0-9]+)/process/$', views.ProcessPage, name='process'),
    url(r'^(?P<trial_id>[0-9]+)/processadj/$', views.ProcessAdjustPage, name='processadj'),
    url(r'^(?P<trial_id>[0-9]+)/processintro/$', views.ProcessIntro, name='processintro'),
    url(r'^(?P<trial_id>[0-9]+)/processcomment/$', views.ProcessComment, name='processcomment'),
    url(r'^(?P<subject_id>[0-9]+)/next/$', views.NextExp, name='next'),
    url(r'^(?P<subject_id>[0-9]+)/text/(?P<page_id>[0-9]+)$', views.TextPage, name='textpage'),
    url(r'^(?P<subject_id>[0-9]+)/thanks/$', views.ThanksPage, name='thanks'),
    url(r'^(?P<pk>[0-9]+)/new/$', views.NewSubjectView, name='new'),
    url(r'^(?P<pk>[0-9]+)/subjectdata/$', views.SubjectQuestionnaireUpdate.as_view(), name='subjectupdate'),
    url(r'^subjects/$', views.SubjectList.as_view(), name='subjectlist'),
    url(r'^subject_detail/(?P<pk>[0-9]+)$', views.SubjectDetail.as_view(), name='subjectdetail'),
    url(r'^scenario_results/(?P<pk>[0-9]+)$', views.ScenarioResults.as_view(), name='scenarioresults'),
    url(r'^final_comments/(?P<pk>[0-9]+)$', views.CommentList, name='finalcomments'),
]
