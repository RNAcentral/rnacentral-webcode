"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
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
from django.core.cache.backends.memcached import PyMemcacheCache


class CustomPyMemcacheCache(PyMemcacheCache):
    """
    This class is being used to avoid this type of error:
    pymemcache.exceptions.MemcacheServerError: b'object too large for cache'
    """

    def __init__(self, *args, **kwargs):
        self.max_cache_size = 1024 * 1024 * 5  # set the maximum size (5MB)
        super().__init__(*args, **kwargs)

    def set(self, key, value, timeout=None, version=None):
        import pickle

        value_size = len(pickle.dumps(value))

        if value_size > self.max_cache_size:
            return False  # do not cache
        return super().set(key, value, timeout, version)
