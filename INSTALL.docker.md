# Docker

[docker](http://www.docker.com/) can be used to easily set up a development
environment for *SkyLines*.

The environment configuration is described in [docker-compose.yml](docker-compose.yml).

The same environment is used on github to run the tests.

## Direct usage

If you are familiar with [Docker](http://www.vagrantup.com/), you can use 
[docker-compose.yml](docker-compose.yml) to set up your development environment.

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

To execute the unit tests, launch:

```
root@xxx:/home/skylines/code# pipenv run py.test -vv
```

You can restrict the unit tests to run by passing a file or a folder:

```
pipenv run py.test -vv tests/api/views/clubs/
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
