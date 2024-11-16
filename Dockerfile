#------------------------------------------------------------------------------
#
# This Dockerfile is meant for containerized deployment with Kubernetes.
#
#-------------------------------------------------------------------------------

FROM python:3.8.15-slim

RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    curl \
    tar \
    git \
    vim && \
    rm -rf /var/lib/apt/lists/*

ENV RNACENTRAL_LOCAL=/srv/rnacentral/local
ARG LOCAL_DEVELOPMENT

# Create folders
RUN \
    mkdir -p $RNACENTRAL_LOCAL && \
    mkdir /srv/rnacentral/log && \
    mkdir /srv/rnacentral/static

# Install node.js
RUN \
    cd $RNACENTRAL_LOCAL && \
    curl -sL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# Create the rnacentral user
RUN useradd -m -d /srv/rnacentral -s /bin/bash rnacentral

# Set work directory
ENV RNACENTRAL_HOME=/srv/rnacentral/rnacentral-webcode
RUN mkdir -p $RNACENTRAL_HOME
WORKDIR $RNACENTRAL_HOME

# Copy requirements
COPY rnacentral/requirements.txt .

# Install requirements
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Install NPM dependencies
ADD rnacentral/portal/static/package.json rnacentral/portal/static/
RUN cd rnacentral/portal/static && npm install --only=production

# Copy and chown all the files to the rnacentral user
COPY rnacentral $RNACENTRAL_HOME/rnacentral
RUN chown -R rnacentral:rnacentral /srv

# Install and configure packages for local development if needed
RUN \
    LOCAL_DEV="${LOCAL_DEVELOPMENT:-False}" && \
    if [ "$LOCAL_DEV" = "True" ] ; then \
        pip3 install -r rnacentral/requirements_dev.txt ; \
        sed -i "13 a import debug_toolbar" "${RNACENTRAL_HOME}"/rnacentral/rnacentral/urls.py ; \
        sed -i "30 a \ \ \ \ url(r'^__debug__/', include(debug_toolbar.urls))," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/urls.py ; \
        sed -i "126 a \ \ \ \ 'debug_toolbar.middleware.DebugToolbarMiddleware'," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/settings.py ; \
        sed -i "188 a \ \ \ \ 'debug_toolbar'," "${RNACENTRAL_HOME}"/rnacentral/rnacentral/settings.py ; \
    fi

# Set user
USER rnacentral

# Run entrypoint
COPY ./entrypoint.sh $RNACENTRAL_HOME
ENTRYPOINT ["/srv/rnacentral/rnacentral-webcode/entrypoint.sh"]

CMD ["gunicorn", "--chdir", "/srv/rnacentral/rnacentral-webcode/rnacentral", "--bind", "0.0.0.0:8000", "rnacentral.wsgi:application", "--worker-class", "gthread", "--threads", "4", "--keep-alive", "10", "--workers", "4", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "--log-level=debug", "--access-logfile", "/dev/stdout", "--error-logfile", "/dev/stderr"]
