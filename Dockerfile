#
# Create a reproducible installation of the RNAcentral website.
#
# All local dependencies are installed manually to mirror the production setup
# where Docker or yum are not available.
#

FROM centos:6.6

RUN yum install -y \
    curl \
    gcc \
    git \
    httpd \
    httpd-devel \
    libaio \
    nc.x86_64 \
    openssl \
    openssl-devel \
    tar \
    unzip \
    zlib-devel

RUN mkdir /rnacentral
RUN mkdir /rnacentral/local
RUN mkdir /rnacentral/static

ENV LOC /rnacentral/local

# Install Python
# NOTE: Python-2.7.11 and python-2.7.11 are DIFFERENT folders, the former contains the sources, the later - binaries
RUN \
    cd $LOC && \
    curl -OL http://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz && \
    tar -zxvf Python-2.7.11.tgz && \
    cd Python-2.7.11 && \
    PREFIX=$LOC/python-2.7.11/ && \
    export LD_RUN_PATH=$PREFIX/lib && \
    ./configure --prefix=$PREFIX  --enable-shared && \
    make && \
    make install && \
    cd $LOC && \
    rm -Rf Python-2.7.11 && \
    rm Python-2.7.11.tgz

# Install virtualenv
RUN \
    cd $LOC && \
    curl -OL  https://pypi.python.org/packages/source/v/virtualenv/virtualenv-15.0.0.tar.gz && \
    tar -zxvf virtualenv-15.0.0.tar.gz && \
    cd virtualenv-15.0.0 && \
    $LOC/python-2.7.11/bin/python setup.py install && \
    cd $LOC && \
    rm -Rf virtualenv-15.0.0.tar.gz && \
    rm -Rf virtualenv-15.0.0

# Create RNAcentral virtual environment
RUN \
    cd $LOC && \
    mkdir virtualenvs && \
    cd virtualenvs && \
    $LOC/python-2.7.11/bin/virtualenv RNAcentral --python=$LOC/python-2.7.11/bin/python

# Install Redis
RUN \
    cd $LOC && \
    curl -OL http://download.redis.io/redis-stable.tar.gz && \
    tar -xvzf redis-stable.tar.gz && \
    cd redis-stable && \
    make && \
    cd $LOC && \
    rm redis-stable.tar.gz && \
    mv redis-stable redis

# Install libevent (memcached requirement)
RUN \
    cd $LOC && \
    curl -OL https://github.com/downloads/libevent/libevent/libevent-2.0.21-stable.tar.gz && \
    tar -zxvf libevent-2.0.21-stable.tar.gz && \
    cd libevent-2.0.21-stable && \
    ./configure --prefix=$LOC/libevent && \
    make && \
    make install && \
    cd $LOC && \
    rm -Rf libevent-2.0.21-stable && \
    rm libevent-2.0.21-stable.tar.gz

# Install memcached (requires libevent)
RUN \
    cd $LOC && \
    curl -OL  http://www.memcached.org/files/memcached-1.4.17.tar.gz && \
    tar -zxvf memcached-1.4.17.tar.gz && \
    cd memcached-1.4.17 && \
    ./configure --prefix=$LOC/memcached --with-libevent=$LOC/libevent/ && \
    make && \
    make install && \
    cd $LOC && \
    rm -Rf memcached-1.4.17 && \
    rm memcached-1.4.17.tar.gz

# Create a user for memcached
RUN adduser -g root xfm_adm

# Install Infernal
RUN \
    cd $LOC && \
    curl -OL http://eddylab.org/infernal/infernal-1.1.1.tar.gz && \
    tar -xvzf infernal-1.1.1.tar.gz && \
    cd infernal-1.1.1 && \
    ./configure --prefix=$LOC/infernal-1.1.1 && \
    make && \
    make install && \
    cd easel && \
    make install && \
    cd $LOC && \
    rm infernal-1.1.1.tar.gz

# Install mod_wsgi
RUN \
    cd $LOC && \
    mkdir httpd && \
    mkdir httpd/modules && \
    curl -L -o mod_wsgi-3.4.tar.gz https://github.com/GrahamDumpleton/mod_wsgi/archive/3.4.tar.gz && \
    tar -zxvf mod_wsgi-3.4.tar.gz && \
    cd mod_wsgi-3.4 && \
    export LD_RUN_PATH=$LOC/python-2.7.11/lib && \
    export LD_LIBRARY_PATH=$LOC/python-2.7.11/lib/:$LD_LIBRARY_PATH && \
    ./configure --with-python=$LOC/python-2.7.11/bin/python && \
    make && \
    mv .libs/mod_wsgi.so $LOC/httpd/modules && \
    cd $LOC && \
    rm -Rf mod_wsgi-3.4 && \
    rm mod_wsgi-3.4.tar.gz

# Define container environment variables
ENV RNACENTRAL_HOME /rnacentral/rnacentral-webcode
ENV RNACENTRAL_LOCAL /rnacentral/local

# Install Django requirements
ADD rnacentral/requirements.txt $RNACENTRAL_HOME/rnacentral/
RUN \
    source $LOC/virtualenvs/RNAcentral/bin/activate && \
    export LD_RUN_PATH=$LOC/instantclient_12_1 && \
    pip install -r $RNACENTRAL_HOME/rnacentral/requirements.txt

# Expose a container port where the website is served
EXPOSE 8000

# Start up the app
ENTRYPOINT \
    source $LOC/virtualenvs/RNAcentral/bin/activate && \
    supervisord -c $RNACENTRAL_HOME/supervisor/supervisor.conf && \
    python $RNACENTRAL_HOME/rnacentral/manage.py runserver 0.0.0.0:8000
