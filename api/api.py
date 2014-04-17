from __future__ import unicode_literals
# coding: utf8
from phaidra import settings
from tastypie.bundle import Bundle
from django.contrib.webdesign.lorem_ipsum import sentence

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf import settings

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key
from django.middleware.csrf import _sanitize_token, constant_time_compare

from django.contrib.auth.models import User
from app.models import Textbook, Unit, Lesson, Slide
from django.utils.text import slugify

from tastypie import fields
from tastypie.authentication import BasicAuthentication, SessionAuthentication, MultiAuthentication, Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest

import json
import random
from random import shuffle

import time

class TextbookResource(ModelResource):
	class Meta:
		queryset = Textbook.objects.all()
		resource_name = 'textbook'
