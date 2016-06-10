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
# start Docker machine
docker-machine start default

# initialize Docker environment
eval $(docker-machine env)

# connect to a running container
docker-machine ls
docker exec -it <container_id> bash 
```

## Technology overview

### Python

* [Django](https://www.djangoproject.com/)
* [Django REST Framework](http://www.django-rest-framework.org/)
* [Fabric](http://www.fabfile.org/)
* [cx_Oracle](http://cx-oracle.sourceforge.net/)
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

## Feedback

Feel free to give feedback using [GitHub issues](https://github.com/RNAcentral/rnacentral-webcode/issues)
or get in touch using the [Contact form](http://rnacentral.org/contact) on our website.
