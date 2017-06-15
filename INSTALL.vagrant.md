# Vagrant

[Vagrant](http://www.vagrantup.com/) is a wrapper around
[VirtualBox](http://www.virtualbox.org/).

It can create a virtual machine on your computer and configure it, so that you
can instantly start developing.  You need to follow these steps to make it work
on your machine:

* Make sure you have [Ruby](http://www.ruby-lang.org/de/) and
  [gem](http://rubygems.org/) installed
* Install VirtualBox through your package manager or from
  [here](https://www.virtualbox.org/wiki/Downloads)
* Install Vagrant by downloading and installing the right package from
  <http://downloads.vagrantup.com/>

Now that you have the necessary tools it is time to create and start the virtual machine:

    # create and start virtual machine
    vagrant up

Once the virtual machine has started it will begin to configure itself with the
necessary things to run a *SkyLines* development server on it. As soon as it is
finished you can call `vagrant ssh` to access the virtual machine from the
terminal. The shared folder with the *SkyLines* code can be found at
`/vagrant`.

# Frontend installation

The frontend is based on ember, a nodejs framework. Unfortunately nodejs/npm is quite resource-intensive,
so it's recommended to build the frontend on the host machine.

* Install [NodeJS](https://nodejs.org/) and [bower](https://bower.io/)

Now you can start and build the frontend with ember:

```
cd ember
npm install
bower install
node_modules/.bin/ember build
```
