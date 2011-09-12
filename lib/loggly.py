import logging
import urllib

from django.utils import simplejson as json

import config
import lib.oauth

from models.user import UserManager

class Loggly(object):
    @staticmethod
    def get_devices(user = None):
        if not user:
            user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)
        try:
            return json.loads(oauth_client.make_request(token, 'http://%s.%s/api/devices' % \
                (user.subdomain, config.LOGGLY_DOMAIN) , 'GET'))
        except ValueError:
            logging.error(json.dumps({'module': 'lib.loggly', 'message': \
                'Subdomain \'%s\' could not load the list of devices' % user.subdomain}))
            raise 

    @staticmethod
    def get_inputs(user = None):
        if not user:
            user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)
        try:
            return json.loads(oauth_client.make_request(token, 'http://%s.%s/api/inputs' % \
                (user.subdomain, config.LOGGLY_DOMAIN) , 'GET'))
        except ValueError:
            logging.error(json.dumps({'module': 'lib.loggly', 'message': \
                'Subdomain \'%s\' could not load the list of inputs' % user.subdomain}))
            raise 

    @staticmethod
    def build_search_query(context):
        if context.get('inputs') or context.get('devices'):
            inputs = context.get('inputs', [])
            devices = context.get('devices', [])
            inputs_string = ' OR '.join('inputname:' + x for x in inputs)
            devices_string = ' OR '.join('device:' + x for x in devices)
            if inputs_string and devices_string:
                return '%s (%s)' % (context['terms'], ' OR '.join((inputs_string, devices_string)))
            else:
                return '%s (%s%s)' % (context['terms'], inputs_string, devices_string)
        else:
            return context['terms']

    @staticmethod
    def build_search_query_string(context, search_from_secs):
        params = {}
        params['from'] = 'NOW-%dSECONDS' % int(search_from_secs)
        params['until'] = 'NOW'
        params['q'] = Loggly.build_search_query(context)

        # inputs - if we get back an empty list in the context, it means all
        return '&'.join([k + '=' + urllib.quote(str(v)) for (k, v) in params.items()])

    @staticmethod
    def build_search_url(context, search_from_secs):
        # _devices is not yet supported - use (device:...) syntax instead for now
        # e.g. https://foo.loggly.com/shell#/_search */_inputs=syslog_udp,test_http/_from=NOW-2MINUTES
        user = UserManager.get_current_user()
        params = []
        params.append('_search %s' % Loggly.build_search_query(context))
        params.append('_from=NOW-%sSECONDS' % search_from_secs)
        return 'http://%s.%s/shell#/%s' % (user.subdomain, config.LOGGLY_DOMAIN, '/'.join(params))

    @staticmethod
    def get_saved_search(id):
        user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)

        try:
            return json.loads(oauth_client.make_request(token, 'http://%s.%s/api/savedsearches/%s' % \
                (user.subdomain, config.LOGGLY_DOMAIN, id), 'GET'))
        except ValueError:
            logging.error(json.dumps({'module': 'lib.loggly', 'message': \
                'Subdomain \'%s\' could not load the saved search with ID %d' % (user.subdomain, id)}))
            raise 

    @staticmethod
    def get_all_saved_searches(user = None):
        if not user:
            user = UserManager.get_current_user()
        oauth_client = lib.oauth.Client(user.subdomain)
        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)

        try:
            return json.loads(oauth_client.make_request(token, 'http://%s.%s/api/savedsearches' % \
                (user.subdomain, config.LOGGLY_DOMAIN), 'GET'))
        except ValueError:
            logging.error(json.dumps({'module': 'lib.loggly', 'message': \
                'Subdomain \'%s\' could not load the list of saved searches' % user.subdomain}))
            raise 
