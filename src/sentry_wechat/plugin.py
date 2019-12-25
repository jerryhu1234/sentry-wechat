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

def split_urls(value):
    if not value:
        return ()
    return filter(bool, (url.strip() for url in value.splitlines()))


def validate_urls(value, **kwargs):
    urls = split_urls(value)
    if any((not u.startswith(("http://", "https://")) or not is_valid_url(u)) for u in urls):
        raise PluginError("Not a valid URL.")
    return "\n".join(urls)

# https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2-xxxx
class WechatForm(notify.NotificationConfigurationForm):
    urls = forms.CharField(
        label=_("Wechat robot url"),
        widget=forms.Textarea(
            attrs={"class": "span6", "placeholder": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2"}
        ),
        help_text=_("Enter Wechat robot url(one per line)."),
    )
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
    user_agent = "sentry-wechat/%s" % version

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('urls', project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "urls",
                "label": "Wechat robot url",
                "type": "textarea",
                "help": "Enter Wechat robot url(one per line).",
                "placeholder": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4929eab2",
                "validators": [validate_urls],
                "required": False,
            }
        ]

    def get_webhook_urls(self, project):
        return split_urls(self.get_option("urls", project))

    def send_webhook(self, url, payload):
        requests.post(
                url=url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
        )

    def get_group_data(self, group, event):
        url = self.get_webhook_urls(group.project)
        title = u"New alert from {}".format(event.project.slug)
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": u"#### {title} \n > environment: {environment} \n > level: {level} \n > logger: {logger} \n > {message} [href]({url})".format(
                    title=title,
                    environment=event.get_tag("environment"),
                    level=event.get_tag("level"),
                    logger=event.get_tag("logger"),
                    message=event.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.id),
                )
            }
        }
        return data

    def notify_users(self, group, event, *args, **kwargs):
        payload = self.get_group_data(group, event)
        for url in self.get_webhook_urls(group.project):
            send_webhook(url, payload)


