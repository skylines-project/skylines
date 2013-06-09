# Vagrant

*Note: This is currently unmaintained and installs PostGIS 1.5 instead of the
necessary 2.x version!*

[Vagrant](http://www.vagrantup.com/) is a wrapper around
[VirtualBox](http://www.virtualbox.org/) and
[Chef](http://www.opscode.com/chef/) (or [Puppet](https://puppetlabs.com/)).

It can create a virtual machine on your computer and configure it, so that you
can instantly start developing.  You need to follow these steps to make it work
on your machine:

* Make sure you have [Ruby](http://www.ruby-lang.org/de/) and
  [gem](http://rubygems.org/) installed
* Install VirtualBox through your package manager or from
  [here](https://www.virtualbox.org/wiki/Downloads)
* Install Vagrant by downloading and installing the right package from
  <http://downloads.vagrantup.com/>
* Install [Librarian](https://github.com/applicationsonline/librarian) for Chef
  by calling: `gem install librarian`

Now that you have the necessary tools it is time to create and start the virtual machine:

    # download necessary chef cookbooks
    librarian-chef install

    # create and start virtual machine
    vagrant up

Once the virtual machine has started it will begin to configure itself with the
necessary things to run a *SkyLines* development server on it. As soon as it is
finished you can call `vagrant ssh` to access the virtual machine from the
terminal. The shared folder with the *SkyLines* code can be found at
`/vagrant`.
