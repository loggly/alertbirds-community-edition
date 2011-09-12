import logging

import tornado.web

from lib.loggly import Loggly
from models.alert import AlertManager, Alert
from models.savedsearch import SavedSearchManager
from models.user import UserManager

class AlertAPIHandler(tornado.web.RequestHandler):
    def get(self, subdomain, action = None, alert_id = None):
        alert = AlertManager.get_alert(alert_id)
        if action == 'mute':
            alert.muted = True
            alert.put()
        elif action == 'unmute':
            alert.muted = False
            alert.put()
        if action == 'enable':
            alert.active = True
            alert.put()
        if action == 'disable':
            alert.active = False
            alert.put()
        if action == 'getssurl':
            saved_search = SavedSearchManager.get_saved_search(alert.saved_search)
            self.write(Loggly.build_search_url(saved_search.context, alert.threshold_time_secs))
        elif action == 'delete':
            alert.delete()
