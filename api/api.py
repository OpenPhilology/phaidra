from __future__ import unicode_literals
# coding: utf8
from phaidra import settings

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf import settings
from django.contrib.auth.models import User
from app.models import Textbook, Unit, Lesson, Slide

from tastypie import fields
from tastypie.resources import ModelResource

import json
import random
from random import shuffle

import time

class TextbookResource(ModelResource):
	class Meta:
		queryset = Textbook.objects.all()
		resource_name = 'textbook'
		allowed_methods = ['get']

class UnitResource(ModelResource):
	class Meta:
		queryset = Unit.objects.all()
		resource_name = 'unit'
		allowed_methods = ['get']

class LessonResource(ModelResource):
	class Meta:
		queryset = Lesson.objects.all()
		resource_name = 'lesson'
		allowed_methods = ['get']

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		allowed_methods = ['get']

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		fields = ['username', 'first_name', 'last_name', 'last_login']
