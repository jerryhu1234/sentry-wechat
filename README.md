sentry-wechat
===============

Install sentry plugins

pip install git+https://github.com/jerryhu1234/sentry-wechat.git
 
Sentry sending Wetchat.

https://github.com/getsentry/sentry/blob/9774d33134368cbd87445837a6087f1ba5c689aa/src/sentry/plugins/sentry_webhooks/plugin.py

eg wechat format:
```
New alert from [onlinebooking-fe],please pay attention to it.
environment: production
level: error
logger: None
This is an example Python exception raven.scripts.runner in main href
```
