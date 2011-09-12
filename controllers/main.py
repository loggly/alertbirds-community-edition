import logging

from django.utils import simplejson as json

import tornado.web

from google.appengine.api import users as google_users

from wtforms import Form, BooleanField, TextField, validators, SelectField
from wtforms.validators import Required

import config
from lib.multidict import MultiDict
import lib.oauth
from models.user import UserManager, User
from models.alert import AlertManager, Alert

from page import PageHandler

class SubdomainForm(Form):
    subdomain = TextField('Subdomain', [Required()])

class MainHandler(PageHandler):
    def get(self, subdomain = None):
        '''
        We're here for one of several reasons:
        1. Initial visit, not logged in, going to '/' (show welcome page)
        2. Initial visit, no User object stored yet in App Engine datastore (returning from google.com)
        3. Return visit, everything normal
        4. Return visit, no subdomain in URL (so going to '/')
        5. User object stored, but access token not yet written (returning from loggly.com)
        6. User object stored, but access token not yet written (App Engine threw exception when returning from Loggly, etc.)
        7. User entered a subdomain, then hit the back button
        '''
        args = self.template_args
        if not google_users.get_current_user():
            # case 1
            logging.info({'module': 'main', 'path': 'case 1'})
            args['login_url'] = google_users.create_login_url(self.request.uri)
            return self.render('splash.html', **args)

        if not UserManager.current_user_exists():
            # case 2
            logging.info({'module': 'main', 'path': 'case 2'})
            args['form'] = SubdomainForm()
            return self.render('subdomain.html', **args)

        user = UserManager.get_current_user()
        if subdomain:
            args['subdomain'] = subdomain
        else:
            args['subdomain'] = user.subdomain

        if self.get_argument('oauth_verifier', None) or not user.access_token_key:
            # cases 5, 6, or 7
            logging.info({'module': 'main', 'path': 'case 5, 6 or 7'})

            oauth_client = lib.oauth.Client(user.subdomain)
 
            if self.get_argument('oauth_verifier', None):
                # case 5 (just in case)
                user.oauth_verifier = self.get_argument('oauth_verifier')
                user.put()
            elif not user.oauth_verifier:
                # case 7
                request_token = oauth_client.generate_token(user.request_token_key, user.request_token_secret)
                url = oauth_client.get_authorize_url(request_token)
                return self.redirect(url)

            request_token = oauth_client.generate_token(user.request_token_key, user.request_token_secret)
            request_token.verifier = user.oauth_verifier

            access_token = oauth_client.get_access_token(request_token)
            
            # store the access token for all future requests
            user.access_token_key = access_token.key
            user.access_token_secret = access_token.secret
            user.new_user = False
            user.put()

            search_result = json.loads(oauth_client.make_request(access_token, 'http://%s.%s/api/facets/date?q=*&from=NOW-1YEAR' % \
                (user.subdomain, config.LOGGLY_DOMAIN), 'GET'))
            logging.info(json.dumps({'module': 'main', 'user': user.email, 'event': 'new user', 'loggly_events_found': search_result['numFound']}))
            if search_result['numFound'] == 0:
                return self.render('nodata.html', **args)

        if not subdomain:
            # case 4
            logging.info({'module': 'main', 'path': 'case 4'})
            # this must come after the others so we don't lose the OAuth parameters from the URL
            return self.redirect('/%s' % user.subdomain)

        # case 3 or 5
        logging.info({'module': 'main', 'path': 'case 3 or 5'})
        if self.request.uri[-1] == '/':
            return self.redirect(self.request.uri[:-1])

        args['alerts'] = AlertManager.get_all_alerts(user.subdomain)
        self.render('main.html', **args)

    def post(self):
        args = self.template_args
        args['form'] = SubdomainForm(MultiDict(self))
        if not args['form'].validate():
            return self.render('subdomain.html', **args)
        subdomain = self.get_argument('subdomain')
        oauth_client = lib.oauth.Client(subdomain)
        request_token = oauth_client.get_request_token()

        # store the request token, will need it to generate access token after AB 
        # is authorized by user in Loggly
        user = User()
        user.request_token_key = request_token.key
        user.request_token_secret = request_token.secret
        user.subdomain = subdomain
        user.email = google_users.get_current_user().nickname()
        user.new_user = True
        user.put()

        url = oauth_client.get_authorize_url(request_token)
        self.redirect(url)
