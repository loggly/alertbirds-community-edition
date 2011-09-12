from google.appengine.ext import db
from google.appengine.api import users as google_users

from django.utils import simplejson as json

class EndpointManager():
    @staticmethod
    def get_endpoint(endpoint_id, email = None):
        if not email:
            email = google_users.get_current_user().nickname()
        return db.GqlQuery('SELECT FROM Endpoint WHERE email = :1 AND __key__ = :2 LIMIT 1', 
            email, db.Key(endpoint_id))[0]

    @staticmethod
    def get_all_endpoints(email = None):
        if not email:
            email = google_users.get_current_user().nickname()
        return db.GqlQuery('SELECT * FROM Endpoint WHERE email = :1', email)

class Endpoint(db.Model):
    email = db.StringProperty()
    subdomain = db.StringProperty()
    provider = db.StringProperty()
    description = db.StringProperty()
    service_key = db.StringProperty()
    alert_text = db.StringProperty()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return json.dumps({'id': unicode(self.key()),
                           'email': self.email,
                           'subdomain': self.subdomain,
                           'provider': self.provider,
                           'description': self.description,
                           'service_key': self.service_key,
                           'alert_text': self.alert_text})
