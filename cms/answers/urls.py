#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from cms.answers.views import AnswerCreateView, AnswerDeleteView, AnswerUpdateView, answer_up


urlpatterns = [
    url(r'^new/$', login_required(AnswerCreateView.as_view()), name='answers-add'),
    url(r'^(?P<answer>[0-9]+)/update/$', login_required(AnswerUpdateView.as_view()), name='answers-edit'),
    url(r'^(?P<answer>[0-9]+)/delete/$', login_required(AnswerDeleteView.as_view()), name='answers-delete'),
    url(r'^(?P<answer>[0-9]+)/up/$', answer_up, name='answers-up'),
    url(r'^(?P<answer>[0-9]+)/down/$', answer_up, name='answers-down'),
]
