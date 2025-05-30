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
import errno
import glob
import io
import os
import pickle
import random
import re
import tempfile
import time
import zlib

from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from django.core.cache.backends.memcached import PyMemcacheCache
from django.core.files.move import file_move_safe


class CustomPyMemcacheCache(PyMemcacheCache):
    """
    This class is being used to avoid this type of error:
    pymemcache.exceptions.MemcacheServerError: b'object too large for cache'
    """

    def __init__(self, *args, **kwargs):
        self.max_cache_size = 1024 * 1024 * 5  # set the maximum size (5MB)
        super().__init__(*args, **kwargs)

    def set(self, key, value, timeout=None, version=None):
        value_size = len(pickle.dumps(value))

        if value_size > self.max_cache_size:
            return False  # do not cache
        return super().set(key, value, timeout, version)


class SitemapsCache(BaseCache):
    """
    This class is required to generate sitemaps
    """

    cache_suffix = ".djcache"

    def __init__(self, dir, params):
        super(SitemapsCache, self).__init__(params)
        self._dir = os.path.abspath(dir)
        self._createdir()

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if self.has_key(key, version):
            return False
        self.set(key, value, timeout, version)
        return True

    def get(self, key, default=None, version=None):
        fname = self._key_to_file(key, version)
        if os.path.exists(fname):
            try:
                with io.open(fname, "rb") as f:
                    if not self._is_expired(f):
                        return pickle.loads(zlib.decompress(f.read()))
            except IOError as e:
                if e.errno == errno.ENOENT:
                    pass  # Cache file was removed after the exists check
        return default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self._createdir()  # Cache dir can be deleted at any time.
        fname = self._key_to_file(key, version)
        self._cull()  # make some room if necessary
        fd, tmp_path = tempfile.mkstemp(dir=self._dir)
        renamed = False
        try:
            with io.open(fd, "wb") as f:
                expiry = self.get_backend_timeout(timeout)
                f.write(pickle.dumps(expiry, -1))
                f.write(zlib.compress(pickle.dumps(value), -1))
            file_move_safe(tmp_path, fname, allow_overwrite=True)
            renamed = True
        finally:
            if not renamed:
                os.remove(tmp_path)

    def delete(self, key, version=None):
        self._delete(self._key_to_file(key, version))

    def _delete(self, fname):
        if not fname.startswith(self._dir) or not os.path.exists(fname):
            return
        try:
            os.remove(fname)
        except OSError as e:
            # ENOENT can happen if the cache file is removed (by another
            # process) after the os.path.exists check.
            if e.errno != errno.ENOENT:
                raise

    def has_key(self, key, version=None):
        fname = self._key_to_file(key, version)
        if os.path.exists(fname):
            with io.open(fname, "rb") as f:
                return not self._is_expired(f)
        return False

    def _cull(self):
        """
        Removes random cache entries if max_entries is reached at a ratio
        of num_entries / cull_frequency. A value of 0 for CULL_FREQUENCY means
        that the entire cache will be purged.
        """
        filelist = self._list_cache_files()
        num_entries = len(filelist)
        if num_entries < self._max_entries:
            return  # return early if no culling is required
        if self._cull_frequency == 0:
            return self.clear()  # Clear the cache when CULL_FREQUENCY = 0
        # Delete a random selection of entries
        filelist = random.sample(filelist, int(num_entries / self._cull_frequency))
        for fname in filelist:
            self._delete(fname)

    def _createdir(self):
        if not os.path.exists(self._dir):
            try:
                os.makedirs(self._dir, 0o700)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise EnvironmentError(
                        "Cache directory '%s' does not exist "
                        "and could not be created'" % self._dir
                    )

    def _key_to_file(self, key, version=None):
        """
        Convert a key into a cache file path. Basically this is the
        root cache path joined with the md5sum of the key and a suffix.
        """
        key = re.sub("[:/#?&=+%]", "_", key)
        return os.path.join(self._dir, "".join([key, self.cache_suffix]))

    def clear(self):
        """
        Remove all the cache files.
        """
        if not os.path.exists(self._dir):
            return
        for fname in self._list_cache_files():
            self._delete(fname)

    def _is_expired(self, f):
        """
        Takes an open cache file and determines if it has expired,
        deletes the file if it is has passed its expiry time.
        """
        exp = pickle.load(f)
        if exp is not None and exp < time.time():
            f.close()  # On Windows a file has to be closed before deleting
            self._delete(f.name)
            return True
        return False

    def _list_cache_files(self):
        """
        Get a list of paths to all the cache files. These are all the files
        in the root cache dir that end on the cache_suffix.
        """
        if not os.path.exists(self._dir):
            return []
        filelist = [
            os.path.join(self._dir, fname)
            for fname in glob.glob1(self._dir, "*%s" % self.cache_suffix)
        ]
        return filelist
