import logging
import hashlib
import math
import time
import traceback

import tornado.escape
import tornado.web

import pusher

from django.utils import simplejson as json

from pagerduty import PagerDuty

import config
import lib.oauth
from lib.loggly import Loggly

from models.alert import AlertManager
from models.endpoint import EndpointManager
from models.savedsearch import SavedSearchManager
from models.user import UserManager

class CronHandler(tornado.web.RequestHandler):
    '''prefix parameter is for sharding'''
    def get(self, token, prefix):
        if token != config.CRON_PASSWORD:
            self.write('nope')
            return
        else:
            # App Engine cron jobs don't always run exactly on the minute,
            # so make sure all times are evenly divisible by 60
            run_time = (int(math.floor(time.time())) // 60) * 60
            alerts = AlertManager.get_all_alerts_systemwide(prefix=prefix)
            for alert in alerts:
                if alert.active == False:
                    continue

                # TODO what if this times out?
                if alert.last_run == 0 or alert.state == 'C' or (run_time - alert.last_run) >= alert.threshold_time_secs:
                    # this is a blanket try/catch so misconfigured endpoints, etc. don't impact other alerts.
                    try:
                        user = UserManager.get_user(alert.email)
                        oauth_client = lib.oauth.Client(user.subdomain)
                        token = oauth_client.generate_token(user.access_token_key, user.access_token_secret)

                        # to create a dummy saved search, POST to
                        # http://davidlanstein.frontend-david1.office.loggly.net/api/savedsearches/create
                        # with this data:
                        # name=foo&context={"search_type":"search", "terms":"ivan tam", "from":"NOW-1DAY", "until":"NOW", "inputs":["logglyapp","logglyweb"], "order":"desc", "buckets": null, "highlighting":true, "rows":20, "start":0, "page":0, "command_string":null}
                        saved_searches = SavedSearchManager.get_all_saved_searches(user)

                        found = False
                        for saved_search in saved_searches:
                            if saved_search.id == alert.saved_search:
                                found = True
                                break
                        if not found:
                            # search was deleted, perhaps?
                            logging.warn({'module': 'controllers.cron', 'message': 'Alert with id \'%s\' is associated with saved search \'%s\', which no longer exists.' % (unicode(alert.key()), saved_search.id)})
                            continue

                        qs = Loggly.build_search_query_string(saved_search.context, alert.threshold_time_secs)

                        try:
                            search_result = json.loads(oauth_client.make_request(token, 'http://%s.%s/api/facets/date?%s' % \
                                (user.subdomain, config.LOGGLY_DOMAIN, qs), 'GET'))
                        except Exception, e:
                            logging.error({'module': 'controllers.cron', 'traceback': traceback.format_exc()})
                            # input name in saved search doesn't exist anymore, etc.
                            continue

                        if alert.threshold_operator == 'gt':
                            fire_alert = search_result['numFound'] > alert.threshold_count
                        elif alert.threshold_operator == 'lt':
                            fire_alert = search_result['numFound'] < alert.threshold_count
                        else:
                            fire_alert = search_result['numFound'] == alert.threshold_count

                        if not fire_alert:
                            if alert.state == 'C':
                                alert.state = 'N'
                                alert.last_state_change = run_time
                                alert_json = {'sound': alert.sound , 'description': tornado.escape.xhtml_escape(alert.description), 'name': tornado.escape.xhtml_escape(alert.name), 'state': alert.state, 'key': unicode(alert.key()), 'muted': alert.muted, 'last_state_change': alert.last_state_change }
                                alert_channel = hashlib.md5('alertbirds' + alert.subdomain).hexdigest()
                                pusher_client = pusher.Pusher(app_id=config.PUSHER_APP_ID, key=config.PUSHER_KEY, secret=config.PUSHER_SECRET)
                                result = pusher_client[alert_channel].trigger('chirp', data=alert_json)

                                if alert.endpoint:
                                    endpoint = EndpointManager.get_endpoint(alert.endpoint, alert.email)
                                    pagerduty = PagerDuty(endpoint.service_key)
                                    pagerduty.resolve(unicode(alert.key()))
                        else:
                            if alert.state == 'N':
                                alert.state = 'C'
                                alert.last_state_change = run_time
                            logging.warn({'module': 'controllers.cron', 'message': 'Alert with id \'%s\' is in a critical state.' % unicode(alert.key())})
                            alert_json = {'sound': alert.sound , 'description': tornado.escape.xhtml_escape(alert.description), 'name': tornado.escape.xhtml_escape(alert.name), 'state': alert.state, 'key': unicode(alert.key()), 'muted': alert.muted, 'last_state_change': alert.last_state_change }
                            alert_channel = hashlib.md5('alertbirds' + alert.subdomain).hexdigest()
                            pusher_client = pusher.Pusher(app_id=config.PUSHER_APP_ID, key=config.PUSHER_KEY, secret=config.PUSHER_SECRET)
                            result = pusher_client[alert_channel].trigger('chirp', data=alert_json)

                            if alert.endpoint:
                                endpoint = EndpointManager.get_endpoint(alert.endpoint, alert.email)
                                pagerduty = PagerDuty(endpoint.service_key)
                                pagerduty.trigger(endpoint.alert_text, unicode(alert.key()), alert.description)

                        # if pagerduty is experiencing an outage, still re-run next minute
                        # that's why we set last_run at the bottom
                        alert.last_run = run_time
                        alert.put()
        
                    except Exception, e:
                        # endpoint misconfigured, who knows what else.  don't impact other users.
                        logging.error({'module': 'controllers.cron', 'traceback': traceback.format_exc()})
