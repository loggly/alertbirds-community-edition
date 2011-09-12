import logging

import tornado.web

from django.utils import simplejson as json

from wtforms import Form, BooleanField, TextField, HiddenField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import Required, Regexp

import config
from lib.loggly import Loggly
import lib.oauth
from lib.multidict import MultiDict

from models.savedsearch import SavedSearchManager, SavedSearch
from models.user import UserManager

def get_device_choices():
    devices = Loggly.get_devices() 
    device_choices = []
    for device in devices:
        device_choices.append((device['ip'], device['ip']))
    return device_choices

def get_input_choices():
    input_choices = []
    for input in Loggly.get_inputs():
        input_choices.append((input['name'], input['name']))
    return input_choices

class SavedSearchForm(Form):
    id = HiddenField('id')
    name = TextField('Name', [Required(), Regexp(r'^[a-zA-Z0-9_]+$', 0, 'Saved search names must contain only letters, numbers, and underscores.')])
    terms = TextField('Search', [Required()])
    inputs = SelectMultipleField(u'Inputs')
    devices = SelectMultipleField(u'Devices')

    def __init__(self, formdata=None, obj=None, prefix='', savedsearch=None, **kwargs):
        if savedsearch:
            kwargs.setdefault('id', savedsearch.id)
            kwargs.setdefault('name', savedsearch.name)
            kwargs.setdefault('terms', savedsearch.context['terms'])
            kwargs.setdefault('inputs', savedsearch.context['inputs']) 
            kwargs.setdefault('devices', savedsearch.context.get('devices', [])) # devices may not be in context
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.inputs.choices = get_input_choices()
        self.devices.choices = get_device_choices()

class SavedSearchAPIHandler(tornado.web.RequestHandler):
    # no easy way to pass errors to get_error_html()
    errors = None

    def get_error_html(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        return json.dumps(self.errors)

    def get(self, subdomain, action = None, id = None):
        if action == 'run':
            user = UserManager.get_current_user()
            oauth_client = lib.oauth.Client(user.subdomain)
            token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)

            saved_search = SavedSearchManager.get_saved_search(id)

            qs = Loggly.build_search_query_string(saved_search.context, self.get_argument('threshold_time_secs'))

            self.write(oauth_client.make_request(token, 'http://%s.%s/api/search/?%s' % \
                (user.subdomain, config.LOGGLY_DOMAIN, qs) , 'GET'))
        if action == 'retrieve':
            if id:
                self.write(json.dumps(Loggly.get_saved_search(id)))
            else:
                self.write(json.dumps(Loggly.get_all_saved_searches()))
        if action == 'delete':
            return self.write(SavedSearchManager.get_saved_search(id).delete())

    def post(self, subdomain, method = None, id = None):
        form = SavedSearchForm(MultiDict(self))
        if not form.validate():
            self.errors = form.errors
            raise tornado.web.HTTPError(400)
            return
        user = UserManager.get_current_user()

        if method == 'create':
            savedsearch = SavedSearch()
        else:
            savedsearch = SavedSearchManager.get_saved_search(id)

        savedsearch.name = self.get_argument('name') 
        savedsearch.context = {'terms': self.get_argument('terms'), 
                               'inputs': self.get_arguments('inputs'), 
                               'devices': self.get_arguments('devices')}

        result = savedsearch.put()
