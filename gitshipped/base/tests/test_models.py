import logging
import json
import urllib
import urlparse

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

import mock

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
    @mock.patch('requests.get')
    def test_github_get(self, mock_requests_get):
        
        # Set up to simulate API requests / responses
        inputs = dict(status_code=200, headers={}, content='')
        outputs = {}
        def my_requests_get(url, headers=None, timeout=None):
            outputs['url'] = url
            outputs['headers'] = headers
            if inputs['content'] is not None:
                content = inputs['content']
            else:
                content = json.dumps(dict(objects=[
                    {"email": inputs['email'],
                     "is_vouched": inputs['vouched']}
                ]))

            return FakeResponse(
                status_code=200,
                headers={},
                content=content,
                json=lambda: {} #json.loads(content)
            )
        mock_requests_get.side_effect = my_requests_get

        url = _github_url('repos/mozilla/kuma')
        logging.debug("URL %s" % url)
        ok_('client_id=%s' % FAKE_ID in url)
        ok_('client_secret=%s' % FAKE_SECRET in url)

        resp = _github_GET('repos/mozilla/kuma')
        logging.debug("RESP %s" % resp.json())

        ok_(False, 'play')

    def test_play(self):
        eq_(4, 2+2)
        ok_(False, 'play')
