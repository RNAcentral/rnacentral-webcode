"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

"""
The throttling classes are overriden after a problem with the Ensembl Das system.

The issue was caused by bad Memcached keys
set by the throttling layer of the RNAcentral API.
The remote address header and the X_FORWARDED_FOR headers
were concatenated with a whitespace character, which is not allowed in Memcached keys.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class SafeCacheKeyAnonRateThrottle(AnonRateThrottle):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """

    def get_cache_key(self, request, view):
        """
        Strip out whitespace from the key.
        """
        unsafe_key = super(SafeCacheKeyAnonRateThrottle, self).get_cache_key(request, view) \
                     or ''
        return unsafe_key.replace(' ', '')


class SafeCacheKeyUserRateThrottle(UserRateThrottle):
    """
    Limits the rate of API calls that may be made by a given user.

    The user id will be used as a unique cache key if the user is
    authenticated.  For anonymous requests, the IP address of the request will
    be used.
    """
    scope = 'user'

    def get_cache_key(self, request, view):
        """
        Strip out whitespace from the key.
        """
        unsafe_key = super(SafeCacheKeyUserRateThrottle, self).get_cache_key(request, view) \
                     or ''
        return unsafe_key.replace(' ', '')
