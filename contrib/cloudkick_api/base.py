# Licensed to Cloudkick, Inc ('Cloudkick') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# Cloudkick licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__all__ = ["Connection"]

import os
import urllib
from oauth import oauth

try:
    import json
except ImportError:
    import simplejson as json

import endpoints


class Connection(object):
    """
    Cloudkick API Connection Object

    Provides an interface to the Cloudkick API over an HTTPS connection,
    using OAuth to authenticate requests.
    """

    API_SERVER = "api.cloudkick.com"
    API_VERSION = "2.0"

    def __init__(self, config_path=None, oauth_key=None, oauth_secret=None,
                 api_server=API_SERVER, api_version=API_VERSION, prefer_params=False):
        self.__oauth_key = oauth_key or None
        self.__oauth_secret = oauth_secret or None
        self.__prefer_params = prefer_params
        self.__api_server = api_server
        self.__api_version = api_version
        if config_path is None:
            config_path = [os.path.join(os.path.expanduser('~'),
                                             ".cloudkick.conf"),
                           "/etc/cloudkick.conf"]
        if not isinstance(config_path, list):
            config_path = [config_path]
        self.config_path = config_path

    def _read_config(self):
        errors = []
        for path in self.config_path:
            try:
                fp = open(path, 'r')
                return self._parse_config(fp)
            except Exception, e:
                errors.append(e)
                continue
        raise IOError("Unable to open configuration files: %s %s" %
                        (", ".join(self.config_path),
                         ", ".join([str(e) for e in errors])))

    def _parse_config(self, fp):
        for line in fp.readlines():
            if len(line) < 1:
                continue
            if line[0] == "#":
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            if key == "oauth_key":
                if not self.__prefer_params or self.__oauth_key is None:
                    self.__oauth_key = value
            if key == "oauth_secret":
                if not self.__prefer_params or self.__oauth_secret is None:
                    self.__oauth_secret = value

    @property
    def oauth_key(self):
        if not self.__oauth_key:
            self._read_config()
        return self.__oauth_key

    @property
    def oauth_secret(self):
        if not self.__oauth_secret:
            self._read_config()
        return self.__oauth_secret

    @property
    def api_version(self):
        return self.__api_version

    @property
    def api_server(self):
        return self.__api_server

    def _filter_params(self, params):
        """Filter out any null parameters"""
        return dict((k, v) for k, v in params.iteritems() if v is not None)

    def _request(self, url, parameters=None, method='GET'):
        if not parameters:
            parameters = None
        else:
            parameters = self._filter_params(parameters)

        signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        consumer = oauth.OAuthConsumer(self.oauth_key, self.oauth_secret)
        if self.api_server[:3] == "127":
            protocol = "http://"
        else:
            protocol = "https://"
        url = '%s%s/%s/%s' % (protocol, self.api_server, self.api_version, url)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                                                                   http_url=url,
                                                                   http_method=method,
                                                                   parameters=parameters)
        oauth_request.sign_request(signature_method, consumer, None)
        if method == "GET":
            url = oauth_request.to_url()
            f = urllib.urlopen(url)
        else:
            url = oauth_request.get_normalized_http_url()
            f = urllib.urlopen(url, oauth_request.to_postdata())
        s = f.read()
        return s

    def _request_json(self, *args):
        r = self._request(*args)

        try:
            return json.loads(r)
        except ValueError:
            return r

    @property
    def addresses(self):
        return endpoints.Addresses(self)

    @property
    def address_types(self):
        return endpoints.AddressTypes(self)

    @property
    def changelogs(self):
        return endpoints.ChangeLogs(self)

    @property
    def checks(self):
        return endpoints.Checks(self)

    @property
    def check_types(self):
        return endpoints.CheckTypes(self)

    @property
    def interesting_metrics(self):
        return endpoints.InterestingMetrics(self)

    @property
    def monitors(self):
        return endpoints.Monitors(self)

    @property
    def nodes(self):
        return endpoints.Nodes(self)

    @property
    def providers(self):
        return endpoints.Providers(self)

    @property
    def provider_types(self):
        return endpoints.ProviderTypes(self)

    @property
    def monitoring_servers(self):
        return endpoints.MonitoringServers(self)

    @property
    def status_nodes(self):
        return endpoints.StatusNodes(self)

    @property
    def tags(self):
        return endpoints.Tags(self)


if __name__ == "__main__":
    from pprint import pprint
    c = Connection()
    nodes = c.nodes.read()
    pprint(nodes)
    nids = [n['id'] for n in nodes['items']]
    checks = c.checks.read(node_ids=nids)
    pprint(checks)
    #check = checks[0][nid][0]
    #now = datetime.now()

    from cloudkick_api import fabhelper
    print
    print "DO FAB STUFF"
    print "HOSTS", fabhelper.hosts()
    print "ROLEDEFS", fabhelper.roledefs()
    print "LOAD", fabhelper.load()
