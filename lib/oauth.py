import httplib
import logging
import sys
import time
import urllib

import oauth2 as oauth

import config

class Client(oauth.Client):
    def __init__(self, subdomain):
        self.request_token_url = 'http://%s.%s%s' % (subdomain, config.LOGGLY_DOMAIN, config.OAUTH_REQUEST_TOKEN_PATH)
        self.access_token_url = 'http://%s.%s%s' % (subdomain, config.LOGGLY_DOMAIN, config.OAUTH_ACCESS_TOKEN_PATH)
        self.authorize_url = 'http://%s.%s%s' % (subdomain, config.LOGGLY_DOMAIN, config.OAUTH_AUTHORIZE_PATH)
        self.callback_url = config.OAUTH_CALLBACK_URL
        self.consumer = oauth.Consumer(config.OAUTH_CONSUMER_KEY, config.OAUTH_CONSUMER_SECRET)
        self.signature_method_plaintext = oauth.SignatureMethod_PLAINTEXT()
        self.signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

        self.connection = httplib.HTTPConnection(config.AB_DOMAIN)

    def get_request_token(self):
        oauth_request = oauth.Request.from_consumer_and_token(self.consumer, http_url = self.request_token_url)
        oauth_request.sign_request(self.signature_method_plaintext, self.consumer, None)

        self.connection.request('GET', self.request_token_url, headers = oauth_request.to_header()) 
        response = self.connection.getresponse()
        token = oauth.Token.from_string(response.read())
        token.set_callback(self.callback_url)

        return token

    def get_authorize_url(self, token):
        oauth_request = oauth.Request.from_token_and_callback(token = token, http_url = self.authorize_url, callback = self.callback_url)
        return oauth_request.to_url()

    def get_access_token(self, request_token):
        oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token = request_token, http_url = self.access_token_url)
        oauth_request.sign_request(self.signature_method_plaintext, self.consumer, request_token)
        
        self.connection.request('GET', self.access_token_url, headers = oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.Token.from_string(response.read())

    def generate_token(self, key, secret):
        return oauth.Token(key, secret)

    def make_request(self, token, url, method = 'GET', params = {}):
        if method == 'POST':
            oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token=token, http_method=method, http_url=url, parameters=params)
        else:
            oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token=token, http_method=method, http_url=url)
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, token)

        if method == 'POST':
            self.connection.request(method, url, body=oauth_request.to_postdata())
        else:
            self.connection.request(method, url, urllib.urlencode(params), headers=oauth_request.to_header())
        response = self.connection.getresponse()
        try:
            return response.read()
        except Exception, e:
            logging.error({'module': 'lib.oauth', 'message': e})
