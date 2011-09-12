import logging
import urllib

from django.utils import simplejson as json

import config
import lib.oauth
from lib.loggly import Loggly

from models.user import UserManager

class SavedSearchManager(object):
    @staticmethod
    def get_saved_search(id):
        result = Loggly.get_saved_search(id)
        return SavedSearch(result['id'], result['name'], result['context'])

    @staticmethod
    def get_all_saved_searches(user = None):
        saved_searches = []
        for result in Loggly.get_all_saved_searches(user):
            saved_search = SavedSearch(result['id'], result['name'], result['context'])
            saved_searches.append(saved_search)
        return saved_searches

class SavedSearch(object):
    id = ''
    name = ''
    #context is a python dictionary, not a json string
    context = ''

    def __init__(self, id = None, name = None, context = None):
        self.id = id
        self.name = name
        self.context = context

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return json.dumps({'id': self.id, 'name': self.name, 'context': self.context})

    def put(self):
        user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)
         
        params = {}
        if self.id:
            params['id'] = self.id
        params['name'] = self.name
        params['context'] = json.dumps(self.context)

        if not self.id:
            method = 'POST'
        else:
            method = 'PUT'

        return oauth_client.make_request(token, 'http://%s.%s/api/savedsearches' % \
            (user.subdomain, config.LOGGLY_DOMAIN), method, params = params)

    def delete(self):
        user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)

        return oauth_client.make_request(token, 'http://%s.%s/api/savedsearches/%s' % \
            (user.subdomain, config.LOGGLY_DOMAIN, self.id), 'DELETE')
