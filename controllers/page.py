from google.appengine.api import users as google_users

import config

from request import RequestHandler

class PageHandler(RequestHandler):
    template_args = {'LOGOUT_URL': google_users.create_logout_url('/'),
                     'TRACKING_INPUT_URL': config.TRACKING_INPUT_URL,
                     'LOGGLY_DOMAIN': config.LOGGLY_DOMAIN,
                     'LOGS_DOMAIN': config.LOGS_DOMAIN,
                     'subdomain': ''}
