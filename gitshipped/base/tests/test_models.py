import os
import os.path
import logging
import json
import urllib
import urlparse

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

import mock
import uritemplate

from django.conf import settings, UserSettingsHolder
from django.utils.functional import wraps
from django.db import models
from django.contrib.auth.models import User, Group
from django import test
from django.core.cache import cache

from . import (FakeResponse, override_constance_settings, override_settings)

from ..models import (_github_url, _github_GET,
                      Project, Deployment,
                      GithubCommit, GithubCompare)

FAKE_ID = 'FAKE_ID'
FAKE_SECRET = 'FAKE_SECRET'


def _load_json(path):
    fn = os.path.join(os.path.dirname(__file__),
                      'fixtures', '%s.json' % path)
    return json.loads(open(fn, 'rb').read())


def mock_get(status_code=200, headers=None, content='', data=None):
    # Set up to simulate API requests / responses
    headers = headers and headers or {}
    inputs = dict(status_code=status_code, headers=headers,
                  content=content, data=data)
    outputs = {}
    def get_fn(url, headers=None, timeout=None):
        outputs['url'] = url
        outputs['headers'] = headers
        if inputs['data']:
            data = inputs['data']
            content = json.dumps(inputs['data'])
        elif inputs['content'] is not None:
            data = None
            content = inputs['content']
        else:
            data = None
            content = ''
        return FakeResponse(
            status_code=status_code,
            headers=headers,
            content=content,
            json=lambda: data
        )
    return (get_fn, inputs, outputs)


class GithubDataTests(test.TestCase):

    def setup(self):

        self.group = Group(name='Kuma')
        self.group.save()

        self.owner = User.objects.create_user(
            'auto_tester', 'auto_tester@example.com', 'auto_tester')

        self.project = Project(
            title = 'Kuma',
            description = 'The Django project that powers MDN',
            url = 'https://developer.mozilla.org',
            github_path = 'mozilla/kuma',
            owner = self.owner,
            group = self.group,
        )
        self.project.save()

    @override_constance_settings(
        GITHUB_API_ID = FAKE_ID,
        GITHUB_API_SECRET = FAKE_SECRET)
    def test_github_url(self):
        url = _github_url('repos/mozilla/kuma')
        ok_('client_id=%s' % FAKE_ID in url)
        ok_('client_secret=%s' % FAKE_SECRET in url)

    @override_constance_settings(
        GITHUB_API_ID = FAKE_ID,
        GITHUB_API_SECRET = FAKE_SECRET)
    @mock.patch('requests.get')
    def test_github_get(self, mock_requests_get):
        (mock_requests_get.side_effect, _, _) = mock_get(
            data = _load_json('repos_mozilla_kuma')
        )
        resp = _github_GET('repos/mozilla/kuma')
        data = resp.json()

        ok_('kuma', data['name'])
        ok_('mozilla/kuma', data['full_name'])
