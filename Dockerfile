# =============================================================================
# Stage 1: Build the Ember.js frontend
# =============================================================================
FROM node:14-buster AS frontend

RUN npm install -g bower

WORKDIR /build

# Install JS dependencies first (cached layer)
COPY ember/package.json ember/yarn.lock ember/bower.json /build/ember/
RUN cd /build/ember && yarn install --frozen-lockfile --non-interactive
RUN cd /build/ember && bower install --allow-root

# Copy the full ember source and build
COPY ember/ /build/ember/

# git-repo-info needs a git repo to read the SHA; create a stub so it
# doesn't return null (which crashes ember-cli with "slice of null").
RUN cd /build/ember && \
    git init && \
    git config user.email "build@docker" && \
    git config user.name "docker" && \
    git add -A && \
    git commit -m "docker build"

# .ember-cli sets outputPath to ../skylines/frontend/static
RUN mkdir -p /build/skylines/frontend
RUN cd /build/ember && yarn build --environment=production


# =============================================================================
# Stage 2: Python backend + MapServer on Debian Buster
# =============================================================================
FROM debian:buster-slim AS backend

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1

# Buster is archived; point apt to archive.debian.org
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    python2.7 \
    python-pip \
    python-setuptools \
    python-wheel \
    python-dev \
    build-essential \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    libffi-dev \
    libssl-dev \
    libboost-python-dev \
    zlib1g-dev \
    cmake \
    cgi-mapserver \
    libmapserver-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv==2020.11.15

WORKDIR /home/skylines/code

# Install Python dependencies from lockfile.
# Export requirements.txt so pip installs packages individually (avoids
# a single failing C++ build from blocking pure-Python packages).
COPY Pipfile Pipfile.lock /home/skylines/code/
RUN pipenv lock -r > /tmp/requirements.txt 2>/dev/null && \
    grep -v xcsoar /tmp/requirements.txt > /tmp/requirements-core.txt && \
    pip install -r /tmp/requirements-core.txt && \
    pip install xcsoar==0.7.0

# Copy application code
COPY skylines/ /home/skylines/code/skylines/
COPY config/ /home/skylines/code/config/
COPY migrations/ /home/skylines/code/migrations/
COPY backend/ /home/skylines/code/backend/
COPY mapproxy/ /home/skylines/code/mapproxy/
COPY mapserver/ /home/skylines/code/mapserver/
COPY manage.py wsgi_skylines.py wsgi_mapproxy.py /home/skylines/code/
COPY pytest.ini /home/skylines/code/

# Copy built frontend assets from Stage 1
COPY --from=frontend /build/skylines/frontend/static/ /home/skylines/code/skylines/frontend/static/

# Create directories for runtime data
RUN mkdir -p /home/skylines/code/htdocs/files \
             /home/skylines/code/htdocs/srtm

EXPOSE 5000

ENV SKYLINES_CONFIG=/home/skylines/code/config/docker.py

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "wsgi_skylines:application"]
