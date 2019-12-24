"""
sentry_wechat.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 by Jerry hu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import

import time
import json
import requests
import logging
import six
import sentry
import sentry_wechat

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sentry.exceptions import PluginError
from sentry.plugins.bases.notify import NotificationPlugin
from sentry.http import is_valid_url, safe_urlopen
from sentry.utils.safe import safe_execute

from sentry.utils.http import absolute_uri
from django.core.urlresolvers import reverse

def validate_urls(value, **kwargs):
    output = []
    for url in value.split('\n'):
        url = url.strip()
        if not url:
            continue
        if not url.startswith(('http://', 'https://')):
            raise PluginError('Not a valid URL.')
        if not is_valid_url(url):
            raise PluginError('Not a valid URL.')
        output.append(url)
    return '\n'.join(output)

# https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2-xxxx
class WechatForm(forms.Form):
    urls = forms.CharField(
        label=_('Wechat robot url'),
        widget=forms.Textarea(attrs={
            'class': 'span6', 'placeholder': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2'}),
        help_text=_('Enter Wechat robot url.'))

    def clean_url(self):
        value = self.cleaned_data.get('url')
        return validate_urls(value)

 
class WechatPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to Wechat.
    """
    author = 'jerry hu'
    author_url = 'https://github.com/jerryhu1234/sentry-wechat'
    version = sentry_wechat.VERSION
    description = "Integrates wechat robot."
    resource_links = [
        ('Bug Tracker', 'https://github.com/jerryhu1234/sentry-wechat/issues'),
        ('Source', 'https://github.com/jerryhu1234/sentry-wechat'),
        ('README', 'https://github.com/jerryhu1234/sentry-wechat/blob/master/README.md'),
    ]

    slug = 'Wechat'
    title = 'Wechat'
    conf_title = title
    conf_key = slug

    project_conf_form = WechatForm
    timeout = getattr(settings, 'SENTRY_WECHAT_TIMEOUT', 3)
    logger = logging.getLogger('sentry.plugins.wechat')

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('urls', project))

    def get_webhook_urls(self, project):
        url = self.get_option('urls', project)
        if not url:
            return ''
        return url

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        url = self.get_webhook_urls(group.project)
        title = u"New alert from {}".format(event.project.slug)
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": u"#### {title} \n > {message} [href]({url})".format(
                    title=title,
                    message=event.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.id),
                )
            }
        }
        requests.post(
            url=url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8")
        )
