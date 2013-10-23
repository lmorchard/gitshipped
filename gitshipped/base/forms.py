from django import forms
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import UserChangeForm

from django.utils.translation import ugettext_lazy as _

from .models import UserProfile

