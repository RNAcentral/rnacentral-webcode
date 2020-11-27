#------------------------------------------------------------------------------
#
# This Dockerfile is meant for containerized deployment with Kubernetes.
#
#-------------------------------------------------------------------------------

FROM python:3.7-slim

RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    curl \
    tar \
    git \
    vim \
    supervisor && \
    useradd -m -d /srv/rnacentral -s /bin/bash rnacentral

ENV RNACENTRAL_HOME=/srv/rnacentral
ENV RNACENTRAL_LOCAL=$RNACENTRAL_HOME/local
ENV SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/srv/rnacentral/supervisor"}
ARG RNACENTRAL_BRANCH

# Create folders. Install Infernal and node.js
RUN \
    mkdir -p $RNACENTRAL_HOME/local && \
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

USER rnacentral

# Download RNAcentral, install requirements and node.js dependencies
RUN \
    cd $RNACENTRAL_HOME && \
    BRANCH="${RNACENTRAL_BRANCH:-master}" && \
    git clone -b "$BRANCH" https://github.com/RNAcentral/rnacentral-webcode.git && \
    pip3 install -r $RNACENTRAL_HOME/rnacentral-webcode/rnacentral/requirements.txt && \
    cd $RNACENTRAL_HOME/rnacentral-webcode/rnacentral/portal/static && npm install --only=production && \
    mkdir $RNACENTRAL_HOME/static

WORKDIR $RNACENTRAL_HOME/rnacentral-webcode
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh", "-c", "/usr/bin/supervisord -c ${SUPERVISOR_CONF_DIR}/supervisord.conf" ]
