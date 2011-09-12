import tornado.web

from wtforms import Form, BooleanField, TextField, validators, SelectField, TextAreaField
from wtforms.validators import Required

from lib.multidict import MultiDict
from models.endpoint import EndpointManager, Endpoint
from models.user import UserManager

from page import PageHandler

class EndpointForm(Form):
    provider = SelectField(u'Endpoint', [Required()], choices=[('pd', 'PagerDuty')])
    description = TextAreaField('Description', [Required()])
    service_key = TextField('Service Key', [Required()])
    alert_text = TextField('Alert Text', [Required()])
    
    def __init__(self, formdata=None, obj=None, prefix='', endpoint=None, **kwargs): 
        if endpoint:
            kwargs.setdefault('provider', endpoint.provider) 
            kwargs.setdefault('description', endpoint.description) 
            kwargs.setdefault('service_key', endpoint.service_key) 
            kwargs.setdefault('alert_text', endpoint.alert_text) 
        Form.__init__(self, formdata, obj, prefix, **kwargs)

class EndpointHandler(PageHandler):
    def get(self, subdomain, method = None, endpoint_id = None):
        args = self.template_args
        if method == 'create':
            args['form'] = EndpointForm()
        else:
            endpoint = EndpointManager.get_endpoint(endpoint_id)
            args['form'] = EndpointForm(endpoint = endpoint)
        args['endpoint_id'] = endpoint_id
        args['method'] = method
        args['subdomain'] = subdomain
        self.render('endpoint.html', **args)
