# Docker

[Docker](http://www.docker.com/) can be used to set up a development environment
for *SkyLines*, even if you're not running Linux as your operating system.

The environment configuration is described in the
[docker-compose.yml](docker-compose.yml) file.

The same setup is also used on GitHub to run the tests.

## docker-compose

[docker-compose](https://docs.docker.com/compose/) can be used to run and
coordinate multiple containers in parallel. Once you have it
[installed](https://docs.docker.com/compose/install/), you should be able to
run `docker-compose up` to automatically build the necessary container images
and run them.

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

```
docker-compose run api pipenv run pytest -vv
```

You can restrict the unit tests to run by passing a file or a folder:

```
docker-compose run api pipenv run pytest -vv tests/api/views/clubs/
```

See the [pytest documentation](https://docs.pytest.org/en/stable/contents.html)
for more details.

## Frontend installation

The frontend is based on Ember.js. It is recommended to build the frontend on
the host machine directly for improved performance.

* Install [Node.js](https://nodejs.org/) and [bower](https://bower.io/)

Now you can start and build the frontend:

```
cd ember
npm install
bower install
node_modules/.bin/ember build
```
