# RNAcentral Website

[![Build Status](http://jenkins.rnacentral.org/buildStatus/icon?job=Update_test.rnacentral.org)](http://jenkins.rnacentral.org/job/rnacentral_testing/)

## About

[RNAcentral](https://rnacentral.org) is an open public resource that offers integrated access to a comprehensive and up-to-date set of non-coding RNA sequences provided by a consortium of Expert Databases.

![RNAcentral Expert Databases](./rnacentral/portal/static/img/expert-databases.png)

The development of RNAcentral is coordinated by the
[European Bioinformatics Institute](https://www.ebi.ac.uk) and is funded by [Wellcome](https://wellcome.org).

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

## Feedback

Please get in touch if you have any feedback using [GitHub issues](https://github.com/RNAcentral/rnacentral-webcode/issues)
or using the [contact us form](https://rnacentral.org/contact).
