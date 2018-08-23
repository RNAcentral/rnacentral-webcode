# RNAcentral Website

[![Build Status](http://jenkins.rnacentral.org/buildStatus/icon?job=rnacentral_testing)](http://jenkins.rnacentral.org/job/rnacentral_testing/)

## About

RNAcentral is an open public resource that offers integrated access to a comprehensive and up-to-date set of ncRNA sequences. For more information, please visit http://rnacentral.org/about-us.

The development of RNAcentral is coordinated by the
[European Bioinformatics Institute](http://www.ebi.ac.uk) and is funded by the
[BBSRC](http://www.bbsrc.ac.uk).

## Installation

1. Clone Git repository:

  ```
  git clone https://github.com/RNAcentral/rnacentral-webcode.git
  ```

2. Edit database connection parameters in `rnacentral/local_settings.py`

3. Run the app using [Docker](https://www.docker.com):

  ```
  export RNACENTRAL_HOME=/path/to/rnacentral/code
  cd $RNACENTRAL_HOME
  docker-compose up --build
  ```

**Docker Cheat Sheet**

```
# connect to a running container
docker ps
docker exec -it <container_id> bash
```

## Testing

### Selenium tests

1. Install `selenium` and `requests` using [virtualenv](https://virtualenv.pypa.io):

  ```
  virtualenv /path/to/testing/virtualenv
  source /path/to/testing/virtualenv/bin/activate
  pip install requests selenium
  ```

1. Install [Gecko Driver](https://github.com/mozilla/geckodriver/releases) and add it to the `PATH`:

  ```
  export PATH=$PATH:/path/to/geckodriver
  ```

1. Start the website locally using Docker (see above).

1. Launch tests against the local RNAcentral website:

  ```sh
  cd $RNACENTRAL_HOME
  python rnacentral/portal/tests/selenium_tests.py
  ```

These tests run automatically using [Travis](https://travis-ci.org/RNAcentral/rnacentral-webcode).

### API tests

1. Login to the running Docker container (see above).

1. Launch tests:

  ```sh
  cd $RNACENTRAL_HOME
  python rnacentral/apiv1/tests.py
  ```

### Application-specific tests

Using Django test runner:

```sh
cd $RNACENTRAL_HOME
python manage.py test portal.tests.description_tests
```

Using [py.test](http://docs.pytest.org/en/latest/) requires creating a file `rnacentral/conftest.py`:

```python
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
```

The following file is also required:

```sh
$ cat pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = rnacentral.settings
```

Tests can then be run with:

```sh
cd $RNACENTRAL_HOME
py.test portal/tests/description_tests.py
```

## Feedback

Feel free to give feedback using [GitHub issues](https://github.com/RNAcentral/rnacentral-webcode/issues)
or get in touch using the [Contact form](http://rnacentral.org/contact) on our website.
