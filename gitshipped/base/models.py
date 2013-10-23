import logging

from urlparse import urljoin, urlparse
from urllib import urlencode

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.db import models

import constance.config
import requests


def _github_url(path, params=None, base='https://api.github.com'):
    params = params and params or dict()
    client_id = constance.config.GITHUB_API_ID
    if not client_id:
        client_id = getattr(settings, 'GITHUB_API_ID', '')
    client_secret = constance.config.GITHUB_API_SECRET
    if not client_secret:
        client_secret = getattr(settings, 'GITHUB_API_SECRET', '')
    params.update(client_id=client_id, client_secret=client_secret)
    return '%s?%s' % (urljoin(base, path), urlencode(params))


def _github_GET(path, params=None, base='https://api.github.com'):
    url = _github_url(path, params, base)
    return requests.get(url)


class Project(models.Model):

    title = models.CharField(max_length=255, default='', blank=True)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=255, default='', blank=True)
    github_path = models.CharField(max_length=255)
    
    owner = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    def add_deployment(self, commit_hash, notes=None):
        deployment = Deployment(project=self, commit_hash=commit_hash,
                                notes=notes)
        deployment.save()
        return deployment


class Deployment(models.Model):
    project = models.ForeignKey(Project)
    commit_hash = models.CharField(max_length=64)

    notes = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)


class GithubCompare(models.Model):
    project = models.ForeignKey(Project)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)


class GithubCommit(models.Model):
    project = models.ForeignKey(Project)
    commit_hash = models.CharField(max_length=64)

    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)
