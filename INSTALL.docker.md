# Docker

[Docker](http://www.docker.com/) can be used to set up a development environment
for *SkyLines*, even if you're not running Linux as your operating system.

The environment configuration is described in the
[docker-compose.yml](docker-compose.yml) file.

The same setup is also used on GitHub to run the tests.

## Quick start (recommended)

The simplest way to run SkyLines is with the multi-stage Dockerfile, which
builds the Ember frontend inside the image — no host Node/yarn required:

```bash
docker compose -f docker-compose.yml up --build
```

This runs only `docker-compose.yml` (ignoring the dev override file) so the
baked frontend assets from the Dockerfile's Ember build stage are used.

Open <http://localhost/> to see the app.

## Development with docker-compose.override.yml

The repo includes a `docker-compose.override.yml` that exposes debug ports
and bind-mounts source directories for live backend reloading. Docker Compose
automatically merges it when you run:

```bash
docker compose up --build
```

**Important caveat:** the override bind-mounts `./skylines` over the image's
`/home/skylines/code/skylines` directory. This hides the baked frontend assets
at `skylines/frontend/static/` (including `index.html`), so the app will return
HTTP 500 if that directory doesn't exist on the host.

### Option A — Copy frontend assets from a one-off build (no host yarn)

Build a temporary frontend image and copy the assets out:

```bash
docker build --target frontend -t skylines-frontend .
docker run --rm skylines-frontend tar -C /build -cf - skylines/frontend/static | tar -xf -
```

Now `./skylines/frontend/static/` exists on the host and the bind-mount works.
Re-run these commands whenever you update `ember/` and need a fresh frontend.

### Option B — Build on the host (if you have Node/yarn)

If you already have Node 20+ and yarn installed:

```bash
cd ember
yarn install --frozen-lockfile
yarn build          # outputs to ../skylines/frontend/static/
cd ..
docker compose up --build
```

### Option C — Skip the override entirely

If you only need to run the app (not edit backend code with live reload):

```bash
docker compose -f docker-compose.yml up --build
```

## Usage with VSCode

If you are less familiar with Docker, [VSCode](https://code.visualstudio.com/) 
makes it easy to bootstrap a development environment to start tinkering with
the *SkyLines* backend code.

All you need to do is install [docker](http://www.vagrantup.com/), 
[VSCode](https://code.visualstudio.com/) and the [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

Check [the documentation](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
for detailed instructions. You can also check a [tutorial](https://docs.microsoft.com/en-us/learn/modules/use-docker-container-dev-env-vs-code/2-use-as-development-environment).

Once you have everything installed you can run the 
`Remote-Containers: ReOpen in Container...` command, and your workspace will be
re-opened from inside the container.

## Running tests

If you want to run the testsuite, launch:

```bash
docker compose run api pipenv run pytest -vv
```

You can restrict the unit tests to run by passing a file or a folder:

```bash
docker compose run api pipenv run pytest -vv tests/api/views/clubs/
```

See the [pytest documentation](https://docs.pytest.org/en/stable/contents.html)
for more details.
