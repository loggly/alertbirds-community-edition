#!/usr/bin/env python

import sys
if sys.version_info < (2, 6):
    import socket

try:
    import json
except ImportError:
    from django.utils import simplejson as json
import urllib2

from pagerduty.version import *

__version__ = VERSION

class PagerDutyException(Exception):
    def __init__(self, status, message, errors):
        super(PagerDutyException, self).__init__(message)
        self.msg = message
        self.status = status
        self.errors = errors
    
    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.status, self.msg, self.errors)
    
    def __str__(self):
        txt = "%s: %s" % (self.status, self.msg)
        if self.errors:
            txt += "\n" + "\n".join("* %s" % x for x in self.errors)
        return txt

class PagerDuty(object):
    def __init__(self, service_key, https=True, timeout=15):
        self.service_key = service_key
        self.api_endpoint = ("http", "https")[https] + "://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.timeout = timeout
    
    def trigger(self, description, incident_key=None, details=None):
        return self._request("trigger", description=description, incident_key=incident_key, details=details)
    
    def acknowledge(self, incident_key, description=None, details=None):
        return self._request("acknowledge", description=description, incident_key=incident_key, details=details)
    
    def resolve(self, incident_key, description=None, details=None):
        return self._request("resolve", description=description, incident_key=incident_key, details=details)
    
    def _request(self, event_type, **kwargs):
        event = {
            "service_key": self.service_key,
            "event_type": event_type,
        }
        for k, v in kwargs.items():
            if v is not None:
                event[k] = v
        encoded_event = json.dumps(event)
        try:
            if sys.version_info < (2, 6):
                socket.setdefaulttimeout(self.timeout)
                res = urllib2.urlopen(self.api_endpoint, encoded_event)
            else:
                res = urllib2.urlopen(self.api_endpoint, encoded_event, self.timeout)
        except urllib2.HTTPError, exc:
            if exc.code != 400:
                raise
            res = exc
        
        result = json.loads(res.read())
        
        if result['status'] != "success":
            raise PagerDutyException(result['status'], result['message'], result['errors'])
        
        # if result['warnings]: ...
        
        return result.get('incident_key')
