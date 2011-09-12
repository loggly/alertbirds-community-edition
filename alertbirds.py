#!/usr/bin/env python

import base64
import os
import sys
import uuid

# for tornado
sys.path.append(os.path.join(os.path.dirname(__file__), 'contrib'))
# for config
sys.path.append(os.path.join(os.path.dirname(__file__), 'etc'))

import tornado.web
import tornado.wsgi
import wsgiref.simple_server

from models.user import UserManager, User

from controllers.main import *
from controllers.alert import *
from controllers.savedsearch import *
from controllers.endpoint import *
from controllers.cron import *
from controllers.api.alert import *
from controllers.api.savedsearch import *
from controllers.api.endpoint import *

# cookie secret from http://groups.google.com/group/python-tornado/browse_thread/thread/9ea50651adee1150
settings = {
    'title': u'Alert Birds',
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'xsrf_cookies': True,
    'cookie_secret': base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
    'autoescape': None,
    'debug': True
}

application = tornado.wsgi.WSGIApplication([
    (r'/', MainHandler),
    (r'/(.*)/api/alert/(.*)/(.*)/?', AlertAPIHandler),
    (r'/(.*)/api/alert/(.*)/?', AlertAPIHandler),
    (r'/(.*)/api/alert/?', AlertAPIHandler),
    (r'/(.*)/api/savedsearch/(.*)/(.*)/?', SavedSearchAPIHandler),
    (r'/(.*)/api/savedsearch/(.*)/?', SavedSearchAPIHandler),
    (r'/(.*)/api/savedsearch/?', SavedSearchAPIHandler),
    (r'/(.*)/api/endpoint/(.*)/(.*)/?', EndpointAPIHandler),
    (r'/(.*)/api/endpoint/(.*)/?', EndpointAPIHandler),
    (r'/(.*)/api/endpoint/?', EndpointAPIHandler),
    (r'/(.*)/alert/(.*)/(.*)/?', AlertHandler),
    (r'/(.*)/alert/(.*)/?', AlertHandler),
    (r'/(.*)/alert/?', AlertHandler),
    (r'/(.*)/savedsearch/(.*)/(.*)/?', SavedSearchHandler),
    (r'/(.*)/savedsearch/(.*)/?', SavedSearchHandler),
    (r'/(.*)/savedsearch/?', SavedSearchHandler),
    (r'/(.*)/endpoint/(.*)/(.*)/?', EndpointHandler),
    (r'/(.*)/endpoint/(.*)/?', EndpointHandler),
    (r'/(.*)/endpoint/?', EndpointHandler),
    (r'/cron/(.*)/(.*)/?', CronHandler),
    (r'/(.*)/?', MainHandler) # must be last
], **settings)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
