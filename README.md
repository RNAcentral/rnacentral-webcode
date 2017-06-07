# RNAcentral Website

[![Build Status](https://travis-ci.org/RNAcentral/rnacentral-webcode.svg?branch=master)](https://travis-ci.org/RNAcentral/rnacentral-webcode)

## About

RNAcentral is an open public resource that offers integrated access to a comprehensive and up-to-date set of ncRNA sequences. For more information, please visit http://rnacentral.org/about-us.

The development of RNAcentral is coordinated by the
[European Bioinformatics Institute](http://www.ebi.ac.uk) and is funded by the
[BBSRC](http://www.bbsrc.ac.uk).

## Installation

1. Clone Git repository:

  ```
  git clone --recursive https://github.com/RNAcentral/rnacentral-webcode.git
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

Using Django test runner:

```sh
cd rnacentral
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
$ cat pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = rnacentral.settings
```

Tests can then be run with:

```sh
cd rnacentral
py.test portal/tests/description_tests.py
```

## Feedback

Feel free to give feedback using [GitHub issues](https://github.com/RNAcentral/rnacentral-webcode/issues)
or get in touch using the [Contact form](http://rnacentral.org/contact) on our website.

## Technology overview

### Python

* [Django](https://www.djangoproject.com/)
* [Django REST Framework](http://www.django-rest-framework.org/)
* [Fabric](http://www.fabfile.org/)
* [Python RQ](http://python-rq.org/)
* see [requirements.txt](rnacentral/requirements.txt) for the full list

### Javascript

* [AngularJS](https://angularjs.org/)
* [Twitter Bootstrap](http://getbootstrap.com/)
* [D3](http://d3js.org/)
* [jQuery](https://jquery.com/)
* [DataTables](http://datatables.net/)
* [Hopscotch](https://github.com/linkedin/hopscotch)
* [Handlebars](http://handlebarsjs.com/)
* [Genoverse](http://genoverse.org)
* see [LICENSE](LICENSE) for more details

### CSS

* [Twitter Bootstrap](http://getbootstrap.com/)
* [Font Awesome](http://fontawesome.io/)
* [Animate.css](https://daneden.github.io/animate.css/)
* see [LICENSE](LICENSE) for more details

### Testing
* [Selenium](http://www.seleniumhq.org/)
* [PhantomJS](http://phantomjs.org/)
* [Travis](https://travis-ci.org/)
* [BrowserStack](http://browserstack.com)

### Other
* [Memcached](http://memcached.org/)
* [Redis](http://redis.io/)
* [Supervisor](http://supervisord.org/)
* [Docker](https://www.docker.com)
