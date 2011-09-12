import tornado.web

from django.utils import simplejson as json

from wtforms import Form, BooleanField, TextField, validators, SelectField, SelectMultipleField, IntegerField, HiddenField
from wtforms.validators import Required, Regexp

from google.appengine.api import users as google_users

import config
from lib.loggly import Loggly
import lib.oauth
from lib.multidict import MultiDict

from models.alert import AlertManager, Alert
from models.user import UserManager
from models.savedsearch import SavedSearchManager, SavedSearch

from page import PageHandler

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

class SavedSearchHandler(PageHandler):
    def get(self, subdomain, method = None, id = None):
        args = self.template_args
        if method == 'create':
            args['form'] = SavedSearchForm() 
        else:
            savedsearch = SavedSearchManager.get_saved_search(id)
            args['form'] = SavedSearchForm(savedsearch = savedsearch)
        args['id'] = id
        args['method'] = method
        args['subdomain'] = subdomain
        self.render('savedsearch.html', **args)
