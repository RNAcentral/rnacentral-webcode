#------------------------------------------------------------------------------
#
# This Dockerfile is meant for containerized deployment with Kubernetes.
#
#-------------------------------------------------------------------------------

FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    curl \
    tar \
    git \
    vim \
    supervisor && \
    rm -rf /var/lib/apt/lists/*

ENV RNACENTRAL_LOCAL=/srv/rnacentral/local
ENV SUPERVISOR_CONF_DIR=/srv/rnacentral/supervisor
ARG LOCAL_DEVELOPMENT

# Create folders
RUN \
    mkdir -p $RNACENTRAL_LOCAL && \
    mkdir -p $SUPERVISOR_CONF_DIR && \
    mkdir /srv/rnacentral/log

# Install Infernal and node.js
RUN \
    cd $RNACENTRAL_LOCAL && \
    curl -OL http://eddylab.org/infernal/infernal-1.1.1.tar.gz && \
    tar -xvzf infernal-1.1.1.tar.gz && \
    cd infernal-1.1.1 && \
    ./configure --prefix=$RNACENTRAL_LOCAL/infernal-1.1.1 && \
    make && \
    make install && \
    cd easel && \
    make install && \
    cd $RNACENTRAL_LOCAL && \
    rm infernal-1.1.1.tar.gz && \
    curl -sL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# Create the rnacentral user
RUN useradd -m -d /srv/rnacentral -s /bin/bash rnacentral

# Set work directory
ENV RNACENTRAL_HOME=/srv/rnacentral/rnacentral-webcode
RUN mkdir -p $RNACENTRAL_HOME
WORKDIR $RNACENTRAL_HOME

# Copy requirements
COPY rnacentral/requirements* .

# Install requirements
RUN pip3 install -r requirements.txt

# Install packages for local development if needed
RUN \
    LOCAL_DEV="${LOCAL_DEVELOPMENT:-False}" && \
    if [ "$LOCAL_DEV" = "True" ] ; then pip3 install -r requirements_dev.txt ; fi

# Install NPM dependencies
ADD rnacentral/portal/static/package.json rnacentral/portal/static/
RUN cd rnacentral/portal/static && npm install --only=production

# Copy and chown all the files to the rnacentral user
COPY rnacentral/ $RNACENTRAL_HOME/
RUN chown -R rnacentral:rnacentral /srv/rnacentral

# Set user
USER rnacentral

# Run entrypoint
COPY ./entrypoint.sh $RNACENTRAL_HOME
ENTRYPOINT ["/srv/rnacentral/rnacentral-webcode/entrypoint.sh"]

# Supervisor
CMD [ "/bin/sh", "-c", "/usr/bin/supervisord -c ${SUPERVISOR_CONF_DIR}/supervisord.conf" ]
