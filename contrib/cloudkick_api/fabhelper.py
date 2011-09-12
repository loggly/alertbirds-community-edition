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


__all__ = ["hosts", "roledefs", "load"]

import sys

from cloudkick_api.base import Connection

_QUERY_CACHE = {}

class RoleDefs(object):

    def _get_data(self, query):
        global _QUERY_CACHE
        if not query in _QUERY_CACHE:
            connection = Connection()
            _QUERY_CACHE[query] = connection.nodes.read(query=query)

        return _QUERY_CACHE[query]

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __getitem__(self, query):
        data = self._get_data(query)

        if data and 'items' in data and len(data['items']) > 0:
            return [node['ipaddress'] for node in data['items']]

        # Throw a KeyError to keep consistent with a dictionary
        raise KeyError(query)

def hosts():
    # TODO: need generic DNS (?)
    rd = RoleDefs()
    try:
        return rd['*']
    except KeyError:
        # Always return SOMETHING!
        return []

def roledefs():
    rd = RoleDefs()
    return rd

def load(x = None):
    from fabric.api import env
    try:
        env.hosts = hosts()
        env.roledefs = roledefs()
    except IOError, e:
        # Don't print a huge stack trace if there's a problem. Most likely cloudkick.conf isn't in the path.
        print e
        sys.exit()
    return x
