import logging
import traceback

from google.appengine.ext import db
from google.appengine.api import users as google_users

class UserManager():
    @staticmethod
    def get_current_user():
        try:
            return UserManager.get_user(google_users.get_current_user().nickname())
        except Exception, e:
            logging.error({'module': 'models.user', 'traceback': traceback.format_exc()})

    @staticmethod
    def current_user_exists():
        try:
            return UserManager.user_exists(google_users.get_current_user().nickname())
        except Exception, e:
            logging.error({'module': 'models.user', 'traceback': traceback.format_exc()})

    @staticmethod
    def get_user(email):
        result = db.GqlQuery('SELECT * FROM User WHERE email = :1 LIMIT 1', email)
        return result[0]

    @staticmethod
    def user_exists(email):
        result = db.GqlQuery('SELECT * FROM User WHERE email = :1 LIMIT 1', email)
        return result.count() > 0

class User(db.Model):
    email = db.StringProperty()
    request_token_key = db.StringProperty()
    request_token_secret = db.StringProperty()
    oauth_verifier = db.StringProperty()
    access_token_key = db.StringProperty()
    access_token_secret = db.StringProperty()
    subdomain = db.StringProperty()
    new_user = db.BooleanProperty()
