"""
sentry_wechat.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 by Jerry hu, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import time
import json
import requests
import logging
import six
import sentry

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sentry.exceptions import PluginError
from sentry.plugins.bases import notify
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
class WechatForm(notify.NotificationConfigurationForm):
    urls = forms.CharField(
        label=_('Wechat robot url'),
        widget=forms.Textarea(attrs={
            'class': 'span6', 'placeholder': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2'}),
        help_text=_('Enter Wechat robot url.'))

    def clean_url(self):
        value = self.cleaned_data.get('url')
        return validate_urls(value)

 
class WechatPlugin(notify.NotificationPlugin):
    author = 'jerry hu'
    author_url = 'https://github.com/jerryhu1234/sentry-wechat'
    version = wechat.VERSION
    description = "Integrates wechat robot."
    resource_links = [
        ('Bug Tracker', 'https://github.com/jerryhu1234/sentry-wechat/issues'),
        ('Source', 'https://github.com/jerryhu1234/sentry-wechat'),
    ]

    slug = 'wechat'
    title = 'wechat'
    conf_title = title
    conf_key = 'wechat'  

    project_conf_form = WechatForm
    timeout = getattr(settings, 'SENTRY_WECHAT_TIMEOUT', 3) 
    logger = logging.getLogger('sentry.plugins.wechat')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('urls', project))

    def get_config(self, project, **kwargs):
        return [{
            'name': 'urls',
            'label': 'wechat robot url',
            'type': 'textarea',
            'help': 'Enter wechat robot url.',
            'placeholder': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2',
            'validators': [validate_urls],
            'required': False
        }] 

    def get_webhook_urls(self, project):
        url = self.get_option('urls', project)
        if not url:
            return ''
        return url 

    def send_webhook(self, url, payload):
        return safe_urlopen(
            url=url,
            json=payload,
            timeout=self.timeout,
            verify_ssl=False,
        )

    def get_group_url(self, group):
        return absolute_uri(reverse('sentry-group', args=[
            group.team.slug,
            group.project.slug,
            group.id,
        ]))

    def notify_users(self, group, event, fail_silently=False): 
        url = self.get_webhook_urls(group.project)
        link = self.get_group_url(group)
        message_format = '[%s] %s   %s'
        message = message_format % (event.server_name, event.message, link)
        # data = {"msgtype": "text",
        #             "text": {
        #                 "content": message
        #             }
        #         }
        data = {
                "msgtype": "text",
                "text": {
                "content": "hello world"
                }
        }
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)