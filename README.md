# RNAcentral Website

[![Build Status](http://jenkins.rnacentral.org/buildStatus/icon?job=Update_test.rnacentral.org)](http://jenkins.rnacentral.org/job/rnacentral_testing/)

## About

RNAcentral is an open public resource that offers integrated access to a comprehensive and up-to-date set of ncRNA sequences. For more information, please visit https://rnacentral.org/about-us.

The development of RNAcentral is coordinated by the
[European Bioinformatics Institute](http://www.ebi.ac.uk) and is funded by the
[BBSRC](http://www.bbsrc.ac.uk).

## Installation

1. Clone Git repository:

  ```
  git clone --recursive https://github.com/RNAcentral/rnacentral-webcode.git
  ```

2. Edit database connection parameters in `rnacentral/local_settings.py`. Use the [public postgres database](https://rnacentral.org/help/public-database) when developing outside the EBI network.

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

### API tests

1. Login to the running Docker container (see above).

1. Launch tests:

  ```sh
  cd $RNACENTRAL_HOME
  python rnacentral/apiv1/tests.py
  ```

## Feedback

Feel free to give feedback using [GitHub issues](https://github.com/RNAcentral/rnacentral-webcode/issues)
or get in touch using the [Contact form](https://rnacentral.org/contact) on our website.

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
* [Genoverse](http://genoverse.org)
* see [LICENSE](LICENSE) for more details

### CSS

* [Twitter Bootstrap](http://getbootstrap.com/)
* [Font Awesome](http://fontawesome.io/)
* [Animate.css](https://daneden.github.io/animate.css/)
* see [LICENSE](LICENSE) for more details

### Other
* [Memcached](http://memcached.org/)
* [Redis](http://redis.io/)
* [Supervisor](http://supervisord.org/)
* [Docker](https://www.docker.com)
