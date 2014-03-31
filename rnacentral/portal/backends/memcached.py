"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.core.cache.backends.memcached import BaseMemcachedCache
import pickle


DEFAULT_MAX_VALUE_LENGTH = 1024 * 1024 # 1Mb

class MemcachedCache(BaseMemcachedCache):
    """
    Reimplementation of the MemcachedCache cache with optional increased
    size limit. This is required for storing items larger than 1Mb.
    Memcached should be launched with `-I 15M` or similar option.
    """
    def __init__(self, server, params):
        #options from the settings['CACHE'][connection]
        self._options = params.get("OPTIONS", {})
        import memcache
        memcache.SERVER_MAX_VALUE_LENGTH = self._options.get('SERVER_MAX_VALUE_LENGTH', DEFAULT_MAX_VALUE_LENGTH)

        super(MemcachedCache, self).__init__(server, params,
                                             library=memcache,
                                             value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            server_max_value_length = self._options.get("SERVER_MAX_VALUE_LENGTH", DEFAULT_MAX_VALUE_LENGTH)
            self._client = self._lib.Client(self._servers, pickleProtocol=pickle.HIGHEST_PROTOCOL, server_max_value_length=server_max_value_length)
        return self._client
