import cgi
import logging

import tornado.web

from wtforms import Form, BooleanField, TextField, validators, SelectField, IntegerField, TextAreaField
from wtforms.validators import Required, NumberRange, Optional, Regexp

import config
from models.endpoint import EndpointManager
from lib.multidict import MultiDict
from models.alert import AlertManager, Alert
from models.user import UserManager
from models.savedsearch import SavedSearchManager

from page import PageHandler

def get_endpoint_choices():
    endpoints = EndpointManager.get_all_endpoints()
    endpoint_choices = []
    for endpoint in endpoints:
        endpoint_choices.append((unicode(endpoint.key()), cgi.escape(endpoint.description)))
    return endpoint_choices

def get_saved_search_choices():
    saved_searches = SavedSearchManager.get_all_saved_searches()
    saved_search_choices = []
    for saved_search in saved_searches:
        saved_search_choices.append((unicode(saved_search.id), cgi.escape(saved_search.name)))
    return saved_search_choices

class AlertForm(Form):
    name = TextField('Name', [Required()])
    description = TextAreaField('Description')
    # Can't use Required() because may be a new SS created that we don't yet know about
    saved_search = SelectField(u'Saved Search', [Required(), Regexp(r'^[0-9]+$')])
    threshold_operator = SelectField(u'Alert if...', [Required()], choices=[('gt', 'greater than'), ('lt', 'less than'), ('eq', 'equal to')])
    threshold_count = IntegerField('#events', [NumberRange(min = -1)]) # Can't use Required() because of stupid behavior that evals 0 to False
    threshold_time_secs = SelectField('Threshold(#events/time)', [Required()], \
        choices=[('300', '5 minutes'), ('600', '10 minutes'), ('900', '15 minutes'), ('1200', '20 minutes'), ('1800', '30 minutes'), ('3600', '60 minutes')])
    sound = SelectField(u'Sound', [Required()], choices=[('crow', 'crow'), ('owls', 'owls'), ('seagull', 'seagull'), ('wren', 'wren'), ('squawk', 'squawk')])
    endpoint = SelectField(u'Endpoint', [Optional()])
    
    def __init__(self, formdata=None, obj=None, prefix='', alert=None, **kwargs): 
        if alert:
            kwargs.setdefault('name', alert.name) 
            kwargs.setdefault('description', alert.description) 
            kwargs.setdefault('saved_search', alert.saved_search) 
            kwargs.setdefault('threshold_operator', alert.threshold_operator) 
            kwargs.setdefault('threshold_count', alert.threshold_count) 
            kwargs.setdefault('threshold_time_secs', alert.threshold_time_secs) 
            kwargs.setdefault('sound', alert.sound) 
            kwargs.setdefault('endpoint', alert.endpoint) 
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.saved_search.choices = get_saved_search_choices()
        self.endpoint.choices = get_endpoint_choices()

class AlertHandler(PageHandler):
    def get(self, subdomain, method = None, alert_id = None):
        args = self.template_args
        if method == 'create':
            args['form'] = AlertForm()
        else:
            alert = AlertManager.get_alert(alert_id)
            args['form'] = AlertForm(alert = alert)
        args['method'] = method
        args['subdomain'] = subdomain
        self.render('alert.html', **args)

    def post(self, subdomain, method = None, alert_id = None):
        form = AlertForm(MultiDict(self))
        if not form.validate():
            args = self.template_args
            args['form'] = form
            args['method'] = method
            args['subdomain'] = subdomain
            return self.render('alert.html', **args)
        user = UserManager.get_current_user()
        if method == 'create':
            alert = Alert()
        else:
            alert = AlertManager.get_alert(alert_id)
        alert.email = user.email
        alert.subdomain = user.subdomain
        alert.name = self.get_argument('name', '')
        alert.description = self.get_argument('description', '')
        alert.saved_search = int(self.get_argument('saved_search'))
        alert.threshold_operator = self.get_argument('threshold_operator')
        alert.threshold_count = int(self.get_argument('threshold_count'))
        alert.threshold_time_secs = int(self.get_argument('threshold_time_secs'))
        alert.sound = self.get_argument('sound')
        alert.endpoint = self.get_argument('endpoint', '')
        if method == 'create':
            alert.active = True
            alert.muted = False
            alert.state = 'N'
            alert.last_run = 0
            alert.last_state_change = 0
        alert.put()
        self.redirect('/%s' % subdomain)
