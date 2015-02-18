# Vagrant

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
* Local (host machine) python virtual environment  
In local python or skylines virtual environment install the following packages needed 
for fabric provisioning. 
        
        $ mkvirtualenv skylines
        $ workon skylines
        $ pip install fabtools
        $ pip install cuisine
        
        if you have problems on osx try
        $ pip install pycrypto==2.3
        $ pip install fabric 
             
        
Now that you have the necessary tools it is time to create and start the virtual machine:

# create and start virtual machine
    host_machine:$ vagrant up
    
Once the virtual machine has started provision it with:
 
    # source activate local virtual environment
    host_machine:$ fab vagrant provision 
 
Fabric script wil install all necessary things to run a *SkyLines* development server on it. 
As soon as it is finished you can call `vagrant ssh` to access the virtual machine from the
terminal. The shared folder with the *SkyLines* code can be found at
`/vagrant`.    

# After vagrant box has been provisioned
        host_machine:$ vagrant ssh
        vagrant:$ workon skylines
        vagrant:$ python ./manage.py db create
        vagrant:$ python ./manage.py import welt2000 --commit
        
        # run dev server visible on host machine
        vagrant:$ python manage.py runserver -t 0.0.0.0 -p 5000
        
        # run celery 
        vagrant:$ python ./manage.py celery runworker                
    
# Fabric
- <http://fabric.readthedocs.org>
- <http://fabtools.readthedocs.org/>
- <https://github.com/sebastien/cuisine>

