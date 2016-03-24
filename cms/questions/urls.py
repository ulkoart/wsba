#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from cms.questions.views import QuestionListView, QuestionDetailView, QuestionCreateView
from cms.questions.views import QuestionUpdateView, QuestionDeleteView

urlpatterns = [
    url(r'^$', login_required(QuestionListView.as_view()), name='questions_list'),
    url(r'^page/(?P<page>[0-9]+)/$', login_required(QuestionListView.as_view()), name='questions_list_paginated'),
    url(r'^(?P<question>[0-9]+)/$', login_required(QuestionDetailView.as_view()), name='questions_detail'),
    url(r'^(?P<question>[0-9]+)/edit$', login_required(QuestionUpdateView.as_view()), name='questions_edit'),
    url(r'^(?P<question>[0-9]+)/delete$', login_required(QuestionDeleteView.as_view()), name='questions_delete'),
    url(r'^new/$', login_required(QuestionCreateView.as_view()), name='questions_add'),
]
