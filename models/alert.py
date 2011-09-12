import hashlib

from google.appengine.ext import db
from google.appengine.api import users as google_users

from django.utils import simplejson as json

class AlertManager(object):
    @staticmethod
    def get_alert(alert_id, email = None):
        if not email:
            email = google_users.get_current_user().nickname()
        return db.GqlQuery('SELECT FROM Alert WHERE email = :1 AND __key__ = :2 LIMIT 1', 
            email, db.Key(alert_id))[0]

    @staticmethod
    def get_all_alerts_systemwide(prefix=None):
        result = db.GqlQuery('SELECT * FROM Alert')
        if prefix:
            alerts = []
            for alert in result:
                if hashlib.md5(unicode(alert.key())).hexdigest().startswith(prefix):
                    alerts.append(alert)
            return alerts
        else:
            return result

    @staticmethod
    def get_all_alerts(subdomain):
        return db.GqlQuery('SELECT * FROM Alert WHERE email = :1 AND subdomain = :2', google_users.get_current_user().nickname(), subdomain)

class Alert(db.Model):
    email = db.StringProperty()
    subdomain = db.StringProperty()
    name = db.StringProperty()
    description = db.TextProperty()
    saved_search = db.IntegerProperty()
    active = db.BooleanProperty()
    threshold_operator = db.StringProperty()
    threshold_count = db.IntegerProperty()
    threshold_time_secs = db.IntegerProperty()
    endpoint = db.StringProperty()
    state = db.StringProperty(choices=set(['C', 'N'])) # 'C'ritical, 'N'ormal
    last_run = db.IntegerProperty()
    last_state_change = db.IntegerProperty()
    sound = db.StringProperty()
    muted = db.BooleanProperty()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return json.dumps({'id': unicode(self.key()),
                           'email': self.email,
                           'subdomain': self.subdomain,
                           'name': self.name,
                           'description': self.description,
                           'saved_search': self.saved_search,
                           'active': self.active,
                           'threshold_operator': self.threshold_operator,
                           'threshold_count': self.threshold_count,
                           'threshold_time_secs': self.threshold_time_secs,
                           'endpoint': self.endpoint,
                           'state': self.state,
                           'last_run': self.last_run,
                           'last_state_change': self.last_state_change,
                           'sound': self.sound,
                           'muted': self.muted})
