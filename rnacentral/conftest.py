# -*- coding: utf-8 -*-

"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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

import django
import pytest

django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Avoid creating/setting up the test database"""
    pass


@pytest.fixture
def db_access_without_rollback_and_truncate(request, django_db_setup,
                                            django_db_blocker):
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.restore)

